"""
customer.py - Handles animal customers, their moods, and orders
Owner: Zara
"""
import random
from src.constants import (
    MOOD_HAPPY, MOOD_IMPATIENT, MOOD_NORMAL,
    HAPPY_TIME, IMPATIENT_TIME, NORMAL_TIME
)


class Customer:
    """Represents an animal customer visiting the cafe."""

    ANIMAL_TYPES = ["cat", "dog", "bunny", "bear", "fox"]

    def __init__(self, x: float, y: float, recipes: dict):
        self.x = x
        self.y = y
        self.recipes = recipes  # dict loaded from recipes.json

        # Randomly assign animal type and mood
        self.animal_type = random.choice(self.ANIMAL_TYPES)
        self.mood = random.choice([MOOD_HAPPY, MOOD_IMPATIENT, MOOD_NORMAL])

        # Pick a random order based on animal preferences
        self.order = self._pick_order()

        # Set patience timer based on mood
        self.time_limit = self._get_time_limit()
        self.time_remaining = self.time_limit
        self.is_served = False
        self.is_leaving = False

    def _pick_order(self) -> str:
        """Pick a random recipe name from available recipes."""
        return random.choice(list(self.recipes.keys()))

    def _get_time_limit(self) -> float:
        """Return patience timer based on mood."""
        mood_times = {
            MOOD_HAPPY: HAPPY_TIME,
            MOOD_IMPATIENT: IMPATIENT_TIME,
            MOOD_NORMAL: NORMAL_TIME,
        }
        return mood_times[self.mood]

    def update(self, delta_time: float):
        """Decrease patience timer each frame."""
        if not self.is_served and not self.is_leaving:
            self.time_remaining -= delta_time
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.is_leaving = True  # Customer leaves unhappy

    def get_patience_ratio(self) -> float:
        """Returns 0.0 (out of time) to 1.0 (full patience)."""
        return max(0.0, self.time_remaining / self.time_limit)

    def get_required_ingredients(self) -> list:
        """Return the list of ingredients needed for this customer's order."""
        return self.recipes.get(self.order, {}).get("ingredients", [])

    def draw(self):
        """Draw the customer on screen (placeholder — replace with sprites)."""
        import arcade
        # Placeholder circle representing the animal
        color_map = {
            "cat": arcade.color.PEACH,
            "dog": arcade.color.TAN,
            "bunny": arcade.color.LAVENDER,
            "bear": arcade.color.BROWN,
            "fox": arcade.color.ORANGE,
        }
        color = color_map.get(self.animal_type, arcade.color.WHITE)
        arcade.draw_circle_filled(self.x, self.y, 40, color)
        arcade.draw_circle_outline(self.x, self.y, 40, arcade.color.DARK_BROWN, 3)

        # Animal label
        arcade.draw_text(
            self.animal_type.capitalize(),
            self.x, self.y - 10,
            arcade.color.DARK_BROWN, 12,
            anchor_x="center"
        )

        # Mood indicator
        mood_icons = {MOOD_HAPPY: "😊", MOOD_IMPATIENT: "😤", MOOD_NORMAL: "😐"}
        arcade.draw_text(
            mood_icons.get(self.mood, ""),
            self.x, self.y + 30,
            arcade.color.BLACK, 18,
            anchor_x="center"
        )

        # Speech bubble with order
        self._draw_speech_bubble()

        # Patience timer bar
        self._draw_patience_bar()

    def _draw_speech_bubble(self):
        """Draw a speech bubble showing the customer's order."""
        import arcade
        bx, by = self.x + 55, self.y + 50
        arcade.draw_rectangle_filled(bx, by, 120, 40, arcade.color.WHITE)
        arcade.draw_rectangle_outline(bx, by, 120, 40, arcade.color.DARK_BROWN, 2)
        arcade.draw_text(
            self.order,
            bx, by - 6,
            arcade.color.DARK_BROWN, 11,
            anchor_x="center"
        )

    def _draw_patience_bar(self):
        """Draw a patience/timer bar below the customer."""
        import arcade
        bar_width = 80
        ratio = self.get_patience_ratio()
        filled = bar_width * ratio

        # Background bar
        arcade.draw_rectangle_filled(self.x, self.y - 60, bar_width, 10, arcade.color.LIGHT_GRAY)

        # Filled portion — green → yellow → red
        if ratio > 0.5:
            bar_color = arcade.color.GREEN
        elif ratio > 0.25:
            bar_color = arcade.color.YELLOW
        else:
            bar_color = arcade.color.RED

        if filled > 0:
            arcade.draw_rectangle_filled(
                self.x - (bar_width - filled) / 2,
                self.y - 60,
                filled, 10, bar_color
            )
        arcade.draw_rectangle_outline(self.x, self.y - 60, bar_width, 10, arcade.color.DARK_GRAY, 1)
