#!/usr/bin/env python3
"""
Bounce Duel - Een 1v1 Pong-achtig spel met Pygame.
Twee spelers besturen paddles om een bal heen en weer te slaan.
De bal versnelt naarmate een ronde vordert.
"""

import pygame
import math
import random
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple, List
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'assets')


@dataclass
class GameConfig:
    """Spelconfiguratie - alle aanpasbare instellingen."""
    WINDOW_WIDTH: int = 1000
    WINDOW_HEIGHT: int = 600
    FPS: int = 60

    PADDLE_WIDTH: int = 10
    PADDLE_HEIGHT: int = 80
    PADDLE_SPEED: int = 400

    BALL_SIZE: int = 8
    INITIAL_BALL_SPEED: int = 300
    MAX_BALL_SPEED: int = 600
    SPEED_INCREMENT: int = 15

    INITIAL_HP: int = 5

    COLORS = {
        'BACKGROUND': (26, 26, 46),
        'PLAYER1': (0, 212, 255),
        'PLAYER2': (255, 0, 110),
        'BALL': (255, 255, 0),
        'TEXT': (255, 255, 255),
        'SUCCESS': (0, 255, 0),
        'SECONDARY': (170, 170, 170),
    }


class GameState(Enum):
    """De mogelijke toestanden van het spel."""
    PLAYING = 1
    GAME_OVER = 2


class AssetLoader:
    """Laadt en beheert afbeeldingen uit de assets map."""

    def __init__(self):
        self.images = {}

    def load_image(self, filename: str, scale: Optional[Tuple[int, int]] = None) -> pygame.Surface:
        """Laad een afbeelding en schaal deze optioneel."""
        path = os.path.join(ASSETS_PATH, filename)

        if not os.path.exists(path):
            logger.warning(f"Bestand niet gevonden: {path}")
            surface = pygame.Surface(scale if scale else (1, 1))
            surface.fill((255, 0, 255))
            return surface

        if filename not in self.images:
            img = pygame.image.load(path).convert_alpha()
            if scale:
                img = pygame.transform.scale(img, scale)
            self.images[filename] = img
        return self.images[filename].copy()


class BackgroundElement:
    """Een bewegend element in de achtergrond (planeet, asteroïde)."""

    def __init__(self, image: pygame.Surface, x: float, y: float, speed_x: float, speed_y: float):
        self.image = image
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.rect = image.get_rect(topleft=(x, y))

    def update(self, dt: float, window_width: int, window_height: int) -> None:
        """Beweeg het element en zorg dat het om het scherm heen loopt."""
        self.x += self.speed_x * dt
        self.y += self.speed_y * dt

        if self.x + self.rect.width < 0:
            self.x = window_width
        if self.x > window_width:
            self.x = -self.rect.width

        if self.y + self.rect.height < 0:
            self.y = window_height
        if self.y > window_height:
            self.y = -self.rect.height

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surface: pygame.Surface) -> None:
        """Teken het element op het scherm."""
        surface.blit(self.image, self.rect)


class Paddle:
    """De paddle (muur) die een speler bestuurt."""

    def __init__(self, x: float, y: float, width: int, height: int,
                 color: Tuple[int, int, int], config: GameConfig) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.velocity_y = 0
        self.speed = config.PADDLE_SPEED
        self.config = config

    def update(self, dt: float, keys: pygame.key.ScalarKeyType,
               key_up: int, key_down: int) -> None:
        """Werk de paddle bij op basis van toetsen."""
        self.velocity_y = 0

        if keys[key_up]:
            self.velocity_y = -self.speed
        elif keys[key_down]:
            self.velocity_y = self.speed

        self.rect.y += self.velocity_y * dt

        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.config.WINDOW_HEIGHT:
            self.rect.bottom = self.config.WINDOW_HEIGHT

    def draw(self, surface: pygame.Surface) -> None:
        """Teken de paddle."""
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        pygame.draw.rect(surface, self.color, self.rect, width=2, border_radius=5)


