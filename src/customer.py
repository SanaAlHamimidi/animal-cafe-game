"""
customer.py - Handles animal customers, their moods, and orders
Owner: Zara
"""
import random
import arcade
from src.constants import (
    MOOD_HAPPY, MOOD_IMPATIENT, MOOD_NORMAL,
    HAPPY_TIME, IMPATIENT_TIME, NORMAL_TIME
)


def draw_rect(cx, cy, w, h, color):
    try:
        arcade.draw_rectangle_filled(cx, cy, w, h, color)
    except AttributeError:
        arcade.draw_lbwh_rectangle_filled(cx - w / 2, cy - h / 2, w, h, color)


def draw_rect_outline(cx, cy, w, h, color, border=2):
    try:
        arcade.draw_rectangle_outline(cx, cy, w, h, color, border)
    except AttributeError:
        arcade.draw_lbwh_rectangle_outline(cx - w / 2, cy - h / 2, w, h, color, border)


class Customer:
    """Represents an animal customer visiting the cafe."""

    ANIMAL_TYPES = ["cat", "dog", "bunny", "bear", "fox"]

    def __init__(self, x: float, y: float, recipes: dict):
        self.x = x
        self.y = y
        self.recipes = recipes

        self.animal_type = random.choice(self.ANIMAL_TYPES)
        self.mood = random.choice([MOOD_HAPPY, MOOD_IMPATIENT, MOOD_NORMAL])
        self.order = self._pick_order()
        self.time_limit = self._get_time_limit()
        self.time_remaining = self.time_limit
        self.is_served = False
        self.is_leaving = False

    def _pick_order(self) -> str:
        return random.choice(list(self.recipes.keys()))

    def _get_time_limit(self) -> float:
        return {MOOD_HAPPY: HAPPY_TIME, MOOD_IMPATIENT: IMPATIENT_TIME, MOOD_NORMAL: NORMAL_TIME}[self.mood]

    def update(self, delta_time: float):
        if not self.is_served and not self.is_leaving:
            self.time_remaining -= delta_time
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.is_leaving = True

    def get_patience_ratio(self) -> float:
        return max(0.0, self.time_remaining / self.time_limit)

    def get_required_ingredients(self) -> list:
        return self.recipes.get(self.order, {}).get("ingredients", [])

    def draw(self):
        color_map = {
            "cat": (255, 200, 180),
            "dog": (210, 180, 140),
            "bunny": (220, 200, 255),
            "bear": (160, 100, 60),
            "fox": (230, 130, 50),
        }
        color = color_map.get(self.animal_type, (255, 255, 255))

        # Body circle
        arcade.draw_circle_filled(self.x, self.y, 40, color)
        arcade.draw_circle_outline(self.x, self.y, 40, (80, 40, 20), 3)

        # Animal label
        arcade.draw_text(self.animal_type.capitalize(), self.x, self.y - 10,
                         (80, 40, 20), 12, anchor_x="center")

        # Mood label
        mood_labels = {MOOD_HAPPY: ":)", MOOD_IMPATIENT: ">:(", MOOD_NORMAL: ":|"}
        arcade.draw_text(mood_labels.get(self.mood, ""), self.x, self.y + 28,
                         (80, 40, 20), 14, anchor_x="center", bold=True)

        self._draw_speech_bubble()
        self._draw_patience_bar()

    def _draw_speech_bubble(self):
        bx, by = self.x + 60, self.y + 55
        draw_rect(bx, by, 120, 36, (255, 255, 255))
        draw_rect_outline(bx, by, 120, 36, (80, 40, 20), 2)
        arcade.draw_text(self.order, bx, by - 7, (80, 40, 20), 11, anchor_x="center")

    def _draw_patience_bar(self):
        bar_width = 80
        ratio = self.get_patience_ratio()
        filled = bar_width * ratio

        # Background
        draw_rect(self.x, self.y - 60, bar_width, 10, (200, 200, 200))

        # Filled portion
        if filled > 0:
            if ratio > 0.5:
                bar_color = (50, 200, 50)
            elif ratio > 0.25:
                bar_color = (220, 200, 0)
            else:
                bar_color = (220, 50, 50)
            draw_rect(self.x - (bar_width - filled) / 2, self.y - 60, filled, 10, bar_color)

        draw_rect_outline(self.x, self.y - 60, bar_width, 10, (100, 100, 100), 1)
