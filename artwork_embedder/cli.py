"""
artwork_embedder.cli
Command-line interface for the artwork embedder tool.
"""

import argparse
from pathlib import Path
from dotenv import load_dotenv
import os

from artwork_embedder.embed import process_all_folders, process_files_individually, clean_album_art, download_cover_from_musicbrainz_id
from artwork_embedder.utils import clean_album_name

def main():
    """Parse arguments and trigger the corresponding operations."""
    parser = argparse.ArgumentParser(
        description="Embed or clean album art in MP3 files."
    )
    parser.add_argument("--music-folder", type=str, required=True,
                        metavar='"MUSIC_FOLDER"',
                        help='Path to folder with album subfolders.')
    
    parser.add_argument("--band", type=str,
                        metavar='"BAND"',
                        help='Band name for album art search.')
    
    parser.add_argument("--album", type=str,
                        metavar='"ALBUM"',
                        help='Only update artwork for this specific album.')
    
    parser.add_argument("--clean-album", type=str,
                        metavar='"CLEAN_ALBUM"',
                        help='Album name to clean (removes embedded artwork).')
    
    parser.add_argument("--brainz", type=str,
                        metavar='"BRAINZ_RELEASE_ID"',
                        help='MusicBrainz release ID to embed artwork directly.')
    
    # Mode flags
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--folders", action="store_true", help="Process album subfolders.")
    mode_group.add_argument("--files", action="store_true", help="Process MP3s at the top level.")

    args = parser.parse_args()
    load_dotenv()
    root = Path(args.music_folder)

    if args.brainz:
        if not args.album:
            print("Please provide --album along with --brainz.")
            exit(1)
        for folder in root.iterdir():
            if folder.is_dir() and clean_album_name(folder.name).lower() == args.album.lower():
                download_cover_from_musicbrainz_id(args.brainz, folder)
                return
        print(f"Album '{args.album}' not found in {args.music_folder}")
        return

    if args.clean_album:
        clean_album_art(args.music_folder, args.clean_album)
    elif args.files:
        process_files_individually(args.music_folder, args.band)
    elif args.folders:
        process_all_folders(args.music_folder, args.band, target_album=args.album)

if __name__ == "__main__":
    main()