class Ball:
    """De bal die heen en weer wordt geslagen."""

    def __init__(self, x: float, y: float, config: GameConfig) -> None:
        self.rect = pygame.Rect(x - config.BALL_SIZE // 2, y - config.BALL_SIZE // 2,
                               config.BALL_SIZE, config.BALL_SIZE)
        self.color = config.COLORS['BALL']
        self.velocity_x = 0
        self.velocity_y = 0
        self.round_start_time = 0
        self.config = config

    def set_velocity_from_angle(self, angle: float, speed: float, direction_x: float = 1) -> None:
        """Stel snelheid in op basis van hoek en snelheid."""
        rad = math.radians(angle)
        self.velocity_x = math.cos(rad) * speed * direction_x
        self.velocity_y = math.sin(rad) * speed

    def update(self, dt: float) -> None:
        """Beweeg de bal en verwerk bounces."""
        self.rect.x += self.velocity_x * dt
        self.rect.y += self.velocity_y * dt

        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity_y = abs(self.velocity_y)
        if self.rect.bottom >= self.config.WINDOW_HEIGHT:
            self.rect.bottom = self.config.WINDOW_HEIGHT
            self.velocity_y = -abs(self.velocity_y)

    def draw(self, surface: pygame.Surface) -> None:
        """Teken de bal met gloeëffect."""
        radius = self.config.BALL_SIZE // 2

        for i in range(4, 0, -1):
            glow_radius = radius + (5 - i) * 2
            glow_color = tuple(int(c * (0.3 - i * 0.05)) for c in self.color)
            pygame.draw.circle(surface, glow_color, self.rect.center, glow_radius)

        pygame.draw.circle(surface, self.color, self.rect.center, radius)

    def is_out_of_bounds(self) -> Optional[str]:
        """Controleer of de bal uit het speelveld is."""
        if self.rect.left < 0:
            return "left"
        if self.rect.right > 1000:
            return "right"
        return None


