import pygame
from pygame.sprite import Sprite


class Alien(Sprite):
    """A class to represent a single alien in the fleet."""

    _image = None

    def __init__(self, ai_game):
        """Initialize the alien and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        self.image = self._get_image()
        self.rect = self.image.get_rect()

        # Start each new alien near the top left of the screen.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the alien's exact horizontal position.
        self.x = float(self.rect.x)

    @classmethod
    def _get_image(cls):
        """Build a simple alien surface once and reuse it."""
        if cls._image is None:
            image = pygame.Surface((48, 36), pygame.SRCALPHA)
            pygame.draw.ellipse(image, (30, 160, 40), (8, 8, 32, 20))
            pygame.draw.circle(image, (20, 140, 30), (10, 16), 8)
            pygame.draw.circle(image, (20, 140, 30), (38, 16), 8)
            pygame.draw.rect(image, (20, 140, 30), (22, 4, 4, 8))
            pygame.draw.circle(image, (255, 255, 255), (18, 16), 4)
            pygame.draw.circle(image, (255, 255, 255), (30, 16), 4)
            pygame.draw.circle(image, (20, 20, 20), (18, 16), 2)
            pygame.draw.circle(image, (20, 20, 20), (30, 16), 2)
            cls._image = image
        return cls._image

    def check_edges(self):
        """Return True if the alien is at the edge of the screen."""
        screen_rect = self.screen.get_rect()
        return self.rect.right >= screen_rect.right or self.rect.left <= 0

    def update(self):
        """Move the alien right or left."""
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x
