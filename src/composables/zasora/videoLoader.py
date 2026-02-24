from pathlib import Path
import random


def load_videos() -> tuple[list[Path], list[int]]:
    video_dir = Path(__file__).parent.parent.parent.parent / "assets" / "video" / "zasora"
    video_files = []
    shuffled_order = []
    if video_dir.exists():
        video_files = list(video_dir.glob("*.webm")) + list(video_dir.glob("*.mp4"))
        indices = list(range(len(video_files)))
        random.shuffle(indices)
        shuffled_order = indices
    return video_files, shuffled_order