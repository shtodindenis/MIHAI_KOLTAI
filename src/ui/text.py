from __future__ import annotations
from typing import Any
import arcade

def draw_wrapped_text(
    text: str,
    x: float,
    y: float,
    width: float,
    font_size: int,
    color: Any,
    font_name: str,
    line_spacing_factor: float = 1.3,
    max_lines: int = 3
) -> float:
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if len(test_line) * font_size * 0.6 > width:
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                lines.append(test_line)
                current_line = ""
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:int(width / (font_size * 0.6)) - 3] + "..."

    curr_y = y
    for line in lines:
        arcade.draw_text(
            line, 
            x, 
            curr_y, 
            color, 
            font_size=font_size, 
            font_name=font_name, 
            anchor_x="left", 
            anchor_y="top"
        )
        curr_y -= font_size * line_spacing_factor
    
    return len(lines) * (font_size * line_spacing_factor)