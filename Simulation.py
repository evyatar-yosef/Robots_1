import pygame
import os
import time
import random

from Robots_1.Drone import Drone, Painter

# Screen dimensions
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
MAP_IMAGE_PATH = os.path.join('p14.png')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)  # Define blue color
GREEN = (0, 255, 0)

MAX_FLY_TIME = 2 * 60  # 8 min in sec


class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Drone Simulation")

        self.map_image = pygame.image.load(MAP_IMAGE_PATH)
        self.map_image = pygame.transform.scale(self.map_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.xstart = 80
        self.ystart = 80
        self.drone = Drone(self.xstart, self.ystart, self.map_image, MAX_FLY_TIME,self.screen,self)  # Initialize drone with starting position (80, 80)

        self.painter = Painter()  # Initialize the painter

        self.clock = pygame.time.Clock()
        self.start_time = time.time()
        self.running = True

        # Create a 2D array representing the color of each pixel on the map
        self.pixel_colors = self.create_pixel_color_array()

        # Initialize buttons for vertical movement
        self.up_button_rect = pygame.Rect(50, 50, 100, 50)  # Rect for up button
        self.down_button_rect = pygame.Rect(50, 150, 100, 50)  # Rect for down button

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
                pixel_color = self.map_image.get_at((x, y))[:3]  # Get the RGB values only

                # Convert the pixel color to a single number (0 for white, 1 for black)
                if pixel_color == WHITE:
                    pixel_value = 0
                elif pixel_color == BLACK:
                    pixel_value = 1
                else:
                    pixel_value = 0  # Default to obstacle for any other color

                # Add the pixel value to the current row
                row_colors.append(pixel_value)

            # Add the current row to the list of pixel colors
            pixel_colors.append(row_colors)

        # Add blue obstacles
        num_blue_obstacles = 50
        obstacle_size = 20

        for _ in range(num_blue_obstacles):
            placed = False
            while not placed:
                x = random.randint(0, width - obstacle_size)
                y = random.randint(0, height - obstacle_size)
                if all(pixel_colors[j][i] == 0 for i in range(x, x + obstacle_size) for j in range(y, y + obstacle_size)):
                    for i in range(x, x + obstacle_size):
                        for j in range(y, y + obstacle_size):
                            pixel_colors[j][i] = 2  # Assuming blue is represented by 2
                    pygame.draw.rect(self.map_image, BLUE, (x, y, obstacle_size, obstacle_size))
                    placed = True

        # Return the 2D list of pixel colors
        return pixel_colors

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.drone.z -= 1  # Increase z-axis value
                    elif event.key == pygame.K_DOWN:
                        self.drone.z += 1  # Decrease z-axis value
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if self.up_button_rect.collidepoint(event.pos):
                            self.drone.z -= 1  # Increase z-axis value
                        elif self.down_button_rect.collidepoint(event.pos):
                            self.drone.z += 1  # Decrease z-axis value

            elapsed_time = time.time() - self.start_time

            if elapsed_time < MAX_FLY_TIME / 2:
                # Continue normal operation
                self.drone.move(self.pixel_colors)
                self.painter.paint(self.map_image, self.drone)  # Paint the pixels around the drone
            else:
                # Go home operation
                if not self.drone.return_home:
                    self.drone.go_home(self.pixel_colors, MAX_FLY_TIME)  # Set the flag to start going home
                self.drone.go_home_step()  # Move one step towards home
                self.painter.paint(self.map_image, self.drone)  # Paint the pixels around the drone

                # Check if drone is at the start point to recharge
                if self.drone.x == self.xstart and self.drone.y == self.ystart:
                    self.drone.recharge_battery()
                    if self.drone.battery == 100.0:
                        self.drone.battery == 100.0
                        self.drone.draw(self.screen)
                        self.update_display()
                        pygame.display.flip()
                        time.sleep(1)

                        self.start_time = time.time()
                        self.drone.move(self.pixel_colors)  # Resume exploration after recharge

            self.update_display()
            self.clock.tick(10)  # 10 Hz sensor update rate

        pygame.quit()

    def update_display(self):
        self.screen.fill(WHITE)
        self.screen.blit(self.map_image, (0, 0))

        self.drone.draw(self.screen)

        # Draw buttons

        pygame.display.flip()

