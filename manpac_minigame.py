import pygame
import sys
import random
import math
import os
from asset_utils import asset_path
from config import CARDS, C_COMMON, C_RARE, C_EPIC, C_LEGENDARY, GLOBAL_CONTROLS
from minigame_view import (
    create_minigame_view,
    present_minigame,
    draw_minigame_settings_button,
    minigame_settings_requested,
    run_minigame_settings)
from asset_utils import (
    load_franziska_sprite)

def run_manpac(screen, g):
    ASSET_DIR = asset_path(
        "manpac")    
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    TILE_SIZE = 40
    PANEL_HEIGHT = 160
    
    MAZE = [
        "WWWWWWWWWWWWWWWWWWWW",
        "W........WW........W",
        "W.WW.WWW....WWW.WW.W",
        "W.WW.WWW.WW.WWW.WW.W",
        "W..................W",
        "W.WW.W.WWWWWW.W.WW.W",
        "W....W...WW...W....W",
        "WWWW.WWW WW WWW.WWWW",
        "    .W        W.    ",
        "WWWW.W WW  WW W.WWWW",
        "    .W W    W W.    ",
        "WWWW.W WWWWWW W.WWWW",
        "    .W        W.    ",
        "WWWW.W WWWWWW W.WWWW",
        "W........WW........W",
        "W.WW.WWW....WWW.WW.W",
        "W..W.....P......W..W",
        "WW.W.W.WWWWWW.W.W.WW",
        "W....W...WW...W....W",
        "WWWWWWWWWWWWWWWWWWWW"
    ]

    SCREEN_WIDTH = len(MAZE[0]) * TILE_SIZE
    SCREEN_HEIGHT = len(MAZE) * TILE_SIZE + PANEL_HEIGHT
    MAZE_HEIGHT = len(MAZE) * TILE_SIZE
    FPS = 60

    
    clock = pygame.time.Clock()

    def load_sound(filename):

        full_path = os.path.join(ASSET_DIR, filename)

        if os.path.exists(
            full_path):

            try:

                return pygame.mixer.Sound(
                    full_path)

            except Exception as exc:

                print(
                    "ManPac sound load failed:",
                    full_path,
                    exc)

        return None
    def load_img(filename, size):

        path = os.path.join(ASSET_DIR, filename)

        if os.path.exists(path):

            try:

                img = pygame.image.load(
                    path).convert_alpha()

                return pygame.transform.smoothscale(img, size)

            except Exception as exc:

                print(
                    "ManPac image load failed:",
                    path,
                    exc)

        return None


    player_img = load_img(
        "img_phoneix.png",
        (36, 36))

    player_damage_img = load_img(
        "img_damage.png",
        (36, 36))

    player_objection_img = load_img(
        "img_objection.png",
        (36, 36))

    badge_img = load_img(
        "img_badge.png",
        (32, 32))
    sound_eat = load_sound("eat.wav")
    sound_objection = load_sound("objection_phoenix.wav")
    sound_objection_miles = load_sound("objection_miles.wav")
    sound_damage = load_sound("damage.wav")
    sound_shout = load_sound("shout.wav")
    sound_running = load_sound("running.wav")

    if sound_running: sound_running.set_volume(0.7)
    running_channel = pygame.mixer.Channel(7)

    font = pygame.font.SysFont("arial", 22, bold=True)
    small_font = pygame.font.SysFont("arial", 15, bold=True)
    big_font = pygame.font.SysFont("arial", 54, bold=True)

    THEMES = {
        "DARK": {
            "BG": (30, 30, 35), "PANEL": (20, 20, 25), "CARD_BG": (40, 40, 50),
            "TEXT": (240, 240, 240), "TITLE": (255, 80, 120), "BTN_MAIN": (180, 40, 80),
            "BTN_HOVER": (220, 60, 100), "BORDER": (80, 80, 100), "GROUND": (20, 20, 25),
            "WALL": (45, 45, 60), "WALL_BORDER": (90, 90, 120), "PLAYER": (255, 220, 60),
            "GHOST_1": (220, 60, 100), "GHOST_2": (255, 184, 222), "GHOST_3": (110, 210, 230),
            "GHOST_4": (240, 150, 70), "POWERUP": (255, 215, 0)
        }
    }
    theme = THEMES["DARK"]
    text_color = theme["TEXT"]
    CARD_ID_COLORS = [
        (70, 150, 255),   
        (70, 210, 120),   
        (175, 100, 255),  
    ]
    controls = GLOBAL_CONTROLS["ManPac"]
    display, screen = create_minigame_view(SCREEN_WIDTH, SCREEN_HEIGHT)
    is_franziska = (
        str(
            getattr(g, "char_class", "BRUISER")
        ).upper()
        == "ASSASSIN")

    franziska_default_img = (
        load_franziska_sprite(
            "default",
            (38, 38))
        if is_franziska
        else None)

    franziska_damage_img = (
        load_franziska_sprite(
            "damage",
            (38, 38))
        if is_franziska
        else None)

    franziska_special_img = (
        load_franziska_sprite(
            "special",
            (38, 38))
        if is_franziska
        else None)

    def get_card_color(card_name):
        rarity = CARDS.get(card_name, {}).get("rarity", "common")
        if rarity == "common": return C_COMMON
        elif rarity == "rare": return C_RARE
        elif rarity == "epic": return C_EPIC
        elif rarity == "legendary": return C_LEGENDARY
        return C_COMMON

    walls = []
    valid_spawn_tiles = []
    pacman_start_x, pacman_start_y = 0, 0
    pacman_radius = TILE_SIZE // 2 - 4
    pacman_speed = 4

    for row_idx, row in enumerate(MAZE):
        for col_idx, char in enumerate(row):
            x, y = col_idx * TILE_SIZE, row_idx * TILE_SIZE
            if char == "W": walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
            elif char == ".": valid_spawn_tiles.append((x + TILE_SIZE // 2, y + TILE_SIZE // 2))
            elif char == "P": pacman_start_x, pacman_start_y = x + TILE_SIZE // 2, y + TILE_SIZE // 2

    def has_collision(x, y, radius):
        test_rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        return any(test_rect.colliderect(w) for w in walls)

    def tile_center(col, row):
        return col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2

    HOUSE_ROW, EXIT_ROW, DOOR_ROW_ABOVE = 10, 8, 8
    RELEASE_GAP = 90
    
    class Ghost:
        def __init__(self, house_col, color_key, door_col, exit_col, release_delay):
            self.house_col = house_col
            self.color_key = color_key
            self.door_col = door_col
            self.exit_col = exit_col
            self.release_delay = release_delay
            self.radius = TILE_SIZE // 2 - 4
            self.speed = 3
            self.reset()

        def reset(self):
            self.start_x, self.start_y = tile_center(self.house_col, HOUSE_ROW)
            self.x, self.y = self.start_x, self.start_y
            self.dx, self.dy = 0, 0
            self.state = "house"
            self.house_dir = -1
            self.timer = self.release_delay
            self.waypoints = [
                tile_center(self.door_col, HOUSE_ROW),
                tile_center(self.door_col, EXIT_ROW),
                tile_center(self.exit_col, EXIT_ROW),
                tile_center(self.exit_col, DOOR_ROW_ABOVE),
            ]
            self.waypoint_index = 0
            self.door_entry_x, self.door_entry_y = tile_center(self.door_col, DOOR_ROW_ABOVE)

        def eaten(self):
            self.state = "eaten"
            if self.dx != 0 or self.dy != 0:
                self.dx, self.dy = -self.dx, -self.dy

        def _move_toward(self, tx, ty):
            if self.x < tx: self.x = min(self.x + self.speed, tx)
            elif self.x > tx: self.x = max(self.x - self.speed, tx)
            if self.y < ty: self.y = min(self.y + self.speed, ty)
            elif self.y > ty: self.y = max(self.y - self.speed, ty)
            return self.x == tx and self.y == ty

        def update(self, px, py, active_power):
            if self.state == "house":
                self.y += self.house_dir * (self.speed / 2)
                if self.y <= self.start_y - 6: self.house_dir = 1
                elif self.y >= self.start_y + 6: self.house_dir = -1
                if self.timer > 0: self.timer -= 1
                else: self.state = "exiting"; self.waypoint_index = 0
            
            elif self.state == "exiting":
                tx, ty = self.waypoints[self.waypoint_index]
                if self._move_toward(tx, ty):
                    self.waypoint_index += 1
                    if self.waypoint_index >= len(self.waypoints):
                        self.state = "free"; self.dx = -self.speed; self.dy = 0
                        
            elif self.state == "entering":
                if self._move_toward(self.start_x, self.start_y):
                    self.state = "house"; self.timer = FPS * 2
            
            elif self.state in ["free", "eaten"]:
                if self.x < 0: self.x = SCREEN_WIDTH
                elif self.x > SCREEN_WIDTH: self.x = 0
                
                spd = self.speed * 1.5 if self.state == "eaten" else self.speed
                cx = (int(self.x) // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
                cy = (int(self.y) // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
                
                if self.state == "eaten" and abs(self.x - self.door_entry_x) <= spd and abs(self.y - self.door_entry_y) <= spd:
                    self.x, self.y = self.door_entry_x, self.door_entry_y
                    self.state = "entering"
                    return

                if abs(self.x - cx) < spd and abs(self.y - cy) < spd:
                    self.x, self.y = cx, cy
                    dirs = [(0, -self.speed), (-self.speed, 0), (0, self.speed), (self.speed, 0)]
                    valid = []
                    for dx, dy in dirs:
                        if (dx, dy) == (-self.dx, -self.dy): continue
                        tx = self.x + (dx/self.speed)*TILE_SIZE
                        ty = self.y + (dy/self.speed)*TILE_SIZE
                        if not has_collision(tx, ty, self.radius): valid.append((dx, dy))
                    
                    if not valid: valid.append((-self.dx, -self.dy))
                    
                    target = (self.door_entry_x, self.door_entry_y) if self.state == "eaten" else (px, py)
                    if active_power and self.state == "free":
                        target = (self.x + (self.x - px), self.y + (self.y - py))
                        
                    if len(valid) > 1:
                        best_d = valid[0]; mind = float('inf')
                        for dx, dy in valid:
                            d = math.hypot(self.x + dx*5 - target[0], self.y + dy*5 - target[1])
                            if d < mind: mind = d; best_d = (dx, dy)
                        self.dx, self.dy = best_d
                    else:
                        self.dx, self.dy = random.choice(valid)
                        
                self.x += self.dx * (1.5 if self.state == "eaten" else 1)
                self.y += self.dy * (1.5 if self.state == "eaten" else 1)

        def draw(self, surf, power_active):
            c = theme[self.color_key]
            if self.state in ["eaten", "entering"]: c = (40, 40, 40)
            elif power_active and self.state == "free": c = (20, 20, 180)
            pygame.draw.circle(surf, c, (int(self.x), int(self.y)), self.radius)

    ghosts = [
        Ghost(8, "GHOST_1", 9, 8, 0),
        Ghost(9, "GHOST_2", 9, 8, RELEASE_GAP),
        Ghost(10, "GHOST_3", 10, 11, RELEASE_GAP*2),
        Ghost(11, "GHOST_4", 10, 11, RELEASE_GAP*3)
    ]

    POWER_UP_TILES = [(1, 1), (18, 1), (1, 14), (18, 14)]
    power_ups = [{"rect": pygame.Rect(tile_center(c, r)[0]-16, tile_center(c, r)[1]-16, 32, 32)} for c, r in POWER_UP_TILES]
    
    reward_cards = g.reward_pool 
    pieces_needed = (
        15
        if "Arcade Token" in getattr(g, "relics", [])
        else 16)

    collectibles = []
    card_progress = [0, 0, 0]
    completed_cards = set()

    avail = [p for p in valid_spawn_tiles if p not in [tile_center(c,r) for c,r in POWER_UP_TILES]]
    spots = random.sample(avail, 15)
    total_collectibles = pieces_needed * 3

    spots = random.sample(avail, total_collectibles)

    for i in range(total_collectibles):
        cx, cy = spots[i]

        collectibles.append({
            "rect": pygame.Rect(cx - 16, cy - 16,32,32),
            "card_idx": i % 3
        })

    pacman_x, pacman_y = pacman_start_x, pacman_start_y
    dx, dy, next_dx, next_dy = 0, 0, 0, 0
    hit_timer = 0
    power_active = False
    power_timer = 0
    
    state = "PLAYING"
    won_card = None
    win_timer = 2.0
    
    start_ticks = pygame.time.get_ticks()
    time_left = 30

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if minigame_settings_requested(
                event,
                g,
                SCREEN_WIDTH,
                SCREEN_HEIGHT):

                display, paused_ms = (
                    run_minigame_settings(
                        display,
                        screen,
                        g))

                start_ticks += paused_ms

                continue

            if event.type == pygame.QUIT:
                
                pygame.quit()
                sys.exit()
            
            if state == "PLAYING" and event.type == pygame.KEYDOWN:
                if event.key == controls["LEFT"]:
                    next_dx, next_dy = -pacman_speed, 0

                elif event.key == controls["RIGHT"]:
                    next_dx, next_dy = pacman_speed, 0

                elif event.key == controls["UP"]:
                    next_dx, next_dy = 0, -pacman_speed

                elif event.key == controls["DOWN"]:
                    next_dx, next_dy = 0, pacman_speed

        if state == "PLAYING":
            seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
            time_left = max(0, 30 - seconds_passed)
            
            if time_left <= 0:
                state = "TIMEOUT"

            if hit_timer > 0:
                hit_timer -= 1
                if hit_timer == 0:
                    pacman_x, pacman_y = pacman_start_x, pacman_start_y
                    dx, dy, next_dx, next_dy = 0, 0, 0, 0
                    for ghost in ghosts: ghost.reset()
            else:
                if power_timer > 0:
                    power_timer -= 1
                    if power_timer == 0: power_active = False

                if (next_dx, next_dy) != (dx, dy):
                    if next_dx != 0:
                        cy = (pacman_y // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
                        if abs(pacman_y - cy) <= 12 and not has_collision(pacman_x + next_dx*2, cy, pacman_radius):
                            pacman_y, dx, dy = cy, next_dx, next_dy
                    elif next_dy != 0:
                        cx = (pacman_x // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
                        if abs(pacman_x - cx) <= 12 and not has_collision(cx, pacman_y + next_dy*2, pacman_radius):
                            pacman_x, dx, dy = cx, next_dx, next_dy

                if not has_collision(pacman_x + dx, pacman_y + dy, pacman_radius):
                    pacman_x += dx; pacman_y += dy
                else: dx, dy = 0, 0

                if pacman_x < 0: pacman_x = SCREEN_WIDTH
                elif pacman_x > SCREEN_WIDTH: pacman_x = 0

                p_rect = pygame.Rect(pacman_x - pacman_radius, pacman_y - pacman_radius, pacman_radius*2, pacman_radius*2)
                for ghost in ghosts:
                    ghost.update(pacman_x, pacman_y, power_active)
                    if ghost.state in ["free", "exiting"]:
                        g_rect = pygame.Rect(ghost.x - ghost.radius, ghost.y - ghost.radius, ghost.radius*2, ghost.radius*2)
                        if p_rect.colliderect(g_rect):
                            if power_active:
                                ghost.eaten()
                                if sound_shout: sound_shout.play()
                            else:
                                hit_timer = int(FPS * 1.2)
                                if sound_damage: sound_damage.play()
                                
                                g.php -= 5
                                if g.php <= 0:
                                    g.php = 0
                                   
                                    return "DEAD"
                            break

                ate = False
                for item in collectibles[:]:
                    if p_rect.colliderect(item["rect"]):
                        collectibles.remove(item)
                        idx = item["card_idx"]
                        card_progress[idx] += 1
                        ate = True
                        if sound_eat: sound_eat.play()
                        
                        if (card_progress[idx] >= pieces_needed and idx not in completed_cards):
                            completed_cards.add(idx)

                for p in power_ups[:]:
                    if p_rect.colliderect(p["rect"]):
                        power_ups.remove(p)
                        power_active = True
                        power_timer = FPS * 8
                        if sound_objection: sound_objection.play()

                if (dx != 0 or dy != 0) and not ate and hit_timer == 0:
                    if sound_running and not running_channel.get_busy():
                        running_channel.play(sound_running, loops=-1)
                else:
                    if running_channel.get_busy(): running_channel.stop()

        # РИСУВАНЕ
        screen.fill(theme["BG"])
        pygame.draw.rect(screen, theme["GROUND"], (0, 0, SCREEN_WIDTH, MAZE_HEIGHT))
        
        for wall in walls:
            pygame.draw.rect(screen, theme["WALL"], wall, border_radius=6)

        for p in power_ups:
            if badge_img:

                screen.blit(badge_img, p["rect"].topleft)

            else:

                pygame.draw.circle(
                    screen,
                    theme["POWERUP"],
                    p["rect"].center,
                    12)

        for item in collectibles:

            card_idx = item["card_idx"]

            id_color = CARD_ID_COLORS[
                card_idx % len(CARD_ID_COLORS)
            ]

            pygame.draw.rect(
                screen,
                id_color,
                item["rect"],
                border_radius=5)

            pygame.draw.rect(
                screen,
                (245, 245, 245),
                item["rect"],
                2,
                border_radius=5)

            lbl = font.render(
                str(card_idx + 1),
                True,
                (255, 255, 255))

            screen.blit(
                lbl,
                lbl.get_rect(
                    center=item["rect"].center))

        if (
            hit_timer == 0
            or (
                hit_timer > 0
                and (
                    hit_timer // 10) % 2 == 0)):

            if is_franziska:

                full_victory = (
                    state == "TIMEOUT"
                    and len(completed_cards)
                    == len(reward_cards))

                if (
                    full_victory
                    and franziska_special_img
                    is not None):

                    player_sprite = (
                        franziska_special_img)

                elif (
                    hit_timer > 0
                    and franziska_damage_img
                    is not None):

                    player_sprite = (
                        franziska_damage_img)

                else:

                    player_sprite = (
                        franziska_default_img)

                if player_sprite:

                    sprite_rect = (
                        player_sprite.get_rect(
                            center=(
                                int(pacman_x),
                                int(pacman_y))))

                    screen.blit(player_sprite, sprite_rect)

            else:


                full_victory = (
                    state == "TIMEOUT"
                    and len(completed_cards)
                    == len(reward_cards)
                )

                if (
                    full_victory
                    and player_objection_img
                    is not None
                ):

                    player_sprite = (
                        player_objection_img
                    )

                elif (
                    hit_timer > 0
                    and player_damage_img
                    is not None
                ):

                    player_sprite = (
                        player_damage_img
                    )

                else:

                    player_sprite = (
                        player_img
                    )

                if player_sprite is not None:

                    sprite_rect = (
                        player_sprite.get_rect(
                            center=(
                                int(pacman_x),
                                int(pacman_y)
                            )
                        )
                    )

                    screen.blit(
                        player_sprite,
                        sprite_rect
                    )
        for ghost in ghosts: ghost.draw(screen, power_active)

        # UI
        pygame.draw.rect(screen, theme["PANEL"], (0, MAZE_HEIGHT, SCREEN_WIDTH, PANEL_HEIGHT))
        
        screen.blit(font.render(f"HP: {g.php}/{g.pmx}", True, (255, 80, 80)), (20, MAZE_HEIGHT + 20))
        
        timer_col = (255, 80, 80) if time_left <= 10 else text_color
        screen.blit(font.render(f"Time: {time_left}s", True, timer_col), (20, MAZE_HEIGHT + 60))
        
        for i in range(len(reward_cards)):

            c_name = reward_cards[i]
            c_prog = card_progress[i]

            id_color = CARD_ID_COLORS[
                i % len(CARD_ID_COLORS)
            ]

            x = 145 + i * 215
            y = MAZE_HEIGHT + 35

            number_rect = pygame.Rect(x, y, 32, 32)

            pygame.draw.rect(
                screen,
                id_color,
                number_rect,
                border_radius=5)

            pygame.draw.rect(
                screen,
                (245, 245, 245),
                number_rect,
                2,
                border_radius=5)

            number_surf = font.render(
                str(i + 1),
                True,
                (255, 255, 255))

            screen.blit(
                number_surf,
                number_surf.get_rect(
                    center=number_rect.center))

            completed = (
                c_prog >= pieces_needed)

            label_color = (
                (50, 220, 50)
                if completed
                else text_color)

            label = font.render(
                f"{c_name} {c_prog}/{pieces_needed}",
                True,
                label_color)

            screen.blit(label,(number_rect.right + 7,y + 3))

                
        if state == "TIMEOUT":
            if running_channel.get_busy(): running_channel.stop()
            wt = big_font.render("TIME OUT!", True, (255, 70, 70))
            screen.blit(wt, wt.get_rect(center=(SCREEN_WIDTH//2, MAZE_HEIGHT//2)))
            win_timer -= dt
            if win_timer <= 0:
               
                won_cards = [reward_cards[i] for i in sorted(completed_cards)]
                return won_cards
        controls_txt = small_font.render(
            f"[{pygame.key.name(controls['UP']).upper()}] Up   "
            f"[{pygame.key.name(controls['DOWN']).upper()}] Down   "
            f"[{pygame.key.name(controls['LEFT']).upper()}] Left   "
            f"[{pygame.key.name(controls['RIGHT']).upper()}] Right",
            True,
            theme["TEXT"])

        screen.blit(
            controls_txt,
            controls_txt.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT - 15)))
        draw_minigame_settings_button(screen, g)
        present_minigame(display, screen)