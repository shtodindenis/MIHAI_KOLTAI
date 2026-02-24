from __future__ import annotations
import json
from pathlib import Path
from typing import TYPE_CHECKING
import arcade
import pyglet
import pyglet.media
from src.states.zasora import ZasoraState
from src.components.phone.zasora.commentPanel import CommentPanel
from src.components.phone.zasora.header import ZasoraHeader
from src.shared.utils import make_rect, make_centered_rect
from src.ui.text import draw_wrapped_text

if TYPE_CHECKING:
    from src.core.asset_manager import AssetManager

ZASORA_HEADER_HEIGHT = 60

class VideoPlayer:
    def __init__(self) -> None:
        self._player: pyglet.media.Player | None = None
        self._source: pyglet.media.Source | None = None
        self._is_playing: bool = False
        self._wants_preload: bool = False

    def load(self, video_path: Path, auto_play: bool = True) -> bool:
        try:
            self.stop()
            self._source = pyglet.media.load(str(video_path))
            self._player = pyglet.media.Player()
            self._player.queue(self._source)
            self._player.volume = 1.0 if auto_play else 0.0
            self._player.play()
            self._is_playing = auto_play
            self._wants_preload = not auto_play
            return True
        except Exception: return False

    def update(self) -> None:
        if self._wants_preload and self._player and self._player.texture:
            self._player.pause()
            self._player.seek(0)
            self._player.volume = 1.0
            self._wants_preload = False

    def is_finished(self) -> bool:
        return not self._player or (not self._player.playing and not self._player.source)
        
    def seek_start(self) -> None:
        if self._player:
            try: self._player.seek(0)
            except Exception: pass

    def pause(self) -> None:
        if self._player and self._is_playing:
            self._player.pause()
            self._is_playing = False
            
    def play(self) -> None:
        if self._player and not self._is_playing:
            self._wants_preload = False
            self._player.volume = 1.0
            self._player.play()
            self._is_playing = True

    def draw(self, x: float, y: float, width: float, height: float) -> None:
        if self._player and self._player.texture:
            self._player.texture.blit(int(x), int(y), width=int(width), height=int(height))

    def stop(self) -> None:
        if self._player:
            self._player.pause()
            self._player.delete()
            self._player = None
        self._source = None
        self._is_playing = self._wants_preload = False

