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

# --- Product class ---
class Product:
    def __init__(self, x, y):
        self.color = random.choice(PRODUCT_COLORS)
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
    current_time = pygame.time.get_ticks()
    if current_time - last_production_time > PRODUCTION_INTERVAL:
        new_product = Product(100, random.randint(50, HEIGHT-50))
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