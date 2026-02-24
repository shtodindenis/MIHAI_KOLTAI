from __future__ import annotations
import orjson
import arcade

def load_json(path: str) -> dict:
    with open(path, "rb") as f:
        return orjson.loads(f.read())

def save_json(path: str, data: dict) -> None:
    with open(path, "wb") as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

def make_rect(x: float, y: float, width: float, height: float) -> arcade.Rect:
    return arcade.Rect(x, x + width, y, y + height, width, height, x + width / 2, y + height / 2)

def make_centered_rect(x: float, y: float, width: float, height: float) -> arcade.Rect:
    left = x - width / 2
    right = x + width / 2
    bottom = y - height / 2
    top = y + height / 2
    return arcade.Rect(left, right, bottom, top, width, height, x, y)