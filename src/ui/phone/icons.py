from __future__ import annotations
from typing import Any
import arcade
from src.shared.utils import make_rect
from src.ui.shapes import draw_rounded_rect

class AppIcon:
    def __init__(self, texture: arcade.Texture | None, label: str, x: float, y: float, size: float = 40.0, scale: float = 1.0, font_name: str | None = None) -> None:
        self.texture, self.label, self.x, self.y, self.size, self.scale, self.font_name = texture, label, x, y, size * scale, scale, font_name
        self.text_height = 20 * scale

    def draw(self) -> None:
        draw_rounded_rect(self.x, self.y, self.size, self.size, arcade.color.BLACK, self.size * 0.2, centered=True)
        if self.texture:
            ts = self.size * 0.75
            arcade.draw_texture_rect(self.texture, make_rect(self.x - ts / 2, self.y - ts / 2, ts, ts))
        if self.label:
            fs = int(10 * self.scale)
            l = self.label if len(self.label) <= int(self.size/(fs*0.45)) else self.label[:int(self.size/(fs*0.45))-3]+"..."
            arcade.draw_text(
                l, 
                self.x, 
                self.y - self.size/2 - fs, 
                arcade.color.WHITE, 
                font_size=fs, 
                font_name=self.font_name or "calibri", 
                anchor_x="center", 
                anchor_y="top"
            )