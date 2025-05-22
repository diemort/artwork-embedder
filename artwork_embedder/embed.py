"""
artwork_embedder.embed
Core logic for embedding and cleaning album artwork in MP3 files.
"""

from pathlib import Path
import music_tag
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3

from .itunes_utils import search_album_art
from .musicbrainz_utils import search_album_art_musicbrainz
from .acoustid_utils import recognize_with_acoustid
from .utils import download_image, clean_album_name

def embed_artwork(mp3_path, image_data, band_name):
    """Embed album artwork into a given MP3 file."""
    if not image_data:
        print(f"No image data for {mp3_path.name}")
        return
    try:
        f = music_tag.load_file(mp3_path)
        current_artist = str(f['artist']).lower()
        has_art = f['artwork'].value is not None
        if has_art and band_name.lower() in current_artist:
            print(f"Skipping (correct artwork already present): {mp3_path.name}")
            return
        if has_art and band_name.lower() not in current_artist:
            print(f"Replacing potentially incorrect artwork in: {mp3_path.name}")
        f['artwork'] = image_data
        f.save()
        print(f"Embedded artwork with music-tag: {mp3_path.name}")
    except Exception as e:
        print(f"music-tag failed on {mp3_path.name}, trying mutagen...")
        try:
            audio = MP3(mp3_path, ID3=ID3)
            if audio.tags is None:
                audio.add_tags()
            audio.tags.delall("APIC")
            audio.tags.add(
                APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=image_data
                )
            )
            audio.save()
            print(f"Embedded artwork with mutagen: {mp3_path.name}")
        except Exception as e2:
            print(f"Failed to embed artwork in {mp3_path.name}: {e2}")

def process_album_folder(folder_path, band_name):
    """Process a folder of MP3s using band and album names for artwork search."""
    folder = Path(folder_path)
    mp3_files = list(folder.rglob("*.mp3"))
    if not mp3_files:
        print(f"No MP3s in {folder.name}")
        return
    print(f"\nProcessing folder: {folder.name}")
    album_name = clean_album_name(folder.name)
    search_query = f"{band_name} {album_name}"
    album_art_url = search_album_art(search_query, expected_artist=band_name)
    if not album_art_url:
        print("Trying MusicBrainz + Cover Art Archive...")
        album_art_url = search_album_art_musicbrainz(band_name, album_name)
    if not album_art_url:
        print("Using AcoustID fallback...")
        album_info = recognize_with_acoustid(mp3_files[0])
        if album_info:
            fallback_query = f"{band_name} {album_info}"
            album_art_url = search_album_art(fallback_query, expected_artist=band_name)
    if album_art_url:
        art_data = download_image(album_art_url)
        if art_data:
            for mp3 in mp3_files:
                embed_artwork(mp3, art_data, band_name)
        else:
            print("Could not download album art.")
    else:
        print("No album art found.")

def process_all_folders(root_path, band_name, target_album=None):
    """Process all subfolders for artwork embedding."""
    root = Path(root_path)
    for folder in root.iterdir():
        if folder.is_dir():
            album_name = clean_album_name(folder.name)
            if target_album and album_name.lower() != target_album.lower():
                continue
            process_album_folder(folder, band_name)

def process_files_individually(root_path, band_name=None):
    """Process individual MP3 files and try to embed artwork."""
    root = Path(root_path)
    mp3_files = list(root.glob("*.mp3"))
    if not mp3_files:
        print("No MP3 files found at top level of music folder.")
        return
    for mp3 in mp3_files:
        base_name = mp3.stem.replace('_', ' ').replace('-', ' ')
        search_query = f"{band_name} {base_name}" if band_name else base_name
        print(f"Searching for artwork using: {search_query}")
        album_art_url = search_album_art(search_query, expected_artist=band_name)
        if not album_art_url:
            print("Fallback to AcoustID fingerprinting...")
            album_info = recognize_with_acoustid(mp3)
            if album_info:
                fallback_query = f"{band_name} {album_info}" if band_name else album_info
                album_art_url = search_album_art(fallback_query)
        if album_art_url:
            art_data = download_image(album_art_url)
            if art_data:
                embed_artwork(mp3, art_data, band_name or "")
            else:
                print(f"Could not download image for {mp3.name}")
        else:
            print(f"No artwork found for {mp3.name}")

def clean_album_art(root_path, album_title):
    """Remove embedded album artwork from matching folders."""
    root = Path(root_path)
    normalized_target = album_title.lower().strip()
    for folder in root.iterdir():
        if folder.is_dir() and normalized_target in clean_album_name(folder.name).lower():
            print(f"\n Cleaning artwork in album: {folder.name}")
            mp3_files = list(folder.rglob("*.mp3"))
            for mp3 in mp3_files:
                try:
                    audio = MP3(mp3, ID3=ID3)
                    if audio.tags:
                        audio.tags.delall("APIC")
                        audio.save()
                        print(f"Removed artwork: {mp3.name}")
                    else:
                        print(f"No tags found in: {mp3.name}")
                except Exception as e:
                    print(f"Failed to clean artwork in {mp3.name}: {e}")

def download_cover_from_musicbrainz_id(release_id, folder_path):
    """Download artwork using MusicBrainz release ID."""
    headers = {
        "User-Agent": "MP3AlbumArtTool/1.0 (you@example.com)"
    }
    meta_url = f"https://coverartarchive.org/release/{release_id}"
    try:
        meta_response = requests.get(meta_url, headers=headers, verify=False)
        if meta_response.status_code == 200:
            images = meta_response.json().get("images", [])
            image_url = next((img["image"] for img in images if img.get("front")), None)
        else:
            image_url = None
    except Exception as e:
        print(f"Could not get metadata from Cover Art Archive: {e}")
        image_url = None

    if not image_url:
        image_url = f"https://coverartarchive.org/release/{release_id}/front-500"
        print(f"Falling back to standard front-500 URL:\n{image_url}")

    try:
        response = requests.get(image_url, headers=headers, verify=False)
        response.raise_for_status()
        image_data = response.content
    except Exception as e:
        print(f"Failed to download artwork: {e}")
        return

    folder = Path(folder_path)
    mp3_files = list(folder.rglob("*.mp3"))
    if not mp3_files:
        print(f"No MP3 files found in {folder}")
        return
    print(f"Embedding artwork into {len(mp3_files)} files in {folder.name}...")
    for mp3 in mp3_files:
        embed_artwork(mp3, image_data, "")

