from __future__ import annotations

import argparse
import json
from pathlib import Path

import orjson
from PyTexturePacker import Packer


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_ROOT = PROJECT_ROOT / "assets"
IMAGES_RAW = ASSETS_ROOT / "images" / "raw"
IMAGES_OUTPUT = ASSETS_ROOT / "images"
CONFIG_PATH = PROJECT_ROOT / "tools" / "atlas_config.json"


def load_config() -> dict:
    with open(CONFIG_PATH, "rb") as f:
        return orjson.loads(f.read())


def build_atlas(
    atlas_key: str,
    atlas_config: dict,
    output_dir: Path,
) -> None:
    scale = atlas_config.get("scale", 1.0)
    atlas_filename = atlas_config.get("atlas", f"{atlas_key}.png")
    json_filename = atlas_config.get("config", f"{atlas_key}.json")
    custom_name = atlas_config.get("custom", atlas_key)
    sprite_mapping = atlas_config.get("sprites", {})

    source_dir = IMAGES_RAW / atlas_key
    if not source_dir.exists():
        print(f"Source directory not found: {source_dir}")
        return

    packer = Packer.create(
        max_width=4096,
        max_height=4096,
        bg_color=0x00000000,
        texture_format=".png",
        atlas_format="json",
        enable_rotated=False
    )

    atlas_path = output_dir / atlas_filename
    json_path = output_dir / json_filename
    output_stem = str(output_dir / atlas_path.stem)

    packer.pack(str(source_dir), output_stem)

    generated_json = Path(f"{output_stem}.json")
    generated_png = Path(f"{output_stem}.png")

    if generated_json != json_path:
        generated_json.rename(json_path)
    if generated_png != atlas_path:
        generated_png.rename(atlas_path)

    with open(json_path, "rb") as f:
        atlas_data = json.load(f)

    for frame_name in atlas_data.get("frames", {}):
        if frame_name in sprite_mapping:
            continue
        base_name = Path(frame_name).stem
        sprite_mapping[frame_name] = base_name

    if "meta" not in atlas_data:
        atlas_data["meta"] = {}
        
    atlas_data["meta"]["scale"] = scale
    atlas_data["meta"]["sprite_mapping"] = sprite_mapping
    atlas_data["meta"]["custom_name"] = custom_name

    with open(json_path, "wb") as f:
        f.write(orjson.dumps(atlas_data, option=orjson.OPT_INDENT_2))

    print(f"Built atlas '{custom_name}': {atlas_filename} + {json_filename}")


def build_all_atlases(output_dir: Path) -> None:
    config = load_config()

    for atlas_key, atlas_config in config.items():
        if atlas_config.get("auto_build", True):
            build_atlas(atlas_key, atlas_config, output_dir)


def build_single_atlas(custom_name: str, output_dir: Path) -> None:
    config = load_config()

    for atlas_key, atlas_config in config.items():
        config_custom = atlas_config.get("custom", atlas_key)
        if config_custom == custom_name or atlas_key == custom_name:
            build_atlas(atlas_key, atlas_config, output_dir)
            return

    print(f"Atlas '{custom_name}' not found in config")


def main() -> None:
    parser = argparse.ArgumentParser(description="Atlas generator")
    parser.add_argument(
        "--atlas",
        "-a",
        type=str,
        help="Build specific atlas by custom name or folder name",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=IMAGES_OUTPUT,
        help="Output directory for atlases",
    )

    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    if args.atlas:
        build_single_atlas(args.atlas, args.output)
    else:
        build_all_atlases(args.output)


if __name__ == "__main__":
    main()