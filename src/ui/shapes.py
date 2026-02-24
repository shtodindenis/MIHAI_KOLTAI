from __future__ import annotations
from typing import Any
import arcade
from src.shared.utils import make_rect

def draw_rounded_rect(
    x: float, 
    y: float, 
    width: float, 
    height: float, 
    color: Any, 
    corner_radius: float,
    centered: bool = False
) -> None:
    bl_x = x - width / 2 if centered else x
    bl_y = y - height / 2 if centered else y
    
    arcade.draw_rect_filled(make_rect(bl_x, bl_y, width, height), color)
    radius = corner_radius
    arcade.draw_circle_filled(bl_x + radius, bl_y + radius, radius, color)
    arcade.draw_circle_filled(bl_x + width - radius, bl_y + radius, radius, color)
    arcade.draw_circle_filled(bl_x + radius, bl_y + height - radius, radius, color)
    arcade.draw_circle_filled(bl_x + width - radius, bl_y + height - radius, radius, color)
    arcade.draw_rect_filled(make_rect(bl_x, bl_y + radius, radius, height - 2 * radius), color)
    arcade.draw_rect_filled(make_rect(bl_x + width - radius, bl_y + radius, radius, height - 2 * radius), color)
    arcade.draw_rect_filled(make_rect(bl_x + radius, bl_y, width - 2 * radius, radius), color)
    arcade.draw_rect_filled(make_rect(bl_x + radius, bl_y + height - radius, width - 2 * radius, radius), color)