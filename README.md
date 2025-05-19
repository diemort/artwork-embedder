# Artwork Embedder

Search iTunes and MusicBrainz for release albums and updates the art work in the ID3 tag in mp3 files.

The code loops over the folders inside `--music-folder` and check the folder name to match the album name, ignoring dates and appended information.

Usage:

```python3 embed_artwork.py --music-folder "<path-to-folder>" --band "<band-name>"```
