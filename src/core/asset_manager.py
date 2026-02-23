from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import arcade
import orjson

from src.shared.types import IAtlasData

if TYPE_CHECKING:
    from collections.abc import Mapping


class AssetManager:
    def __init__(self, assets_root: Path) -> None:
        self.assets_root = assets_root
        self.images_root = assets_root / "images"
        self.atlases: dict[str, Any] = {}
        self.textures: dict[str, arcade.Texture] = {}
        self.atlas_data: dict[str, IAtlasData] = {}
        self.sprite_names: dict[str, dict[str, str]] = {}

    def load_atlas(self, atlas_name: str, atlas_path: Path, json_path: Path) -> None:
        atlas_image = arcade.load_texture(str(atlas_path))
        with open(json_path, "rb") as f:
            data: IAtlasData = orjson.loads(f.read())

        self.atlas_data[atlas_name] = data
        self.atlases[atlas_name] = atlas_image

        meta = data.get("meta", {})
        scale = meta.get("scale", 1.0)
        sprite_mapping = meta.get("sprite_mapping", {})

        for frame_name, frame_data in data["frames"].items():
            frame = frame_data["frame"]
            x, y = frame["x"], frame["y"]
            w, h = frame["w"], frame["h"]
            
            cropped_image = atlas_image.image.crop((x, y, x + w, y + h))
            texture = arcade.Texture(image=cropped_image)

            base_name = Path(frame_name).stem
            custom_name = sprite_mapping.get(frame_name, base_name)
            self.textures[custom_name] = texture

        self.sprite_names[atlas_name] = sprite_mapping

    def get_texture(self, name: str) -> arcade.Texture | None:
        return self.textures.get(name)

    def get_atlas(self, name: str) -> Any | None:
        return self.atlases.get(name)

    def get_atlas_data(self, name: str) -> IAtlasData | None:
        return self.atlas_data.get(name)

    def load_all_atlases(self, output_dir: Path) -> None:
        config_path = Path(__file__).parent.parent.parent / "tools" / "atlas_config.json"
        if not config_path.exists():
            return

        with open(config_path, "rb") as f:
            config: dict = orjson.loads(f.read())

        for atlas_key, atlas_config in config.items():
            if not atlas_config.get("auto_build", True):
                continue

            custom_name = atlas_config.get("custom", atlas_key)
            atlas_filename = atlas_config.get("atlas", f"{atlas_key}.png")
            json_filename = atlas_config.get("config", f"{atlas_key}.json")

            atlas_path = output_dir / atlas_filename
            json_file_path = output_dir / json_filename

            if atlas_path.exists() and json_file_path.exists():
                self.load_atlas(custom_name, atlas_path, json_file_path)

    def add_sprite_mapping(self, atlas_name: str, mapping: dict[str, str]) -> None:
        if atlas_name not in self.sprite_names:
            self.sprite_names[atlas_name] = {}
        self.sprite_names[atlas_name].update(mapping)