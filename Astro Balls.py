import pygame
import pygame_menu

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running_ = True

while running_:
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            running_ = False
