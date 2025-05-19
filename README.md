# Artwork Embedder

A tool to search **iTunes** and **MusicBrainz** for album releases and automatically embed album artwork into the ID3 tags of MP3 files.

The script loops over folders inside the specified `--music-folder`, using the folder name as the album title (while ignoring leading dates or suffixes like disc numbers or tags).

---

## Setup

All required Python packages and system dependencies can be installed using:

```bash
./setup_mp3_env.sh
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

## Clean existing artwork

To remove existing album art from MP3s in a given album folder:

```python
python3 embed_artwork.py --music-folder "<path-to-folder>" --band "<band-name>"
```

## Test Mode (iTunes + MusicBrainz Search Preview)

Use the included test script to preview album metadata and check if artwork is available on both iTunes and MusicBrainz:

```python
python3 test_art_sources.py --band "The Beatles" --album "Yellow Submarine"
```

This returns a list of matching releases and indicates whether artwork is available for each.
