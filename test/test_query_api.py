import argparse
import requests

# --- CLI ARGUMENTS ---
parser = argparse.ArgumentParser(description="Query MusicBrainz and iTunes for album metadata and artwork availability.")
parser.add_argument("--band", required=True, help="Artist/Band name (e.g. 'Iron Maiden')")
parser.add_argument("--album", required=True, help="Album name (e.g. 'Best Of The Beast')")
args = parser.parse_args()

artist = args.band
album = args.album

headers = {
    "User-Agent": "AlbumArtChecker/1.0 (you@example.com)"
}

# ============================
# 🎯 MUSICBRAINZ TEST
# ============================

print(f"\n🔍 Querying MusicBrainz for '{artist} - {album}'...\n")

query_url = (
    f"https://musicbrainz.org/ws/2/release/?query=release:\"{album}\"%20AND%20artist:\"{artist}\""
    "&fmt=json&limit=20"
)

try:
    response = requests.get(query_url, headers=headers, verify=False)
    response.raise_for_status()
except Exception as e:
    print(f"❌ MusicBrainz Error: {e}")
    exit()

releases = response.json().get("releases", [])

if not releases:
    print("❌ No MusicBrainz releases found.")
else:
    print(f"✅ Found {len(releases)} MusicBrainz releases:\n")
    for r in releases:
        title = r.get("title", "N/A")
        date = r.get("date", "Unknown")
        country = r.get("country", "??")
        release_id = r.get("id", "")
        label_info = r.get("label-info", [])
        label = label_info[0]['label']['name'] if label_info else "Unknown label"

        # Check for cover art via metadata endpoint
        cover_meta_url = f"https://coverartarchive.org/release/{release_id}"
        try:
            art_resp = requests.get(cover_meta_url, headers=headers, verify=False)
            has_art = False
            if art_resp.status_code == 200:
                images = art_resp.json().get("images", [])
                has_front = any(img.get("front") for img in images)
                has_art = has_front or len(images) > 0
        except Exception:
            has_art = False

        art_status = "🎨 Artwork Available" if has_art else "🚫 No Artwork"
        print(f"🎵 {title} ({date}) [{country}] — {label}")
        print(f"   🔗 https://musicbrainz.org/release/{release_id}")
        print(f"   🖼️  {art_status}\n")

# ============================
# 🍏 iTUNES TEST
# ============================

print(f"\n🍏 Querying iTunes for '{artist} - {album}'...\n")

itunes_url = f"https://itunes.apple.com/search?term={requests.utils.quote(artist + ' ' + album)}&media=music&entity=album&limit=10"

try:
    itunes_response = requests.get(itunes_url)
    itunes_response.raise_for_status()
except Exception as e:
    print(f"❌ iTunes Error: {e}")
    exit()

itunes_data = itunes_response.json()
results = itunes_data.get("results", [])

if not results:
    print("❌ No iTunes results found.")
else:
    found = False
    for result in results:
        r_artist = result.get("artistName", "").lower()
        r_album = result.get("collectionName", "")
        if artist.lower() in r_artist:
            artwork_url = result.get("artworkUrl100", "").replace("100x100bb", "600x600bb")
            print(f"🎵 {r_album} — by {result['artistName']}")
            print(f"   🖼️  Artwork URL: {artwork_url}\n")
            found = True

    if not found:
        print("⚠️ iTunes returned results, but none matched the expected artist.")

