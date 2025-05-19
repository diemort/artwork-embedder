import os
import re
import requests
from pathlib import Path
import music_tag
from dotenv import load_dotenv
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3
import acoustid
import argparse
import musicbrainzngs

# Load API key from .env
load_dotenv()
ACOUSTID_API_KEY = os.getenv("ACOUSTID_API_KEY")
if not ACOUSTID_API_KEY:
    ACOUSTID_API_KEY = input("🔑 Enter your AcoustID API key: ")

def recognize_with_acoustid(mp3_path):
    try:
        results = acoustid.match(ACOUSTID_API_KEY, str(mp3_path))
        for score, rid, title, artist in results:
            if title and artist:
                print(f"🎵 Fingerprinted: {artist} - {title}")
                return f"{artist} {title}"
    except Exception as e:
        print(f"⚠️ AcoustID error for {mp3_path.name}: {e}")
    return None

# Configure MusicBrainz
musicbrainzngs.set_useragent("MP3AlbumArtTool", "1.0", "your-email@example.com")

import requests

def search_album_art_musicbrainz(band_name, album_name):
    """
    Search MusicBrainz for all releases that match the given band and album name.
    Return the first cover image URL from Cover Art Archive that has a valid front image.
    """
    headers = {
        "User-Agent": "MP3AlbumArtTool/1.0 (you@example.com)"
    }

    query_url = (
        f"https://musicbrainz.org/ws/2/release/?query=release:\"{album_name}\"%20AND%20artist:\"{band_name}\""
        "&fmt=json&limit=20"
    )

    try:
        response = requests.get(query_url, headers=headers, verify=False)
        if response.status_code != 200:
            print(f"❌ Failed to query MusicBrainz: {response.status_code}")
            return None

        releases = response.json().get("releases", [])
        if not releases:
            print("❌ MusicBrainz: No matching releases found.")
            return None

        print(f"🎯 MusicBrainz returned {len(releases)} possible releases.")

        for release in releases:
            release_id = release.get("id")
            title = release.get("title", "Unknown Title")
            date = release.get("date", "Unknown Date")
            artist_credit = release.get("artist-credit", [])
            artist = artist_credit[0]["name"] if artist_credit else band_name

            cover_meta_url = f"https://coverartarchive.org/release/{release_id}"
            try:
                art_resp = requests.get(cover_meta_url, headers=headers, verify=False)
                if art_resp.status_code == 200:
                    images = art_resp.json().get("images", [])
                    for img in images:
                        if img.get("front"):
                            print(f"✅ Found artwork for release: {title} by {artist} ({date})")
                            return f"https://coverartarchive.org/release/{release_id}/front-500"
                else:
                    print(f"🚫 No artwork metadata for: {title} ({release_id})")
            except Exception as e:
                print(f"⚠️ Error checking artwork for {release_id}: {e}")

        print("❌ No releases with valid artwork found.")
        return None

    except Exception as e:
        print(f"❌ MusicBrainz query failed: {e}")
        return None

def search_album_art(query, expected_artist=None):
    try:
        url = f"https://itunes.apple.com/search?term={requests.utils.quote(query)}&media=music&entity=album&limit=10"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data['resultCount'] == 0:
            print("❌ No results found.")
            return None

        expected = expected_artist.lower() if expected_artist else None

        for result in data['results']:
            result_artist = result.get('artistName', '').lower()
            if expected and expected in result_artist:
                print(f"✅ Found album: {result['collectionName']} by {result['artistName']}")
                return result['artworkUrl100'].replace('100x100bb', '600x600bb')

        print(f"❌ No album art found matching artist '{expected_artist}'.")
        return None  # no fallback to wrong artist!

    except Exception as e:
        print(f"⚠️ Failed to search album art: {e}")
        return None

