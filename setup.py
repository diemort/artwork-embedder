from setuptools import setup, find_packages

setup(
    name="artwork-embedder",
    version="0.1.0",
    description="Search and embed album artwork in MP3 files using iTunes and MusicBrainz.",
    author="diemort",
    packages=find_packages(),
    install_requires=[
        "requests",
        "mutagen",
        "music-tag",
        "tinytag",
        "pyacoustid",
        "python-dotenv",
        "musicbrainzngs"
    ],
    entry_points={
        "console_scripts": [
            "embed_artwork = artwork_embedder.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12,<3.13',
)
