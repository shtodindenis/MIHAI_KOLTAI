from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING
import arcade
from src.states.calc import CalcState
from src.shared.utils import make_rect
from src.ui.shapes import draw_rounded_rect

if TYPE_CHECKING:
    from src.core.asset_manager import AssetManager

BUTTONS = [
    ["C", "±", "%", "/"],
    ["7", "8", "9", "*"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "="]
]

class CalcApp:
    def __init__(self, asset_manager: AssetManager, app_area_x: float, app_area_y: float, app_area_w: float, app_area_h: float, scale_factor: float) -> None:
        self.asset_manager = asset_manager
        self.state = CalcState()
        self.scale_factor = scale_factor
        self.font_path = str(Path(__file__).parent.parent.parent.parent.parent / "assets" / "font.ttf")
        self.button_rects: list[tuple[arcade.Rect, str, tuple[int, int, int, int], tuple[int, int, int, int]]] = []
        self.resize(app_area_x, app_area_y, app_area_w, app_area_h)

    def resize(self, app_area_x: float, app_area_y: float, app_area_w: float, app_area_h: float) -> None:
        self.app_x = app_area_x
        self.app_y = app_area_y
        self.app_w = app_area_w
        self.app_h = app_area_h
        self._calculate_layout()

    def _calculate_layout(self) -> None:
        self.button_rects.clear()
        padding = 10 * self.scale_factor
        display_h = self.app_h * 0.35
        buttons_h = self.app_h - display_h
        
        cols = 4
        rows = 5
        
        btn_w = (self.app_w - padding * (cols + 1)) / cols
        btn_h = (buttons_h - padding * (rows + 1)) / rows
        
        start_y = self.app_y + buttons_h - padding - btn_h
        
        for r_idx, row in enumerate(BUTTONS):
            c_idx = 0
            while c_idx < len(row):
                char = row[c_idx]
                is_zero = (char == "0")
                
                w = btn_w * 2 + padding if is_zero else btn_w
                x = self.app_x + padding + c_idx * (btn_w + padding)
                y = start_y - r_idx * (btn_h + padding)
                
                rect = make_rect(x, y, w, btn_h)
                
                if char in ("/", "*", "-", "+"):
                    bg_col = (255, 255, 255, 255)
                    txt_col = (0, 0, 0, 255)
                elif char == "=":
                    bg_col = (255, 255, 255, 255)
                    txt_col = (0, 0, 0, 255)
                elif char in ("C", "±", "%"):
                    bg_col = (80, 80, 80, 255)
                    txt_col = (255, 255, 255, 255)
                else:
                    bg_col = (30, 30, 30, 255)
                    txt_col = (255, 255, 255, 255)
                    
                self.button_rects.append((rect, char, bg_col, txt_col))
                
                c_idx += 2 if is_zero else 1

    def start(self) -> None:
        self.state.is_running = True

    def stop(self) -> None:
        self.state.is_running = False

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not self.state.is_running:
            return False
            
        if self.app_x <= x <= self.app_x + self.app_w and self.app_y <= y <= self.app_y + self.app_h:
            if button == arcade.MOUSE_BUTTON_LEFT:
                for rect, char, _, _ in self.button_rects:
                    if rect.left <= x <= rect.right and rect.bottom <= y <= rect.top:
                        self.state.input_char(char)
                        return True
            return True
        return False

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not self.state.is_running:
            return False
        return False

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> bool:
        if not self.state.is_running:
            return False
        return False

    def update(self, delta_time: float) -> None:
        pass

    def draw(self) -> None:
        if not self.state.is_running:
            return

        arcade.draw_rect_filled(make_rect(self.app_x, self.app_y, self.app_w, self.app_h), (10, 10, 10, 255))
        
        display_y = self.app_y + self.app_h - 20 * self.scale_factor
        
        if self.state.expression:
            arcade.draw_text(
                self.state.expression,
                self.app_x + self.app_w - 20 * self.scale_factor,
                display_y,
                (150, 150, 150, 255),
                font_size=int(16 * self.scale_factor),
                font_name=self.font_path,
                anchor_x="right",
                anchor_y="top"
            )
            
        arcade.draw_text(
            self.state.display,
            self.app_x + self.app_w - 20 * self.scale_factor,
            display_y - 30 * self.scale_factor,
            arcade.color.WHITE,
            font_size=int(36 * self.scale_factor),
            font_name=self.font_path,
            anchor_x="right",
            anchor_y="top"
        )
        
        for rect, char, bg_col, txt_col in self.button_rects:
            r = 15 * self.scale_factor
            if char == "0":
                draw_rounded_rect(rect.left, rect.bottom, rect.width, rect.height, bg_col, r)
            else:
                draw_rounded_rect(rect.left, rect.bottom, rect.width, rect.height, bg_col, r)
                
            arcade.draw_text(
                char,
                rect.left + rect.width / 2,
                rect.bottom + rect.height / 2,
                txt_col,
                font_size=int(18 * self.scale_factor),
                font_name=self.font_path,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )