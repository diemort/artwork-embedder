"""
artwork_embedder.itunes_utils
Functions to search and retrieve album art from iTunes.
"""

import requests

def search_album_art(query, expected_artist=None):
    """
    Search the iTunes API for album artwork.

    Args:
        query (str): Search string combining artist and album name.
        expected_artist (str, optional): Artist to match against results.

    Returns:
        str or None: URL to a 600x600 image if found, else None.
    """
    try:
        url = f"https://itunes.apple.com/search?term={requests.utils.quote(query)}&media=music&entity=album&limit=10"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data['resultCount'] == 0:
            print("No results found.")
            return None

        expected = expected_artist.lower() if expected_artist else None

        for result in data['results']:
            result_artist = result.get('artistName', '').lower()
            if expected and expected in result_artist:
                print(f"Found album: {result['collectionName']} by {result['artistName']}")
                return result['artworkUrl100'].replace('100x100bb', '600x600bb')

        print(f"No album art found matching artist '{expected_artist}'.")
        return None

    except Exception as e:
        print(f"Failed to search album art: {e}")
        return None

