"""
artwork_embedder.acoustid_utils
Utilities for AcoustID fingerprint recognition.
"""

import os
import acoustid
from dotenv import load_dotenv

# Load environment variable for AcoustID API key
load_dotenv()
ACOUSTID_API_KEY = os.getenv("ACOUSTID_API_KEY")

def recognize_with_acoustid(mp3_path):
    """
    Identify the song by its audio fingerprint using AcoustID.

    Args:
        mp3_path (Path): Path to the MP3 file.

    Returns:
        str or None: A string like "Artist Title" if a match is found, else None.
    """
    if not ACOUSTID_API_KEY:
        print("⚠️  AcoustID API key not set. Skipping AcoustID lookup.")
        return None

    try:
        results = acoustid.match(ACOUSTID_API_KEY, str(mp3_path))
        for score, rid, title, artist in results:
            if title and artist:
                print(f"🎵 Fingerprinted: {artist} - {title}")
                return f"{artist} {title}"
    except Exception as e:
        print(f"⚠️ AcoustID error for {mp3_path.name}: {e}")
    return None

