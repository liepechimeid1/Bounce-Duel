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
      self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("BOUNCE DUEL")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 16)

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

self.paddle1 = Paddle(20, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, CYAN)
 self.paddle2 = Paddle(WINDOW_WIDTH - 20 - PADDLE_WIDTH, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, MAGENTA)

         self.paddle1.update(dt, keys, pygame.K_w, pygame.K_s)
        self.paddle2.update(dt, keys, pygame.K_UP, pygame.K_DOWN)

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

              if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT

       if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity_y = abs(self.velocity_y)
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.velocity_y = -abs(self.velocity_y)
            
        while running:
          # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    