import pygame
import random
import math
import json
import os
import sys
import json
import os
import sys

# Initialize Pygame
pygame.init()

# Screen setup
width = 1000
height = 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Advanced Car Racing Game")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (169, 169, 169)
green = (0, 255, 0)
blue = (0, 0, 255)
pink = (255, 105, 180)
yellow = (255, 255, 0)
orange = (255, 165, 0)
red = (255, 0, 0)
explosion_color = (255, 69, 0)  # Orange-red for explosion

# Users file
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        users = json.load(open(USERS_FILE))
        # Ensure new format
        for name, data in list(users.items()):
            if isinstance(data, int):
                users[name] = {"score": data, "color": blue}
            elif isinstance(data, dict) and "color" not in data:
                data["color"] = blue
        return users
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# Clock and font
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)
large_font = pygame.font.SysFont(None, 60)

# Visual effects
particles = []  # particle list for exhaust/trail effects
lane_offset = 0  # used for moving dashed center line

# Car settings
player_width = 50
player_height = 80
player_speed = 5  # Player's speed

# Enemy car settings
enemy_width = 50
enemy_height = 80
enemy_speed = 7  # Enemy cars move faster than the player
num_enemies = 7  # Number of enemy cars

# Users file
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        users = json.load(open(USERS_FILE))
        # Ensure new format
        for name, data in list(users.items()):
            if isinstance(data, int):
                users[name] = {"score": data, "color": blue}
            elif isinstance(data, dict) and "color" not in data:
                data["color"] = blue
        return users
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# Highest score (per user)
highest_score = 0


def draw_player(x, y, color):
    """Draw the player's car."""
    draw_car(x, y, color, player_width, player_height)


def draw_car(x, y, color, w, h):
    """Draw a generic car body at (x,y) with size w x h."""
    # Shadow
    shadow_surf = pygame.Surface((w + 10, int(h * 0.14)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 120), shadow_surf.get_rect())
    screen.blit(shadow_surf, (x - 5, y + h - int(h * 0.14)))

    # Body
    body_rect = pygame.Rect(int(x), int(y), int(w), int(h))
    pygame.draw.rect(screen, color, body_rect, border_radius=max(4, int(w * 0.12)))

    # Windshield highlight
    wind = pygame.Rect(x + w // 6, y + h // 8, w * 2 // 3, h // 3)
    pygame.draw.rect(screen, (200, 230, 255), wind, border_radius=max(2, int(w * 0.06)))

    # Wheels (scaled)
    wheel_r = max(4, int(min(w, h) * 0.12))
    pygame.draw.circle(screen, (20, 20, 20), (int(x + w * 0.22), int(y + h - wheel_r / 2)), wheel_r)
    pygame.draw.circle(screen, (20, 20, 20), (int(x + w * 0.78), int(y + h - wheel_r / 2)), wheel_r)

    # Roof highlight line
    pygame.draw.line(screen, (255, 255, 255), (x + max(4, w * 0.12), y + max(4, h * 0.08)),
                     (x + w - max(4, w * 0.12), y + max(4, h * 0.08)), 2)


def draw_enemy(x, y):
    """Draw the enemy car."""
    draw_car(x, y, (180, 0, 0), enemy_width, enemy_height)
    # Headlights (positioned relative to enemy size)
    hl_r = max(3, int(min(enemy_width, enemy_height) * 0.08))
    pygame.draw.circle(screen, (255, 255, 200), (int(x + enemy_width * 0.16), int(y + enemy_height * 0.15)), hl_r)
    pygame.draw.circle(screen, (255, 255, 200), (int(x + enemy_width * 0.84), int(y + enemy_height * 0.15)), hl_r)


def show_text(msg, color, x, y, font_size=40):
    """Display text on the screen."""
    text_font = pygame.font.SysFont(None, font_size)
    text = text_font.render(msg, True, color)
    screen.blit(text, [x, y])


def draw_counters(current_score=0):
    """Draw the score counters on screen (top left and top right)."""
    # Show current score on top left
    show_text(f"Score: {current_score}", white, 10, 10)
    
    # Show high score in all users on top left
    all_high = max((u["score"] for u in users.values() if isinstance(u, dict)), default=0)
    user_with_high = max(users, key=lambda u: users[u]["score"] if isinstance(users[u], dict) else users[u]) if users else "None"
    show_text(f"High Score In All Users: {all_high} by {user_with_high}", white, 10, 40)
    
    # Show user's high score on top right
    show_text(f"Your High Score: {highest_score}", white, width - 300, 10)


def reset_enemies():
    """Generate multiple enemies with random positions and directions."""
    enemies = []
    for _ in range(num_enemies):
        enemy_x = random.randint(0, width - enemy_width)
        enemy_y = random.randint(-800, -100)  # Start enemies off-screen
        enemy_swerve = random.choice([-2, 2])  # Random left/right movement
        enemies.append({"x": enemy_x, "y": enemy_y, "swerve": enemy_swerve})
    return enemies


def explosion_effect(x, y):
    """Create a quick explosion effect at the given coordinates."""
    for radius in range(20, 120, 20):  # Gradually increase the radius
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*explosion_color, 180 - radius), (radius, radius), radius)
        screen.blit(surf, (x - radius, y - radius))
        pygame.display.update()
        pygame.time.delay(40)


