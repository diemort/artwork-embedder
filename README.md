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

## Test Mode (iTunes + MusicBrainz Search Preview)

Use the included test script to preview album metadata and check if artwork is available on both iTunes and MusicBrainz:

```python
python3 test_art_sources.py --band "The Beatles" --album "Yellow Submarine"
```

This returns a list of matching releases and indicates whether artwork is available for each.

The mp3 file _Uplifting Era_ of Optimistic Big Band is freely available at:

https://pixabay.com/pt/music/otimista-optimistic-big-band-uplifting-era-337455/
