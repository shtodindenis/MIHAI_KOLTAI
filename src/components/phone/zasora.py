from __future__ import annotations

import json
import random
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

import arcade
import pyglet
import pyglet.media

from src.states.zasora import ZasoraState

if TYPE_CHECKING:
    from src.core.asset_manager import AssetManager

ZASORA_HEADER_HEIGHT = 60
ZASORA_LOGO_SIZE = 40

def _make_rect(x: float, y: float, width: float, height: float) -> arcade.Rect:
    return arcade.Rect(x, x + width, y, y + height, width, height, x + width / 2, y + height / 2)

class VideoPlayer:
    def __init__(self) -> None:
        self._player: pyglet.media.Player | None = None
        self._source: pyglet.media.Source | None = None
        self._is_playing: bool = False

    def load(self, video_path: Path) -> bool:
        try:
            self._source = pyglet.media.load(str(video_path))
            self._player = pyglet.media.Player()
            self._player.queue(self._source)
            self._player.play()
            self._is_playing = True
            return True
        except Exception:
            return False

    def is_finished(self) -> bool:
        if not self._player:
            return True
        return not self._player.playing and not self._player.source

    def draw(self, x: float, y: float, width: float, height: float) -> None:
        if self._player and self._player.texture:
            self._player.texture.blit(x, y, width=width, height=height)

    def stop(self) -> None:
        if self._player:
            self._player.pause()
            self._player.delete()
            self._player = None
        self._source = None
        self._is_playing = False

