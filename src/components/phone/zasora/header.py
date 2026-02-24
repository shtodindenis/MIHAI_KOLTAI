from __future__ import annotations
import arcade
from typing import TYPE_CHECKING
from pathlib import Path
from src.shared.utils import make_rect

if TYPE_CHECKING:
    from src.core.asset_manager import AssetManager

class ZasoraHeader:
    def __init__(self, asset_manager: AssetManager, scale_factor: float) -> None:
        self.asset_manager = asset_manager
        self.scale_factor = scale_factor
        self.logo_texture = self.asset_manager.get_texture("zasora")
        self.font_path = str(Path(__file__).parent.parent.parent.parent.parent / "assets" / "font.ttf")

    def draw(self, app_x: float, app_y: float, app_w: float, app_h: float, header_height: float) -> None:
        hy = app_y + app_h - header_height
        arcade.draw_rect_filled(make_rect(app_x, hy, app_w, header_height), (0, 0, 0, 200))
        ls, lx, lcy = 40 * self.scale_factor, app_x + 10 * self.scale_factor, hy + header_height / 2
        if self.logo_texture: arcade.draw_texture_rect(self.logo_texture, make_rect(lx, lcy - ls / 2, ls, ls))
        arcade.draw_text("ZASORA", lx + ls + 15 * self.scale_factor, lcy, arcade.color.WHITE, int(22 * self.scale_factor), self.font_path, "left", "center", True)