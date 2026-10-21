import pygame
import random
import math


# ==============================================================
# BRAITENBERG VEHICLE 7 — ASSOCIATIVE (PAVLOVIAN) LEARNING
#
# The book's idea: the vehicle is born already reacting to one thing (hitting a wall).
# Everything else it senses (color) starts out meaning nothing to it.
# But if a neutral thing (color) keeps happening at the same time as the built-in reaction (wall hit),
# the vehicle slowly wires the two together.
# Eventually the neutral thing alone can trigger the reaction.
#

#   - "unconditioned stimulus" = the built-in trigger (wall hit)
#   - "conditioned stimulus"   = the neutral thing that becomes
#                                 meaningful through learning (color)
#   - "association" / "fear"  = the learned connection strength
#                                 between a color and the reaction
# ==============================================================

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle 7 — learns to fear a color")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

BLACK = (15, 15, 20)
WHITE = (255, 255, 255)
VEHICLE_COLOR = (100, 200, 255)
SENSOR_COLOR = (0, 255, 0)
RED = (220, 20, 40)     # one of the two "conditioned stimulus" colors
BLUE = (30, 144, 255)   # the other one


# --- TUNING KNOBS ---

SENSOR_SPREAD = math.pi / 5   # how wide apart the two sensors point (angle, radians)
SENSE_RANGE = 180             # How far the vehicle can see
LEARN_RATE = 0.02             #  How fast it learns (per frame while paused)
                               # (bigger = learns to be afraid faster)
DECAY_RATE = 0.0015           # How fast it forgets (per frame)
                               # (bigger = forgets faster)
TURN_GAIN = 0.15              # How aggressively it turns away from threats
                               # (bigger = more dramatic avoidance)
PAUSE_TIME = 0.4              # How long it's stunned after hitting a wall
                               # (this frozen window is also the only time learning happens)


class Source:
    """A colored dot on the screen. Its color is the 'conditioned stimulus' —
    meaningless to the vehicle until it gets paired with a wall hit."""
    def __init__(self, x, y, color):
        self.x, self.y, self.color = x, y, color
        self.radius = 18


