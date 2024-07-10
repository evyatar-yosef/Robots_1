import pygame
import os
import time
import random
from Robots_1.Drone import Drone, Painter
from Robots_1.Drone2 import Drone2

# Screen dimensions
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
MAP_IMAGE_PATH = os.path.join('p14.png')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)  # Define blue color
GREEN = (0, 255, 0)

# Maximum flight time (8 minutes in seconds)
MAX_FLY_TIME = 8 * 60

class Simulation:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Drone Simulation")

        # Load and scale the map image
        self.map_image = pygame.image.load(MAP_IMAGE_PATH)
        self.map_image = pygame.transform.scale(self.map_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Set the starting position for the drone
        self.xstart = 80
        self.ystart = 80
        # Initialize the drone with the starting position, map image, max flight time, screen, and simulation
        self.drone = Drone(self.xstart, self.ystart, self.map_image, MAX_FLY_TIME, self.screen, self)

        # Initialize the painter
        self.painter = Painter()

        # Initialize the clock and start time
        self.clock = pygame.time.Clock()
        self.start_time = time.time()
        self.running = True

        # Create a 2D array representing the color of each pixel on the map
        self.pixel_colors = self.create_pixel_color_array()

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
                # Randomly choose a position for the obstacle
                x = random.randint(0, width - obstacle_size)
                y = random.randint(0, height - obstacle_size)
                # Ensure the chosen area is free of obstacles
                if all(pixel_colors[j][i] == 0 for i in range(x, x + obstacle_size) for j in range(y, y + obstacle_size)):
                    # Place the obstacle by setting the pixel values to 2 (blue)
                    for i in range(x, x + obstacle_size):
                        for j in range(y, y + obstacle_size):
                            pixel_colors[j][i] = 2  # Assuming blue is represented by 2
                    # Draw the obstacle on the map image
                    pygame.draw.rect(self.map_image, BLUE, (x, y, obstacle_size, obstacle_size))
                    placed = True  # Exit the loop once the obstacle is placed

        # Return the 2D list of pixel colors
        return pixel_colors

    def run(self):
        # Main loop
        while self.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False  # Exit the loop if the quit event is detected

            # Calculate elapsed time since the start
            elapsed_time = time.time() - self.start_time

            if elapsed_time < MAX_FLY_TIME / 2:
                # Normal operation: the drone continues moving and painting
                self.drone.move(self.pixel_colors)
                self.painter.paint(self.map_image, self.drone)  # Paint the pixels around the drone
            else:
                # Go home operation: the drone starts returning home
                if not self.drone.return_home:
                    self.drone.go_home(self.pixel_colors, MAX_FLY_TIME)  # Set the flag to start going home
                self.drone.go_home_step(self.pixel_colors)  # Move one step towards home
                self.painter.paint(self.map_image, self.drone)  # Paint the pixels around the drone

                # Check if the drone has reached the start point
                if self.drone.x == self.xstart and self.drone.y == self.ystart:
                    self.drone.recharge_battery()  # Recharge the battery
                    if self.drone.battery == 100.0:
                        self.drone.battery = 100.0  # Ensure the battery level is set to 100%
                        self.drone.draw(self.screen)  # Draw the drone on the screen
                        self.update_display()  # Update the display
                        pygame.display.flip()  # Update the full display surface to the screen
                        time.sleep(1)  # Pause for a moment

                        self.start_time = time.time()  # Reset the start time
                        self.drone.move(self.pixel_colors)  # Resume exploration after recharge

            self.update_display()  # Update the display
            self.clock.tick(15)  # 10 Hz sensor update rate

        pygame.quit()  # Quit pygame when the loop ends

    def update_display(self):
        # Fill the screen with white color
        self.screen.fill(WHITE)
        # Blit the map image onto the screen
        self.screen.blit(self.map_image, (0, 0))
        # Draw the drone on the screen
        self.drone.draw(self.screen)
        # Update the full display surface to the screen
        pygame.display.flip()
