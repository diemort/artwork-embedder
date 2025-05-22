"""
artwork_embedder.musicbrainz_utils
Functions to query MusicBrainz and Cover Art Archive for album artwork.
"""

import requests
import musicbrainzngs

# Configure MusicBrainz API user-agent
musicbrainzngs.set_useragent("MP3AlbumArtTool", "1.0", "your-email@example.com")

def search_album_art_musicbrainz(band_name, album_name):
    """
    Query MusicBrainz for album releases and retrieve album art from Cover Art Archive.

    Args:
        band_name (str): Artist/band name.
        album_name (str): Album title.

    Returns:
        str or None: URL to the front album cover if found, else None.
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
            print(f"Failed to query MusicBrainz: {response.status_code}")
            return None

        releases = response.json().get("releases", [])
        if not releases:
            print("MusicBrainz: No matching releases found.")
            return None

        print(f"MusicBrainz returned {len(releases)} possible releases.")

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
                            print(f"Found artwork for release: {title} by {artist} ({date})")
                            return f"https://coverartarchive.org/release/{release_id}/front-500"
                else:
                    print(f"No artwork metadata for: {title} ({release_id})")
            except Exception as e:
                print(f"Error checking artwork for {release_id}: {e}")

        print("No releases with valid artwork found.")
        return None

    except Exception as e:
        print(f"MusicBrainz query failed: {e}")
        return None

