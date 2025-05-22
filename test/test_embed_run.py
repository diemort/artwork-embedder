# test/test_all_cases.py
# This test script validates the embed_artwork.py functionality across 3 scenarios:
# 1. Embedding album art by looping over subfolders using iTunes metadata
# 2. Embedding album art by falling back to MusicBrainz
# 3. Embedding artwork in a single MP3 file using AcoustID fingerprinting

import os
import shutil
import subprocess
from pathlib import Path
from mutagen.id3 import ID3, APIC, ID3NoHeaderError

# Define paths and constants
TEST_ROOT = Path("test_embed")
LOCAL_MP3 = Path("Cosmonkey-Rainy.mp3")  # local source file
ORIG_FILENAME = "Cosmonkey-Rainy.mp3"
FILENAME_1A1B = "Rainy.mp3"
FILENAME_2 = ORIG_FILENAME
BAND = "Cosmonkey"
ALBUM = "Rainy"
SCRIPT_PATH = Path(__file__).resolve().parent.parent / "embed_artwork.py"

# Define the different test scenarios
cases = {
    "1a_itunes_folder": {
        "desc": "Subfolder search via iTunes",
        "folder": TEST_ROOT / "1a_itunes_folder" / BAND / ALBUM,
        "args": ["--folders"],
        "filename": FILENAME_1A1B,
        "pass_album": False
    },
    "1b_musicbrainz_folder": {
        "desc": "Subfolder search via MusicBrainz fallback",
        "folder": TEST_ROOT / "1b_musicbrainz_folder" / BAND / ALBUM,
        "args": ["--folders"],
        "filename": FILENAME_1A1B,
        "pass_album": False
    },
    "2_acoustid_file": {
        "desc": "Single file via AcoustID",
        "folder": TEST_ROOT / "2_acoustid_file",
        "args": ["--files"],
        "filename": FILENAME_2,
        "pass_album": True
    },
}

# Collect results from each test case
summary = {}

# Copies the local MP3 file into the test directory
def prepare_mp3(target_path):
    if target_path.exists():
        print(f"MP3 already exists at {target_path}, skipping copy.")
        return

    if not LOCAL_MP3.exists():
        raise FileNotFoundError(f"Local source MP3 not found: {LOCAL_MP3}")

    target_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Copying {LOCAL_MP3} to {target_path}...")
    shutil.copyfile(LOCAL_MP3, target_path)

# Runs an individual test case and checks for embedded artwork
def run_case(key, config):
    folder = config["folder"]
    filename = config["filename"]
    mp3_path = folder / filename
    prepare_mp3(mp3_path)

    print(f"\nRunning case: {config['desc']}")
    print(f"Searching iTunes for: {BAND} - {ALBUM}")
    print(f"Searching MusicBrainz for: {BAND} - {ALBUM}")

    cmd = [
        "python3", str(SCRIPT_PATH),
        "--music-folder", str(folder.parent.parent if config["args"] == ["--folders"] else folder),
        "--band", BAND
    ]

    if config.get("pass_album", True):
        cmd += ["--album", ALBUM]

    cmd += config["args"]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("=== STDOUT ===")
    print(result.stdout)
    print("=== STDERR ===")
    print(result.stderr)

    try:
        try:
            audio = ID3(mp3_path)
        except ID3NoHeaderError:
            audio = ID3()
            audio.save(mp3_path)
            audio = ID3(mp3_path)

        has_art = any(isinstance(f, APIC) for f in audio.values())
        summary[key] = (True, config["desc"]) if has_art else (False, f"{config['desc']} (No artwork embedded)")
    except Exception as e:
        summary[key] = (False, f"{config['desc']} (Error: {e})")

# Run all test cases
if __name__ == "__main__":
    if TEST_ROOT.exists():
        shutil.rmtree(TEST_ROOT)

    for key, cfg in cases.items():
        run_case(key, cfg)

    print("\nSummary:")
    for key, (ok, note) in summary.items():
        status = "OK" if ok else "FAIL"
        print(f"{status} - {note}")
