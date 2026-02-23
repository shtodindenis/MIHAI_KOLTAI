"""Phone state module."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path


class PhoneState(Enum):
    """Phone state enumeration."""

    OFF = auto()
    BOOTING = auto()
    ON = auto()


@dataclass
class PhoneData:
    """Phone state data class."""

    state: PhoneState = PhoneState.OFF
    boot_start_time: float = 0.0
    power_button_blocked: bool = False
    power_button_block_time: float = 0.0
    videos_loaded: bool = False
    video_files: list[Path] = field(default_factory=list)

    def reset(self) -> None:
        """Reset phone state to initial."""
        self.state = PhoneState.OFF
        self.boot_start_time = 0.0
        self.power_button_blocked = False
        self.power_button_block_time = 0.0
        self.videos_loaded = False
        self.video_files.clear()
