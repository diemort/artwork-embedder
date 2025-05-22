"""
artwork_embedder.utils
Common utility functions shared across modules.
"""

import re
import requests

def clean_album_name(folder_name):
    """
    Normalize album folder names by removing date prefixes and suffix tags.

    Args:
        folder_name (str): Folder name containing album title and extra info.

    Returns:
        str: Cleaned album name string.
    """
    # Remove leading [YYYY] or (YYYY)
    name = re.sub(r"^[\[(]\d{4}[\])]\s*", "", folder_name)
    # Remove trailing/embedded tags like (Live Album), [2 CD], etc
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"\[.*?\]", "", name)
    # Strip and normalize whitespace
    return name.strip()

def download_image(url):
    """
    Download an image from a URL.

    Args:
        url (str): URL to download image from.

    Returns:
        bytes or None: Image content if successful, else None.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Download failed: {e}")
        return None

