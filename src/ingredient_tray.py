"""
ingredient_tray.py - Manages clickable ingredients the player can select
Owner: Zara
"""
import arcade


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
        return (abs(click_x - self.x) <= self.width / 2 and
                abs(click_y - self.y) <= self.height / 2)

    def toggle(self):
        self.selected = not self.selected

    def draw(self):
        color = (255, 240, 150) if self.selected else (245, 225, 180)
        border = (200, 100, 0) if self.selected else (120, 70, 30)
        draw_rect(self.x, self.y, self.width, self.height, color)
        draw_rect_outline(self.x, self.y, self.width, self.height, border, 3 if self.selected else 1)
        arcade.draw_text(self.name, self.x, self.y - 8, (80, 40, 20), 11,
                         anchor_x="center", width=self.width - 4, align="center")


class IngredientTray:
    """Displays all available ingredients at the bottom of the screen."""

    def __init__(self, all_ingredients: list, start_x=100, y=80, spacing=100):
        self.ingredients = []
        for i, name in enumerate(all_ingredients):
            self.ingredients.append(Ingredient(name, start_x + i * spacing, y))

        self.submit_x = 880
        self.submit_y = 80
        self.submit_w = 110
        self.submit_h = 45

    def on_click(self, x: float, y: float):
        for ing in self.ingredients:
            if ing.is_clicked(x, y):
                ing.toggle()
                return "ingredient"
        if (abs(x - self.submit_x) <= self.submit_w / 2 and
                abs(y - self.submit_y) <= self.submit_h / 2):
            return "submit"
        return None

    def get_selected(self) -> list:
        return [ing.name for ing in self.ingredients if ing.selected]

    def clear_selection(self):
        for ing in self.ingredients:
            ing.selected = False

    def draw(self):
        draw_rect(500, 80, 1000, 100, (200, 150, 100))
        try:
            arcade.draw_line(0, 130, 1000, 130, (80, 40, 20), 3)
        except Exception:
            pass
        for ing in self.ingredients:
            ing.draw()
        draw_rect(self.submit_x, self.submit_y, self.submit_w, self.submit_h, (40, 160, 40))
        arcade.draw_text("Serve!", self.submit_x, self.submit_y - 8,
                         (255, 255, 255), 14, anchor_x="center", bold=True)
