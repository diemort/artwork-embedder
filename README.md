# Artwork Embedder

Search iTunes and MusicBrainz for release albums and updates the art work in the ID3 tag in mp3 files.

The code loops over the folders inside `--music-folder` and check the folder name to match the album name, ignoring dates and appended information.

## Setup:

The necessary Python modules and applications can be automatically installed and local OS can be ready for embed art work with:

```python3 setup_mp3_env.sh```

An API key is needed from AcoustID in case a fallback option is desired. This API key can be added to the header of the setup files or given as keyboard input.

## Usage:

```python3 embed_artwork.py --music-folder "<path-to-folder>" --band "<band-name>"```

In case art work is already present in the mp3 files, option `--clean` removes it from the given album name:

```python3 embed_artwork.py --music-folder "<path-to-folder>" --band "<band-name>"```

## A test file is given to check of the band name and album name for API search in iTunes and MusicBrainz:

```python3 test_art_sources.py --band "The Beatles" --album "Yellow Submarine"```
