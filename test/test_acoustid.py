import acoustid
import os
import argparse
from dotenv import load_dotenv

# Load API key from .env if available
load_dotenv()
API_KEY = os.getenv("ACOUSTID_API_KEY")

# CLI arguments
parser = argparse.ArgumentParser(description="Test AcoustID fingerprinting and lookup.")
parser.add_argument("file", type=str, help="Path to the MP3 file to test")
parser.add_argument("--key", type=str, help="AcoustID API key (overrides .env)")
args = parser.parse_args()

# Use API key from CLI if provided
if args.key:
    API_KEY = args.key

# Check if we have an API key
if not API_KEY:
    print("Error: AcoustID API key not found. Use --key or set it in .env")
    exit(1)

# Check if file exists
if not os.path.isfile(args.file):
    print(f"Error: File '{args.file}' not found.")
    exit(1)

# Step 1: Generate fingerprint
try:
    duration, fingerprint = acoustid.fingerprint_file(args.file)
    print(f"Fingerprint OK. Duration: {duration}s")
except Exception as e:
    print(f"Failed to generate fingerprint: {e}")
    exit(1)

# Step 2: Query AcoustID
try:
    print("Querying AcoustID...")
    result = acoustid.lookup(API_KEY, fingerprint, duration, meta="recordings+releasegroups+compress")

    if result.get("status") != "ok":
        print(f"AcoustID returned error: {result.get('status')}")
        print(result)
        exit(1)

    matches = result.get("results", [])
    if not matches:
        print("No matches found.")
    else:
        print(f"Top match:")
        for recording in matches[0].get("recordings", []):
            title = recording.get("title", "Unknown title")
            artists = recording.get("artists", [])
            artist_names = ", ".join(a['name'] for a in artists) if artists else "Unknown artist"
            print(f"{artist_names} - {title}")
except Exception as e:
    print(f"AcoustID request failed: {e}")
