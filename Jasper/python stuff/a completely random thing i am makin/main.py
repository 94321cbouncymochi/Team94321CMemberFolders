import os
import pygame

pygame.mixer.init()

def open_image(file):
    os.startfile(file)

main_folder = os.path.dirname(os.path.abspath(__file__))
open_image("assets\images\everwinter_without_mercy.jpg")