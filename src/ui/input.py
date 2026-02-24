from __future__ import annotations
import arcade
from src.shared.utils import make_rect

class TextInput:
    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        self.x, self.y, self.width, self.height, self.text, self.is_active = x, y, width, height, "", False

    def draw(self) -> None:
        color = arcade.color.WHITE if self.is_active else arcade.color.GRAY
        arcade.draw_rect_outline(make_rect(self.x, self.y, self.width, self.height), color, 2)
        arcade.draw_text(
            self.text + ("_" if self.is_active else ""), 
            self.x + 5, 
            self.y + self.height/2, 
            arcade.color.WHITE, 
            anchor_y="center"
        )