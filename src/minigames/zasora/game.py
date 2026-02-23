"""Zasora minigame with video player."""

from __future__ import annotations

import random
from pathlib import Path

import pyglet
import pyglet.media


class ZasoraGame:
    """Zasora minigame that plays videos in shuffled order with TikTok-style navigation."""

    def __init__(self) -> None:
        self.video_files: list[Path] = []
        self.shuffled_order: list[int] = []
        self.current_index: int = 0
        self.videos_played: int = 0

        self._player: pyglet.media.Player | None = None
        self._is_playing: bool = False

    def load_videos(self) -> None:
        """Load and shuffle video files."""
        video_dir = Path(__file__).parent.parent.parent.parent / "assets" / "video" / "zasora"
        if video_dir.exists():
            self.video_files = list(video_dir.glob("*.webm"))

            # Create shuffled order
            indices = list(range(len(self.video_files)))
            random.shuffle(indices)
            self.shuffled_order = indices

    def start(self) -> None:
        """Start playing videos."""
        if not self.video_files:
            self.load_videos()

        if self.video_files and self.shuffled_order:
            self._play_current_video()
            self._is_playing = True

    def stop(self) -> None:
        """Stop video playback."""
        self._stop_video()
        self._is_playing = False

    def _stop_video(self) -> None:
        """Stop current video."""
        if self._player:
            self._player.pause()
            self._player.delete()
            self._player = None

    def _play_current_video(self) -> None:
        """Play current video from shuffled list."""
        self._stop_video()

        if not self.shuffled_order or self.current_index >= len(self.shuffled_order):
            return

        actual_index = self.shuffled_order[self.current_index]
        if actual_index >= len(self.video_files):
            return

        video_path = self.video_files[actual_index]
        if video_path.exists():
            try:
                self._player = pyglet.media.Player()
                source = pyglet.media.load(str(video_path))
                self._player.queue(source)
                self._player.play()
            except Exception as e:
                print(f"Failed to play video {video_path}: {e}")

    def next_video(self) -> None:
        """Go to next video in shuffled order."""
        self.videos_played += 1
        self.current_index += 1

        # Loop back when all videos played
        if self.current_index >= len(self.shuffled_order):
            self.current_index = 0
            self.videos_played = 0

        if self._is_playing:
            self._play_current_video()

    def prev_video(self) -> None:
        """Go to previous video."""
        if self.current_index > 0:
            self.current_index -= 1
            self.videos_played = max(0, self.videos_played - 1)

            if self._is_playing:
                self._play_current_video()

    def update(self, delta_time: float) -> None:
        """Update game state."""
        if not self._is_playing:
            return

        # Check if video finished
        if self._player and not self._player.source:
            self.next_video()

    @property
    def current_video_path(self) -> Path | None:
        """Get current video path."""
        if not self.video_files or not self.shuffled_order:
            return None

        actual_index = self.shuffled_order[self.current_index]
        if actual_index < len(self.video_files):
            return self.video_files[actual_index]
        return None

    @property
    def video_info(self) -> dict:
        """Get current video info."""
        return {
            "current": self.current_index + 1,
            "total": len(self.video_files),
            "path": self.current_video_path,
        }
