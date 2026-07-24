import json
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
IMAGES_DIR = os.path.join(ROOT_DIR, "images")
DISPLAY_DIR = os.path.join(IMAGES_DIR, "display")

MODS_DIR = os.path.join(TOOLS_DIR, "mods")
CACHE_DIR = os.path.join(TOOLS_DIR, "cache")
CACHE_ICONS_DIR = os.path.join(CACHE_DIR, "icons")

README_PATH = os.path.join(ROOT_DIR, "README.md")
COMPATIBILITY_PATH = os.path.join(ROOT_DIR, "compatibility.md")

STATS_PATH = os.path.join(TOOLS_DIR, "stats.json")
METADATA_PATH = os.path.join(TOOLS_DIR, "mod_metadata.json")
EXTRACTED_DIR = os.path.join(TOOLS_DIR, "extracted")
FRAMES_DIR = os.path.join(TOOLS_DIR, "frames")
COLORS_PATH = os.path.join(TOOLS_DIR, "colors.json")

GITHUB_REPO = "https://github.com/Arcdashckr/Effect-Icon-Plus"
MODRINTH_HEADERS = {
    "User-Agent": "Arcdashckr/Effect-Icon-Plus-Downloader (arcdashckr@gmail.com)"
}

def file_exists(path):
    return os.path.isfile(path)

def dir_exists(path):
    return os.path.isdir(path)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def load_json(path, default=None):
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_metadata():
    return load_json(METADATA_PATH)

def save_metadata(data):
    save_json(METADATA_PATH, data)

def load_stats():
    return load_json(STATS_PATH)

def save_stats(data):
    save_json(STATS_PATH, data)