def text_input_screen():
    """Screen to input username."""
    input_text = ""
    cursor_visible = True
    cursor_timer = 0
    cursor_blink_rate = 500  # milliseconds
    while True:
        current_time = pygame.time.get_ticks()
        if current_time - cursor_timer > cursor_blink_rate:
            cursor_visible = not cursor_visible
            cursor_timer = current_time

        screen.fill(gray)
        show_text("Enter Username:", black, width // 4, height // 3, font_size=50)
        show_text(input_text, black, width // 4, height // 2, font_size=40)
        
        # Draw blinking cursor
        if cursor_visible:
            text_width = font.size(input_text)[0]
            cursor_x = width // 4 + text_width
            cursor_y = height // 2
            pygame.draw.line(screen, black, (cursor_x, cursor_y), (cursor_x, cursor_y + 40), 2)
        
        show_text("Type and click Enter or press Enter key", black, width // 4, height // 2 + 60, font_size=20)

        # Back button
        pygame.draw.rect(screen, red, [width // 4, height // 2 + 100, 100, 50])
        show_text("Back", black, width // 4 + 25, height // 2 + 110)

        # Enter button
        pygame.draw.rect(screen, green, [width // 4 + 120, height // 2 + 100, 100, 50])
        show_text("Enter", black, width // 4 + 145, height // 2 + 110)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if width // 4 <= mouse_x <= width // 4 + 100 and height // 2 + 100 <= mouse_y <= height // 2 + 150:
                    return ""  # Cancel
                elif width // 4 + 120 <= mouse_x <= width // 4 + 220 and height // 2 + 100 <= mouse_y <= height // 2 + 150:
                    if input_text.strip():
                        return input_text.strip()
            if event.type == pygame.KEYDOWN:
                cursor_visible = True  # Reset cursor visibility when typing
                cursor_timer = current_time
                if event.key == pygame.K_RETURN and input_text.strip():
                    return input_text.strip()
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isalnum() or event.unicode == ' ':
                    input_text += event.unicode


def edit_user_screen(user, users):
    """Screen to edit user name and color."""
    current_name = user
    current_color = users[user].get("color", blue)
    new_name = current_name
    new_color = current_color

    # Colors: (color, font_color, name)
    color_options = [
        (red, white, "Red"),
        (orange, black, "Orange"),
        (yellow, black, "Yellow"),
        (green, white, "Green"),
        (blue, white, "Blue"),
        ((128, 0, 128), white, "Purple"),  # Purple
        (pink, black, "Pink"),
        ((150, 75, 0), white, "Brown"),  # Brown
        ((255, 215, 0), white, "Golden"),  # Golden
        ((192, 192, 192), black, "Silver"),  # Silver
        (black, white, "Black"),
        (white, black, "White"),
        
    ]

    while True:
        screen.fill(gray)
        show_text(f"Editing {current_name}", black, width // 4, height // 4, font_size=50)

        # Name change button
        pygame.draw.rect(screen, green, [width // 4, height // 3, 200, 50])
        show_text("Change Name", black, width // 4 + 20, height // 3 + 10)

        # Color selection
        show_text("Select Color:", black, width // 4, height // 2, font_size=40)
        for i, (col, font_col, name) in enumerate(color_options):
            row = i // 4
            col_idx = i % 4
            x = width // 4 + col_idx * 120
            y_pos = height // 2 + 50 + row * 60
            pygame.draw.rect(screen, col, [x, y_pos, 100, 50])
            if col == new_color:
                pygame.draw.rect(screen, (255, 255, 255), [x, y_pos, 100, 50], 3)  # White border for selection
            show_text(name, font_col, x + 10, y_pos + 10)

        # Save button
        pygame.draw.rect(screen, green, [width // 2, height // 2 + 260, 200, 50])
        show_text("Save", black, width // 2 + 70, height // 2 + 270)

        # Back button
        pygame.draw.rect(screen, red, [width // 2 - 120, height // 2 + 260, 100, 50])
        show_text("Back", black, width // 2 - 100, height // 2 + 270)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return current_name, current_color
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Change name
                if width // 4 <= mouse_x <= width // 4 + 200 and height // 3 <= mouse_y <= height // 3 + 50:
                    new_name = text_input_screen()
                    if not new_name.strip():
                        new_name = current_name
                    current_name = new_name  # Update the title
                # Color selection
                for i, (col, font_col, name) in enumerate(color_options):
                    row = i // 4
                    col_idx = i % 4
                    x = width // 4 + col_idx * 120
                    y_pos = height // 2 + 50 + row * 60
                    if x <= mouse_x <= x + 100 and y_pos <= mouse_y <= y_pos + 50:
                        new_color = col
                # Save
                if width // 2 <= mouse_x <= width // 2 + 200 and height // 2 + 260 <= mouse_y <= height // 2 + 310:
                    return new_name, new_color
                # Back
                if width // 2 - 120 <= mouse_x <= width // 2 - 20 and height // 2 + 260 <= mouse_y <= height // 2 + 310:
                    return current_name, current_color  # Cancel, return original


def countdown():
    """Display a countdown (3, 2, 1, GO!) before the game starts."""
    # Countdown from 3 to 1
    for number in range(3, 0, -1):
        screen.fill(gray)
        show_text("Get Ready!", black, width // 2 - 120, height // 2 - 120, font_size=50)
        show_text(str(number), black, width // 2 - 30, height // 2 - 40, font_size=120)
        pygame.display.update()
        pygame.time.delay(1000)  # Wait for 1 second
    
    # Show "GO!" message
    screen.fill(gray)
    show_text("GO!", black, width // 2 - 60, height // 2 - 40, font_size=120)
    pygame.display.update()
    pygame.time.delay(500)  # Brief pause on GO!


def user_selection_screen(users):
    """Display user selection screen."""
    while True:
        screen.fill(gray)
        show_text("Select User", black, width // 3, height // 4, font_size=60)

        button_y = height // 3
        user_buttons = []
        for user in users:
            # User button
            user_color = users[user].get("color", blue) if isinstance(users[user], dict) else blue
            user_rgb = tuple(user_color) if isinstance(user_color, list) else user_color
            # Determine font color based on background color
            if user_rgb in [orange, yellow, pink, green, (192, 192, 192), white]:
                font_color = black
            else:
                font_color = white
            user_rect = pygame.Rect(width // 3, button_y, 250, 50)
            pygame.draw.rect(screen, user_rgb, user_rect)
            show_text(user, font_color, width // 3 + 10, button_y + 10)
            user_buttons.append((user_rect, user))

            # Edit button
            edit_rect = pygame.Rect(width // 3 + 260, button_y, 80, 50)
            pygame.draw.rect(screen, (150, 150, 150), edit_rect)
            show_text("Edit", black, width // 3 + 270, button_y + 10)
            user_buttons.append((edit_rect, f"edit_{user}"))

            button_y += 60

        # Add User button
        add_rect = pygame.Rect(width // 3, button_y, 300, 50)
        pygame.draw.rect(screen, green, add_rect)
        show_text("Add User", black, width // 3 + 80, button_y + 10)

        # Draw counters (top left and top right)
        draw_counters()

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for rect, action in user_buttons:
                    if rect.collidepoint((mouse_x, mouse_y)):
                        if action.startswith("edit_"):
                            user = action[5:]
                            new_name, new_color = edit_user_screen(user, users)
                            if new_name != user:
                                users[new_name] = users[user]
                                del users[user]
                            if isinstance(users[new_name], dict):
                                users[new_name]["color"] = new_color
                            else:
                                users[new_name] = {"score": users[new_name], "color": new_color}
                            save_users(users)
                        else:
                            return action
                if add_rect.collidepoint((mouse_x, mouse_y)):
                    new_user = text_input_screen()
                    if new_user and new_user not in users:
                        users[new_user] = {"score": 0, "color": blue}
                        save_users(users)
                        # Go to edit screen for the new user
                        edited_name, edited_color = edit_user_screen(new_user, users)
                        if edited_name != new_user:
                            users[edited_name] = users[new_user]
                            del users[new_user]
                        users[edited_name]["color"] = edited_color
                        save_users(users)


def start_game_screen():
    """Display the Start Game screen with a Start Game button."""
    while True:
        screen.fill(gray)
        show_text("Dodge The Cars!", black, width // 4, height // 3, font_size=100)

        # Draw Start Game button
        pygame.draw.rect(screen, green, [width // 3, height // 3 + 200, 300, 50])
        show_text("Start Game", black, width // 3 + 80, height // 3 + 210)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Check if Start Game button is clicked
                if width // 3 <= mouse_x <= width // 3 + 300 and height // 3 + 200 <= mouse_y <= height // 3 + 250:
                    return  # Start the game


def car_selection_screen():
    """Display the car selection screen."""
    while True:
        screen.fill(gray)
        show_text("Select Your Car", black, width // 3, height // 4, font_size=60)

        # Back button (top left)
        pygame.draw.rect(screen, red, [20, 20, 100, 40])
        show_text("< Back", black, 30, 25)

        # Display car options as small car previews
        preview_w = player_width
        preview_h = player_height
        x1 = width // 5
        x2 = 2 * width // 5
        x3 = 3 * width // 5
        x4 = 4 * width // 5
        y = height // 2

        draw_car(x1, y, blue, preview_w, preview_h)
        draw_car(x2, y, pink, preview_w, preview_h)
        draw_car(x3, y, yellow, preview_w, preview_h)
        draw_car(x4, y, orange, preview_w, preview_h)

        # Display labels under previews
        show_text("Blue", black, x1, y + preview_h + 10)
        show_text("Pink", black, x2, y + preview_h + 10)
        show_text("Yellow", black, x3, y + preview_h + 10)
        show_text("Orange", black, x4, y + preview_h + 10)

        # Draw counters (top left and top right)
        draw_counters()

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Check back button
                if 20 <= mouse_x <= 120 and 20 <= mouse_y <= 60:
                    return None  # Go back to user selection
                # Check which car is clicked
                if width // 5 <= mouse_x <= width // 5 + player_width and height // 2 <= mouse_y <= height // 2 + player_height:
                    return blue
                elif 2 * width // 5 <= mouse_x <= 2 * width // 5 + player_width and height // 2 <= mouse_y <= height // 2 + player_height:
                    return pink
                elif 3 * width // 5 <= mouse_x <= 3 * width // 5 + player_width and height // 2 <= mouse_y <= height // 2 + player_height:
                    return yellow
                elif 4 * width // 5 <= mouse_x <= 4 * width // 5 + player_width and height // 2 <= mouse_y <= height // 2 + player_height:
                    return orange


def game_over_screen(score):
    """Display the Game Over screen with the score, Play Again, and End Session buttons."""
    global highest_score

    # Update the highest score
    if score > highest_score:
        highest_score = score

    while True:
        screen.fill(gray)
        show_text("Game Over!", black, width // 3, height // 3, font_size=60)
        show_text(f"Your Score: {score}", black, width // 3, height // 3 + 60)
        show_text(f"Highest Score: {highest_score}", black, width // 3, height // 3 + 120)

        # Draw Play Again button
        pygame.draw.rect(screen, green, [width // 3, height // 3 + 200, 300, 50])
        show_text("Play Again", black, width // 3 + 80, height // 3 + 210)

        # Draw End Session button
        pygame.draw.rect(screen, red, [width // 3, height // 3 + 270, 300, 50])
        show_text("End Session", black, width // 3 + 70, height // 3 + 280)

        # Draw counters (top left and top right)
        draw_counters(score)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Check if Play Again button is clicked
                if width // 3 <= mouse_x <= width // 3 + 300 and height // 3 + 200 <= mouse_y <= height // 3 + 250:
                    return 'play_again'  # Restart the game
                # Check if End Session button is clicked
                if width // 3 <= mouse_x <= width // 3 + 300 and height // 3 + 270 <= mouse_y <= height // 3 + 320:
                    return 'end_session'  # Go to end session screen


def end_session_screen():
    """Display the End Session screen with Home Screen and Close Game buttons."""
    while True:
        screen.fill(gray)
        show_text("End Session", black, width // 3, height // 4, font_size=60)

        # Draw Go to Home Screen button
        pygame.draw.rect(screen, green, [width // 3, height // 3 + 100, 300, 50])
        show_text("Home Screen", black, width // 3 + 50, height // 3 + 110)

        # Draw Close Game button
        pygame.draw.rect(screen, red, [width // 3, height // 3 + 170, 300, 50])
        show_text("Close Game", black, width // 3 + 80, height // 3 + 180)

        # Draw counters (top left and top right)
        draw_counters()

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'close'
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Check if Home Screen button is clicked
                if width // 3 <= mouse_x <= width // 3 + 300 and height // 3 + 100 <= mouse_y <= height // 3 + 150:
                    return 'home'
                # Check if Close Game button is clicked
                if width // 3 <= mouse_x <= width // 3 + 300 and height // 3 + 170 <= mouse_y <= height // 3 + 220:
                    return 'close'


def game_loop(player_color):
    """Main game loop."""
    global highest_score
    global particles, lane_offset

    # Initialize player and enemies
    player_x = width // 2 - player_width // 2
    player_y = height - player_height - 10
    enemies = reset_enemies()

    # Show countdown before the round starts
    countdown()

    running = True
    score = 0
    current_enemy_speed = enemy_speed  # Reset enemy speed
    particles = []
    lane_offset = 0

    while running:
        screen.fill(gray)

        # Draw background and road with moving dashed center line
        # Draw sky/side areas
        screen.fill((34, 120, 60))  # green-ish sides
        road_rect = pygame.Rect(width * 0.15, 0, width * 0.7, height)
        pygame.draw.rect(screen, (40, 40, 40), road_rect)

        # Road side stripes
        pygame.draw.rect(screen, (100, 100, 100), (width * 0.15 - 10, 0, 10, height))
        pygame.draw.rect(screen, (100, 100, 100), (width * 0.85, 0, 10, height))

        # Moving dashed center line
        dash_h = 40
        gap = 20
        lane_offset = (lane_offset + 8) % (dash_h + gap)
        cx = width // 2
        for i in range(-1, height // (dash_h + gap) + 2):
            dy = i * (dash_h + gap) + lane_offset - 100
            pygame.draw.rect(screen, (220, 220, 220), (cx - 5, dy, 10, dash_h))

        # Add subtle road texture lines
        for i in range(0, height, 60):
            pygame.draw.line(screen, (50, 50, 50), (width * 0.15 + 5, i), (width * 0.85 - 5, i), 1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Keypresses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < width - player_width:
            player_x += player_speed
        if keys[pygame.K_UP] and player_y > 0:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < height - player_height:
            player_y += player_speed

        # Move enemies
        for enemy in enemies:
            enemy["y"] += current_enemy_speed
            enemy["x"] += enemy["swerve"]

            # Make enemies swerve left and right
            if enemy["x"] <= 0 or enemy["x"] >= width - enemy_width:
                enemy["swerve"] *= -1  # Reverse direction if hitting screen edges

            # Reset enemy position when it goes off-screen
            if enemy["y"] > height:
                enemy["y"] = random.randint(-800, -100)
                enemy["x"] = random.randint(0, width - enemy_width)
                enemy["swerve"] = random.choice([-2, 2])
                score += 1
                current_enemy_speed += 0.1  # Gradually increase speed

            # Collision detection
            if (player_y < enemy["y"] + enemy_height and
                player_y + player_height > enemy["y"] and
                player_x < enemy["x"] + enemy_width and
                player_x + player_width > enemy["x"]):
                explosion_effect(player_x + player_width // 2, player_y + player_height // 2)
                # Update high score immediately
                if score > highest_score:
                    highest_score = score
                    users[current_user]["score"] = highest_score
                decision = game_over_screen(score)
                return decision  # End game loop and propagate decision

            # Draw enemy
            draw_enemy(enemy["x"], enemy["y"])

        # Draw player
        draw_player(player_x, player_y, player_color)

        # Particle exhaust behind player
        if keys[pygame.K_DOWN] or keys[pygame.K_UP] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            # spawn a particle behind the car
            px = player_x + player_width // 2
            py = player_y + player_height
            particles.append({"x": px + random.randint(-6, 6), "y": py, "r": random.randint(4, 8), "life": 30})

        # Update and draw particles
        for p in particles[:]:
            p["y"] += 2
            p["x"] += random.uniform(-0.5, 0.5)
            p["life"] -= 1
            alpha = max(0, min(255, int(255 * (p["life"] / 30))))
            surf = pygame.Surface((p["r"] * 2, p["r"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (200, 200, 200, alpha), (p["r"], p["r"]), p["r"])
            screen.blit(surf, (p["x"] - p["r"], p["y"] - p["r"]))
            if p["life"] <= 0:
                particles.remove(p)

        # Show counters
        draw_counters(score)

        pygame.display.update()
        clock.tick(60)

    return 'quit'


# Start the game
users = load_users()
current_user = None
while True:
    start_game_screen()
    if not current_user:
        current_user = user_selection_screen(users)
        if current_user not in users:
            users[current_user] = {"score": 0, "color": blue}
        highest_score = users[current_user]["score"]

    player_color = car_selection_screen()
    if player_color is None:
        current_user = None  # Go back to user selection
        continue
    # Run rounds until the player chooses to end the session
    while True:
        decision = game_loop(player_color)
        if decision == 'play_again':
            continue  # start a new round with same car
        elif decision == 'end_session':
            choice = end_session_screen()
            if choice == 'close':
                users[current_user]["score"] = highest_score
                save_users(users)
                pygame.quit()
                sys.exit(0)
            elif choice == 'home':
                users[current_user]["score"] = highest_score
                save_users(users)
                current_user = None
                break  # Go back to user selection
        elif decision == 'quit' or decision is None:
            users[current_user]["score"] = highest_score
            save_users(users)
            pygame.quit()
            sys.exit(0)