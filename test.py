def move(self, pixel_colors, sensor_range=MAX_DISTANCE_PIXELS):
    possible_moves = [
        ("up", (self.x, self.y - DRONE_SPEED)),
        ("down", (self.x, self.y + DRONE_SPEED)),
        ("right", (self.x + DRONE_SPEED, self.y)),
        ("left", (self.x - DRONE_SPEED, self.y)),
        ("up-right", (self.x + DRONE_SPEED, self.y - DRONE_SPEED)),
        ("up-left", (self.x - DRONE_SPEED, self.y - DRONE_SPEED)),
        ("down-right", (self.x + DRONE_SPEED, self.y + DRONE_SPEED)),
        ("down-left", (self.x - DRONE_SPEED, self.y + DRONE_SPEED)),
    ]

    valid_moves = []
    for direction, (new_x, new_y) in possible_moves:
        obstacle_free = True
        for dx in range(self.drone_image.get_width()):
            for dy in range(self.drone_image.get_height()):
                nx_pixel = new_x + dx
                ny_pixel = new_y + dy
                if 0 <= nx_pixel < SCREEN_WIDTH and 0 <= ny_pixel < SCREEN_HEIGHT:
                    if pixel_colors[ny_pixel][nx_pixel] == 1:  # Check if pixel is an obstacle (black pixel)
                        obstacle_free = False
                        break
            if not obstacle_free:
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
                nx_pixel = int(round(self.center_x + (sensor_range+8) * math.cos(math.radians(direction_angle))))  # Adjusted for x-axis inversion
                ny_pixel = int(round(self.center_y - (sensor_range+8) * math.sin(math.radians(direction_angle))))  # Adjusted for y-axis inversion
                if 0 <= nx_pixel < SCREEN_WIDTH and 0 <= ny_pixel < SCREEN_HEIGHT:
                    if pixel_colors[ny_pixel][nx_pixel] != 1:
                        chosen_move = move
                        break
        if not chosen_move:
            for move in unvisited_moves:
                direction_angle = self.get_direction(move[0])
                nx_pixel = int(round(self.center_x + (sensor_range +8) * math.cos(math.radians(direction_angle))))
                ny_pixel = int(round(self.center_y - (sensor_range +8) * math.sin(math.radians(direction_angle))))  # Adjusted for y-axis inversion
                if 0 <= nx_pixel < SCREEN_WIDTH and 0 <= ny_pixel < SCREEN_HEIGHT:
                    if pixel_colors[ny_pixel][nx_pixel] != 1:
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
            for offset in range(-self.drone_image.get_width() // 2, self.drone_image.get_width() // 2 + 1):
                if self.last_direction in ["up", "down", "up-right", "up-left", "down-right", "down-left"]:
                    nx_pixel = int(round(self.center_x + offset))
                    ny_pixel = int(round(self.center_y + step * (1 if self.last_direction in ["down", "down-right", "down-left"] else -1)))
                else:  # "left" or "right"
                    nx_pixel = int(round(self.center_x + step * (1 if self.last_direction in ["right", "up-right", "down-right"] else -1)))
                    ny_pixel = int(round(self.center_y + offset))

                if 0 <= nx_pixel < SCREEN_WIDTH and 0 <= ny_pixel < SCREEN_HEIGHT:
                    if pixel_colors[ny_pixel][nx_pixel] == 2:
                        # Fly over the blue object by incrementing z until clear
                        while pixel_colors[ny_pixel][nx_pixel] == 2 and self.z < 2:  # Assuming 2 is the maximum height
                            self.z += 1
                            print(f"Flying over blue object at ({nx_pixel}, {ny_pixel}), z = {self.z}")
                            break
                    # Check if flying over blue object is complete, then return to original height
                    if self.z >= 1 and pixel_colors[ny_pixel][nx_pixel] != 2:
                        self.z -= 1
                        print(f"Returning to original height after flying over blue object, z = {self.z}")
                        break

        print(f"Moving {chosen_move[0]} to ({self.x}, {self.y}, {self.z})")
        return True
    else:
        print("No valid move found, drone is stuck.")
        return False





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