class Vehicle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.angle = random.uniform(0, 2 * math.pi)
        self.radius = 30

        # THE LEARNED MEMORY.
        # This dictionary is the vehicle's associative memory = vehicle's brain.
        # 0.0 = "no fear learned yet" up to 1.0 = "maximum fear". It starts empty
        # Everything else in this file exists to update or use these two numbers.
        self.assoc = {RED: 0.0, BLUE: 0.0}

        self.paused_until = 0.0   # Time when it can move again, vehicle is frozen & learning
        self.frame = 0

        # These are just for printing to the screen (the HUD -heads up display) they don't affect behavior.
        self.speed = 0.0
        self.rotation = 0.0
        self.threat_L = 0.0
        self.threat_R = 0.0
        self.sense_L = {RED: 0.0, BLUE: 0.0}
        self.sense_R = {RED: 0.0, BLUE: 0.0}

    def sensor_positions(self):
        """Where the left and right 'feelers' currently are, based on heading."""
        lx = self.x + 40 * math.cos(self.angle - SENSOR_SPREAD)
        ly = self.y + 40 * math.sin(self.angle - SENSOR_SPREAD)
        rx = self.x + 40 * math.cos(self.angle + SENSOR_SPREAD)
        ry = self.y + 40 * math.sin(self.angle + SENSOR_SPREAD)
        return (lx, ly), (rx, ry)

    def sense_color(self, sources, sx, sy):
        """What color(s) does a sensor at (sx, sy) currently detect, and how strongly?
        Returns a number 0.0-1.0 per color: 0 = nothing felt, 1 = right on top of it.
        This is all perception — no learning happens here, just measuring the world."""

        #Think of each sensor as an eye. The closer a colored light is, the stronger the signal.
        # The vehicle can detect red and blue separately.
        signal = {RED: 0.0, BLUE: 0.0}
        for s in sources:
            d = math.hypot(s.x - sx, s.y - sy)
            strength = max(0.0, 1.0 - d / SENSE_RANGE)   # closer = stronger, 0 past SENSE_RANGE
            signal[s.color] = max(signal[s.color], strength)   # take the strongest source of that color
        return signal

    def update(self, sources, now):
        self.frame += 1

        # ----------------------------------------------------------------
        # STATE 1: FROZEN /
        # LEARNING
        # This block only runs for PAUSE_TIME seconds right after a wall hit.
        # This is the only place in the whole program where self.assoc changes upward.

        # When the vehicle hits a wall, it pauses for 0.4 seconds.
        # During this pause, it looks at whatever color it's seeing and increases that color's association weight.
        # This is the associative learning

        # ----------------------------------------------------------------
        if now < self.paused_until:
            (lx, ly), (rx, ry) = self.sensor_positions()
            self.sense_L = self.sense_color(sources, lx, ly)
            self.sense_R = self.sense_color(sources, rx, ry)
            for color in (RED, BLUE):
                sig = max(self.sense_L[color], self.sense_R[color])
                if sig > 0.1:  # only counts as visible above a small noise threshold
                    # THE LEARNING RULE: nudge this color's fear up, capped at 1.0.
                    # If the vehicle wasn't seeing this color when it crashed,
                    # this line never runs for that color -> no false associations.

                    # This is Pavlov's bell. If the vehicle is frozen (just hit a wall)
                    # and it sees a color clearly, it adds a little bit of 'fear' to that specific color.
                    self.assoc[color] = min(1.0, self.assoc[color] + LEARN_RATE)

            self.speed = 0.0
            self.rotation = 0.0
            return  # frozen -> skip all movement code below

        # ----------------------------------------------------------------
        # STATE 2: NORMAL MOVEMENT
        # ----------------------------------------------------------------

        # FORGETTING: every normal frame, every association fades a little.
        # This is extinction in learning theory — memories weaken without reinforcement.
        # Associations slowly decay over time. If the vehicle never sees a color while hitting a wall, it gradually forgets that fear.
        # This prevents it from being permanently scared of things that are no longer dangerous.
        # adaptive behavior
        for color in (RED, BLUE):
            self.assoc[color] = max(0.0, self.assoc[color] - DECAY_RATE)

        # PERCEPTION: what do the two feelers currently see?
        (lx, ly), (rx, ry) = self.sensor_positions()
        left = self.sense_color(sources, lx, ly)
        right = self.sense_color(sources, rx, ry)

        # BEHAVIOR = PERCEPTION x MEMORY.
        # This is the payoff of learning: "threat" isn't just raw color signal,
        # it's raw signal multiplied by how much fear has been learned for that color.
        # If assoc[RED] is still 0 (never learned), red contributes nothing here,
        # no matter how strongly it's sensed -> vehicle drives right through it.
        threat_L = self.assoc[RED] * left[RED] + self.assoc[BLUE] * left[BLUE]
        threat_R = self.assoc[RED] * right[RED] + self.assoc[BLUE] * right[BLUE]

        # STEERING: turn AWAY from whichever side has more threat.
        # If threat_R > threat_L, this comes out NEGATIVE -> turns left, away from the right.
        # avoidance behavior
        turn = (threat_L - threat_R) * TURN_GAIN
        wander = random.uniform(-0.03, 0.03)  # small random jitter so it doesn't move in a dead straight line
        self.angle += turn + wander

        # Slow down when something threatening is nearby, like flinching.
        speed = 2.5 * (1.0 - 0.5 * max(threat_L, threat_R))
        self.x += speed * math.cos(self.angle)
        self.y += speed * math.sin(self.angle)

        # stash values purely so the on-screen HUD can display them
        self.sense_L, self.sense_R = left, right
        self.threat_L, self.threat_R = threat_L, threat_R
        self.speed = speed
        self.rotation = turn

        # ----------------------------------------------------------------
        # THE UNCONDITIONED STIMULUS: hitting a wall.
        # This check is independent of any learning. the vehicle always
        # reacts to walls, from frame 1, before it has learned anything.
        # That's what makes it "unconditioned": built-in, not learned.
        # ----------------------------------------------------------------
        hit_wall = (self.x < self.radius or self.x > WIDTH - self.radius or
                    self.y < self.radius or self.y > HEIGHT - self.radius)
        if hit_wall:
            # clamp position so it doesn't get stuck outside the screen
            self.x = max(self.radius, min(WIDTH - self.radius, self.x))
            self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
            self.paused_until = now + PAUSE_TIME   # enter state 1 next frame
            # aim roughly back toward the center so the bounce doesn't re-hit immediately
            self.angle = math.atan2(HEIGHT / 2 - self.y, WIDTH / 2 - self.x) + random.uniform(-0.4, 0.4)

    def draw(self, surface):
        pygame.draw.circle(surface, VEHICLE_COLOR, (int(self.x), int(self.y)), self.radius)
        for (sx, sy) in self.sensor_positions():
            pygame.draw.circle(surface, SENSOR_COLOR, (int(sx), int(sy)), 6)


def main():
    vehicle = Vehicle(WIDTH // 2, HEIGHT // 2)
    vehicle2 = Vehicle(WIDTH // 3, HEIGHT // 3)

    # Scatter starting sources, alternating red/blue
    sources = []
    for i in range(8):
        color = RED if i % 2 == 0 else BLUE
        sources.append(Source(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), color))

    running = True
    while running:
        now = pygame.time.get_ticks() / 1000.0
        screen.fill(BLACK)

        # --- mouse controls: left-click adds a source, right-click removes the nearest one ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if event.button == 1:
                    color = RED if len(sources) % 2 == 0 else BLUE
                    sources.append(Source(mx, my, color))
                elif event.button == 3 and sources:
                    closest = min(sources, key=lambda s: math.hypot(s.x - mx, s.y - my))
                    sources.remove(closest)

        for s in sources:
            pygame.draw.circle(screen, s.color, (int(s.x), int(s.y)), s.radius)

        vehicle.update(sources, now)
        vehicle2.update(sources, now)
        vehicle.draw(screen)
        vehicle2.draw(screen)

        # --- HUD: live numbers so you can point at exactly what's happening ---
        state = "PAUSED (learning)" if now < vehicle.paused_until else "moving"
        lines = [
            "Left-click: add source (alternates red/blue)   Right-click: remove nearest",
            f"State: {state}",
            f"Speed: {vehicle.speed:.2f}   Rotation: {vehicle.rotation:.3f}",
            f"Threat  L: {vehicle.threat_L:.2f}   R: {vehicle.threat_R:.2f}",
            f"Sense RED   L: {vehicle.sense_L[RED]:.2f}  R: {vehicle.sense_R[RED]:.2f}   "
            f"Fear: {vehicle.assoc[RED]:.2f}",
            f"Sense BLUE  L: {vehicle.sense_L[BLUE]:.2f}  R: {vehicle.sense_R[BLUE]:.2f}   "
            f"Fear: {vehicle.assoc[BLUE]:.2f}",
        ]
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, WHITE), (20, 20 + i * 24))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()