class HealthBar:
    """De HP bar van een speler - toont hartjes."""

    def __init__(self, x: float, y: float, max_hp: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.color = color

    def set_hp(self, hp: int) -> None:
        """Stel huige HP in."""
        self.current_hp = max(0, min(hp, self.max_hp))

    def draw(self, surface: pygame.Surface) -> None:
        """Teken hartjes voor elke HP."""
        heart_size = 30
        spacing = 35

        for i in range(self.max_hp):
            x_pos = self.x + i * spacing

            points = [
                (x_pos + heart_size // 2, self.y + heart_size),
                (x_pos, self.y + heart_size // 2),
                (x_pos + heart_size // 4, self.y),
                (x_pos + heart_size // 2, self.y + heart_size // 4),
                (x_pos + heart_size - heart_size // 4, self.y),
                (x_pos + heart_size, self.y + heart_size // 2),
            ]

            if i < self.current_hp:
                pygame.draw.polygon(surface, self.color, points)
            else:
                pygame.draw.polygon(surface, (80, 80, 80), points, 2)


class BounceDuelGame:
    """Het hoofd spel."""

    def __init__(self, config: Optional[GameConfig] = None) -> None:
        self.config = config or GameConfig()
        self.asset_loader = AssetLoader()

        pygame.init()
        logger.info("Pygame geïnitialiseerd")

        self.screen = pygame.display.set_mode((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        pygame.display.set_caption("BOUNCE DUEL")
        self.clock = pygame.time.Clock()

        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 16)

        self._initialize_background()
        self._initialize_game_objects()
        logger.info("Spel geïnitialiseerd")

    def _initialize_background(self) -> None:
        """Laad achtergrond en bewegende elementen."""
        self.background_img = self.asset_loader.load_image('blue-back.png',
                                                           scale=(self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        self.logo = self.asset_loader.load_image('logo.png', scale=(450, 450))

        self.background_elements: List[BackgroundElement] = []

        planet_big = self.asset_loader.load_image('prop-planet-big.png', scale=(80, 80))
        planet_small = self.asset_loader.load_image('prop-planet-small.png', scale=(50, 50))
        asteroid1 = self.asset_loader.load_image('asteroid-1.png', scale=(40, 40))
        asteroid2 = self.asset_loader.load_image('asteroid-2.png', scale=(35, 35))

        for _ in range(3):
            x = random.randint(0, self.config.WINDOW_WIDTH)
            y = random.randint(-100, self.config.WINDOW_HEIGHT)
            speed_x = random.uniform(-30, 30)
            speed_y = random.uniform(20, 80)
            self.background_elements.append(BackgroundElement(planet_big, x, y, speed_x, speed_y))

        for _ in range(5):
            x = random.randint(0, self.config.WINDOW_WIDTH)
            y = random.randint(-100, self.config.WINDOW_HEIGHT)
            speed_x = random.uniform(-50, 50)
            speed_y = random.uniform(30, 100)
            self.background_elements.append(BackgroundElement(asteroid1, x, y, speed_x, speed_y))

        for _ in range(4):
            x = random.randint(0, self.config.WINDOW_WIDTH)
            y = random.randint(-100, self.config.WINDOW_HEIGHT)
            speed_x = random.uniform(-40, 40)
            speed_y = random.uniform(25, 90)
            self.background_elements.append(BackgroundElement(planet_small, x, y, speed_x, speed_y))

    def _initialize_game_objects(self) -> None:
        """Maak paddles, bal en HP bars."""
        self.paddle1 = Paddle(20, self.config.WINDOW_HEIGHT // 2 - self.config.PADDLE_HEIGHT // 2,
                             self.config.PADDLE_WIDTH, self.config.PADDLE_HEIGHT,
                             self.config.COLORS['PLAYER1'], self.config)

        self.paddle2 = Paddle(self.config.WINDOW_WIDTH - 20 - self.config.PADDLE_WIDTH,
                             self.config.WINDOW_HEIGHT // 2 - self.config.PADDLE_HEIGHT // 2,
                             self.config.PADDLE_WIDTH, self.config.PADDLE_HEIGHT,
                             self.config.COLORS['PLAYER2'], self.config)

        self.ball = Ball(self.config.WINDOW_WIDTH // 2, self.config.WINDOW_HEIGHT // 2, self.config)

        self.health_bar1 = HealthBar(50, 20, self.config.INITIAL_HP, self.config.COLORS['PLAYER1'])
        self.health_bar2 = HealthBar(self.config.WINDOW_WIDTH - 200, 20, self.config.INITIAL_HP, self.config.COLORS['PLAYER2'])

        self.player1_hp = self.config.INITIAL_HP
        self.player2_hp = self.config.INITIAL_HP
        self.state = GameState.PLAYING
        self.ball_round_start_time = 0
        self.winner_text = ""

        self.reset_ball()

    def reset_ball(self) -> None:
        """Reset de bal naar het midden."""
        self.ball.rect.center = (self.config.WINDOW_WIDTH // 2, self.config.WINDOW_HEIGHT // 2)

        angle = random.choice([-30, 30])
        direction = random.choice([1, -1])

        self.ball.set_velocity_from_angle(angle, self.config.INITIAL_BALL_SPEED, direction)
        self.ball_round_start_time = pygame.time.get_ticks()

    def get_ball_current_speed(self) -> float:
        """Bereken huidge balsnelheid (versnelt naarmate ronde vordert)."""
        elapsed_ms = pygame.time.get_ticks() - self.ball_round_start_time
        elapsed_s = elapsed_ms / 1000.0

        speed = self.config.INITIAL_BALL_SPEED + elapsed_s * self.config.SPEED_INCREMENT
        speed = max(self.config.INITIAL_BALL_SPEED, min(speed, self.config.MAX_BALL_SPEED))
        return speed

    def handle_paddle_collision(self, paddle: Paddle) -> None:
        """Verwerk collision en bereken bounce hoek."""
        relative_intersect_y = (paddle.rect.centery - self.ball.rect.centery) / (self.config.PADDLE_HEIGHT / 2)
        relative_intersect_y = max(-1, min(1, relative_intersect_y))

        bounce_angle = relative_intersect_y * 75
        direction = 1 if paddle == self.paddle1 else -1

        current_speed = self.get_ball_current_speed()
        self.ball.set_velocity_from_angle(bounce_angle, current_speed, direction)

    def check_collisions(self) -> None:
        """Controleer collisions met paddles."""
        if self.ball.rect.colliderect(self.paddle1.rect):
            self.ball.rect.left = self.paddle1.rect.right
            self.handle_paddle_collision(self.paddle1)

        if self.ball.rect.colliderect(self.paddle2.rect):
            self.ball.rect.right = self.paddle2.rect.left
            self.handle_paddle_collision(self.paddle2)

    def update(self, dt: float, keys: pygame.key.ScalarKeyType) -> None:
        """Update spellogica."""
        if self.state != GameState.PLAYING:
            return

        for element in self.background_elements:
            element.update(dt, self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)

        self.paddle1.update(dt, keys, pygame.K_w, pygame.K_s)
        self.paddle2.update(dt, keys, pygame.K_UP, pygame.K_DOWN)
        self.ball.update(dt)
        self.check_collisions()

        out_of_bounds = self.ball.is_out_of_bounds()
        if out_of_bounds == "left":
            self.player1_hp -= 1
            self.health_bar1.set_hp(self.player1_hp)
            logger.info(f"Speler 1 mist! HP: {self.player1_hp}")
            if self.player1_hp <= 0:
                self.end_game("SPELER 2 WINT!")
            else:
                self.reset_ball()
        elif out_of_bounds == "right":
            self.player2_hp -= 1
            self.health_bar2.set_hp(self.player2_hp)
            logger.info(f"Speler 2 mist! HP: {self.player2_hp}")
            if self.player2_hp <= 0:
                self.end_game("SPELER 1 WINT!")
            else:
                self.reset_ball()

    def end_game(self, winner_text: str) -> None:
        """Beëindig het spel."""
        self.state = GameState.GAME_OVER
        self.winner_text = winner_text
        logger.info(f"Spel beëindigd: {winner_text}")

    def draw(self) -> None:
        """Teken het scherm."""
        if self.state == GameState.PLAYING:
            self._draw_playing_state()
        else:
            self.screen.fill(self.config.COLORS['BACKGROUND'])
            self._draw_game_over_state()

        pygame.display.flip()

    def _draw_playing_state(self) -> None:
        """Teken het spel."""
        self.screen.blit(self.background_img, (0, 0))

        for element in self.background_elements:
            element.draw(self.screen)

        self.paddle1.draw(self.screen)
        self.paddle2.draw(self.screen)
        self.ball.draw(self.screen)

        self.health_bar1.draw(self.screen)
        self.health_bar2.draw(self.screen)

        current_speed = self.get_ball_current_speed()
        speed_text = self.font_small.render(f"Speed: {current_speed:.0f}", True, self.config.COLORS['SECONDARY'])
        self.screen.blit(speed_text, (self.config.WINDOW_WIDTH // 2 - 40, 70))

    def _draw_game_over_state(self) -> None:
        """Teken het winnaar-scherm."""
        logo_rect = self.logo.get_rect(center=(self.config.WINDOW_WIDTH // 2, 200))
        self.screen.blit(self.logo, logo_rect)

        winner_render = self.font_large.render(self.winner_text, True, self.config.COLORS['SUCCESS'])
        winner_rect = winner_render.get_rect(center=(self.config.WINDOW_WIDTH // 2, self.config.WINDOW_HEIGHT // 2))
        self.screen.blit(winner_render, winner_rect)

        restart_text = self.font_medium.render("Druk R om opnieuw te starten", True, self.config.COLORS['SECONDARY'])
        restart_rect = restart_text.get_rect(center=(self.config.WINDOW_WIDTH // 2, self.config.WINDOW_HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)

    def restart(self) -> None:
        """Start het spel opnieuw."""
        logger.info("Spel herstart")
        self._initialize_game_objects()

    def run(self) -> None:
        """Hoofd game loop."""
        logger.info("Game loop gestart")
        running = True

        try:
            while running:
                dt = self.clock.tick(self.config.FPS) / 1000.0

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        logger.info("Spel afgesloten door gebruiker")
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.restart()

                keys = pygame.key.get_pressed()
                self.update(dt, keys)
                self.draw()

        except Exception as e:
            logger.error(f"Fout in game loop: {e}", exc_info=True)

        finally:
            pygame.quit()
            logger.info("Pygame afgesloten")


if __name__ == "__main__":
    try:
        game = BounceDuelGame()
        game.run()
    except Exception as e:
        logger.error(f"Kritieke fout: {e}", exc_info=True)
        raise
