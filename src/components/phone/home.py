from __future__ import annotations
import arcade
from typing import TYPE_CHECKING
from src.shared.utils import make_centered_rect, make_rect
from src.ui.shapes import draw_rounded_rect

if TYPE_CHECKING:
    from src.core.asset_manager import AssetManager

APP_ICON_SIZE = 40
APP_ICON_TEXT_HEIGHT = 20
APP_POSITIONS = {
    "zasora": (85, 125),
    "calc": (155, 125)
}

class PhoneHome:
    def __init__(self, asset_manager: AssetManager, scale_factor: float, scaled_width: float, scaled_height: float, phone_height: float):
        self.asset_manager = asset_manager
        self.scale_factor = scale_factor
        self.scaled_width = scaled_width
        self.scaled_height = scaled_height
        self.phone_height = phone_height
        self.screen_on_texture = self.asset_manager.get_texture("SCREEN_ON")
        self.zasora_icon_texture = self.asset_manager.get_texture("zasora")
        self.calc_icon_texture = self.asset_manager.get_texture("calc")

    def draw(self, phone_x: float, phone_y: float):
        if self.screen_on_texture:
            arcade.draw_texture_rect(
                self.screen_on_texture,
                make_centered_rect(phone_x + self.scaled_width / 2, phone_y + self.scaled_height / 2, self.scaled_width, self.scaled_height),
            )
        
        font_path = "assets/font.ttf"
        for app_name, (pos_x, pos_y) in APP_POSITIONS.items():
            if app_name == "zasora":
                self._draw_app_icon(self.zasora_icon_texture, "zasora", phone_x, phone_y, pos_x, pos_y, str(font_path))
            elif app_name == "calc":
                self._draw_app_icon(self.calc_icon_texture, "calc", phone_x, phone_y, pos_x, pos_y, str(font_path))

    def _draw_app_icon(self, icon_texture, label, phone_x, phone_y, base_x, base_y, font_name):
        icon_size = APP_ICON_SIZE * self.scale_factor
        bl_x = phone_x + base_x * self.scale_factor
        bl_y = phone_y + (self.phone_height - base_y) * self.scale_factor - icon_size

        draw_rounded_rect(bl_x, bl_y, icon_size, icon_size, arcade.color.BLACK, icon_size * 0.2)

        if icon_texture:
            texture_size = icon_size * 0.75
            texture_offset = (icon_size - texture_size) / 2
            arcade.draw_texture_rect(
                icon_texture,
                make_rect(bl_x + texture_offset, bl_y + texture_offset, texture_size, texture_size),
            )

        font_size = int(12 * self.scale_factor)
        arcade.draw_text(
            label, bl_x + icon_size / 2, bl_y - font_size * 0.5,
            arcade.color.WHITE, font_size=font_size, font_name=font_name,
            anchor_x="center", anchor_y="top"
        )

    def check_app_icon_click(self, x, y, phone_x, phone_y) -> str | None:
        for app_name, (pos_x, pos_y) in APP_POSITIONS.items():
            icon_size = APP_ICON_SIZE * self.scale_factor
            text_height = APP_ICON_TEXT_HEIGHT * self.scale_factor
            bl_x = phone_x + pos_x * self.scale_factor
            bl_y = phone_y + (self.phone_height - pos_y) * self.scale_factor - icon_size
            if bl_x <= x <= bl_x + icon_size and bl_y - text_height <= y <= bl_y + icon_size:
                return app_name
        return None