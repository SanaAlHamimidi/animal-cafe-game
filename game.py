"""
game.py - Main game window with menu, gameplay, and end screen states
Owner: Sana (setup, scoring, timer) & Zara (customers, UI)
"""
import arcade
import json
import random
import os

from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    STATE_MENU, STATE_PLAYING, STATE_GAME_OVER,
    COLOR_BG, COLOR_TEXT, COLOR_SCORE
)
from src.customer import Customer
from src.order_checker import OrderChecker
from src.ingredient_tray import IngredientTray


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
GAME_DURATION = 120  # seconds per round


class AnimalCafeGame(arcade.Window):
    """Main game window managing all states and game logic."""

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(COLOR_BG)

        self.state = STATE_MENU
        self.recipes: dict = {}
        self.all_ingredients: list = []

        # Game objects (set up in setup())
        self.customers: list[Customer] = []
        self.order_checker: OrderChecker = None
        self.tray: IngredientTray = None

        # Game timer
        self.game_time_remaining = GAME_DURATION

        # Feedback message after serving
        self.feedback_message = ""
        self.feedback_timer = 0.0

        # Customer spawn timer
        self.spawn_timer = 0.0
        self.spawn_interval = 8.0  # seconds between new customers

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def setup(self):
        """Load data and initialize game objects."""
        self._load_data()
        self._reset_game()

    def _load_data(self):
        """Load recipes.json and animal_preferences.json."""
        recipes_path = os.path.join(DATA_DIR, "recipes.json")
        try:
            with open(recipes_path) as f:
                self.recipes = json.load(f)
        except FileNotFoundError:
            print(f"Warning: {recipes_path} not found. Using defaults.")
            self.recipes = {
                "Cupcake":    {"ingredients": ["flour", "sugar", "butter", "egg"]},
                "Cookie":     {"ingredients": ["flour", "sugar", "butter"]},
                "Muffin":     {"ingredients": ["flour", "sugar", "egg", "milk"]},
                "Croissant":  {"ingredients": ["flour", "butter", "milk"]},
                "Cake Pop":   {"ingredients": ["flour", "sugar", "butter", "egg", "sprinkles"]},
            }

        # Collect all unique ingredients across all recipes
        seen = set()
        for recipe in self.recipes.values():
            for ing in recipe["ingredients"]:
                seen.add(ing)
        self.all_ingredients = sorted(list(seen))

    def _reset_game(self):
        """Reset all game state for a new round."""
        self.customers = []
        self.order_checker = OrderChecker()
        self.tray = IngredientTray(self.all_ingredients)
        self.game_time_remaining = GAME_DURATION
        self.feedback_message = ""
        self.feedback_timer = 0.0
        self.spawn_timer = 0.0
        self._spawn_customer()  # Start with one customer

    def _spawn_customer(self):
        """Add a new customer at a position along the counter."""
        if len(self.customers) >= 3:
            return  # Max 3 customers at once
        x_positions = [200, 450, 700]
        occupied = {int(c.x) for c in self.customers}
        available = [x for x in x_positions if x not in occupied]
        if not available:
            return
        x = random.choice(available)
        self.customers.append(Customer(x, 420, self.recipes))

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def on_update(self, delta_time: float):
        if self.state != STATE_PLAYING:
            return

        # Game countdown
        self.game_time_remaining -= delta_time
        if self.game_time_remaining <= 0:
            self.game_time_remaining = 0
            self.state = STATE_GAME_OVER
            return

        # Update customers
        for customer in self.customers[:]:
            customer.update(delta_time)
            if customer.is_leaving:
                self.order_checker.customer_left_without_serving()
                self.customers.remove(customer)

        # Spawn new customers
        self.spawn_timer += delta_time
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self._spawn_customer()

        # Feedback message timeout
        if self.feedback_timer > 0:
            self.feedback_timer -= delta_time
            if self.feedback_timer <= 0:
                self.feedback_message = ""

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def on_draw(self):
        self.clear()
        if self.state == STATE_MENU:
            self._draw_menu()
        elif self.state == STATE_PLAYING:
            self._draw_game()
        elif self.state == STATE_GAME_OVER:
            self._draw_game_over()

    def _draw_menu(self):
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (255, 220, 180)
        )
        arcade.draw_text(
            "🐾 Animal Cafe 🐾",
            SCREEN_WIDTH // 2, 500,
            COLOR_TEXT, 52, anchor_x="center", bold=True
        )
        arcade.draw_text(
            "Serve adorable animal customers before their patience runs out!",
            SCREEN_WIDTH // 2, 400,
            COLOR_TEXT, 18, anchor_x="center"
        )
        arcade.draw_text(
            "Click ingredients → Press SERVE → Score points!",
            SCREEN_WIDTH // 2, 355,
            COLOR_TEXT, 16, anchor_x="center"
        )
        # Play button
        arcade.draw_rectangle_filled(SCREEN_WIDTH // 2, 260, 200, 60, (180, 100, 60))
        arcade.draw_text(
            "PLAY",
            SCREEN_WIDTH // 2, 245,
            arcade.color.WHITE, 28, anchor_x="center", bold=True
        )

    def _draw_game(self):
        # Cafe background
        arcade.draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                     SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG)
        # Counter
        arcade.draw_rectangle_filled(SCREEN_WIDTH // 2, 300, SCREEN_WIDTH, 20, (180, 120, 80))

        # Draw customers
        for customer in self.customers:
            customer.draw()

        # Draw ingredient tray
        self.tray.draw()

        # HUD — score and timer
        arcade.draw_text(
            f"Score: {self.order_checker.total_score}",
            20, SCREEN_HEIGHT - 40,
            COLOR_SCORE, 22, bold=True
        )
        mins = int(self.game_time_remaining) // 60
        secs = int(self.game_time_remaining) % 60
        arcade.draw_text(
            f"Time: {mins}:{secs:02d}",
            SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40,
            COLOR_TEXT, 22, bold=True
        )

        # Feedback
        if self.feedback_message:
            arcade.draw_text(
                self.feedback_message,
                SCREEN_WIDTH // 2, 200,
                arcade.color.DARK_GREEN, 20,
                anchor_x="center", bold=True
            )

    def _draw_game_over(self):
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT, (255, 210, 170)
        )
        summary = self.order_checker.get_summary()
        arcade.draw_text("Game Over!", SCREEN_WIDTH // 2, 530,
                         COLOR_TEXT, 50, anchor_x="center", bold=True)
        arcade.draw_text(f"Final Score: {summary['score']}",
                         SCREEN_WIDTH // 2, 440, COLOR_SCORE, 34, anchor_x="center")
        arcade.draw_text(f"Orders Completed: {summary['completed']}",
                         SCREEN_WIDTH // 2, 385, COLOR_TEXT, 22, anchor_x="center")
        arcade.draw_text(f"Orders Missed: {summary['missed']}",
                         SCREEN_WIDTH // 2, 345, COLOR_TEXT, 22, anchor_x="center")
        arcade.draw_text(f"Accuracy: {summary['accuracy']}%",
                         SCREEN_WIDTH // 2, 305, COLOR_TEXT, 22, anchor_x="center")
        # Replay button
        arcade.draw_rectangle_filled(SCREEN_WIDTH // 2, 220, 220, 60, (180, 100, 60))
        arcade.draw_text("PLAY AGAIN", SCREEN_WIDTH // 2, 205,
                         arcade.color.WHITE, 22, anchor_x="center", bold=True)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def on_mouse_press(self, x, y, button, modifiers):
        if self.state == STATE_MENU:
            # Check PLAY button click
            if abs(x - SCREEN_WIDTH // 2) <= 100 and abs(y - 260) <= 30:
                self._reset_game()
                self.state = STATE_PLAYING

        elif self.state == STATE_PLAYING:
            action = self.tray.on_click(x, y)
            if action == "submit":
                self._handle_submit()

        elif self.state == STATE_GAME_OVER:
            if abs(x - SCREEN_WIDTH // 2) <= 110 and abs(y - 220) <= 30:
                self._reset_game()
                self.state = STATE_PLAYING

    def _handle_submit(self):
        """Process the player's assembled order against the first waiting customer."""
        if not self.customers:
            self.feedback_message = "No customers yet!"
            self.feedback_timer = 2.0
            return

        # Serve the customer who has been waiting longest (first in list)
        customer = self.customers[0]
        player_ingredients = self.tray.get_selected()

        if not player_ingredients:
            self.feedback_message = "Select some ingredients first!"
            self.feedback_timer = 2.0
            return

        result = self.order_checker.check_order(
            customer.get_required_ingredients(),
            player_ingredients,
            customer.get_patience_ratio()
        )

        self.feedback_message = result["message"]
        self.feedback_timer = 2.5
        customer.is_served = True
        self.customers.remove(customer)
        self.tray.clear_selection()
        self._spawn_customer()
