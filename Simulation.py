# simulation.py

import pygame
import os
import time
from Drone import Drone, Painter  # Import the Drone and Painter classes

# Screen dimensions
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
MAP_IMAGE_PATH = os.path.join('p14.png')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

MAX_FLY_TIME = 8 * 60  # 8 min in sec

class Simulation:
    def __init__(self):  # Corrected method name
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Drone Simulation")

        self.map_image = pygame.image.load(MAP_IMAGE_PATH)
        self.map_image = pygame.transform.scale(self.map_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.drone = Drone(80, 80, self.map_image)  # Initialize drone with starting position (80, 80)

        self.painter = Painter()  # Initialize the painter

        self.clock = pygame.time.Clock()
        self.start_time = time.time()
        self.running = True

        # Create a 2D array representing the color of each pixel on the map
        self.pixel_colors = self.create_pixel_color_array()
        print(self.pixel_colors[100][100])

    def create_pixel_color_array(self):
        # Get the dimensions (width and height) of the map image
        width, height = self.map_image.get_size()

        # Initialize an empty list to store the color values of each pixel
        pixel_colors = []

        # Loop over each row (y-coordinate) of the image
        for y in range(height):
            # Initialize an empty list for the current row
            row_colors = []

            # Loop over each column (x-coordinate) of the image
            for x in range(width):
                # Get the color of the pixel at position (x, y)
                pixel_color = self.map_image.get_at((x, y))

                # Convert the pixel color to a single number (0 for white, 1 for black)
                pixel_value = 0 if pixel_color == WHITE else 1

                # Add the pixel value to the current row
                row_colors.append(pixel_value)

            # Add the current row to the list of pixel colors
            pixel_colors.append(row_colors)

        # Return the 2D list of pixel colors
        return pixel_colors

    def run(self):
        while self.running and (time.time() - self.start_time) < MAX_FLY_TIME:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Continue frame sense
            self.drone.move(self.pixel_colors)
            self.painter.paint(self.map_image, self.drone)  # Paint the pixels around the drone
            self.update_display()
            self.clock.tick(10)  # 10 Hz sensor update rate

        pygame.quit()

    def update_display(self):
        self.screen.fill(WHITE)
        self.screen.blit(self.map_image, (0, 0))
        self.drone.draw(self.screen)
        print("Drone pos(", self.drone.x, ",", self.drone.y, ")")

        pygame.display.flip()
