"""
Spectacular 2D platformer with 20 levels.

How to run:
1) Ensure you have pygame installed: pip install pygame
2) Run: python3 bestgame.py

No external assets or URLs required; everything is drawn with shapes.
"""

import pygame, sys, random

# ----- Constants -----
WIDTH, HEIGHT = 960, 540
FPS = 60
GRAVITY = 0.7
PLAYER_SPEED = 5
PLAYER_JUMP = 15
TOTAL_LEVELS = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY = (140, 200, 255)
PLATFORM_COLOR = (100, 70, 50)
GEM_COLOR = (255, 215, 0)
SPIKE_COLOR = (200, 20, 20)
HUD_BG = (50, 50, 50)

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont('Arial', 20)
BIG_FONT = pygame.font.SysFont('Arial', 36)

# ----- Button Class -----
class Button:
    def __init__(self, rect, text, color=(80,80,80), text_color=WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=6)
        txt = FONT.render(self.text, True, self.text_color)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
# ----- Player Class -----
class Player:
    WIDTH, HEIGHT = 36, 48

    def __init__(self, x, y, color=(200, 50, 50), speed=PLAYER_SPEED, jump=PLAYER_JUMP):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.vx = 0
        self.vy = 0
        self.color = color
        self.speed = speed
        self.jump_power = jump
        self.on_ground = False
        self.collected = 0

    def apply_gravity(self):
        self.vy += GRAVITY

    def move(self, platforms):
        # Horizontal
        self.rect.x += int(self.vx)
        self.collide(self.vx, 0, platforms)
        # Vertical
        self.rect.y += int(self.vy)
        self.on_ground = False
        self.collide(0, self.vy, platforms)

    def collide(self, vx, vy, platforms):
        for p in platforms:
            if self.rect.colliderect(p):
                if vx > 0: self.rect.right = p.left; self.vx = 0
                if vx < 0: self.rect.left = p.right; self.vx = 0
                if vy > 0: self.rect.bottom = p.top; self.vy = 0; self.on_ground = True
                if vy < 0: self.rect.top = p.bottom; self.vy = 0

    def jump(self):
        if self.on_ground:
            self.vy = -self.jump_power

    def draw(self, surf, offset_x):
        r = self.rect.move(-offset_x, 0)
        pygame.draw.rect(surf, self.color, r, border_radius=6)

