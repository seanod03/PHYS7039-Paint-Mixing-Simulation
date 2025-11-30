import pygame
import sys
import random
import time

# Pygame setup 
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Factory Machine Simulator")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 24)
# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PRODUCT_COLORS = [(200, 50, 50), (50, 200, 50), (50, 50, 200), (200, 200, 50)]

# Paint mixing state -

# Base colours as pure RGB
BASE_COLORS = {
    "red":    (255, 0, 0),
    "green":  (0, 255, 0),
    "blue":   (0, 0, 255),
    "yellow": (255, 255, 0),
}
# Quality Check Settings 
BROWN_REF = (150, 75, 0)      # reference brown colour
BROWN_THRESHOLD = 80          # distance threshold (tweak as needed)
qc_result = None              # will store "PASS" or "FAIL"

# Logging
LOG_FILENAME = "PaintSim_log.txt"

# Slider values 
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

# Paint mixing state 

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

COLOR_ORDER = ["red", "green", "blue", "yellow"]
current_slider_index = 0  # start with red selected
SLIDER_STEP = 0.1

# Selection / confirmation state
production_paused = False      # when True, no new squares are generated
selected_color = None          # stores the colour at the moment of selection

# Order of sliders for keyboard control
COLOR_ORDER = ["red", "green", "blue", "yellow"]
current_slider_index = 0  # start by controlling "red"

# How much to change the slider per key press
SLIDER_STEP = 0.1  # This can be changed, 0.2, 0.05, etc.


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
        return (150, 150, 150) #Neutral Grey

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

def handle_slider_key(event):
    """
    Use arrow keys to control sliders:
      LEFT / RIGHT: change which colour is selected
      UP / DOWN: increase / decrease selected slider value
      SPACE: toggle selected slider on/off
    """
    global current_slider_index, production_paused, selected_color, qc_result

    if event.type != pygame.KEYDOWN:
        return

    # Change selected colour with LEFT / RIGHT
    if event.key == pygame.K_RIGHT:
        current_slider_index = (current_slider_index + 1) % len(COLOR_ORDER)
    elif event.key == pygame.K_LEFT:
        current_slider_index = (current_slider_index - 1) % len(COLOR_ORDER)

    current_name = COLOR_ORDER[current_slider_index]

    # Increase / decrease slider value with UP / DOWN
    if event.key == pygame.K_UP:
        slider_values[current_name] = slider_values[current_name] + SLIDER_STEP
        if slider_values[current_name] > 1.0:
            slider_values[current_name] = 1.0
        # auto-enable when you adjust it
        slider_enabled[current_name] = True

    if event.key == pygame.K_DOWN:
        slider_values[current_name] = slider_values[current_name] - SLIDER_STEP
        if slider_values[current_name] < 0.0:
            slider_values[current_name] = 0.0

    # SPACE toggles on/off for that slider
    if event.key == pygame.K_SPACE:
        slider_enabled[current_name] = not slider_enabled[current_name]
    
    # ENTER: toggle selection / confirmation state
    if event.key == pygame.K_RETURN:
        production_paused = not production_paused
        if production_paused:
            #Lock in colour
            selected_color = mix_color()

            #Run quality check
            passed = quality_check(selected_color)
            global qc_result
            qc_result = "PASS" if passed else "FAIL"

            #Log selection event
            log_selection_event(selected_color, passed)

            print("Selected:", selected_color, "QC:", qc_result)
        
        else:
            selected_color = None
            qc_result = None
            print("Selection Cleared (Production resumed)")
        
     
    # 'C' key: clear the log file
    if event.key == pygame.K_c:
        clear_log_file()



    
