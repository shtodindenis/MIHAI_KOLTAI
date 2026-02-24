import base64
import json
from pathlib import Path
from typing import TYPE_CHECKING

from src.shared.constants import DATA_DIR

if TYPE_CHECKING:
    from src.states.zasora import VideoInteractionState

def _get_file_path() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filename = base64.b64encode(b"zasora_data").decode("utf-8")
    return DATA_DIR / filename

def load_interactions() -> dict[str, "VideoInteractionState"]:
    from src.states.zasora import VideoInteractionState
    file_path = _get_file_path()
    interactions = {}
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                encoded_data = f.read()
                decoded_data = base64.b64decode(encoded_data).decode("utf-8")
                data = json.loads(decoded_data)
                for k, v in data.items():
                    interactions[k] = VideoInteractionState(
                        likes=v.get("likes", 0),
                        is_liked=v.get("is_liked", False),
                        comments=v.get("comments", [])
                    )
        except Exception:
            pass
    return interactions

def save_interactions(interactions: dict[str, "VideoInteractionState"]) -> None:
    file_path = _get_file_path()
    data = {
        k: {
            "likes": v.likes,
            "is_liked": v.is_liked,
            "comments": v.comments
        }
        for k, v in interactions.items()
    }
    try:
        json_str = json.dumps(data, ensure_ascii=False)
        encoded_data = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(encoded_data)
    except Exception:
        pass