#!/usr/bin/env python3
import pygame
import math
import random
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
FPS = 60

# Game constants
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 80
BALL_SIZE = 8
PADDLE_SPEED = 400
INITIAL_BALL_SPEED = 300
MAX_BALL_SPEED = 600
SPEED_INCREMENT = 15  # pixels/sec per second

# Colors
BLACK = (26, 26, 46)
CYAN = (0, 212, 255)
MAGENTA = (255, 0, 110)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2

class Paddle:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.velocity_y = 0
        self.speed = PADDLE_SPEED

    def update(self, dt, keys, key_up, key_down):
        # Handle input
        self.velocity_y = 0
        if keys[key_up]:
            self.velocity_y = -self.speed
        elif keys[key_down]:
            self.velocity_y = self.speed

        # Move paddle
        self.rect.y += self.velocity_y * dt

        # Keep in bounds
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class Ball:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - BALL_SIZE // 2, y - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        self.color = YELLOW
        self.velocity_x = 0
        self.velocity_y = 0
        self.round_start_time = 0

    def set_velocity_from_angle(self, angle, speed, direction_x=1):
        """Set velocity based on angle and speed"""
        rad = math.radians(angle)
        self.velocity_x = math.cos(rad) * speed * direction_x
        self.velocity_y = math.sin(rad) * speed

    def update(self, dt):
        # Move ball
        self.rect.x += self.velocity_x * dt
        self.rect.y += self.velocity_y * dt

        # Bounce off top and bottom
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity_y = abs(self.velocity_y)
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.velocity_y = -abs(self.velocity_y)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.rect.center, BALL_SIZE // 2)

    def is_out_of_bounds(self):
        """Check if ball is out of bounds (left or right)"""
        if self.rect.left < 0:
            return "left"
        if self.rect.right > WINDOW_WIDTH:
            return "right"
        return None

class BounceDuelGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("BOUNCE DUEL")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 16)

        # Initialize game objects
        self.paddle1 = Paddle(20, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, CYAN)
        self.paddle2 = Paddle(WINDOW_WIDTH - 20 - PADDLE_WIDTH, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, MAGENTA)
        self.ball = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        # Game state
        self.player1_hp = 5
        self.player2_hp = 5
        self.state = GameState.PLAYING
        self.ball_round_start_time = 0

        self.reset_ball()

    def reset_ball(self):
        """Reset ball to center with random angle"""
        self.ball.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        # Random angle between -30 and 30 degrees
        angle = random.choice([-30, 30])
        direction = random.choice([1, -1])

        self.ball.set_velocity_from_angle(angle, INITIAL_BALL_SPEED, direction)
        self.ball_round_start_time = pygame.time.get_ticks()

    def get_ball_current_speed(self):
        """Calculate current ball speed based on round elapsed time"""
        elapsed_ms = pygame.time.get_ticks() - self.ball_round_start_time
        elapsed_s = elapsed_ms / 1000.0

        speed = INITIAL_BALL_SPEED + elapsed_s * SPEED_INCREMENT
        speed = max(INITIAL_BALL_SPEED, min(speed, MAX_BALL_SPEED))
        return speed

    def handle_paddle_collision(self, paddle):
        """Handle ball collision with paddle and calculate bounce"""
        # Calculate relative intersection point on paddle (-1 to 1)
        relative_intersect_y = (paddle.rect.centery - self.ball.rect.centery) / (PADDLE_HEIGHT / 2)
        relative_intersect_y = max(-1, min(1, relative_intersect_y))

        # Calculate bounce angle (max 75 degrees)
        bounce_angle = relative_intersect_y * 75

        # Determine direction
        if paddle == self.paddle1:
            direction = 1
        else:
            direction = -1

        # Get accelerated speed and set new velocity
        current_speed = self.get_ball_current_speed()
        self.ball.set_velocity_from_angle(bounce_angle, current_speed, direction)

    def check_collisions(self):
        """Check ball collisions with paddles"""
        if self.ball.rect.colliderect(self.paddle1.rect):
            self.ball.rect.left = self.paddle1.rect.right  # Prevent ball sticking
            self.handle_paddle_collision(self.paddle1)

        if self.ball.rect.colliderect(self.paddle2.rect):
            self.ball.rect.right = self.paddle2.rect.left  # Prevent ball sticking
            self.handle_paddle_collision(self.paddle2)

    def update(self, dt, keys):
        """Update game state"""
        if self.state != GameState.PLAYING:
            return

        # Update paddles
        self.paddle1.update(dt, keys, pygame.K_w, pygame.K_s)
        self.paddle2.update(dt, keys, pygame.K_UP, pygame.K_DOWN)

        # Update ball
        self.ball.update(dt)

        # Check collisions
        self.check_collisions()

        # Check if ball is out of bounds
        out_of_bounds = self.ball.is_out_of_bounds()
        if out_of_bounds == "left":
            self.player2_hp -= 1
            if self.player2_hp <= 0:
                self.end_game("PLAYER 1 WINT!")
            else:
                self.reset_ball()
        elif out_of_bounds == "right":
            self.player1_hp -= 1
            if self.player1_hp <= 0:
                self.end_game("PLAYER 2 WINT!")
            else:
                self.reset_ball()

    def end_game(self, winner_text):
        """End the game"""
        self.state = GameState.GAME_OVER
        self.winner_text = winner_text

    def draw(self):
        """Draw all game elements"""
        self.screen.fill(BLACK)

        if self.state == GameState.PLAYING:
            # Draw game objects
            self.paddle1.draw(self.screen)
            self.paddle2.draw(self.screen)
            self.ball.draw(self.screen)

            # Draw UI
            hp_text = self.font_medium.render(f"P1: ❤ {self.player1_hp}     P2: ❤ {self.player2_hp}", True, WHITE)
            self.screen.blit(hp_text, (50, 20))

            current_speed = self.get_ball_current_speed()
            speed_text = self.font_small.render(f"Speed: {current_speed:.0f}", True, (170, 170, 170))
            self.screen.blit(speed_text, (WINDOW_WIDTH - 200, 20))

        else:  # GAME_OVER
            # Draw winner text
            winner_render = self.font_large.render(self.winner_text, True, GREEN)
            winner_rect = winner_render.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(winner_render, winner_rect)

            # Draw restart instruction
            restart_text = self.font_medium.render("Druk R om opnieuw te starten", True, (170, 170, 170))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def restart(self):
        """Restart the game"""
        self.player1_hp = 5
        self.player2_hp = 5
        self.state = GameState.PLAYING
        self.reset_ball()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart()

            # Get pressed keys
            keys = pygame.key.get_pressed()

            # Update
            self.update(dt, keys)

            # Draw
            self.draw()

        pygame.quit()

if __name__ == "__main__":
    game = BounceDuelGame()
    game.run()
