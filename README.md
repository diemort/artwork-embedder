# Artwork Embedder

A tool to search **iTunes** and **MusicBrainz** for album releases and automatically embed album artwork into the ID3 tags of MP3 files.

The script loops over folders inside the specified `--music-folder`, using the folder name as the album title (while ignoring leading dates or suffixes like disc numbers or tags).

---

## Setup

All required Python packages and system dependencies can be installed using:

```bash
bash setup_mp3_env.sh
```

The script detects your operating system and installs chromaprint, fpcalc, and the required Python modules in a virtual environment.

You’ll need an AcoustID API key if you want to enable audio fingerprint fallback. You can either:
	•	Add it directly to the top of the setup script (APIKEY=...)
	•	Or input it interactively when prompted.
 
## Usage

To process all albums in a music directory and embed album art using both iTunes and MusicBrainz:

```python
python3 embed_artwork.py --music-folder "<path-to-folder>" --band "<band-name>"
```

If you already know the MusicBrainz release ID for a specific album, you can bypass iTunes and metadata matching by directly embedding the artwork from the Cover Art Archive.

This is useful for:
	•	Ensuring accurate artwork for a specific release version
	•	Handling edge cases where iTunes or MusicBrainz search returns incorrect results

```python
python3 embed_artwork.py --music-folder "<path-to-albums>" \
                         --album "<album-name>" \
                         --brainz "<musicbrainz-release-id>"
```

This will:
	•	Locate the folder inside `--music-folder` whose name matches `--album` (ignoring leading years or tags)
	•	Download the artwork for the given MusicBrainz release ID
	•	Embed the cover into all .mp3 files inside that album folder

This option is ideal when you want full control over the exact release version being tagged.

## Clean existing artwork

To remove existing album art from MP3s in a given album folder:

```python
python3 embed_artwork.py --music-folder "<path-to-folder>" --band "<band-name>"
```

## Test Mode (iTunes, MusicBrainz & Embed Functionality)

This project includes automated tests for verifying artwork embedding logic using freely available MP3s.

### 1. Search Metadata Only

Use the following script to preview album metadata and check if artwork is available on both iTunes and MusicBrainz:

```bash
python3 test_query_api.py --band "Cosmonkey" --album "Rainy"
```

This returns a list of matching releases and indicates whether artwork is available for each.

2. Full Embed Test (All Modes)

The `test_embed_run.py` script runs all embedding modes:
	•	1a. Folder-based search via iTunes
	•	1b. Folder-based fallback via MusicBrainz
	•	2. Single file via fallback (no AcoustID)

To run all test modes:

```python
python3 test_embed_run.py
```

This will:
	•	Use the local test MP3 file `Cosmonkey-Rainy.mp3` (must be in the same folder)
	•	Copy it to test folders
	•	Attempt to embed artwork using the actual logic in `embed_artwork.py`

Each mode checks for:
	•	Metadata match
	•	Successful download of artwork
	•	Valid embedding using music-tag or mutagen

Test File

The MP3 file used in tests is:

🎵 Cosmonkey – Rainy

Make sure Cosmonkey-Rainy.mp3 is present in the same directory as the test scripts.

This track is freely available for download and use. It was originally obtained via YouTube, but you may substitute any valid MP3 if needed.
