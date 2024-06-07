import time

import pygame
import os
import math  # Import for trigonometric calculations

DRONE_SPEED = 2   # 10 pixeles per minute = 25 cm
PIXEL_SIZE = 2.5 / 100  # 2.5 cm to meters
MAX_DISTANCE_METERS = 1  # 2 meters
MAX_DISTANCE_PIXELS = int(MAX_DISTANCE_METERS / PIXEL_SIZE)  # Convert meters to pixels

# Screen dimensions
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800

drone_image_path = os.path.join('drone.jpeg')  # Make sure the path is correct

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)  # Color for painting pixels
RED = (255,0,0)

class Drone:
    def __init__(self, x, y, map_image):
        self.x = x
        self.y = y
        self.map_image = map_image
        self.visited = set()  # Set to keep track of visited coordinates
        self.visited.add((self.x, self.y))  # Mark the starting position as visited
        self.drone_image = pygame.image.load(drone_image_path)
        self.drone_image = pygame.transform.scale(self.drone_image, (15, 15))
        self.update_center()  # Update center coordinates upon initialization
        self.last_direction = None  # Variable to store the last direction
        self.start_time = time.time()
        self.move_history = []
        self.return_home = False

    def draw(self, screen):
        # Draw drone on screen...
        screen.blit(self.drone_image, (self.x, self.y))

        # Render orientation text
        font = pygame.font.SysFont(None, 25)
        orientation_text = font.render(f"Orientation: {self.last_direction}", True, RED)
        screen.blit(orientation_text, (50, 280))

        # Calculate and render time of flight
        elapsed_time = round(time.time() - self.start_time, 2)
        time_text = font.render(f"Time of Flight: {elapsed_time} s", True, RED)
        screen.blit(time_text, (50, 300))

        # Render current position
        position_text = font.render(f"Position: ({self.x}, {self.y})", True, RED)
        screen.blit(position_text, (50, 320))

    def update_center(self):
        self.center_x = self.x + self.drone_image.get_width() // 2
        self.center_y = self.y + self.drone_image.get_height() // 2

    def get_direction(self, direction_name):
        directions = {
            "up": 90,
            "down": 270,
            "right": 0,
            "left": 180,
            "up_left": 135,
            "up_right": 45,
            "down_left": 225,
            "down_right": 315
        }
        return directions[direction_name]

    def move(self, pixel_colors, sensor_range=MAX_DISTANCE_PIXELS):
        # Define possible moves and their corresponding coordinates
        possible_moves = [
            ("up", (self.x, self.y - DRONE_SPEED)),
            ("down", (self.x, self.y + DRONE_SPEED)),
            ("right", (self.x + DRONE_SPEED, self.y)),
            ("left", (self.x - DRONE_SPEED, self.y)),
        ]

        # Filter out moves that are out of bounds or into obstacles within sensor range
        valid_moves = []
        for direction, (new_x, new_y) in possible_moves:
            obstacle_free = True
            direction_angle = self.get_direction(direction)
            for step in range(1, sensor_range + 1):  # Check pixels along the move direction
                nx_pixel = int(round(self.center_x + step * math.cos(math.radians(direction_angle))))
                ny_pixel = int(round(self.center_y - step * math.sin(math.radians(direction_angle))))  # Adjusted for y-axis inversion
                if 0 <= nx_pixel < SCREEN_WIDTH and 0 <= ny_pixel < SCREEN_HEIGHT:
                    if pixel_colors[ny_pixel][nx_pixel] == 1:
                        obstacle_free = False
                        break  # Stop checking if an obstacle is found

            if obstacle_free:
                valid_moves.append((direction, (new_x, new_y)))

        # Separate valid moves into unvisited and visited
        unvisited_moves = []
        visited_moves = []

        for move in valid_moves:
            if move[1] not in self.visited:
                unvisited_moves.append(move)
            else:
                visited_moves.append(move)

        # Choose a move, prioritizing the last direction if possible

        chosen_move = None
        if self.last_direction :
            for move in unvisited_moves:
                if move[0] == self.last_direction:
                    direction_angle = self.get_direction(move[0])
                    nx_pixel = int(round(self.center_x + (sensor_range + 8) * math.cos(math.radians(direction_angle))))
                    ny_pixel = int(round(self.center_y - (sensor_range + 8) * math.sin(math.radians(direction_angle))))  # Adjusted for y-axis inversion
                    if 0 <= nx_pixel < SCREEN_WIDTH and 0 <= ny_pixel < SCREEN_HEIGHT:
                        if pixel_colors[ny_pixel][nx_pixel] == 0:
                            print("1111111111111111")

                            chosen_move = move
                            break
            if not chosen_move:
                for move in unvisited_moves:
                    direction_angle = self.get_direction(move[0])
                    nx_pixel = int(round(self.center_x + (sensor_range + 8) * math.cos(math.radians(direction_angle))))
                    ny_pixel = int(round(self.center_y - (sensor_range + 8) * math.sin(math.radians(direction_angle))))  # Adjusted for y-axis inversion
                    if 0 <= nx_pixel < SCREEN_WIDTH and 0 <= ny_pixel < SCREEN_HEIGHT:
                        if pixel_colors[ny_pixel][nx_pixel] == 0:
                            print("2222222222222222")

                            chosen_move = move
                            break


        if not chosen_move:
            print("333333333333")
            for move in unvisited_moves:
                if move[0] == self.last_direction:
                    chosen_move = move
                    break
            if not chosen_move:
                for move in visited_moves:
                    if move[0] == self.last_direction:
                        chosen_move = move
                        break

        if not chosen_move:
            print("4444444444444")
            if unvisited_moves:
                chosen_move = unvisited_moves[0]
            elif visited_moves:
                chosen_move = visited_moves[0]

        # Move the drone to the chosen position and update center coordinates
        if chosen_move:
            self.x, self.y = chosen_move[1]
            self.visited.add((self.x, self.y))
            self.update_center()  # Update center coordinates after moving
            self.last_direction = chosen_move[0]  # Update last direction
            self.move_history.append((self.x,self.y))
            print(f"Moving {chosen_move[0]} to ({self.x}, {self.y})")
            return True
        else:
            print("No valid move found, drone is stuck.")
            return False

    def go_home(self):
        self.return_home = True

    def go_home_step(self):
        if self.return_home and self.move_history:
            # Pop the last move from the history and move the drone to that position
            last_position = self.move_history.pop()
            self.x, self.y = last_position
            self.update_center()
            print(f"Returning to ({self.x}, {self.y})")
            if not self.move_history:
                self.return_home = False  # Stop returning home when the history is empty


class Painter:
    def __init__(self, sensor_range=MAX_DISTANCE_PIXELS):
        self.sensor_range = sensor_range

    def paint(self, map_image, drone):
        for direction_angle in range(0, 360, 1):  # Check in all directions
            for step in range(1, self.sensor_range + 1):
                nx_pixel = int(round(drone.center_x + step * math.cos(math.radians(direction_angle))))
                ny_pixel = int(round(drone.center_y - step * math.sin(math.radians(direction_angle))))  # Adjusted for y-axis inversion
                if 0 <= nx_pixel < SCREEN_WIDTH and 0 <= ny_pixel < SCREEN_HEIGHT:
                    current_color = map_image.get_at((nx_pixel, ny_pixel))
                    if current_color != BLACK:  # Avoid painting black pixels
                        map_image.set_at((nx_pixel, ny_pixel), YELLOW)
