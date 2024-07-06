from queue import PriorityQueue
import pygame
import os
import math
import time

DRONE_SPEED = 2   # 10 pixels per minute = 25 cm
PIXEL_SIZE = 2.5 / 100  # 2.5 cm to meters
MAX_DISTANCE_METERS = 1  # 2 meters
MAX_DISTANCE_PIXELS = int(MAX_DISTANCE_METERS  / PIXEL_SIZE)  # Convert meters to pixels

# Screen dimensions
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800

drone_image_path = os.path.join('drone.jpeg')  # Make sure the path is correct

# Colors for painting pixels
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


class Drone:

    def __init__(self, x, y, map_image, max_fly_time, screen, simulation):
        self.x = x
        self.y = y
        self.z = 1  # Initialize z value as 1
        self.map_image = map_image
        self.visited = set()  # Set to keep track of visited coordinates
        self.visited.add((self.x, self.y, self.z))  # Mark the starting position as visited
        self.drone_image = pygame.image.load(drone_image_path)
        self.drone_image = pygame.transform.scale(self.drone_image, (15, 15))
        self.update_center()  # Update center coordinates upon initialization
        self.last_direction = None  # Variable to store the last direction
        self.start_time = time.time()
        self.move_history = []
        self.battery = 100.0  # Battery starts at 100%
        self.return_home = False
        self.max_fly_time = max_fly_time
        self.battery_decrease_rate = max_fly_time / 100.0
        self.isrecharged = False
        self.screen = screen
        self.simulation = simulation
        self.goal = None  # Initialize goal for A*

    def draw(self, screen):
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
        position_text = font.render(f"Position: ({self.x}, {self.y}, {self.z})", True, RED)
        screen.blit(position_text, (50, 320))

        # Render battery percentage
        battery_text = font.render(f"Battery: {int(self.battery)}%", True, RED)
        screen.blit(battery_text, (50, 340))

    def update_center(self):
        self.center_x = self.x + self.drone_image.get_width() // 2
        self.center_y = self.y + self.drone_image.get_height() // 2

    def get_direction(self, direction_name):
        directions = {
            "up": 90,
            "down": 270,
            "right": 0,
            "left": 180,
        }
        return directions[direction_name]

    def move(self, pixel_colors, sensor_range=MAX_DISTANCE_PIXELS):
        possible_moves = [
            ("up", (self.x, self.y - DRONE_SPEED)),
            ("down", (self.x, self.y + DRONE_SPEED)),
            ("right", (self.x + DRONE_SPEED, self.y)),
            ("left", (self.x - DRONE_SPEED, self.y)),
        ]

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
                        break

            if obstacle_free:
                valid_moves.append((direction, (new_x, new_y)))

        unvisited_moves = []
        visited_moves = []

        for move in valid_moves:
            if (move[1][0], move[1][1], self.z) not in self.visited:
                unvisited_moves.append(move)
            else:
                visited_moves.append(move)

        chosen_move = None
        if self.last_direction:
            for move in unvisited_moves:
                if move[0] == self.last_direction:
                    direction_angle = self.get_direction(move[0])
                    nx_pixel = int(round(self.center_x + (sensor_range + 8) * math.cos(math.radians(direction_angle))))
                    ny_pixel = int(round(self.center_y - (sensor_range + 8) * math.sin(math.radians(direction_angle))))  # Adjusted for y-axis inversion
                    if 0 <= nx_pixel < SCREEN_WIDTH and 0 <= ny_pixel < SCREEN_HEIGHT:
                        if pixel_colors[ny_pixel][nx_pixel] == 0:
                            chosen_move = move
                            break
            if not chosen_move:
                for move in unvisited_moves:
                    direction_angle = self.get_direction(move[0])
                    nx_pixel = int(round(self.center_x + (sensor_range + 8) * math.cos(math.radians(direction_angle))))
                    ny_pixel = int(round(self.center_y - (sensor_range + 8) * math.sin(math.radians(direction_angle))))  # Adjusted for y-axis inversion
                    if 0 <= nx_pixel < SCREEN_WIDTH and 0 <= ny_pixel < SCREEN_HEIGHT:
                        if pixel_colors[ny_pixel][nx_pixel] == 0:
                            chosen_move = move
                            break

        if not chosen_move:
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
            if unvisited_moves:
                chosen_move = unvisited_moves[0]
            elif visited_moves:
                chosen_move = visited_moves[0]

        if chosen_move:
            self.x, self.y = chosen_move[1]
            self.visited.add((self.x, self.y, self.z))
            self.update_center()
            self.update_battery()
            self.last_direction = chosen_move[0]
            self.move_history.append((self.x, self.y, self.z))

            # Adjust z value only when the drone reaches the new position
            direction_angle = self.get_direction(self.last_direction)
            for step in range(1, DRONE_SPEED + 1):
                nx_pixel = int(round(self.center_x + step * math.cos(math.radians(direction_angle))))
                ny_pixel = int(round(self.center_y - step * math.sin(math.radians(direction_angle))))  # Adjusted for y-axis inversion

                if 0 <= nx_pixel < SCREEN_WIDTH and 0 <= ny_pixel < SCREEN_HEIGHT:
                    # Check pixels directly in front of the drone
                    check_x = nx_pixel
                    check_y = ny_pixel

                    if 0 <= check_x < SCREEN_WIDTH and 0 <= check_y < SCREEN_HEIGHT:
                        if pixel_colors[check_y][check_x] == 2:
                            # Fly over the blue object by incrementing z until clear
                            while pixel_colors[check_y][check_x] == 2 and self.z < 2:  # Assuming 2 is the maximum height
                                self.z += 1
                                print(f"Flying over blue object at ({check_x}, {check_y}), z = {self.z}")
                                break
                        # Check if flying over blue object is complete, then return to original height
                        if self.z >= 1 and pixel_colors[check_y][check_x] != 2:
                            self.z -= 1
                            print(f"Returning to original height after flying over blue object, z = {self.z}")
                            break

            print(f"Moving {chosen_move[0]} to ({self.x}, {self.y}, {self.z})")
            return True
        else:
            print("No valid move found, drone is stuck.")
            return False

    def go_home(self, pixel_colors, total_flight_time):
        self.return_home = True
        self.goal = (80, 80)  # Starting point as the goal
        self.battery_decrease_rate = total_flight_time / 100
        self.dynamic_a_star(pixel_colors)

    def dynamic_a_star(self, pixel_colors, sensor_range=MAX_DISTANCE_PIXELS):
        start = (self.x, self.y)
        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        def heuristic(a, b):
            """Manhattan distance heuristic."""
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        while not frontier.empty():
            current_cost, current = frontier.get()

            if current == self.goal:
                break

            for direction in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                dx, dy = direction
                next_step = (current[0] + dx, current[1] + dy)

                if 0 <= next_step[0] < SCREEN_WIDTH and 0 <= next_step[1] < SCREEN_HEIGHT:
                    # Check if next_step is within the extended sensor range
                    if self.is_within_extended_sensor_range(next_step, sensor_range + 1):
                        if pixel_colors[next_step[1]][next_step[0]] != 1:  # Check if it's not an obstacle
                            new_cost = cost_so_far[current] + 1  # Assuming each step costs 1 for simplicity

                            if next_step not in cost_so_far or new_cost < cost_so_far[next_step]:
                                cost_so_far[next_step] = new_cost
                                priority = new_cost + heuristic(self.goal, next_step)
                                frontier.put((priority, next_step))
                                came_from[next_step] = current

                                # Move to the next_step
                                self.x, self.y = next_step
                                self.update_center()
                                print(f"Moving to ({self.x}, {self.y})")

                                if current == self.goal:
                                    break

        # Reconstruct path from goal to start if needed
        if self.x != self.goal[0] or self.y != self.goal[1]:
            self.path_to_home = self.reconstruct_path(start, came_from)
        else:
            self.path_to_home = []

    def is_within_extended_sensor_range(self, position, sensor_range):
        """Check if a position is within the drone's extended sensor range."""
        center_x, center_y = self.center_x, self.center_y
        nx_pixel = position[0]
        ny_pixel = position[1]

        # Calculate distance from center to the position
        distance = math.sqrt((nx_pixel - center_x) ** 2 + (ny_pixel - center_y) ** 2)

        # Adjusted sensor range
        extended_range = sensor_range + 8  # Adding 8 to the sensor range

        return distance <= extended_range

    def reconstruct_path(self, start, came_from):
        path = []
        current = self.goal
        while current != start:
            path.append(current)
            current = came_from.get(current)
            if current is None:
                print(f"Error: Path reconstruction failed. No parent for {current}.")
                return []
        path.reverse()
        return path

    def go_home_step(self):
        if self.return_home and self.path_to_home:
            next_position = self.path_to_home.pop(0)
            self.x, self.y = next_position
            self.update_center()
            self.update_battery()
            print(f"Returning to ({self.x}, {self.y})")
            if not self.path_to_home:
                self.return_home = False

    def update_battery(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time > self.max_fly_time:
            self.battery = 0
        else:
            remaining_time_ratio = (self.max_fly_time - elapsed_time) / self.max_fly_time
            self.battery = remaining_time_ratio * 100.0

        # Ensure battery doesn't go below 0
        if self.battery < 0:
            self.battery = 0

    def recharge_battery(self):
        self.battery = 100.0
        self.start_time = time.time()
        print("Battery recharged to 100%")


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
                    if current_color != BLACK and current_color != BLUE:  # Avoid painting black and blue pixels
                        map_image.set_at((nx_pixel, ny_pixel), YELLOW)


    # def go_home(self):
    #     self.return_home = True
    #     self.battery_decrease_rate = total_flight_time / 100
    #
    # def go_home_step(self):
    #     if self.return_home and self.move_history:
    #         last_position = self.move_history.pop()
    #         self.x, self.y, self.z = last_position
    #         self.update_center()
    #         self.update_batery()
    #         print(f"Returning to ({self.x}, {self.y}, {self.z})")
    #         if not self.move_history:
    #             self.return_home = False