class ZasoraApp:
    def __init__(self, asset_manager: AssetManager, app_area_x: float, app_area_y: float, app_area_w: float, app_area_h: float, scale_factor: float) -> None:
        self.asset_manager = asset_manager
        self.state = ZasoraState()
        self.scale_factor = scale_factor
        self.resize(app_area_x, app_area_y, app_area_w, app_area_h)
        self._swipe_start_y = self.state.y_offset = 0.0
        self._is_swiping = False
        self._video_player, self._next_video_player, self._prev_video_player = VideoPlayer(), VideoPlayer(), VideoPlayer()
        self.comment_panel = CommentPanel(self.state, scale_factor)
        self.header = ZasoraHeader(asset_manager, scale_factor)
        self.font_path = str(Path(__file__).parent.parent.parent.parent.parent / "assets" / "font.ttf")
        self._load_resources()
        
    def resize(self, app_area_x: float, app_area_y: float, app_area_w: float, app_area_h: float) -> None:
        self.app_x, self.app_y, self.app_w, self.app_h = app_area_x, app_area_y, app_area_w, app_area_h
        self.header_height = ZASORA_HEADER_HEIGHT * getattr(self, "scale_factor", 1.0)
        self.video_area_x, self.video_area_y, self.video_area_width = self.app_x, self.app_y, self.app_w
        self.video_area_height = self.app_h - self.header_height

    def _load_resources(self) -> None:
        self.like_tex = self.asset_manager.get_texture("like")
        self.unlike_tex = self.asset_manager.get_texture("unlike")
        self.comment_tex = self.asset_manager.get_texture("comment")
        phrases_path = Path(__file__).parent.parent.parent.parent.parent / "assets" / "stories" / "phrases.json"
        if phrases_path.exists():
            try:
                with open(phrases_path, "r", encoding="utf-8") as f: self.state.phrases = json.load(f)
            except Exception: self.state.phrases = {}
        self._load_current_video()

    def start(self) -> None:
        self.state.is_running = True
        self._video_player.seek_start()
        self._video_player.play()

    def stop(self) -> None:
        self.state.is_running = False
        self._video_player.pause()

    def _load_current_video(self) -> None:
        if vid := self.state.get_current_video(): self._video_player.load(vid, False)
        if nxt := self.state.get_video_by_offset(1): self._next_video_player.load(nxt, False)
        if prv := self.state.get_video_by_offset(-1): self._prev_video_player.load(prv, False)

    def _finalize_swipe(self) -> None:
        threshold = self.video_area_height * 0.25
        if abs(self.state.y_offset) > threshold:
            direction = 1 if self.state.y_offset > 0 else -1
            if direction == 1:
                self.state.next_video()
                self._prev_video_player.stop()
                self._prev_video_player, self._video_player = self._video_player, self._next_video_player
                self._next_video_player = VideoPlayer()
                if nxt := self.state.get_video_by_offset(1): self._next_video_player.load(nxt, False)
            elif self.state.current_video_index > 0:
                self.state.prev_video()
                self._next_video_player.stop()
                self._next_video_player, self._video_player = self._video_player, self._prev_video_player
                self._prev_video_player = VideoPlayer()
                if prv := self.state.get_video_by_offset(-1): self._prev_video_player.load(prv, False)
            self._video_player.play()
        self.state.y_offset = 0.0
        self._video_player.seek_start()
        if not self.state.show_comments: self._video_player.play()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not self.state.is_running: return False
        if self.state.show_comments:
            action = self.comment_panel.on_mouse_press(x, y, self.app_x, self.app_y, self.app_w, self.app_h * 0.65, self.state.get_current_video())
            if action in ("close", "outside"):
                self.state.show_comments = False
                self._video_player.play()
            return True
        if self.app_x <= x <= self.app_x + self.app_w and self.app_y <= y <= self.app_y + self.app_h:
            if button == arcade.MOUSE_BUTTON_LEFT:
                self._is_swiping, self._swipe_start_y, self.state.swipe_velocity = True, y, 0
                return True
        return False

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if self._is_swiping and button == arcade.MOUSE_BUTTON_LEFT:
            self._is_swiping = False
            if abs(self._swipe_start_y - y) < 10: self._handle_click(x, y)
            else: self._finalize_swipe()
            return True
        return False
        
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> bool:
        if self._is_swiping and not self.state.show_comments:
            self.state.y_offset += dy
            self._video_player.pause()
            return True
        return False

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if self.state.show_comments: self.comment_panel.on_key_press(symbol, modifiers, self.state.get_current_video())

    def on_text(self, text: str) -> None:
        if self.state.show_comments: self.comment_panel.on_text(text)
        
    def _handle_click(self, x: float, y: float) -> None:
        lx, ly, ls = self.app_x + self.app_w - 40 * self.scale_factor, self.app_y + self.video_area_height / 2, 35 * self.scale_factor
        if lx - ls/2 <= x <= lx + ls/2:
            if ly - ls/2 <= y <= ly + ls/2: self._toggle_like(); return
            if ly - 65 * self.scale_factor - ls/2 <= y <= ly - 65 * self.scale_factor + ls/2:
                self.state.show_comments = True
                self._video_player.pause(); return
        self.state.is_paused = not self.state.is_paused
        if self.state.is_paused: self._video_player.pause()
        else: self._video_player.play()
            
    def _toggle_like(self) -> None:
        if vid := self.state.get_current_video():
            inter = self.state.get_interaction(vid.name)
            inter.is_liked = not inter.is_liked
            inter.likes += 1 if inter.is_liked else -1
            self.state.save_interactions()

    def update(self, delta_time: float) -> None:
        for p in [self._video_player, self._next_video_player, self._prev_video_player]: p.update()
        if not self.state.is_running: return
        if not self._is_swiping and self.state.y_offset != 0:
            if abs(self.state.y_offset) < 5:
                self.state.y_offset = 0
                if not self.state.is_paused and not self.state.show_comments: self._video_player.play()
            else: self.state.y_offset *= 0.8 
        if self._video_player.is_finished() and not self.state.is_paused and not self._is_swiping and self.state.y_offset == 0 and not self.state.show_comments:
            self.state.y_offset = self.video_area_height * 0.45 
            self._finalize_swipe()

    def draw(self) -> None:
        if not self.state.is_running: return
        ctx = arcade.get_window().ctx
        old_scissor = ctx.scissor
        ctx.scissor = (int(self.app_x), int(self.app_y), int(self.app_w), int(self.app_h))
        arcade.draw_rect_filled(make_rect(self.app_x, self.app_y, self.app_w, self.app_h), arcade.color.BLACK)
        yo = self.state.y_offset
        if yo > 0: self._next_video_player.draw(self.video_area_x, self.video_area_y + yo - self.video_area_height, self.video_area_width, self.video_area_height)
        if yo < 0: self._prev_video_player.draw(self.video_area_x, self.video_area_y + yo + self.video_area_height, self.video_area_width, self.video_area_height)
        self._video_player.draw(self.video_area_x, self.video_area_y + yo, self.video_area_width, self.video_area_height)
        if self.state.is_paused and not self.state.show_comments:
            arcade.draw_circle_filled(self.app_x + self.app_w/2, self.app_y + self.video_area_height/2, 30 * self.scale_factor, (0, 0, 0, 150))
            arcade.draw_triangle_filled(self.app_x + self.app_w/2 - 10 * self.scale_factor, self.app_y + self.video_area_height/2 + 15 * self.scale_factor, self.app_x + self.app_w/2 - 10 * self.scale_factor, self.app_y + self.video_area_height/2 - 15 * self.scale_factor, self.app_x + self.app_w/2 + 15 * self.scale_factor, self.app_y + self.video_area_height/2, arcade.color.WHITE)
        if vid := self.state.get_current_video():
            self._draw_overlay(vid); self._draw_interactions(vid)
            if self.state.show_comments: self.comment_panel.draw(vid, self.app_x, self.app_y, self.app_w, self.app_h * 0.65)
        self.header.draw(self.app_x, self.app_y, self.app_w, self.app_h, self.header_height)
        ctx.scissor = old_scissor

    def _draw_overlay(self, current_vid: Path) -> None:
        info = self.state.phrases.get(current_vid.name, {})
        auth, desc = info.get("author", ""), info.get("describe", "")
        if auth or desc:
            pad, afs, dfs, aw = 10 * self.scale_factor, int(14 * self.scale_factor), int(12 * self.scale_factor), self.app_w - 70 * self.scale_factor 
            h = pad * 2 + (afs * 1.5 if auth else 0) + (len(desc.split())//3 + 1) * dfs * 1.3
            arcade.draw_rect_filled(make_rect(self.app_x + 5 * self.scale_factor, self.app_y + 10 * self.scale_factor, aw + pad * 2, h), (0, 0, 0, 150))
            tx, cy = self.app_x + 5 * self.scale_factor + pad, self.app_y + 10 * self.scale_factor + h - pad
            if auth:
                arcade.draw_text(
                    f"@{auth}", tx, cy, arcade.color.WHITE, 
                    font_size=afs, font_name=self.font_path, 
                    anchor_x="left", anchor_y="top", bold=True
                )
                cy -= afs * 1.5
            draw_wrapped_text(desc, tx, cy, aw, dfs, arcade.color.WHITE, self.font_path)

    def _draw_interactions(self, current_vid: Path) -> None:
        inter = self.state.get_interaction(current_vid.name)
        ix, ly, r = self.app_x + self.app_w - 25 * self.scale_factor, self.app_y + self.video_area_height / 2, 18 * self.scale_factor
        for y, tex, val in [(ly, self.like_tex if inter.is_liked else self.unlike_tex, inter.likes), (ly - 65 * self.scale_factor, self.comment_tex, len(inter.comments))]:
            arcade.draw_circle_filled(ix, y, r, (0, 0, 0, 150))
            if tex: arcade.draw_texture_rect(tex, make_centered_rect(ix, y, r * 1.2, r * 1.2))
            arcade.draw_text(
                str(val), ix, y - r - 5 * self.scale_factor, arcade.color.WHITE, 
                font_size=int(12 * self.scale_factor), font_name=self.font_path, 
                anchor_x="center", anchor_y="top"
            )