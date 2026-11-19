import pygame.font
from pygame.sprite import Group

from ship import Ship


class Scoreboard:
    """A class to report scoring information."""

    def __init__(self, ai_game):
        """Initialize scorekeeping attributes."""
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        self.text_color = (30, 30, 30)
        self.font = pygame.font.SysFont(None, 40)
        self.title_font = pygame.font.SysFont(None, 64)

        self.prep_images()

    def prep_images(self):
        """Prepare the images for every HUD element."""
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_player()
        self.prep_ships()
        self.prep_leaderboard()

    def prep_score(self):
        """Turn the score into a rendered image."""
        rounded_score = round(self.stats.score, -1)
        score_str = f"Score: {rounded_score:,}"
        self.score_image = self.font.render(score_str, True, self.text_color, self.settings.bg_color)
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def prep_high_score(self):
        """Turn the high score into a rendered image."""
        high_score = round(self.stats.high_score, -1)
        high_score_str = f"High score: {high_score:,}"
        self.high_score_image = self.font.render(
            high_score_str, True, self.text_color, self.settings.bg_color
        )
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = 20

    def prep_level(self):
        """Turn the level into a rendered image."""
        level_str = f"Level: {self.stats.level}"
        self.level_image = self.font.render(level_str, True, self.text_color, self.settings.bg_color)
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 10

    def prep_player(self):
        """Turn the current player's name into a rendered image."""
        name = self.stats.player_name or "Player"
        self.player_image = self.font.render(name, True, self.text_color, self.settings.bg_color)
        self.player_rect = self.player_image.get_rect()
        self.player_rect.left = 20
        self.player_rect.top = 20

    def prep_ships(self):
        """Show how many ships are left."""
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship = Ship(self.ai_game)
            ship.rect.x = 10 + ship_number * (ship.rect.width + 10)
            ship.rect.y = 60
            self.ships.add(ship)

    def prep_leaderboard(self):
        """Render the top saved scores for the inactive screen."""
        self.leaderboard_images = []
        heading = self.font.render("Top scores", True, self.text_color, self.settings.bg_color)
        heading_rect = heading.get_rect()
        heading_rect.centerx = self.screen_rect.centerx
        heading_rect.top = self.screen_rect.centery + 50
        self.leaderboard_images.append((heading, heading_rect))

        top_records = self.stats.records[:5]
        if not top_records:
            empty = self.font.render("No scores yet", True, self.text_color, self.settings.bg_color)
            empty_rect = empty.get_rect()
            empty_rect.centerx = self.screen_rect.centerx
            empty_rect.top = heading_rect.bottom + 10
            self.leaderboard_images.append((empty, empty_rect))
            return

        top = heading_rect.bottom + 10
        for record in top_records:
            line = f"{record['name']}  {record['score']:,}"
            image = self.font.render(line, True, self.text_color, self.settings.bg_color)
            rect = image.get_rect()
            rect.centerx = self.screen_rect.centerx
            rect.top = top
            self.leaderboard_images.append((image, rect))
            top += 36

    def check_high_score(self):
        """Check to see if there's a new high score."""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()

    def show_score(self):
        """Draw scores, level, player name, and ships to the screen."""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.player_image, self.player_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.ships.draw(self.screen)

    def show_leaderboard(self):
        """Draw the saved scores."""
        for image, rect in self.leaderboard_images:
            self.screen.blit(image, rect)
