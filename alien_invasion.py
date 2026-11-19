import sys
from time import sleep

import pygame

from alien import Alien
from bullet import Bullet
from button import Button
from game_stats import GameStats, save_score
from scoreboard import Scoreboard
from setting import Setting
from ship import Ship


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Setting()
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption("Alien Invasion")

        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()
        self.play_button = Button(self, "Play")
        self.entering_name = True
        self.player_name = ""
        self.name_font = pygame.font.SysFont(None, 48)
        self.prompt_font = pygame.font.SysFont(None, 64)

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            elif event.type == pygame.KEYDOWN:
                if self.entering_name:
                    self._check_name_keydown(event)
                else:
                    self._check_keydown_events(event)
            elif event.type == pygame.KEYUP and not self.entering_name:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.entering_name:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_name_keydown(self, event):
        """Collect the player's name before the game starts."""
        if event.key == pygame.K_RETURN:
            name = self.player_name.strip()
            if name:
                self.stats.player_name = name
                self.entering_name = False
                self.sb.prep_player()
                self._start_game()
        elif event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif event.key == pygame.K_ESCAPE:
            self._quit_game()
        elif event.unicode and event.unicode.isprintable() and len(self.player_name) < 16:
            self.player_name += event.unicode

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            self._quit_game()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p and not self.stats.game_active:
            self._start_game()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self._start_game()

    def _start_game(self):
        """Reset the game and begin play."""
        self.settings.initialize_dynamic_settings()
        self.stats.reset_stats()
        self.stats.game_active = True
        self.sb.prep_images()

        self.aliens.empty()
        self.bullets.empty()
        self._create_fleet()
        self.ship.center_ship()

        pygame.mouse.set_visible(False)

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if self.stats.game_active and len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update bullet positions and get rid of old bullets."""
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()

        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        self._check_aliens_bottom()

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if not self.stats.game_active:
            return

        self.stats.ships_left -= 1
        self.sb.prep_ships()

        if self.stats.ships_left > 0:
            self.aliens.empty()
            self.bullets.empty()
            self._create_fleet()
            self.ship.center_ship()
            sleep(0.5)
        else:
            self._end_game()

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.screen.get_rect().bottom:
                self._ship_hit()
                break

    def _create_fleet(self):
        """Create the fleet of aliens."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        current_x = alien_width
        current_y = alien_height + 120

        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _save_current_score(self):
        """Store the current name and score once per finished game."""
        if self.stats.score_saved or not self.stats.player_name:
            return
        self.stats.records = save_score(self.stats.player_name, self.stats.score)
        self.stats.score_saved = True
        self.sb.prep_high_score()
        self.sb.prep_leaderboard()

    def _end_game(self):
        """Stop play and record the result."""
        self._save_current_score()
        self.stats.game_active = False
        self.aliens.empty()
        self.bullets.empty()
        pygame.mouse.set_visible(True)

    def _quit_game(self):
        """Save an in-progress score, then exit."""
        if self.stats.game_active:
            self._save_current_score()
        sys.exit()

    def _draw_name_prompt(self):
        """Draw the name-entry screen."""
        title = self.prompt_font.render("Alien Invasion", True, (30, 30, 30), self.settings.bg_color)
        title_rect = title.get_rect()
        title_rect.centerx = self.screen.get_rect().centerx
        title_rect.top = 180
        self.screen.blit(title, title_rect)

        prompt = self.name_font.render(
            "Enter your name, then press Enter", True, (30, 30, 30), self.settings.bg_color
        )
        prompt_rect = prompt.get_rect()
        prompt_rect.centerx = self.screen.get_rect().centerx
        prompt_rect.top = title_rect.bottom + 40
        self.screen.blit(prompt, prompt_rect)

        shown = self.player_name if self.player_name else "_"
        name_image = self.prompt_font.render(shown, True, (0, 80, 0), self.settings.bg_color)
        name_rect = name_image.get_rect()
        name_rect.centerx = self.screen.get_rect().centerx
        name_rect.top = prompt_rect.bottom + 30
        self.screen.blit(name_image, name_rect)

        self.sb.show_leaderboard()

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)

        if self.entering_name:
            self._draw_name_prompt()
        else:
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            self.ship.blitme()
            self.aliens.draw(self.screen)
            self.sb.show_score()

            if not self.stats.game_active:
                self.play_button.draw_button()
                self.sb.show_leaderboard()

        pygame.display.flip()


if __name__ == "__main__":
    # Make a game instance and run the game.
    ai = AlienInvasion()
    ai.run_game()