def color_distance(c1, c2):
    """
    Euclidean distance between two RGB colours.
    """
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    return ((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2) ** 0.5

def quality_check(color):
    """
    Returns True if colour is NOT brown-like (PASS),
    False if colour is too close to brown (FAIL).
    """
    dist = color_distance(color, BROWN_REF)
    return dist >= BROWN_THRESHOLD


def log_production_event(mixed_color):
    """
    Log a product being produced while the machine is running.
    Records time, RGB colour, and slider states.
    """
    timestamp = time.ctime()
    line = "PRODUCTION\t" + timestamp
    line = line + f"\tRGB={mixed_color}"

    # Add slider info
    for name in COLOR_ORDER:
        value = slider_values[name]
        enabled = slider_enabled[name]
        line = line + f"\t{name}={value:.2f} ({'ON' if enabled else 'OFF'})"

    # Write to file
    logfile = open(LOG_FILENAME, "a")
    logfile.write(line + "\n")
    logfile.close()


def log_selection_event(selected_color, passed):
    """
    Log a user-confirmed selection (when ENTER is pressed and QC is run).
    """
    timestamp = time.ctime()
    line = "SELECTION\t" + timestamp
    line = line + f"\tRGB={selected_color}\tQC={'PASS' if passed else 'FAIL'}"

    # Add slider info at the moment of selection
    for name in COLOR_ORDER:
        value = slider_values[name]
        enabled = slider_enabled[name]
        line = line + f"\t{name}={value:.2f} ({'ON' if enabled else 'OFF'})"

    logfile = open(LOG_FILENAME, "a")
    logfile.write(line + "\n")
    logfile.close()


def clear_log_file():
    """
    Clear the log file contents (user interaction).
    Called when the user presses 'C'.
    """
    timestamp = time.ctime()
    logfile = open(LOG_FILENAME, "w")
    logfile.write("LOG CLEARED at " + timestamp + "\n")
    logfile.close()
    print("Log file cleared.")

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

# Mark the start of a new run in the log file
run_time = time.ctime()
logfile = open("LOG_FILENAME.txt", "a")
logfile.write("\n=== NEW RUN at " + run_time + " ===\n")
logfile.close()


# Main loop 
running = True
while running:
    dt = clock.tick(60)  # keep loop running ~60 fps

    # Get all events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # handle slider controls
        handle_slider_key(event)

    # Produce a new product every few seconds 

    current_time = pygame.time.get_ticks()
    if (not production_paused) and (current_time - last_production_time > PRODUCTION_INTERVAL):
        # get the current mixed colour from sliders
        mixed_rgb = mix_color()

        new_product = Product(100, random.randint(50, HEIGHT-50), mixed_rgb)
        products.append(new_product)
        last_production_time = current_time

        # Log this production event
        log_production_event(mixed_rgb)


        # later: log to file here
        print(f"Produced product at {time.ctime(new_product.timestamp)}")


    # --- Drawing ---
        # --- Drawing ---
    screen.fill(WHITE)

    # Machine representation
    pygame.draw.rect(screen, BLACK, (50, HEIGHT // 2 - 50, 60, 100), 2)

    # Preview of current mixed colour (top-right corner)
    preview_color = mix_color()
    preview_rect = pygame.Rect(WIDTH - 120, 20, 100, 50)
    pygame.draw.rect(screen, preview_color, preview_rect)      # filled with mix colour
    pygame.draw.rect(screen, BLACK, preview_rect, 2)           # black outline
    
    # Reference colour circle + label
    ref_x = preview_rect.x + preview_rect.width // 2
    ref_y = preview_rect.y + preview_rect.height + 40
    ref_radius = 20
    pygame.draw.circle(screen, BROWN_REF, (ref_x, ref_y), ref_radius)
    pygame.draw.circle(screen, BLACK, (ref_x, ref_y), ref_radius, 2)
    label_surface = font.render("Reference Colour", True, BLACK)
    label_rect = label_surface.get_rect(center=(ref_x, ref_y + 35))
    screen.blit(label_surface, label_rect)


    # QC result beside preview box
    if production_paused and qc_result is not None:
        qc_color = (0, 180, 0) if qc_result == "PASS" else (200, 0, 0)
        qc_surface = font.render(f"{qc_result}", True, qc_color)

        qc_x = preview_rect.x - 100
        qc_y = preview_rect.y + 15
        screen.blit(qc_surface, (qc_x, qc_y))


    # Show slider information (horizontally along the bottom)
    font = pygame.font.SysFont(None, 24)

    base_y = HEIGHT - 40  # vertical position for slider labels

    for i, name in enumerate(COLOR_ORDER):
        value = slider_values[name]
        enabled = slider_enabled[name]

        # X position for this slider "slot"
        base_x = 40 + i * 130  # spreads 4 sliders across the width

        # Small colour swatch for this base colour
        swatch_rect = pygame.Rect(base_x, base_y - 30, 80, 20)
        pygame.draw.rect(screen, BASE_COLORS[name], swatch_rect)
        pygame.draw.rect(screen, BLACK, swatch_rect, 1)

        # Mark selected slider with ">"
        prefix = "> " if i == current_slider_index else "  "
        label = f"{prefix}{name[:1].upper()}: {value:.2f} ({'ON' if enabled else 'OFF'})"

        text_surface = font.render(label, True, BLACK)
        screen.blit(text_surface, (base_x, base_y))

    # Status + QC text above the sliders, left side
    status_text = "Selection: LOCKED (no new squares)" if production_paused else "Selection: LIVE"
    status_surface = font.render(status_text, True, BLACK)
    screen.blit(status_surface, (20, base_y - 60))

    # Show whether production is live or paused
    status_text = "Selection: LOCKED (no new squares)" if production_paused else "Selection: LIVE"
    status_surface = font.render(status_text, True, BLACK)
    
    # Draw products
    for p in products:
        p.draw(screen)

    pygame.display.flip()


pygame.quit()
sys.exit()
 