class ZasoraApp:
    def __init__(
        self,
        asset_manager: AssetManager,
        app_area_x: float,
        app_area_y: float,
        app_area_w: float,
        app_area_h: float,
        scale_factor: float
    ) -> None:
        self.asset_manager = asset_manager
        self.state = ZasoraState()
        self.app_x = app_area_x
        self.app_y = app_area_y
        self.app_w = app_area_w
        self.app_h = app_area_h
        self.scale_factor = scale_factor
        self.header_height = ZASORA_HEADER_HEIGHT * scale_factor
        self.video_area_x = self.app_x
        self.video_area_y = self.app_y
        self.video_area_width = self.app_w
        self.video_area_height = self.app_h - self.header_height
        self._swipe_start_y: float = 0.0
        self._swipe_threshold: float = 50 * scale_factor
        self._is_swiping: bool = False
        self._last_swipe_time: float = 0.0
        self._swipe_cooldown: float = 0.3
        self._video_player = VideoPlayer()
        self._load_textures()
        self._load_videos()
        self._load_phrases()

    def _load_textures(self) -> None:
        self.zasora_logo_texture = self.asset_manager.get_texture("zasora")

    def _load_videos(self) -> None:
        video_dir = Path(__file__).parent.parent.parent.parent / "assets" / "video" / "zasora"
        if video_dir.exists():
            self.state.video_files = list(video_dir.glob("*.webm")) + list(video_dir.glob("*.mp4"))
            indices = list(range(len(self.state.video_files)))
            random.shuffle(indices)
            self.state.shuffled_order = indices

    def _load_phrases(self) -> None:
        phrases_path = Path(__file__).parent.parent.parent.parent / "assets" / "stories" / "phrases.json"
        if phrases_path.exists():
            with open(phrases_path, "r", encoding="utf-8") as f:
                try:
                    self.state.phrases = json.load(f)
                except Exception:
                    self.state.phrases = {}

    def start(self) -> None:
        self.state.is_running = True
        self._load_current_video()

    def stop(self) -> None:
        self.state.is_running = False
        self._video_player.stop()
        self.state.reset()

    def _load_current_video(self) -> None:
        self._video_player.stop()
        video_path = self.state.get_current_video()
        if video_path and video_path.exists():
            self._video_player.load(video_path)

    def _next_video(self) -> None:
        self.state.next_video()
        self._load_current_video()

    def _prev_video(self) -> None:
        self.state.prev_video()
        self._load_current_video()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not self.state.is_running:
            return False
        if button == arcade.MOUSE_BUTTON_LEFT:
            if (
                self.app_x <= x <= self.app_x + self.app_w
                and self.app_y <= y <= self.app_y + self.app_h
            ):
                self._is_swiping = True
                self._swipe_start_y = y
                return True
        return False

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not self.state.is_running or not self._is_swiping:
            return False
        if button == arcade.MOUSE_BUTTON_LEFT:
            self._is_swiping = False
            swipe_distance = y - self._swipe_start_y
            current_time = arcade.get_window().time
            if swipe_distance > self._swipe_threshold:
                if current_time - self._last_swipe_time > self._swipe_cooldown:
                    self._next_video()
                    self._last_swipe_time = current_time
                    return True
            elif swipe_distance < -self._swipe_threshold:
                if current_time - self._last_swipe_time > self._swipe_cooldown:
                    if self.state.current_video_index > 0:
                        self._prev_video()
                        self._last_swipe_time = current_time
                    return True
        return False

    def update(self, delta_time: float) -> None:
        if not self.state.is_running:
            return
        if self._video_player.is_finished():
            self._next_video()

    def draw(self) -> None:
        if not self.state.is_running:
            return

        header_y = self.app_y + self.app_h - self.header_height
        arcade.draw_rect_filled(
            _make_rect(self.app_x, header_y, self.app_w, self.header_height),
            arcade.color.BLACK,
        )

        logo_size = ZASORA_LOGO_SIZE * self.scale_factor
        logo_x = self.app_x + 10 * self.scale_factor
        logo_center_y = header_y + self.header_height / 2

        if self.zasora_logo_texture:
            arcade.draw_texture_rect(
                self.zasora_logo_texture,
                _make_rect(logo_x, logo_center_y - logo_size / 2, logo_size, logo_size),
            )

        font_path = Path(__file__).parent.parent.parent.parent / "assets" / "font.ttf"
        arcade.draw_text(
            "ZASORA",
            logo_x + logo_size + 15 * self.scale_factor,
            logo_center_y,
            arcade.color.WHITE,
            font_size=int(22 * self.scale_factor),
            font_name=str(font_path),
            anchor_x="left",
            anchor_y="center",
            bold=True,
        )

        self._draw_video()

        current_vid = self.state.get_current_video()
        if current_vid:
            phrase_info = self.state.phrases.get(current_vid.name, {})
            author = phrase_info.get("author", "")
            desc = phrase_info.get("describe", "")
            if author or desc:
                padding = 8 * self.scale_factor
                author_fs = int(14 * self.scale_factor)
                desc_fs = int(12 * self.scale_factor)
                
                max_chars = max(4, int((self.app_w - 30 * self.scale_factor) / (desc_fs * 0.5)))
                desc_lines = textwrap.wrap(desc, width=max_chars) if desc else []
                if len(desc_lines) > 3:
                    desc_lines = desc_lines[:3]
                    if len(desc_lines[-1]) > max_chars - 3:
                        desc_lines[-1] = desc_lines[-1][:max_chars-3] + "..."
                    else:
                        desc_lines[-1] += "..."
                        
                author_h = author_fs * 1.5 if author else 0
                desc_line_h = desc_fs * 1.3
                
                bg_w = self.app_w - 10 * self.scale_factor
                bg_h = padding * 2 + author_h + len(desc_lines) * desc_line_h
                bg_x = self.app_x + 5 * self.scale_factor
                bg_y = self.app_y + 10 * self.scale_factor
                
                arcade.draw_rect_filled(
                    _make_rect(bg_x, bg_y, bg_w, bg_h),
                    (0, 0, 0, 150)
                )
                
                text_x = bg_x + 10 * self.scale_factor
                current_y = bg_y + bg_h - padding
                
                if author:
                    arcade.draw_text(
                        author,
                        text_x,
                        current_y,
                        arcade.color.WHITE,
                        font_size=author_fs,
                        font_name=str(font_path),
                        anchor_x="left",
                        anchor_y="top",
                        bold=True
                    )
                    current_y -= author_h
                    
                for line in desc_lines:
                    arcade.draw_text(
                        line,
                        text_x,
                        current_y,
                        arcade.color.WHITE,
                        font_size=desc_fs,
                        font_name=str(font_path),
                        anchor_x="left",
                        anchor_y="top"
                    )
                    current_y -= desc_line_h

    def _draw_video(self) -> None:
        if self._video_player._player and self._video_player._player.texture:
            self._video_player.draw(
                self.video_area_x,
                self.video_area_y,
                self.video_area_width,
                self.video_area_height,
            )
        else:
            arcade.draw_text(
                "Loading...",
                self.video_area_x + self.video_area_width / 2,
                self.video_area_y + self.video_area_height / 2,
                arcade.color.GRAY,
                font_size=int(16 * self.scale_factor),
                anchor_x="center",
                anchor_y="center",
            )