from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.composables.zasora.dataLoader import load_interactions

@dataclass
class VideoInteractionState:
    likes: int = 0
    is_liked: bool = False
    comments: list[dict[str, str]] = field(default_factory=list)

@dataclass
class ZasoraState:
    is_running: bool = False
    video_files: list[Path] = field(default_factory=list)
    shuffled_order: list[int] = field(default_factory=list)
    current_video_index: int = 0
    videos_played: int = 0
    phrases: dict[str, dict[str, str]] = field(default_factory=dict)
    interactions: dict[str, VideoInteractionState] = field(default_factory=dict)
    y_offset: float = 0.0
    swipe_velocity: float = 0.0
    show_comments: bool = False
    is_paused: bool = False

    def __post_init__(self) -> None:
        from src.composables.zasora.dataLoader import load_interactions
        from src.composables.zasora.videoLoader import load_videos
        self.interactions = load_interactions()
        self.video_files, self.shuffled_order = load_videos()

    def reset(self) -> None:
        self.is_running = False
        self.current_video_index = 0
        self.videos_played = 0
        self.y_offset = 0.0
        self.swipe_velocity = 0.0
        self.show_comments = False
        self.is_paused = False

    def next_video(self) -> int:
        self.videos_played += 1
        self.current_video_index += 1
        if self.current_video_index >= len(self.shuffled_order):
            self.current_video_index = 0
            self.videos_played = 0
        self.show_comments = False
        self.is_paused = False
        return self.current_video_index

    def prev_video(self) -> int:
        if self.current_video_index > 0:
            self.current_video_index -= 1
            self.videos_played = max(0, self.videos_played - 1)
        self.show_comments = False
        self.is_paused = False
        return self.current_video_index

    def get_current_video(self) -> Path | None:
        if not self.video_files or not self.shuffled_order:
            return None
        actual_index = self.shuffled_order[self.current_video_index]
        if actual_index < len(self.video_files):
            return self.video_files[actual_index]
        return None

    def get_video_by_offset(self, offset: int) -> Path | None:
        if not self.video_files or not self.shuffled_order:
            return None
        idx = self.current_video_index + offset
        if 0 <= idx < len(self.shuffled_order):
            actual_index = self.shuffled_order[idx]
            if actual_index < len(self.video_files):
                return self.video_files[actual_index]
        return None

    def get_interaction(self, video_name: str) -> VideoInteractionState:
        if video_name not in self.interactions:
            self.interactions[video_name] = VideoInteractionState()
        return self.interactions[video_name]

    def save_interactions(self) -> None:
        from src.composables.zasora.dataLoader import save_interactions
        save_interactions(self.interactions)