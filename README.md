
# 🎵 artwork-embedder

Embed album artwork in MP3 files using iTunes, MusicBrainz, and AcoustID. Supports both bulk processing of folders and individual file tagging.

---

## 📦 Features

- Search for album artwork from:
  - **iTunes API**
  - **MusicBrainz + Cover Art Archive**
  - **AcoustID** fallback (requires API key)
- Embed artwork using:
  - `music-tag` (preferred)
  - `mutagen` (fallback)
- Clean embedded artwork from MP3 files
- CLI support for batch folder and file processing
- Compatible with macOS, Linux, and WSL

---

## 📁 Installation & Setup

### Requirements

- Python 3.12.x
- ffmpeg (for `fpcalc` via chromaprint)
- An AcoustID API key (for optional fingerprinting support)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/artwork-embedder.git
cd artwork-embedder

2. Create a virtual environment

python3.12 -m venv mp3tagger-env
source mp3tagger-env/bin/activate

3. Install requirements

pip install -r requirements.txt

4. Set AcoustID API key (optional)

Register at https://acoustid.org/api-key and create a .env file:

ACOUSTID_API_KEY="your-api-key-here"


⸻

🚀 Usage

Run the CLI via:

python -m artwork_embedder.cli --music-folder "./albums" --band "Radiohead" --folders

Options

Option	Description
--music-folder	Path to folder with MP3s or album subfolders
--band	Name of the band or artist
--album	Only process the given album name
--clean-album	Remove artwork from the specified album
--brainz	Embed artwork directly from MusicBrainz release ID
--folders	Loop over subfolders (for album processing)
--files	Process individual MP3 files (top-level only)


⸻

🧪 Test Mode

Use the provided test suite to simulate all modes of operation:

python3 test/test_embed_run.py

This script will:
	•	Copy the MP3 file Cosmonkey-Rainy.mp3 into test folders
	•	Run embedding using:
	•	Folder/iTunes match
	•	Folder/MusicBrainz match
	•	File/AcoustID fallback
	•	Print a final summary report

File required:
Make sure Cosmonkey-Rainy.mp3 is placed in the root test/ directory.

⸻

🧱 Project Structure

artwork_embedder/
├── __init__.py
├── cli.py               # CLI interface
├── embed.py             # Embed/Clean logic
├── itunes_utils.py      # iTunes search logic
├── musicbrainz_utils.py # MusicBrainz + Cover Art logic
├── acoustid_utils.py    # AcoustID fingerprint recognition
├── utils.py             # Common helpers (image download, name cleanup)


⸻

📘 Documentation

Each module contains clear docstrings for easy documentation generation. You can use tools like pdoc, mkdocs, or Sphinx to build HTML/Markdown docs.

⸻

✅ Example Commands

# Embed artwork for each subfolder
python -m artwork_embedder.cli --music-folder "albums/" --band "The Beatles" --folders

# Clean artwork from one album
python -m artwork_embedder.cli --music-folder "albums/" --clean-album "Abbey Road"

# Embed artwork using MusicBrainz release ID
python -m artwork_embedder.cli --music-folder "albums/" --album "OK Computer" --brainz abc123 --folders

# Process individual files using AcoustID
python -m artwork_embedder.cli --music-folder "singles/" --band "Coldplay" --files


⸻

📄 License

MIT License. Free to use and distribute with attribution.

