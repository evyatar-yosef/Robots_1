# Robots_1
# Drone Simulation Project

## Overview

This project is a simulation of a drone navigating through a map, avoiding obstacles, and returning to its starting position after a certain period. The simulation is built using Python and Pygame, providing a graphical representation of the drone's movement and painting the map based on its exploration.

## Features

- **Drone Navigation**: The drone moves across a predefined map, avoiding obstacles.
- **Obstacle Detection**: The drone uses a sensor to detect obstacles within a certain range.
- **Map Painting**: The drone paints the map yellow in areas it has explored.
- **Return to Start**: After a set time, the drone returns to its starting position.
- **Real-time Display**: The simulation updates in real-time, showing the drone's position, orientation, and flight time.

## Technologies Used

- **Python**: The primary programming language used for the simulation.
- **Pygame**: A set of Python modules designed for writing video games. Used here to handle graphics and the game loop.

## Installation

1. **Clone the repository**:
    git clone https://github.com/your-username/drone-simulation.git
    ```
2. **Navigate to the project directory**:
    cd drone-simulation
    ```
3. **Install the required dependencies**:
    pip install pygame
    ```

## Usage

1. **Ensure you have the necessary files**:
    - `p14.png`: The map image file.
    - `drone.jpeg`: The image file for the drone.
    - `Simulation.py`: The main simulation script.
    - `Drone.py`: Contains the `Drone` and `Painter` classes.

2. **Run the simulation**:
    ```bash
    python Simulation.py
    ```

## Code Structure

### Simulation.py

The main script that runs the simulation. It initializes the Pygame window, loads the map and drone images, and controls the main game loop.

### Drone.py

Contains the `Drone` and `Painter` classes:

- **Drone**: Handles the drone's movement, obstacle detection, and returning to the start position.
- **Painter**: Responsible for painting the map based on the drone's exploration.

## How It Works

1. **Initialization**: The simulation sets up the Pygame window and loads the map and drone images.
2. **Movement**: The drone moves across the map, avoiding obstacles and painting explored areas.
3. **Returning Home**: After a predefined flight time, the drone returns to its starting position using the recorded move history.
4. **Display Update**: The Pygame window updates in real-time to show the drone's position, orientation, and flight time.

## Future Enhancements

- **Enhanced Obstacle Detection**: Improve the sensor range and accuracy.
- **Dynamic Map Loading**: Allow loading different maps for the drone to navigate.
- **Advanced Navigation Algorithms**: Implement more sophisticated algorithms for pathfinding and obstacle avoidance.

