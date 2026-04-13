"""
ingredient_tray.py - Manages clickable ingredients the player can select
Owner: Zara
"""
import arcade


class Ingredient:
    """A clickable ingredient on the tray."""

    def __init__(self, name: str, x: float, y: float, width=80, height=60):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selected = False

    def is_clicked(self, click_x: float, click_y: float) -> bool:
        """Return True if the click falls within this ingredient."""
        return (
            abs(click_x - self.x) <= self.width / 2 and
            abs(click_y - self.y) <= self.height / 2
        )

    def toggle(self):
        self.selected = not self.selected

    def draw(self):
        """Draw the ingredient as a colored box with label."""
        color = arcade.color.LIGHT_YELLOW if self.selected else arcade.color.BEIGE
        border = arcade.color.DARK_ORANGE if self.selected else arcade.color.DARK_BROWN

        arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height, color)
        arcade.draw_rectangle_outline(self.x, self.y, self.width, self.height, border,
                                      3 if self.selected else 1)
        arcade.draw_text(
            self.name,
            self.x, self.y - 8,
            arcade.color.DARK_BROWN, 11,
            anchor_x="center", width=self.width - 4, align="center"
        )


class IngredientTray:
    """
    Displays all available ingredients at the bottom of the screen.
    The player clicks to select/deselect them, then submits the order.
    """

    def __init__(self, all_ingredients: list, start_x=100, y=80, spacing=100):
        self.ingredients: list[Ingredient] = []
        for i, name in enumerate(all_ingredients):
            ing = Ingredient(name, start_x + i * spacing, y)
            self.ingredients.append(ing)

        # Submit button
        self.submit_x = 880
        self.submit_y = 80
        self.submit_w = 110
        self.submit_h = 45

    def on_click(self, x: float, y: float):
        """Toggle ingredient or detect submit button click."""
        for ing in self.ingredients:
            if ing.is_clicked(x, y):
                ing.toggle()
                return "ingredient"

        if (abs(x - self.submit_x) <= self.submit_w / 2 and
                abs(y - self.submit_y) <= self.submit_h / 2):
            return "submit"

        return None

    def get_selected(self) -> list:
        """Return names of currently selected ingredients."""
        return [ing.name for ing in self.ingredients if ing.selected]

    def clear_selection(self):
        """Deselect all ingredients after order is submitted."""
        for ing in self.ingredients:
            ing.selected = False

    def draw(self):
        # Tray background
        arcade.draw_rectangle_filled(500, 80, 1000, 100, (200, 150, 100))
        arcade.draw_line(0, 130, 1000, 130, arcade.color.DARK_BROWN, 3)

        for ing in self.ingredients:
            ing.draw()

        # Submit button
        arcade.draw_rectangle_filled(
            self.submit_x, self.submit_y, self.submit_w, self.submit_h,
            arcade.color.DARK_GREEN
        )
        arcade.draw_text(
            "Serve!",
            self.submit_x, self.submit_y - 8,
            arcade.color.WHITE, 14,
            anchor_x="center", bold=True
        )
