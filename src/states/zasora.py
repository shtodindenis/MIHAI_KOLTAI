from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ZasoraState:
    is_running: bool = False
    video_files: list[Path] = field(default_factory=list)
    shuffled_order: list[int] = field(default_factory=list)
    current_video_index: int = 0
    videos_played: int = 0
    phrases: dict[str, dict[str, str]] = field(default_factory=dict)

    def reset(self) -> None:
        self.is_running = False
        self.current_video_index = 0
        self.videos_played = 0

    def next_video(self) -> int:
        self.videos_played += 1
        self.current_video_index += 1
        if self.current_video_index >= len(self.shuffled_order):
            self.current_video_index = 0
            self.videos_played = 0
        return self.current_video_index

    def prev_video(self) -> int:
        if self.current_video_index > 0:
            self.current_video_index -= 1
            self.videos_played = max(0, self.videos_played - 1)
        return self.current_video_index

    def get_current_video(self) -> Path | None:
        if not self.video_files or not self.shuffled_order:
            return None
        actual_index = self.shuffled_order[self.current_video_index]
        if actual_index < len(self.video_files):
            return self.video_files[actual_index]
        return None