# ----- Level Generation -----
def generate_level(level_num, width=3000, height=HEIGHT):
    platforms, gems, spikes = [], [], []

    # Ground
    platforms.append(pygame.Rect(0, height-40, width, 40))
    # Starter platform
    platforms.append(pygame.Rect(50, height-140, 200, 20))

    x = 300
    gap_base = max(200 - level_num*3, 100)
    platform_width_base = max(150 - level_num*2, 100)
    prev_py = height - 140

    while x < width - 300:
        pw = random.randint(platform_width_base, platform_width_base + 80)
        py = random.randint(max(120, prev_py - 80), min(height-120, prev_py + 80))
        platforms.append(pygame.Rect(x, py, pw, 20))

        # Gem on platform
        if random.random() < 0.6:
            gems.append(pygame.Rect(x + pw//2 - 8, py - 18, 16, 16))

        # Spikes
        if random.random() < min(0.18 + level_num*0.01, 0.45):
            sx = x + random.randint(10, max(10, pw-10))
            sy = py - 16
            spikes.append(pygame.Rect(sx, sy, 20, 16))

        prev_py = py
        x += random.randint(gap_base, gap_base + 120)

    # Extra gems
    for _ in range(3 + level_num//3):
        gx = random.randint(200, width-200)
        gy = random.randint(100, height-180)
        gems.append(pygame.Rect(gx-8, gy-8, 16, 16))

    # Ground spikes
    for _ in range(level_num//2):
        sx = random.randint(350, width-200)
        sy = height - 56
        spikes.append(pygame.Rect(sx, sy, 22, 16))

    # Exit
    exit_rect = pygame.Rect(width-120, height-120, 80, 80)

    return {'width': width, 'platforms': platforms, 'gems': gems, 'spikes': spikes, 'exit': exit_rect}

# ----- Draw Level -----
def draw_level(surf, world, offset_x):
    surf.fill(SKY)
    for p in world['platforms']:
        pygame.draw.rect(surf, PLATFORM_COLOR, p.move(-offset_x,0))
    for g in world['gems']:
        pygame.draw.ellipse(surf, GEM_COLOR, g.move(-offset_x,0))
    for s in world['spikes']:
        r = s.move(-offset_x,0)
        ax = r.left + r.width//2
        pygame.draw.polygon(surf, SPIKE_COLOR, [(r.left,r.bottom),(r.right,r.bottom),(ax,r.top)])
    ex = world['exit'].move(-offset_x,0)
    pygame.draw.rect(surf, (80,200,80), ex, border_radius=6)
    txt = FONT.render('EXIT', True, BLACK)
    surf.blit(txt, txt.get_rect(center=ex.center))

# ----- Final Screen -----
def show_final_screen(player):
    done = False
    while not done:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: done = True
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: done = True
        SCREEN.fill((10,10,30))
        t1 = BIG_FONT.render('Congratulations!', True, (255,220,180))
        t2 = FONT.render(f'You finished all levels with {player.collected} gems (last level).', True, WHITE)
        t3 = FONT.render('Press ESC or close window to exit.', True, WHITE)
        SCREEN.blit(t1, t1.get_rect(center=(WIDTH//2, HEIGHT//2-40)))
        SCREEN.blit(t2, t2.get_rect(center=(WIDTH//2, HEIGHT//2+10)))
        SCREEN.blit(t3, t3.get_rect(center=(WIDTH//2, HEIGHT//2+50)))
        pygame.display.flip()
        CLOCK.tick(30)

# ----- Game Loop -----
def run_game():
    # Player selection
    players = [
        {'name':'Red','color':(200,50,50),'speed':5,'jump':15},
        {'name':'Blue','color':(50,100,220),'speed':5,'jump':15},
        {'name':'Green','color':(50,220,110),'speed':5,'jump':15},
    ]
    selected = None
    while selected is None:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button==1:
                mx,my = ev.pos
                for i,p in enumerate(players):
                    bx = 120 + i*260
                    br = pygame.Rect(bx,220,220,200)
                    if br.collidepoint((mx,my)):
                        selected = Player(80, HEIGHT-200, color=p['color'], speed=p['speed'], jump=p['jump'])
        SCREEN.fill(SKY)
        SCREEN.blit(BIG_FONT.render('Choose Your Player', True, BLACK), (WIDTH//2-160,100))
        for i,p in enumerate(players):
            bx = 120 + i*260
            br = pygame.Rect(bx,220,220,200)
            pygame.draw.rect(SCREEN, HUD_BG, br, border_radius=10)
            pygame.draw.rect(SCREEN, p['color'], pygame.Rect(bx+40,260,140,120), border_radius=8)
            SCREEN.blit(FONT.render(p['name'], True, WHITE), (bx+10,230))
        SCREEN.blit(FONT.render('Click a character to select', True, BLACK), (20, HEIGHT-40))
        pygame.display.flip()
        CLOCK.tick(FPS)

    # Main game variables
    level_index = 1
    player = selected
    offset_x = 0
    level_completed = False
    game_over = False
    show_level_popup = False
    game_over_messages = [
        "You're Dead! (¬‿¬)",
        "You're bad at this! (> _ <)",
        "Haha! U fell! (' _ ')",
        "Better luck next time! (heehee!)",
        "Ouch! That must've hurt! (×_×)",
        "Try again! (ºoº)",
        "Don't give up! (^_−)",
        "So close! (•_•)",
        "Keep practicing! (◑_◐)"
    ]
    current_game_over_message = None
    jump_pressed = False
    world = generate_level(level_index)
    total_gems_in_level = len(world['gems'])
    player.collected = 0

    # Buttons
    level_button = Button((12,12,110,36),'Level')
    next_level_btn = Button((WIDTH//2-80, HEIGHT//2+60, 160,44),'Next Level')
    retry_btn = Button((WIDTH//2-80, HEIGHT//2+60, 160,44),'Retry')

    running = True
    while running:
        dt = CLOCK.tick(FPS)/1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: running = False
            if ev.type == pygame.KEYDOWN:
                if ev.key==pygame.K_r and level_completed:
                    world = generate_level(level_index)
                    total_gems_in_level = len(world['gems'])
                    player.rect.topleft=(80,HEIGHT-200); player.vx=player.vy=0; player.collected=0
                    level_completed = False
            if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                if level_button.is_clicked(ev.pos): show_level_popup = not show_level_popup
                if level_completed and next_level_btn.is_clicked(ev.pos):
                    if level_index < TOTAL_LEVELS:
                        level_index += 1
                        world = generate_level(level_index)
                        total_gems_in_level = len(world['gems'])
                        player.rect.topleft=(80,HEIGHT-200); player.vx=player.vy=0; player.collected=0
                        level_completed = False
                    else:
                        show_final_screen(player); running=False
                if game_over and retry_btn.is_clicked(ev.pos):
                    world = generate_level(level_index)
                    total_gems_in_level = len(world['gems'])
                    player.rect.topleft=(80,HEIGHT-200); player.vx=player.vy=0; player.collected=0
                    game_over = False
                    current_game_over_message = None

        if not (game_over or level_completed):
            # Input
            keys = pygame.key.get_pressed()
            player.vx = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: player.vx = -player.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player.vx = player.speed

            # Jump
            if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
                if not jump_pressed:
                    player.jump()
                    jump_pressed = True
            else:
                jump_pressed = False

            # Physics
            player.apply_gravity()
            player.move(world['platforms'])

            # Check if hit the floor
            if player.on_ground and player.rect.bottom == HEIGHT - 40:
                game_over = True

            # Collect gems
            remaining = []
            for g in world['gems']:
                if player.rect.colliderect(g): player.collected += 1
                else: remaining.append(g)
            world['gems'] = remaining

            # Spikes & fall
            for s in world['spikes']:
                if player.rect.colliderect(s): game_over = True; break
            if player.rect.top > HEIGHT+200: game_over = True

            # Exit
            if player.rect.colliderect(world['exit']): level_completed = True

        # Camera
        offset_x = max(0, min(world['width']-WIDTH, player.rect.centerx - WIDTH//3))

        # Draw
        draw_level(SCREEN, world, offset_x)
        player.draw(SCREEN, offset_x)

        # HUD
        hud_rect = pygame.Rect(WIDTH-180,12,168,84)
        pygame.draw.rect(SCREEN, HUD_BG, hud_rect, border_radius=8)
        SCREEN.blit(FONT.render(f'Gems: {player.collected}/{total_gems_in_level}', True, WHITE), (WIDTH-168,30))
        level_button.draw(SCREEN)
        if show_level_popup:
            pop = pygame.Rect(12,56,160,48)
            pygame.draw.rect(SCREEN, HUD_BG, pop, border_radius=8)
            SCREEN.blit(FONT.render(f'Current Level: {level_index}/{TOTAL_LEVELS}', True, WHITE), (22,66))

        # Level completed overlay
        if level_completed:
            overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            SCREEN.blit(overlay,(0,0))
            SCREEN.blit(BIG_FONT.render('Level Completed!', True, (255,230,180)), (WIDTH//2-140, HEIGHT//2-20))
            next_level_btn.draw(SCREEN)

        # Game over overlay
        if game_over:
            overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            SCREEN.blit(overlay,(0,0))
            if current_game_over_message is None:
                current_game_over_message = random.choice(game_over_messages)
            SCREEN.blit(BIG_FONT.render(current_game_over_message, True, (240,120,120)), (WIDTH//2-150, HEIGHT//2-20))
            retry_btn.draw(SCREEN)

        SCREEN.blit(FONT.render('Use arrow keys or A/D to move, Space to jump', True, BLACK), (12, HEIGHT-28))
        pygame.display.flip()

    pygame.quit()


if __name__=='__main__':
    run_game()