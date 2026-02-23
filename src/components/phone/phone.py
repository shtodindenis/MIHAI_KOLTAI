from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import arcade
from PIL import Image, ImageEnhance

from src.shared.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from src.states.phone import PhoneData, PhoneState

if TYPE_CHECKING:
    from src.components.phone.zasora import ZasoraApp
    from src.core.asset_manager import AssetManager

def _make_rect(x: float, y: float, width: float, height: float) -> arcade.Rect:
    return arcade.Rect(x, x + width, y, y + height, width, height, x + width / 2, y + height / 2)

def _make_centered_rect(x: float, y: float, width: float, height: float) -> arcade.Rect:
    left = x - width / 2
    right = x + width / 2
    bottom = y - height / 2
    top = y + height / 2
    return arcade.Rect(left, right, bottom, top, width, height, x, y)

PHONE_WIDTH = 400
PHONE_HEIGHT = 640
ADD_SCALE_PHONE_FACTOR = 1.1
BOOT_DURATION = 1.0

APP_ICON_SIZE = 40
APP_ICON_TEXT_HEIGHT = 20

APP_POSITIONS = {
    "zasora": (85, 125),
}

class Phone:
    def __init__(self, asset_manager: AssetManager) -> None:
        self.asset_manager = asset_manager
        self.scale_factor = (SCREEN_HEIGHT / PHONE_HEIGHT) * ADD_SCALE_PHONE_FACTOR
        self.scaled_width = PHONE_WIDTH * self.scale_factor
        self.scaled_height = PHONE_HEIGHT * self.scale_factor
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        self.phone_x = self.center_x - self.scaled_width / 2
        self.phone_y = self.center_y - self.scaled_height / 2
        self.power_button_size = 64 * self.scale_factor
        self.power_button_x = SCREEN_WIDTH - self.power_button_size - 20
        self.power_button_y = 20
        self.state = PhoneData()
        self._boot_elapsed: float = 0.0
        self._load_textures()
        self._gray_power_button_texture: arcade.Texture | None = None
        self._zasora_app: ZasoraApp | None = None

    def resize(self, width: float, height: float) -> None:
        self.center_x = width / 2
        self.center_y = height / 2
        self.phone_x = self.center_x - self.scaled_width / 2
        self.phone_y = self.center_y - self.scaled_height / 2
        self.power_button_x = width - self.power_button_size - 20
        self.power_button_y = 20
        if self._zasora_app:
            self._zasora_app.app_x = self.phone_x + 70 * self.scale_factor
            self._zasora_app.app_y = self.phone_y + 90 * self.scale_factor
            self._zasora_app.video_area_x = self._zasora_app.app_x
            self._zasora_app.video_area_y = self._zasora_app.app_y

    @property
    def zasora_app(self) -> ZasoraApp:
        if self._zasora_app is None:
            from src.components.phone.zasora import ZasoraApp
            app_w = 230 * self.scale_factor
            app_h = 435 * self.scale_factor
            app_x = self.phone_x + 70 * self.scale_factor
            app_y = self.phone_y + 90 * self.scale_factor
            self._zasora_app = ZasoraApp(
                self.asset_manager,
                app_x,
                app_y,
                app_w,
                app_h,
                self.scale_factor,
            )
        return self._zasora_app

    @property
    def current_app(self) -> str | None:
        if self.zasora_app.state.is_running:
            return "zasora"
        return None

    def _load_textures(self) -> None:
        self.body_texture = self.asset_manager.get_texture("telefon_body")
        self.screen_off_texture = self.asset_manager.get_texture("SCREEN_OFF")
        self.screen_black_texture = self.asset_manager.get_texture("SCREEN_BLACK")
        self.screen_on_texture = self.asset_manager.get_texture("SCREEN_ON")
        self.power_button_texture = self.asset_manager.get_texture("powerbtn")
        self.turtle_logo_texture = self.asset_manager.get_texture("turtlelogo")
        self.zasora_icon_texture = self.asset_manager.get_texture("zasora")

    def _create_gray_power_button(self) -> arcade.Texture | None:
        if self.power_button_texture is None:
            return None
        img = self.power_button_texture.image
        if not isinstance(img, Image.Image):
            return None
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.7)
        return arcade.Texture(image=img)

    def _get_gray_power_button(self) -> arcade.Texture | None:
        if self._gray_power_button_texture is None:
            self._gray_power_button_texture = self._create_gray_power_button()
        return self._gray_power_button_texture

    def _load_videos(self) -> list[Path]:
        video_dir = Path(__file__).parent.parent.parent.parent / "assets" / "video" / "zasora"
        if video_dir.exists():
            return list(video_dir.glob("*.webm")) + list(video_dir.glob("*.mp4"))
        return []

    def _start_boot(self) -> None:
        self.state.state = PhoneState.BOOTING
        self.state.power_button_blocked = True
        self.state.videos_loaded = False
        self._boot_elapsed = 0.0
        self.state.video_files = self._load_videos()

    def _complete_boot(self) -> None:
        self.state.state = PhoneState.ON
        self.state.videos_loaded = True
        self.state.power_button_blocked = False

    def _toggle_power(self) -> None:
        if self.state.state == PhoneState.OFF:
            self._start_boot()
        elif self.state.state == PhoneState.ON and not self.state.power_button_blocked:
            self.state.state = PhoneState.OFF
            self.state.power_button_blocked = True
            self.state.power_button_block_time = 0.3
            self._close_app()

    def _launch_app(self, app_name: str) -> None:
        if app_name == "zasora":
            self.zasora_app.start()

    def _close_app(self) -> None:
        if self.zasora_app.state.is_running:
            self.zasora_app.stop()

    def _check_app_icon_click(self, x: float, y: float) -> bool:
        if self.state.state != PhoneState.ON:
            return False
        for app_name, (pos_x, pos_y) in APP_POSITIONS.items():
            icon_size = APP_ICON_SIZE * self.scale_factor
            text_height = APP_ICON_TEXT_HEIGHT * self.scale_factor
            bl_x = self.phone_x + pos_x * self.scale_factor
            bl_y = self.phone_y + (PHONE_HEIGHT - pos_y) * self.scale_factor - icon_size
            if (
                bl_x <= x <= bl_x + icon_size
                and bl_y - text_height <= y <= bl_y + icon_size
            ):
                self._launch_app(app_name)
                return True
        return False

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if self.zasora_app.state.is_running:
            if self.zasora_app.on_mouse_press(x, y, button, modifiers):
                return True
            if button == arcade.MOUSE_BUTTON_RIGHT:
                self._close_app()
                return True
        if button == arcade.MOUSE_BUTTON_LEFT:
            if (
                self.power_button_x <= x <= self.power_button_x + self.power_button_size
                and self.power_button_y <= y <= self.power_button_y + self.power_button_size
            ):
                if not self.state.power_button_blocked:
                    self._toggle_power()
                return True
            if self.state.state == PhoneState.ON:
                if self._check_app_icon_click(x, y):
                    return True
        return False

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if self.zasora_app.state.is_running:
            if self.zasora_app.on_mouse_release(x, y, button, modifiers):
                return True
        return False

    def update(self, delta_time: float) -> None:
        if self.zasora_app.state.is_running:
            self.zasora_app.update(delta_time)
        if self.state.power_button_blocked and self.state.state == PhoneState.ON:
            self.state.power_button_block_time -= delta_time
            if self.state.power_button_block_time <= 0:
                self.state.power_button_blocked = False
        if self.state.state == PhoneState.BOOTING:
            self._boot_elapsed += delta_time
            if self._boot_elapsed >= BOOT_DURATION:
                self._complete_boot()

    def _draw_scaled_texture(
        self,
        texture: arcade.Texture | None,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:
        if texture is None:
            return
        arcade.draw_texture_rect(
            texture,
            _make_centered_rect(x, y, width, height),
        )

    def _draw_app_icon(
        self,
        icon_texture: arcade.Texture | None,
        label: str,
        base_x: float,
        base_y: float,
        font_name: str,
    ) -> None:
        icon_size = APP_ICON_SIZE * self.scale_factor
        max_text_height = APP_ICON_TEXT_HEIGHT * self.scale_factor
        bl_x = self.phone_x + base_x * self.scale_factor
        bl_y = self.phone_y + (PHONE_HEIGHT - base_y) * self.scale_factor - icon_size

        self._draw_rounded_rect_filled(
            bl_x, bl_y, icon_size, icon_size,
            arcade.color.BLACK,
            corner_radius=icon_size * 0.2,
        )

        if icon_texture:
            texture_size = icon_size * 0.75
            texture_offset = (icon_size - texture_size) / 2
            arcade.draw_texture_rect(
                icon_texture,
                _make_rect(
                    bl_x + texture_offset,
                    bl_y + texture_offset,
                    texture_size,
                    texture_size,
                ),
            )

        font_size = int(12 * self.scale_factor)
        label_y = bl_y - font_size * 0.5
        center_x = bl_x + icon_size / 2
        display_label = self._truncate_label(label, icon_size * 1.5, font_name, font_size, max_text_height)

        arcade.draw_text(
            display_label,
            center_x,
            label_y,
            arcade.color.WHITE,
            font_size=font_size,
            font_name=font_name,
            anchor_x="center",
            anchor_y="top",
        )

    def _truncate_label(
        self,
        label: str,
        available_width: float,
        font_name: str,
        font_size: int,
        max_height: float,
    ) -> str:
        max_chars = int(available_width / (font_size * 0.5))
        if len(label) > max_chars:
            return label[:max_chars - 3] + "..."
        return label

    def _draw_rounded_rect_filled(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        color: tuple[int, int, int],
        corner_radius: float,
    ) -> None:
        arcade.draw_rect_filled(
            _make_rect(x, y, width, height),
            color,
        )
        radius = corner_radius
        arcade.draw_circle_filled(x + radius, y + radius, radius, color)
        arcade.draw_circle_filled(x + width - radius, y + radius, radius, color)
        arcade.draw_circle_filled(x + radius, y + height - radius, radius, color)
        arcade.draw_circle_filled(x + width - radius, y + height - radius, radius, color)
        arcade.draw_rect_filled(_make_rect(x, y + radius, radius, height - 2 * radius), color)
        arcade.draw_rect_filled(_make_rect(x + width - radius, y + radius, radius, height - 2 * radius), color)
        arcade.draw_rect_filled(_make_rect(x + radius, y, width - 2 * radius, radius), color)
        arcade.draw_rect_filled(_make_rect(x + radius, y + height - radius, width - 2 * radius, radius), color)

    def _draw_boot_screen(self) -> None:
        screen_x = self.phone_x
        screen_y = self.phone_y
        self._draw_scaled_texture(
            self.screen_black_texture,
            screen_x + self.scaled_width / 2,
            screen_y + self.scaled_height / 2,
            self.scaled_width,
            self.scaled_height,
        )
        progress = min(self._boot_elapsed / BOOT_DURATION, 1.0)
        logo_size = 128 * self.scale_factor
        logo_x = self.center_x - 15 * self.scale_factor
        logo_y = self.center_y + 50 * self.scale_factor

        if self.turtle_logo_texture:
            arcade.draw_texture_rect(
                self.turtle_logo_texture,
                _make_centered_rect(logo_x, logo_y, logo_size, logo_size),
            )

        font_path = Path(__file__).parent.parent.parent.parent / "assets" / "font.ttf"
        arcade.draw_text(
            "TURTLE OS",
            logo_x,
            logo_y - logo_size / 2 - 20 * self.scale_factor,
            arcade.color.WHITE,
            font_size=int(24 * self.scale_factor),
            font_name=str(font_path),
            anchor_x="center",
            anchor_y="top",
        )
        booting_text = "booting" + "." * int(progress * 3)
        arcade.draw_text(
            booting_text,
            self.center_x,
            logo_y - logo_size / 2 - 50 * self.scale_factor,
            arcade.color.GRAY,
            font_size=int(16 * self.scale_factor),
            font_name=str(font_path),
            anchor_x="center",
            anchor_y="top",
        )

    def _draw_home_screen(self) -> None:
        screen_x = self.phone_x
        screen_y = self.phone_y
        self._draw_scaled_texture(
            self.screen_on_texture,
            screen_x + self.scaled_width / 2,
            screen_y + self.scaled_height / 2,
            self.scaled_width,
            self.scaled_height,
        )
        font_path = Path(__file__).parent.parent.parent.parent / "assets" / "font.ttf"
        for app_name, (pos_x, pos_y) in APP_POSITIONS.items():
            if app_name == "zasora":
                self._draw_app_icon(
                    self.zasora_icon_texture,
                    "zasora",
                    pos_x,
                    pos_y,
                    str(font_path),
                )

    def draw(self) -> None:
        screen_x = self.phone_x
        screen_y = self.phone_y

        self._draw_scaled_texture(
            self.screen_black_texture,
            screen_x + self.scaled_width / 2,
            screen_y + self.scaled_height / 2,
            self.scaled_width,
            self.scaled_height,
        )

        if self.state.state == PhoneState.OFF:
            self._draw_scaled_texture(
                self.screen_off_texture,
                screen_x + self.scaled_width / 2,
                screen_y + self.scaled_height / 2,
                self.scaled_width,
                self.scaled_height,
            )
        elif self.state.state == PhoneState.BOOTING:
            self._draw_boot_screen()
        elif self.state.state == PhoneState.ON:
            if self.zasora_app.state.is_running:
                self.zasora_app.draw()
            else:
                self._draw_home_screen()

        if self.body_texture:
            arcade.draw_texture_rect(
                self.body_texture,
                _make_rect(self.phone_x, self.phone_y, self.scaled_width, self.scaled_height),
            )

        if self.power_button_texture:
            if self.state.power_button_blocked:
                gray_texture = self._get_gray_power_button()
                if gray_texture:
                    arcade.draw_texture_rect(
                        gray_texture,
                        _make_rect(self.power_button_x, self.power_button_y, self.power_button_size, self.power_button_size),
                    )
                else:
                    arcade.draw_texture_rect(
                        self.power_button_texture,
                        _make_rect(self.power_button_x, self.power_button_y, self.power_button_size, self.power_button_size),
                    )
                    arcade.draw_rect_filled(
                        _make_rect(self.power_button_x, self.power_button_y, self.power_button_size, self.power_button_size),
                        (128, 128, 128, 128),
                    )
            else:
                arcade.draw_texture_rect(
                    self.power_button_texture,
                    _make_rect(self.power_button_x, self.power_button_y, self.power_button_size, self.power_button_size),
                )

    def get_videos(self) -> list[Path]:
        return self.state.video_files.copy()