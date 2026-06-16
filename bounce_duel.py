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

        while running:
          # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    