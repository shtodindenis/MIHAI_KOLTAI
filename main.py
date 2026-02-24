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

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.phone.resize(width, height)

    def on_draw(self) -> None:
        self.clear()
        self.phone.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        self.phone.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        self.phone.on_mouse_release(x, y, button, modifiers)
        
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        self.phone.on_mouse_motion(x, y, dx, dy)

    def update(self, delta_time: float) -> None:
        self.phone.update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)
        self.phone.on_key_press(symbol, modifiers)

    def on_text(self, text: str) -> None:
        self.phone.on_text(text)

def main() -> None:
    window = GameWindow()
    arcade.run()

if __name__ == "__main__":
    main()