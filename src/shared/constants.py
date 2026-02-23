from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ASSETS_DIR = PROJECT_ROOT / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
RAW_IMAGES_DIR = IMAGES_DIR / "raw"
SOUNDS_DIR = ASSETS_DIR / "sounds"
VIDEO_DIR = ASSETS_DIR / "video"
STORIES_DIR = ASSETS_DIR / "stories"
MAPS_DIR = ASSETS_DIR / "maps"

ATLAS_CONFIG_PATH = PROJECT_ROOT / "tools" / "atlas_config.json"

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "ZHOSKO"