def download_image(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.content
    except Exception as e:
        print(f"⚠️ Download failed: {e}")
        return None

def embed_artwork(mp3_path, image_data, band_name):
    if not image_data:
        print(f"⚠️ No image data for {mp3_path.name}")
        return

    try:
        f = music_tag.load_file(mp3_path)

        current_artist = str(f['artist']).lower()
        has_art = f['artwork'].value is not None

        # If artwork is present and artist matches, skip
        if has_art and band_name.lower() in current_artist:
            print(f"⏭️  Skipping (correct artwork already present): {mp3_path.name}")
            return

        # If artwork is present but artist tag is incorrect, replace
        if has_art and band_name.lower() not in current_artist:
            print(f"♻️ Replacing potentially incorrect artwork in: {mp3_path.name}")

        f['artwork'] = image_data
        f.save()
        print(f"✅ Embedded artwork with music-tag: {mp3_path.name}")
    except Exception as e:
        print(f"⚠️ music-tag failed on {mp3_path.name}, trying mutagen...")

        try:
            audio = MP3(mp3_path, ID3=ID3)
            if audio.tags is None:
                audio.add_tags()

            # Remove old APIC frame(s) if any
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
            print(f"✅ Embedded artwork with mutagen: {mp3_path.name}")
        except Exception as e2:
            print(f"❌ Failed to embed artwork in {mp3_path.name}: {e2}")

def clean_album_name(folder_name):
    # Step 1: Remove leading [YYYY]
    name = re.sub(r"^\[\d{4}\]\s*", "", folder_name)

    # Step 2: Remove any trailing/embedded (Text) or [Text]
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"\[.*?\]", "", name)

    # Step 3: Clean extra spaces
    return name.strip()

def process_album_folder(folder_path, band_name):
    folder = Path(folder_path)
    mp3_files = list(folder.rglob("*.mp3"))  # Recursive search in case of "CD 1", "CD 2", etc.

    if not mp3_files:
        print(f"🚫 No MP3s in {folder.name}")
        return

    print(f"\n📁 Processing folder: {folder.name}")

    album_name = clean_album_name(folder.name)
    search_query = f"{band_name} {album_name}"

    # Try iTunes API: band + album
    album_art_url = search_album_art(search_query, expected_artist=band_name)

    # Fallback 1: try MusicBrainz + Cover Art Archive
    if not album_art_url:
        print("🎯 Trying MusicBrainz + Cover Art Archive...")
        album_art_url = search_album_art_musicbrainz(band_name, album_name)

    # Fallback 2: AcoustID (only if nothing else worked)
    if not album_art_url:
        print("🔍 Using AcoustID fallback...")
        album_info = recognize_with_acoustid(mp3_files[0])
        if album_info:
            fallback_query = f"{band_name} {album_info}"
            album_art_url = search_album_art(fallback_query, expected_artist=band_name)

    # If found, download and embed
    if album_art_url:
        art_data = download_image(album_art_url)
        if art_data:
            for mp3 in mp3_files:
                embed_artwork(mp3, art_data, band_name)
        else:
            print("⚠️ Could not download album art.")
    else:
        print("❌ No album art found.")

def clean_album_art(root_path, album_title):
    root = Path(root_path)
    normalized_target = album_title.lower().strip()

    for folder in root.iterdir():
        if folder.is_dir() and normalized_target in clean_album_name(folder.name).lower():
            print(f"\n🧹 Cleaning artwork in album: {folder.name}")
            mp3_files = list(folder.rglob("*.mp3"))
            for mp3 in mp3_files:
                try:
                    audio = MP3(mp3, ID3=ID3)
                    if audio.tags:
                        audio.tags.delall("APIC")
                        audio.save()
                        print(f"✅ Removed artwork: {mp3.name}")
                    else:
                        print(f"⏭️  No tags found in: {mp3.name}")
                except Exception as e:
                    print(f"❌ Failed to clean artwork in {mp3.name}: {e}")

def process_all_folders(root_path, band_name, target_album=None):
    root = Path(root_path)
    for folder in root.iterdir():
        if folder.is_dir():
            album_name = clean_album_name(folder.name)
            if target_album:
                if album_name.lower() != target_album.lower():
                    continue  # Skip non-matching folders
            process_album_folder(folder, band_name)

def main():
    parser = argparse.ArgumentParser(description="Embed or clean album art in MP3 files.")
    parser.add_argument("--music-folder", type=str, required=True, help="Path to folder with album subfolders.")
    parser.add_argument("--band", type=str, help="Band name for album art search (used when embedding).")
    parser.add_argument("--album", type=str, help="Only update artwork for this specific album (matches folder name).")
    parser.add_argument("--clean-album", type=str, help="Album name to clean (removes embedded artwork).")

    args = parser.parse_args()

    if args.clean_album:
        clean_album_art(args.music_folder, args.clean_album)
    elif args.band:
        process_all_folders(args.music_folder, args.band, target_album=args.album)
    else:
        print("❌ Please provide either --band for embedding or --clean-album for cleaning.")

if __name__ == "__main__":
    main()

