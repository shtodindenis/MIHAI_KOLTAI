from pathlib import Path

import arcade

from src.components.phone import Phone
from src.core.asset_manager import AssetManager
from src.shared.constants import SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH

class GameWindow(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
        arcade.set_background_color(arcade.color.BLACK)

        project_root = Path(__file__).parent
        assets_root = project_root / "assets"

        self.asset_manager = AssetManager(assets_root)
        images_output = assets_root / "images"
        self.asset_manager.load_all_atlases(images_output)

        self.phone = Phone(self.asset_manager)
        arcade.schedule(self.update, 1/60)
        
        self._update_buttons(self.width, self.height)

    def _update_buttons(self, width: int, height: int) -> None:
        self.close_btn_rect = arcade.Rect(
            width - 50, width, height - 50, height, 50, 50, width - 25, height - 25
        )
        self.fs_btn_rect = arcade.Rect(
            width - 100, width - 50, height - 50, height, 50, 50, width - 75, height - 25
        )

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.phone.resize(width, height)
        self._update_buttons(width, height)

    def on_draw(self) -> None:
        self.clear()
        self.phone.draw()
        
        arcade.draw_rect_filled(self.close_btn_rect, arcade.color.RED)
        arcade.draw_text("X", self.close_btn_rect.x, self.close_btn_rect.y, arcade.color.WHITE, anchor_x="center", anchor_y="center", bold=True)
        
        arcade.draw_rect_filled(self.fs_btn_rect, arcade.color.GRAY)
        arcade.draw_text("[ ]", self.fs_btn_rect.x, self.fs_btn_rect.y, arcade.color.WHITE, anchor_x="center", anchor_y="center", bold=True)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.close_btn_rect.left <= x <= self.close_btn_rect.right and self.close_btn_rect.bottom <= y <= self.close_btn_rect.top:
                self.close()
                return
            if self.fs_btn_rect.left <= x <= self.fs_btn_rect.right and self.fs_btn_rect.bottom <= y <= self.fs_btn_rect.top:
                self.set_fullscreen(not self.fullscreen)
                return

        self.phone.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        self.phone.on_mouse_release(x, y, button, modifiers)

    def update(self, delta_time: float) -> None:
        self.phone.update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ESCAPE:
            self.close()
        elif symbol == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

def main() -> None:
    window = GameWindow()
    arcade.run()

if __name__ == "__main__":
    main()