# braitenberg-vehicle-7
A Python &amp; Pygame simulation of Braitenberg Vehicle 7, exploring Pavlovian (classical) conditioning and Hebbian learning in a synthetic agent.

# Braitenberg Vehicle 7 – Associative Learning in Pygame

A simple 2D simulation of Valentino Braitenberg's Vehicle 7 built with Python and Pygame. 

The goal of this project is to model classical (Pavlovian) conditioning and Hebbian plasticity in a minimal synthetic agent.

## What is Vehicle 7?

In Braitenberg's book, Vehicles: Experiments in Synthetic Psychology, earlier vehicles operate on fixed wiring. Vehicle 7 introduces learning through association:

- Innate Reflex (Unconditioned Stimulus / UCS): The vehicle naturally halts whenever it hits a screen boundary.
- Neutral Input (Neutral Stimulus / NS): Coloured lights (red and blue dots) mean nothing to the vehicle initially.
- Hebbian Association: If the vehicle repeatedly crashes into a wall while facing a specific colour, the connection weight between that colour and the stop reflex gets stronger ("neurons that fire together, wire together").
- Extinction / Decay: Without reinforcement, learned fear weights gradually fade over time so the vehicle does not stay permanently terrified of harmless sources.

## How the Simulation Works

- Sensors: Two directional feelers measuring the distance and intensity of nearby red and blue dots.
- Memory (`self.assoc`): A dictionary mapping each colour to a fear value between `0.0` and `1.0`.
- Steering: Threat is calculated as `signal * fear`. If the right sensor detects a higher threat than the left, the vehicle steers away and slows down.

## Controls

- Left Click: Place a new light source (alternates red and blue).
- Right Click: Remove the nearest light source.
- HUD: Displays current speed, turning angle, sensor readings, and real-time fear levels.

## Requirements & Setup

```bash
pip install pygame
python vehicle_7.py
