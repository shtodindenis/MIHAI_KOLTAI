from __future__ import annotations
import arcade
from typing import TYPE_CHECKING
from src.states.phone import PhoneState
from src.shared.utils import make_rect, make_centered_rect

if TYPE_CHECKING:
    from src.states.phone import PhoneData

class PhoneLayout:
    def __init__(self, asset_manager, scale_factor, scaled_width, scaled_height, center_x, center_y):
        self.asset_manager = asset_manager
        self.scale_factor = scale_factor
        self.scaled_width = scaled_width
        self.scaled_height = scaled_height
        self.power_button_size = 64 * self.scale_factor
        self.home_button_size = 64 * self.scale_factor
        self.body_texture = self.asset_manager.get_texture("telefon_body")
        self.screen_off_texture = self.asset_manager.get_texture("SCREEN_OFF")
        self.screen_black_texture = self.asset_manager.get_texture("SCREEN_BLACK")
        self.power_button_texture = self.asset_manager.get_texture("powerbtn")
        self.home_button_texture = self.asset_manager.get_texture("homebtn")
        self.turtle_logo_texture = self.asset_manager.get_texture("turtlelogo")
        self.resize(center_x, center_y, center_x * 2, center_y * 2)

    def resize(self, center_x, center_y, width, height):
        self.phone_x = center_x - self.scaled_width / 2
        self.phone_y = center_y - self.scaled_height / 2
        self.power_button_x = width - self.power_button_size - 20
        self.power_button_y = 20
        self.home_button_x = self.power_button_x - self.home_button_size - 20
        self.home_button_y = 20
        self.center_x, self.center_y = center_x, center_y

    def draw_base(self):
        if self.screen_black_texture:
            arcade.draw_texture_rect(
                self.screen_black_texture,
                make_centered_rect(self.phone_x + self.scaled_width / 2, self.phone_y + self.scaled_height / 2, self.scaled_width, self.scaled_height),
            )

    def draw_off_screen(self):
        if self.screen_off_texture:
            arcade.draw_texture_rect(
                self.screen_off_texture,
                make_centered_rect(self.phone_x + self.scaled_width / 2, self.phone_y + self.scaled_height / 2, self.scaled_width, self.scaled_height),
            )

    def draw_boot_screen(self, progress: float):
        logo_size = 128 * self.scale_factor
        logo_x, logo_y = self.center_x - 15 * self.scale_factor, self.center_y + 50 * self.scale_factor
        if self.turtle_logo_texture:
            arcade.draw_texture_rect(self.turtle_logo_texture, make_centered_rect(logo_x, logo_y, logo_size, logo_size))
        
        font = "assets/font.ttf"
        arcade.draw_text(
            "TURTLE OS", logo_x, logo_y - logo_size / 2 - 20 * self.scale_factor, 
            arcade.color.WHITE, font_size=int(24 * self.scale_factor), 
            font_name=font, anchor_x="center", anchor_y="top"
        )
        arcade.draw_text(
            "booting" + "." * int(progress * 3), self.center_x, 
            logo_y - logo_size / 2 - 50 * self.scale_factor, arcade.color.GRAY, 
            font_size=int(16 * self.scale_factor), font_name=font, anchor_x="center", anchor_y="top"
        )

    def draw_overlay(self, state: PhoneData):
        if self.body_texture:
            arcade.draw_texture_rect(self.body_texture, make_rect(self.phone_x, self.phone_y, self.scaled_width, self.scaled_height))
        
        for btn, tex, x, y, size, blocked in [("power", self.power_button_texture, self.power_button_x, self.power_button_y, self.power_button_size, state.power_button_blocked), ("home", self.home_button_texture, self.home_button_x, self.home_button_y, self.home_button_size, state.state in (PhoneState.OFF, PhoneState.BOOTING))]:
            if tex:
                arcade.draw_texture_rect(tex, make_rect(x, y, size, size))
                if blocked:
                    arcade.draw_rect_filled(make_rect(x, y, size, size), (128, 128, 128, 128))