from __future__ import annotations

from typing import TYPE_CHECKING
import arcade

from src.shared.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from src.states.phone import PhoneData, PhoneState
from src.components.phone.layout import PhoneLayout
from src.components.phone.home import PhoneHome

if TYPE_CHECKING:
    from src.components.phone.zasora.app import ZasoraApp
    from src.components.phone.calc.app import CalcApp
    from src.core.asset_manager import AssetManager

PHONE_WIDTH = 400
PHONE_HEIGHT = 640
ADD_SCALE_PHONE_FACTOR = 1.1
BOOT_DURATION = 1.0


class Phone:
    def __init__(self, asset_manager: AssetManager) -> None:
        self.asset_manager = asset_manager
        self.scale_factor = (SCREEN_HEIGHT / PHONE_HEIGHT) * ADD_SCALE_PHONE_FACTOR
        self.scaled_width = PHONE_WIDTH * self.scale_factor
        self.scaled_height = PHONE_HEIGHT * self.scale_factor
        
        center_x = SCREEN_WIDTH / 2
        center_y = SCREEN_HEIGHT / 2
        
        self.state = PhoneData()
        self._boot_elapsed: float = 0.0
        
        self.layout = PhoneLayout(self.asset_manager, self.scale_factor, self.scaled_width, self.scaled_height, center_x, center_y)
        self.home = PhoneHome(self.asset_manager, self.scale_factor, self.scaled_width, self.scaled_height, PHONE_HEIGHT)
        
        self._zasora_app: ZasoraApp | None = None
        self._calc_app: CalcApp | None = None
        
        _ = self.zasora_app
        _ = self.calc_app

    def resize(self, width: float, height: float) -> None:
        self.layout.resize(width / 2, height / 2, width, height)
        
        app_x = self.layout.phone_x + 70 * self.scale_factor
        app_y = self.layout.phone_y + 90 * self.scale_factor
        app_w = 230 * self.scale_factor
        app_h = 435 * self.scale_factor
        
        if self._zasora_app:
            self._zasora_app.resize(app_x, app_y, app_w, app_h)
            
        if self._calc_app:
            self._calc_app.resize(app_x, app_y, app_w, app_h)

    @property
    def zasora_app(self) -> ZasoraApp:
        if self._zasora_app is None:
            from src.components.phone.zasora.app import ZasoraApp
            app_w = 230 * self.scale_factor
            app_h = 435 * self.scale_factor
            app_x = self.layout.phone_x + 70 * self.scale_factor
            app_y = self.layout.phone_y + 90 * self.scale_factor
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
    def calc_app(self) -> CalcApp:
        if self._calc_app is None:
            from src.components.phone.calc.app import CalcApp
            app_w = 230 * self.scale_factor
            app_h = 435 * self.scale_factor
            app_x = self.layout.phone_x + 70 * self.scale_factor
            app_y = self.layout.phone_y + 90 * self.scale_factor
            self._calc_app = CalcApp(
                self.asset_manager,
                app_x,
                app_y,
                app_w,
                app_h,
                self.scale_factor,
            )
        return self._calc_app

    def _start_boot(self) -> None:
        self.state.state = PhoneState.BOOTING
        self.state.power_button_blocked = True
        self.state.videos_loaded = False
        self._boot_elapsed = 0.0

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

    def _go_home(self) -> None:
        if self.state.state == PhoneState.ON:
            self._close_app()

    def _close_app(self) -> None:
        if self.zasora_app.state.is_running:
            self.zasora_app.stop()
        if self.calc_app.state.is_running:
            self.calc_app.stop()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if button == arcade.MOUSE_BUTTON_LEFT:
            pb_rect_left = self.layout.power_button_x
            pb_rect_right = self.layout.power_button_x + self.layout.power_button_size
            pb_rect_bottom = self.layout.power_button_y
            pb_rect_top = self.layout.power_button_y + self.layout.power_button_size
            
            if pb_rect_left <= x <= pb_rect_right and pb_rect_bottom <= y <= pb_rect_top:
                if not self.state.power_button_blocked:
                    self._toggle_power()
                return True
                
            hb_rect_left = self.layout.home_button_x
            hb_rect_right = self.layout.home_button_x + self.layout.home_button_size
            hb_rect_bottom = self.layout.home_button_y
            hb_rect_top = self.layout.home_button_y + self.layout.home_button_size
            
            if hb_rect_left <= x <= hb_rect_right and hb_rect_bottom <= y <= hb_rect_top:
                if self.state.state == PhoneState.ON:
                    self._go_home()
                return True

        if self.zasora_app.state.is_running:
            if self.zasora_app.on_mouse_press(x, y, button, modifiers):
                return True
            if button == arcade.MOUSE_BUTTON_RIGHT:
                self._close_app()
                return True
                
        if self.calc_app.state.is_running:
            if self.calc_app.on_mouse_press(x, y, button, modifiers):
                return True
            if button == arcade.MOUSE_BUTTON_RIGHT:
                self._close_app()
                return True

        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.state.state == PhoneState.ON and not self.zasora_app.state.is_running and not self.calc_app.state.is_running:
                app_clicked = self.home.check_app_icon_click(x, y, self.layout.phone_x, self.layout.phone_y)
                if app_clicked == "zasora":
                    self.zasora_app.start()
                    return True
                elif app_clicked == "calc":
                    self.calc_app.start()
                    return True
        return False

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if self.zasora_app.state.is_running:
            if self.zasora_app.on_mouse_release(x, y, button, modifiers):
                return True
        if self.calc_app.state.is_running:
            if self.calc_app.on_mouse_release(x, y, button, modifiers):
                return True
        return False

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> bool:
        if self.zasora_app.state.is_running:
            return self.zasora_app.on_mouse_motion(x, y, dx, dy)
        if self.calc_app.state.is_running:
            return self.calc_app.on_mouse_motion(x, y, dx, dy)
        return False

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if self.zasora_app.state.is_running:
            self.zasora_app.on_key_press(symbol, modifiers)

    def on_text(self, text: str) -> None:
        if self.zasora_app.state.is_running:
            self.zasora_app.on_text(text)

    def update(self, delta_time: float) -> None:
        if self._zasora_app:
            self._zasora_app.update(delta_time)
        if self._calc_app:
            self._calc_app.update(delta_time)
            
        if self.state.power_button_blocked and self.state.state == PhoneState.ON:
            self.state.power_button_block_time -= delta_time
            if self.state.power_button_block_time <= 0:
                self.state.power_button_blocked = False
                
        if self.state.state == PhoneState.BOOTING:
            self._boot_elapsed += delta_time
            if self._boot_elapsed >= BOOT_DURATION:
                self._complete_boot()

    def draw(self) -> None:
        self.layout.draw_base()

        if self.state.state == PhoneState.OFF:
            self.layout.draw_off_screen()
        elif self.state.state == PhoneState.BOOTING:
            progress = min(self._boot_elapsed / BOOT_DURATION, 1.0)
            self.layout.draw_boot_screen(progress)
        elif self.state.state == PhoneState.ON:
            if self.zasora_app.state.is_running:
                self.zasora_app.draw()
            elif self.calc_app.state.is_running:
                self.calc_app.draw()
            else:
                self.home.draw(self.layout.phone_x, self.layout.phone_y)

        self.layout.draw_overlay(self.state)