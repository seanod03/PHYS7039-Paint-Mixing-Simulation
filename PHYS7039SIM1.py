import pygame
import sys
import random
import time

# --- Pygame setup ---
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Factory Machine Simulator")
clock = pygame.time.Clock()

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PRODUCT_COLORS = [(200, 50, 50), (50, 200, 50), (50, 50, 200), (200, 200, 50)]

# --- Paint mixing state (we will hook this in later) ---

# Base colours as pure RGB
BASE_COLORS = {
    "red":    (255, 0, 0),
    "green":  (0, 255, 0),
    "blue":   (0, 0, 255),
    "yellow": (255, 255, 0),
}

# Slider values (how much of each colour).
# For now, these are just placeholders; we will change them with keys later.
slider_values = {
    "red": 0.0,
    "green": 0.0,
    "blue": 0.0,
    "yellow": 0.0,
}

# On/off state for each slider
slider_enabled = {
    "red": False,
    "green": False,
    "blue": False,
    "yellow": False,
}

# --- Paint mixing state (we will hook this in later) ---

BASE_COLORS = {
    "red":    (255, 0, 0),
    "green":  (0, 255, 0),
    "blue":   (0, 0, 255),
    "yellow": (255, 255, 0),
}

slider_values = {
    "red": 0.0,
    "green": 0.0,
    "blue": 0.0,
    "yellow": 0.0,
}

slider_enabled = {
    "red": False,
    "green": False,
    "blue": False,
    "yellow": False,
}

def mix_color():
    """
    Combine the enabled sliders into one RGB colour.

    Each slider_value is treated as a 'strength' or 'amount' of that base colour.
    Only sliders that are enabled contribute to the mix.
    """
    # 1. Work out total "amount" of enabled colours
    total = 0.0
    for name, value in slider_values.items():
        if slider_enabled[name]:
            total = total + value

    # 2. If nothing is enabled or everything is zero, return a neutral grey
    if total == 0:
        return (150, 150, 150)

    # 3. Weighted average of base colours
    r_sum = 0.0
    g_sum = 0.0
    b_sum = 0.0

    for name, value in slider_values.items():
        if slider_enabled[name]:
            base_r, base_g, base_b = BASE_COLORS[name]
            weight = value / total  # normalised weight
            r_sum = r_sum + base_r * weight
            g_sum = g_sum + base_g * weight
            b_sum = b_sum + base_b * weight

    # 4. Convert back to integers 0–255
    return (int(r_sum), int(g_sum), int(b_sum))


# --- Product class ---
class Product:
    def __init__(self, x, y, color):
        # colour is now passed in instead of chosen randomly
        self.color = color
        self.rect = pygame.Rect(x, y, 40, 20)
        self.timestamp = time.time()  # record production time

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)



# --- Machine state ---
products = []
last_production_time = 0
PRODUCTION_INTERVAL = 2000  # milliseconds


# --- Main loop ---
running = True
while running:
    dt = clock.tick(60)  # keep loop running ~60 fps

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Produce a new product every few seconds ---
        # --- Produce a new product every few seconds ---
    current_time = pygame.time.get_ticks()
    if current_time - last_production_time > PRODUCTION_INTERVAL:
        # get the current mixed colour from sliders
        mixed_rgb = mix_color()

        new_product = Product(100, random.randint(50, HEIGHT-50), mixed_rgb)
        products.append(new_product)
        last_production_time = current_time

        # later: log to file here
        print(f"Produced product at {time.ctime(new_product.timestamp)}")


    # --- Drawing ---
    screen.fill(WHITE)

    # Machine representation
    pygame.draw.rect(screen, BLACK, (50, HEIGHT//2 - 50, 60, 100), 2)
    
    # Draw products
    for p in products:
        p.draw(screen)

    pygame.display.flip()


pygame.quit()
sys.exit()
 