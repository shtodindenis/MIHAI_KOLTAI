"""App icon UI component."""

from __future__ import annotations

import arcade


def _make_rect(x: float, y: float, width: float, height: float) -> arcade.Rect:
    """Create arcade.Rect from x, y, width, height (x, y is bottom-left corner)."""
    return arcade.Rect(x, x + width, y, y + height, width, height, x + width / 2, y + height / 2)


def _make_centered_rect(x: float, y: float, width: float, height: float) -> arcade.Rect:
    """Create arcade.Rect from center x, y and width, height."""
    left = x - width / 2
    right = x + width / 2
    bottom = y - height / 2
    top = y + height / 2
    return arcade.Rect(left, right, bottom, top, width, height, x, y)


class AppIcon:
    """App icon component with rounded square background."""

    def __init__(
        self,
        texture: arcade.Texture | None,
        label: str,
        x: float,
        y: float,
        size: float = 40.0,
        scale: float = 1.0,
        font_name: str | None = None,
    ) -> None:
        """
        Initialize app icon.

        Args:
            texture: Icon texture (drawn over black rounded square background)
            label: Text label below icon
            x: X position (center)
            y: Y position (center of icon, not including label)
            size: Icon size in pixels
            scale: Scale factor
            font_name: Font name for label
        """
        self.texture = texture
        self.label = label
        self.x = x
        self.y = y
        self.size = size * scale
        self.scale = scale
        self.font_name = font_name

        # Text height below icon
        self.text_height = 20 * scale

    def draw(self) -> None:
        """Draw the app icon."""
        # Draw black rounded square background (x, y is center)
        self._draw_rounded_rect_filled(
            self.x, self.y, self.size, self.size,
            arcade.color.BLACK,
            corner_radius=self.size * 0.2,  # 20% rounded corners
        )

        # Draw icon texture (75% of square size, centered)
        if self.texture:
            texture_size = self.size * 0.75
            texture_offset = (self.size - texture_size) / 2
            arcade.draw_texture_rect(
                self.texture,
                _make_rect(
                    self.x - self.size / 2 + texture_offset,
                    self.y - self.size / 2 + texture_offset,
                    texture_size,
                    texture_size,
                ),
            )

        # Draw label (immediately below icon, max 20px height, truncate with dots if needed)
        if self.label:
            font_size = int(10 * self.scale)  # Smaller font size
            label_y = self.y - self.size / 2 - font_size  # Start immediately below icon

            # Truncate label if it doesn't fit
            display_label = self._truncate_label(
                self.label, self.size, self.font_name or "calibri", font_size, self.text_height
            )

            arcade.draw_text(
                display_label,
                self.x,
                label_y,
                arcade.color.WHITE,
                font_size=font_size,
                font_name=self.font_name or "calibri",
                anchor_x="center",
                anchor_y="top",
            )

    def _truncate_label(
        self,
        label: str,
        available_width: float,
        font_name: str,
        font_size: int,
        max_height: float,
    ) -> str:
        """Truncate label with dots if it doesn't fit in available space."""
        # Simple truncation: if text is too long, cut it and add dots
        # Use smaller multiplier to allow more characters (0.45 instead of 0.6)
        max_chars = int(available_width / (font_size * 0.45))
        if len(label) > max_chars:
            return label[:max_chars - 3] + "..."
        return label

    def _draw_rounded_rect_filled(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        color: tuple[int, int, int],
        corner_radius: float,
    ) -> None:
        """Draw a filled rounded rectangle (x, y is center)."""
        # Convert center to bottom-left
        bl_x = x - width / 2
        bl_y = y - height / 2

        # Draw main rectangle
        arcade.draw_rect_filled(
            _make_rect(bl_x, bl_y, width, height),
            color,
        )

        # Draw corner circles
        radius = corner_radius
        # Bottom-left
        arcade.draw_circle_filled(
            bl_x + radius, bl_y + radius, radius, color
        )
        # Bottom-right
        arcade.draw_circle_filled(
            bl_x + width - radius, bl_y + radius, radius, color
        )
        # Top-left
        arcade.draw_circle_filled(
            bl_x + radius, bl_y + height - radius, radius, color
        )
        # Top-right
        arcade.draw_circle_filled(
            bl_x + width - radius, bl_y + height - radius, radius, color
        )

        # Draw side rectangles to fill gaps
        # Left
        arcade.draw_rect_filled(
            _make_rect(bl_x, bl_y + radius, radius, height - 2 * radius),
            color,
        )
        # Right
        arcade.draw_rect_filled(
            _make_rect(bl_x + width - radius, bl_y + radius, radius, height - 2 * radius),
            color,
        )
        # Bottom
        arcade.draw_rect_filled(
            _make_rect(bl_x + radius, bl_y, width - 2 * radius, radius),
            color,
        )
        # Top
        arcade.draw_rect_filled(
            _make_rect(bl_x + radius, bl_y + height - radius, width - 2 * radius, radius),
            color,
        )
