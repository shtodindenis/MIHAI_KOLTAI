from __future__ import annotations
import arcade
from pathlib import Path
from src.states.zasora import ZasoraState
from src.shared.utils import make_rect

class CommentPanel:
    def __init__(self, state: ZasoraState, scale_factor: float) -> None:
        self.state = state
        self.scale_factor = scale_factor
        self.font_path = str(Path(__file__).parent.parent.parent.parent.parent / "assets" / "font.ttf")
        self.input_text = ""
        self.is_typing = False

    def on_mouse_press(self, x: float, y: float, cx: float, cy: float, cw: float, ch: float, current_vid: Path | None) -> str:
        if cx <= x <= cx + cw and cy <= y <= cy + ch:
            cs = 30 * self.scale_factor
            if cx + cw - cs - 10 * self.scale_factor <= x <= cx + cw and cy + ch - cs - 10 * self.scale_factor <= y <= cy + ch:
                self.is_typing = False
                return "close"
            self.is_typing = (cx + 10 * self.scale_factor <= x <= cx + cw - 10 * self.scale_factor and cy + 10 * self.scale_factor <= y <= cy + 40 * self.scale_factor)
            return "consume"
        self.is_typing = False
        return "outside"

    def on_key_press(self, symbol: int, modifiers: int, current_vid: Path | None) -> None:
        if self.is_typing and current_vid:
            if symbol == arcade.key.BACKSPACE: self.input_text = self.input_text[:-1]
            elif symbol in (arcade.key.ENTER, arcade.key.NUM_ENTER) and self.input_text.strip():
                self.state.get_interaction(current_vid.name).comments.insert(0, {"author": "Player", "text": self.input_text.strip()})
                self.state.save_interactions()
                self.input_text, self.is_typing = "", False

    def on_text(self, text: str) -> None:
        if self.is_typing and len(self.input_text) < 50 and text.isprintable(): self.input_text += text

    def draw(self, current_vid: Path, cx: float, cy: float, cw: float, ch: float) -> None:
        inter = self.state.get_interaction(current_vid.name)
        arcade.draw_rect_filled(make_rect(cx, cy, cw, ch), (25, 25, 25, 255))
        arcade.draw_text(
            f"{len(inter.comments)} комментариев", cx + cw/2, cy + ch - 15 * self.scale_factor, 
            arcade.color.WHITE, font_size=int(14 * self.scale_factor), 
            font_name=self.font_path, anchor_x="center", anchor_y="top", bold=True
        )
        
        close_x, close_y, cs = cx + cw - 20 * self.scale_factor, cy + ch - 20 * self.scale_factor, 6 * self.scale_factor
        arcade.draw_line(close_x - cs, close_y - cs, close_x + cs, close_y + cs, arcade.color.GRAY, 2)
        arcade.draw_line(close_x - cs, close_y + cs, close_x + cs, close_y - cs, arcade.color.GRAY, 2)
        arcade.draw_line(cx, cy + ch - 40 * self.scale_factor, cx + cw, cy + ch - 40 * self.scale_factor, (50, 50, 50, 255), 1)
        
        y_pos = cy + ch - 60 * self.scale_factor
        if not inter.comments:
            arcade.draw_text(
                "Нет комментариев", cx + cw/2, y_pos - 20 * self.scale_factor, 
                arcade.color.GRAY, font_size=int(14 * self.scale_factor), 
                font_name=self.font_path, anchor_x="center", anchor_y="top"
            )
        else:
            for comment in inter.comments[:5]:
                auth, txt = comment.get("author", "Player"), comment.get("text", "")
                ax, ay = cx + 20 * self.scale_factor, y_pos - 10 * self.scale_factor
                arcade.draw_circle_filled(ax, ay, 12 * self.scale_factor, arcade.color.GRAY)
                arcade.draw_text(
                    auth[0].upper(), ax, ay + 4 * self.scale_factor, arcade.color.WHITE, 
                    font_size=int(10 * self.scale_factor), font_name=self.font_path, 
                    anchor_x="center", anchor_y="center", bold=True
                )
                arcade.draw_text(
                    auth, cx + 40 * self.scale_factor, y_pos, (150, 150, 150, 255), 
                    font_size=int(12 * self.scale_factor), font_name=self.font_path, 
                    anchor_x="left", anchor_y="top", bold=True
                )
                arcade.draw_text(
                    txt, cx + 40 * self.scale_factor, y_pos - 18 * self.scale_factor, arcade.color.WHITE, 
                    font_size=int(13 * self.scale_factor), font_name=self.font_path, 
                    anchor_x="left", anchor_y="top"
                )
                y_pos -= 55 * self.scale_factor

        arcade.draw_rect_filled(make_rect(cx, cy, cw, 50 * self.scale_factor), (35, 35, 35, 255))
        arcade.draw_rect_filled(make_rect(cx + 10 * self.scale_factor, cy + 10 * self.scale_factor, cw - 20 * self.scale_factor, 30 * self.scale_factor), (60, 60, 60, 255) if self.is_typing else (50, 50, 50, 255))
        disp, col = (self.input_text + ("|" if self.is_typing else ""), arcade.color.WHITE) if self.input_text or self.is_typing else ("Добавить комментарий...", arcade.color.GRAY)
        arcade.draw_text(
            disp, cx + 20 * self.scale_factor, cy + 25 * self.scale_factor, col, 
            font_size=int(12 * self.scale_factor), font_name=self.font_path, 
            anchor_x="left", anchor_y="center"
        )