import pygame
import sys
import random
import math
import os
from config import GLOBAL_CONTROLS
from minigame_view import (
    create_minigame_view,
    present_minigame,
    screen_to_virtual,
    draw_minigame_settings_button,
    minigame_settings_requested,
    run_minigame_settings)
from asset_utils import asset_path
from asset_utils import (
    asset_path,
    load_franziska_sprite)

pygame.init()

FRANZISKA_ASSET_DIR = asset_path(
    "bullethell")

def load_anim_folder(
    folder_name,
    size=(280, 180)):

    folder_path = os.path.join(FRANZISKA_ASSET_DIR, folder_name)

    frames = []

    if os.path.exists(
        folder_path):

        files = sorted(
            os.listdir(
                folder_path),
            key=lambda x: (
                len(x),
                x)
        )

        for filename in files:

            if filename.lower().endswith(
                (
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".gif")
            ):

                try:

                    img = pygame.image.load(
                        os.path.join(folder_path, filename)
                    )

                    img = pygame.transform.scale(img, size)

                    frames.append(
                        img)

                except Exception as exc:

                    print(
                        "Franziska frame failed:",
                        filename,
                        exc)

    if not frames:

        surf = pygame.Surface(size, pygame.SRCALPHA)

        frames.append(surf)

    return frames




VIRTUAL_WIDTH = 800
VIRTUAL_HEIGHT = 600
pygame.display.set_caption("Ace Attorney Boss Fight - Franziska von Karma")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24, bold=True)
big_font = pygame.font.SysFont("Arial", 40, bold=True)
small_font = pygame.font.SysFont("Arial", 18, bold=True)


BG_COLOR = (15, 15, 20)
WHITE = (255, 255, 255)
PLAYER_COLOR = (255, 0, 0)
BOSS_COLOR = (100, 150, 255)
HOVER_COLOR = (255, 150, 0) 
HP_RED = (255, 0, 0)
HP_YELLOW = (255, 255, 0)


WHIP_WARNING = (100, 50, 50)
WHIP_STRIKE = (200, 240, 255)
PAPER_COLOR = (240, 240, 240)
OBJ_COLOR = (255, 215, 0)


def load_phoenix_image(
    filename,
    size,
    fallback_color,
    flip_x=False):

    path = os.path.join(
        FRANZISKA_ASSET_DIR,
        "phoenix",
        filename)

    try:

        img = pygame.image.load(
            path)

        img = pygame.transform.scale(img, size)

        if flip_x:
            img = pygame.transform.flip(
                img,
                True,
                False)

        return img

    except Exception as exc:

        print(
            "Phoenix image load failed:",
            path,
            exc)

        surf = pygame.Surface(size, pygame.SRCALPHA)

        surf.fill(
            fallback_color)

        return surf


PHOENIX_SIZE = (120, 120)

img_phoenix_idle = load_phoenix_image(
    "img_phoneix.png",
    PHOENIX_SIZE,
    (50, 150, 255),
    flip_x=True)

img_phoenix_damage = load_phoenix_image(
    "img_damage.png",
    PHOENIX_SIZE,
    (180, 80, 80))

img_phoenix_attack = load_phoenix_image(
    "img_phoneix_attack.png",
    PHOENIX_SIZE,
    (255, 180, 80))


boss_anims = {
    "default": load_anim_folder("franny_default"),
    "damage_high": load_anim_folder("franny_damage_high"),
    "damage_low": load_anim_folder("franny_damage_low"),
    "victory": load_anim_folder("franny_victory"),
    "objection": load_anim_folder("franny_object"),
    "whip_1": load_anim_folder("franny_whip_1"),         
    "whip_2": load_anim_folder("franny_whip_2"),         
    "whip_3": load_anim_folder("franny_whip_3"),         
    "tears": load_anim_folder("franny_tears"),           
    "crying": load_anim_folder("franny_crying")
}

flavor_texts = [
    "Franziska von Karma readies her whip...",
    "Foolish fool!",
    "A von Karma always aims for perfection.",
    "Objection! I will whip you into shape!"
]

def draw_player_stats(screen, hp, max_hp, b_hp, b_max_hp, boss_state, boss_frame_idx, boss_flinch_timer):
    WIDTH, HEIGHT = screen.get_size()
    
    hp_text = font.render(f"{hp} / {max_hp}", True, WHITE)
    screen.blit(hp_text, (20, HEIGHT - 40))
    pygame.draw.rect(screen, HP_RED, (120, HEIGHT - 40, 200, 20))
    if hp > 0:
        ratio = hp / max_hp
        pygame.draw.rect(screen, HP_YELLOW, (120, HEIGHT - 40, int(200 * ratio), 20))
        
    boss_text = font.render(f"Boss HP: {b_hp} / {b_max_hp}", True, WHITE)
    screen.blit(boss_text, (WIDTH - 250, HEIGHT - 40))
    pygame.draw.rect(screen, HP_RED, (WIDTH - 250, HEIGHT - 70, 200, 20))
    if b_hp > 0:
        boss_ratio = b_hp / b_max_hp
        pygame.draw.rect(screen, BOSS_COLOR, (WIDTH - 250, HEIGHT - 70, int(200 * boss_ratio), 20))
    

        
    current_img = boss_anims[
        boss_state
    ][
        int(boss_frame_idx)
    ]

    img_rect = current_img.get_rect(
        center=(
            WIDTH // 2,
            120)
    )

    screen.blit(current_img, img_rect)

def run_undertale_boss(screen, g):
    WIDTH = VIRTUAL_WIDTH
    HEIGHT = VIRTUAL_HEIGHT

    display, screen = create_minigame_view(WIDTH, HEIGHT)
    is_franziska = (
        str(
            getattr(g, "char_class", "BRUISER")
        ).upper()
        == "ASSASSIN")

    img_franziska_default = (
        load_franziska_sprite("default", PHOENIX_SIZE)
        if is_franziska
        else None)

    img_franziska_damage = (
        load_franziska_sprite("damage", PHOENIX_SIZE)
        if is_franziska
        else None)

    img_franziska_special = (
        load_franziska_sprite("special", PHOENIX_SIZE)
        if is_franziska
        else None)
    controls = GLOBAL_CONTROLS[
        "UndertaleBoss"
    ]
    # --- Динамични Арени (центрирани спрямо новия екран) ---
    arena_attack = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 75, 600, 150)
    arena_defend = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 25, 300, 150)
    current_arena = arena_attack

    player_hp = g.php
    player_max_hp = g.pmx
    
    player_size = 8
    player_speed = 3
    player_rect = pygame.Rect(0, 0, player_size, player_size)
    player_rect.center = arena_attack.center

    boss_max_hp = 150
    boss_hp = boss_max_hp
    boss_flinch_timer = 0
    player_flinch_timer = 0
    phoenix_action_timer = 0

    boss_state = "default"
    boss_frame_idx = 0.0

    skillcheck_active = False
    bar_x = 0
    bar_speed = 8
    bar_dir = 1
    hit_effect_timer = 0    
    last_damage_dealt = 0
    
    spin_hit_cooldown = 0
    objection_hit_cooldown = 0

    phase = "ATTACK"
    phase_timer = 400 
    rain_stage = 0
    rain_stage_timer = 0

    current_flavor = random.choice(flavor_texts)
    attack_types = ["PAPER_RAIN", "WHIP_H", "WHIP_V", "OBJECTION", "SPIN", "SAFE_SPOT"]
    current_attack = random.choice(attack_types)
    projectiles = []
    spawn_timer = 0
    safe_spot_is_horiz = True


    buttons = [
        {"name": "ATTACK", "rect": pygame.Rect(WIDTH//2 - 200, HEIGHT//2 + 100, 120, 50), "action": "fight"},
        {"name": "HEAL (+20)", "rect": pygame.Rect(WIDTH//2 + 80, HEIGHT//2 + 100, 120, 50), "action": "item"}
    ]

    attack_test_buttons = [
        {"name": "RAIN",   "attack": "PAPER_RAIN", "rect": pygame.Rect(15, 58, 95, 35)},
        {"name": "WHIP H", "attack": "WHIP_H",     "rect": pygame.Rect(15, 100, 95, 35)},
        {"name": "WHIP V", "attack": "WHIP_V",     "rect": pygame.Rect(15, 142, 95, 35)},

        {"name": "OBJ",    "attack": "OBJECTION",  "rect": pygame.Rect(WIDTH - 110, 58, 95, 35)},
        {"name": "SPIN",   "attack": "SPIN",       "rect": pygame.Rect(WIDTH - 110, 100, 95, 35)},
        {"name": "SAFE",   "attack": "SAFE_SPOT",  "rect": pygame.Rect(WIDTH - 110, 142, 95, 35)},
        {"name": "RANDOM", "attack": "RANDOM",     "rect": pygame.Rect(WIDTH - 125, 184, 110, 35)},
    ]

    running = True
    while running:
        clock.tick(60) 
        mouse_pos = screen_to_virtual(
            pygame.mouse.get_pos(),
            WIDTH,
            HEIGHT)
        
        for event in pygame.event.get():
            if minigame_settings_requested(
                event,
                g,
                WIDTH,
                HEIGHT):

                display, _ = (
                    run_minigame_settings(
                        display,
                        screen,
                        g)
                )

                continue
            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()
                
            if skillcheck_active:
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or (event.type == pygame.KEYDOWN and event.key == controls["ACTION"]):
                    center_x = current_arena.centerx
                    max_dist = current_arena.width / 2

                    dist = abs(bar_x - center_x)
                    accuracy = max(0.0, 1.0 - (dist / max_dist))
                    damage = int(accuracy * 35)

                    boss_hp -= damage
                    last_damage_dealt = damage 
                    
                    boss_flinch_timer = 18 
                    skillcheck_active = False
                    hit_effect_timer = 40 
                    phoenix_action_timer = 40

                    if damage >= 20:
                        boss_state = "damage_high"
                    else:
                        boss_state = "damage_low"
                    boss_frame_idx = 0

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if phase == "ATTACK":
                    for btn in buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            if btn["action"] == "fight":
                                skillcheck_active = True
                                bar_x = current_arena.left
                                bar_dir = 1
                            elif btn["action"] == "item":
                                player_hp = min(player_max_hp, player_hp + 20)
                                g.php = player_hp
                                phoenix_action_timer = 12
                                phase = "DEFEND"
                                phase_timer = 400
                                current_attack = random.choice(attack_types)
                                safe_spot_is_horiz = True
                                player_rect.center = arena_defend.center
                                projectiles.clear()
                                spawn_timer = 0
                            break

                for btn in attack_test_buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        if btn["attack"] == "RANDOM":
                            current_attack = random.choice(attack_types)
                        else:
                            current_attack = btn["attack"]
                        
                        phase = "DEFEND"
                        phase_timer = 400
                        projectiles.clear()
                        spawn_timer = 0
                        safe_spot_is_horiz = True
                        player_rect.center = arena_defend.center
                        break


        if boss_hp <= 0:

            if (
                is_franziska
                and img_franziska_special
                is not None):

                phoenix_x = 20
                phoenix_y = HEIGHT - 150

                screen.blit(
                    img_franziska_special,
                    (
                        phoenix_x,
                        phoenix_y)
                )

                present_minigame(display, screen)

                pygame.time.delay(
                    500)

            return "WIN"

        if player_hp <= 0:
            g.php = 0
            return "DEAD"

        if skillcheck_active:
            bar_x += bar_speed * bar_dir
            if bar_x >= current_arena.right:
                bar_x = current_arena.right
                bar_dir = -1
            elif bar_x <= current_arena.left:
                bar_x = current_arena.left
                bar_dir = 1
        
        if hit_effect_timer > 0:
            hit_effect_timer -= 1
            if hit_effect_timer == 0:
                phase = "DEFEND"
                phase_timer = 400
                current_attack = random.choice(attack_types)
                safe_spot_is_horiz = True
                player_rect.center = arena_defend.center
                projectiles.clear()
                spawn_timer = 0
        if phoenix_action_timer > 0:
            phoenix_action_timer -= 1
        
        if phase == "ATTACK":
            current_arena = arena_attack
            keys = pygame.key.get_pressed()
            if keys[controls["LEFT"]]:
                player_rect.x -= player_speed

            if keys[controls["RIGHT"]]:
                player_rect.x += player_speed

            if keys[controls["UP"]]:
                player_rect.y -= player_speed

            if keys[controls["DOWN"]]:
                player_rect.y += player_speed
            player_rect.clamp_ip(current_arena)

        elif phase == "DEFEND" and not skillcheck_active:
            current_arena = arena_defend
            phase_timer -= 1
            
            keys = pygame.key.get_pressed()
            if keys[controls["LEFT"]]:
                player_rect.x -= player_speed

            if keys[controls["RIGHT"]]:
                player_rect.x += player_speed

            if keys[controls["UP"]]:
                player_rect.y -= player_speed

            if keys[controls["DOWN"]]:
                player_rect.y += player_speed
            player_rect.clamp_ip(current_arena)
            
            spawn_timer += 1
            
            if current_attack == "PAPER_RAIN" and rain_stage == 0:
                rain_stage = 1
                rain_stage_timer = 0
                boss_frame_idx = 0.0
                spawn_timer = 0
                pw = random.randint(15, 30)
                ph = random.randint(20, 40)
                px = random.randint(current_arena.left, current_arena.right - pw)
                py = current_arena.top - ph
                
            elif current_attack == "OBJECTION" and spawn_timer >= 45:

                side = random.choice([
                    "top",
                    "bottom",
                    "left",
                    "right"
                ])

                size = 25
                inset = 12

                if side == "top":

                    px = random.randint(current_arena.left, current_arena.right - size)

                    py = (
                        current_arena.top
                        + inset)

                elif side == "bottom":

                    px = random.randint(current_arena.left, current_arena.right - size)

                    py = (
                        current_arena.bottom
                        - size
                        - inset)

                elif side == "left":

                    px = (
                        current_arena.left
                        + inset)

                    py = random.randint(current_arena.top, current_arena.bottom - size)

                else:

                    px = (
                        current_arena.right
                        - size
                        - inset)

                    py = random.randint(current_arena.top, current_arena.bottom - size)

              
                    
                angle = math.atan2(player_rect.centery - (py + size/2), player_rect.centerx - (px + size/2))
                
                projectiles.append({
                    "type": "OBJECTION",
                    "rect": pygame.Rect(
                        px,
                        py,
                        size,
                        size),
                    "vx": math.cos(angle) * 4.5,
                    "vy": math.sin(angle) * 4.5,
                    "color": OBJ_COLOR,
                    "damage": 5,

                    "warning": 12
                })
                spawn_timer = 0

            elif current_attack == "WHIP_H" and spawn_timer >= 40:
                wy = random.randint(current_arena.top, current_arena.bottom - 20)
                projectiles.append({
                    "type": "WHIP",
                    "rect": pygame.Rect(current_arena.left, wy, current_arena.width, 20),
                    "timer": 45,
                    "state": "WARNING"
                })
                spawn_timer = 0

            elif current_attack == "WHIP_V" and spawn_timer >= 40:
                wx = random.randint(current_arena.left, current_arena.right - 20)
                projectiles.append({
                    "type": "WHIP",
                    "rect": pygame.Rect(wx, current_arena.top, 20, current_arena.height),
                    "timer": 45,
                    "state": "WARNING"
                })
                spawn_timer = 0

            elif current_attack == "SPIN" and spawn_timer >= 60:
                if not any(p.get("type") == "SPIN" for p in projectiles):
                    random_angle = random.uniform(0, 2 * math.pi)
                    random_speed = random.choice([0.05, -0.05])
                    
                    proj = {
                        "type": "SPIN",
                        "angle": random_angle,
                        "speed": random_speed, 
                        "length": 300,
                        "thickness": 12,
                        "warmup": 40,
                        "active_timer": 300
                    }
                    projectiles.append(proj)
                spawn_timer = 0

            elif current_attack == "SAFE_SPOT" and spawn_timer >= 75:
                safe_size = 60 
                whip_thickness = 30 
                spacing = 35 

                if safe_spot_is_horiz:
                    safe_x = random.randint(current_arena.left, current_arena.right - safe_size)
                    for y in range(current_arena.top, current_arena.bottom, spacing):
                        if safe_x > current_arena.left:
                            projectiles.append({"type": "WHIP", "rect": pygame.Rect(current_arena.left, y, safe_x - current_arena.left, whip_thickness), "timer": 45, "state": "WARNING"})
                        if safe_x + safe_size < current_arena.right:
                            projectiles.append({"type": "WHIP", "rect": pygame.Rect(safe_x + safe_size, y, current_arena.right - (safe_x + safe_size), whip_thickness), "timer": 45, "state": "WARNING"})
                else:
                    safe_y = random.randint(current_arena.top, current_arena.bottom - safe_size)
                    for x in range(current_arena.left, current_arena.right, spacing):
                        if safe_y > current_arena.top:
                            projectiles.append({"type": "WHIP", "rect": pygame.Rect(x, current_arena.top, whip_thickness, safe_y - current_arena.top), "timer": 45, "state": "WARNING"})
                        if safe_y + safe_size < current_arena.bottom:
                            projectiles.append({"type": "WHIP", "rect": pygame.Rect(x, safe_y + safe_size, whip_thickness, current_arena.bottom - (safe_y + safe_size)), "timer": 45, "state": "WARNING"})
                
                safe_spot_is_horiz = not safe_spot_is_horiz
                spawn_timer = 0
            if spin_hit_cooldown > 0:
                spin_hit_cooldown -= 1
            if objection_hit_cooldown > 0:
                objection_hit_cooldown -= 1

            for proj in reversed(projectiles):
                if proj["type"] == "NORMAL":
                    proj["rect"].x += proj["vx"]
                    proj["rect"].y += proj["vy"]
                    if proj["rect"].colliderect(player_rect):
                        player_hp -= proj["damage"]
                        g.php = max(0, player_hp)
                        player_flinch_timer = 15
                        if proj in projectiles: projectiles.remove(proj)
                    elif not current_arena.colliderect(proj["rect"]):
                        if proj in projectiles: projectiles.remove(proj)
                        
                elif proj["type"] == "PAPER":
                    proj["rect"].x += proj["speed_x"]
                    proj["rect"].y += proj["speed_y"]
                    if proj["rect"].colliderect(player_rect):
                        player_hp -= 5
                        g.php = max(0, player_hp)
                        player_flinch_timer = 15
                        if proj in projectiles: projectiles.remove(proj)
                    elif proj["rect"].top > current_arena.bottom:
                        if proj in projectiles: projectiles.remove(proj)

                elif proj["type"] == "OBJECTION":

                    if proj.get("warning", 0) > 0:

                        proj["warning"] -= 1

                    else:

                        proj["rect"].x += proj["vx"]
                        proj["rect"].y += proj["vy"]

                        if proj["rect"].colliderect(
                            player_rect):

                            if objection_hit_cooldown <= 0:

                                player_hp -= proj["damage"]

                                g.php = max(0, player_hp)

                                player_flinch_timer = 15

                                objection_hit_cooldown = 20

                            if proj in projectiles:
                                projectiles.remove(proj)

                            continue

         
                        outer_rect = current_arena.inflate(80, 80)

                        if not outer_rect.colliderect(
                            proj["rect"]):

                            if proj in projectiles:
                                projectiles.remove(proj)
                        
                elif proj["type"] == "WHIP":
                    proj["timer"] -= 1
                    if proj["timer"] <= 0:
                        if proj["state"] == "WARNING":
                            proj["state"] = "STRIKE"
                            proj["timer"] = 10 
                        elif proj["state"] == "STRIKE":
                            projectiles.remove(proj)
                    if proj["state"] == "STRIKE" and proj["rect"].colliderect(player_rect):
                        player_hp -= 5
                        g.php = max(0, player_hp)
                        player_flinch_timer = 15
                        projectiles.remove(proj) 
                        
                elif proj["type"] == "SPIN":
                    if proj["warmup"] > 0:
                        proj["warmup"] -= 1
                    else:
                        proj["active_timer"] -= 1
                        proj["angle"] += proj["speed"]
                        if proj["active_timer"] <= 0:
                            projectiles.remove(proj)
                            continue
                        
                        cx, cy = current_arena.center
                        hit = False
                        for i in range(0, int(proj["length"]), 10):
                            test_x = cx + math.cos(proj["angle"]) * i
                            test_y = cy + math.sin(proj["angle"]) * i
                            if player_rect.collidepoint(test_x, test_y):
                                hit = True
                                break
                        if (
                            hit
                            and spin_hit_cooldown <= 0):

                            player_hp -= 5

                            g.php = max(0, player_hp)

                            player_flinch_timer = 15


                            spin_hit_cooldown = 30

            if phase_timer <= 0:
                phase = "ATTACK"
                current_flavor = random.choice(flavor_texts)
                current_attack = None
                projectiles.clear()
                player_rect.center = arena_attack.center


        new_state = boss_state
        if player_hp <= 0:
            new_state = "victory"
        elif hit_effect_timer > 0:
            pass 
        elif phase == "DEFEND":
            current_arena = arena_defend
            if current_attack == "OBJECTION":
                new_state = "objection"
            elif current_attack == "WHIP_H":
                new_state = "whip_3"
            elif current_attack == "SPIN":
                new_state = "whip_2"
            elif current_attack == "WHIP_V":
                new_state = "whip_1"
            elif current_attack == "PAPER_RAIN":
                rain_stage_timer += 1
                if rain_stage == 1:
                    new_state = "crying"
                    if random.randint(1, 10) == 1:
                        px = random.randint(int(current_arena.left), int(current_arena.right) - 15)
                        py = int(current_arena.top) - 20
                        projectiles.append({
                        "type": "PAPER",
                        "rect": pygame.Rect(px, py, 15, 20),
                        "speed_x": random.uniform(-1.0, 1.0),
                        "speed_y": random.uniform(2.5, 4.5)
                        })
                    if rain_stage_timer >= 180:
                        rain_stage = 2
                        rain_stage_timer = 0
                        boss_frame_idx = 0.0
                elif rain_stage == 2:
                    new_state = "tears"
                    if rain_stage_timer >= 30:
                        rain_stage = 3
                        rain_stage_timer = 0
                        boss_frame_idx = 0.0
                elif rain_stage == 3:
                    new_state = "tears"
                    if int(boss_frame_idx) >= len(boss_anims["tears"]) - 1:
                        rain_stage = 4
                        rain_stage_timer = 0
                        boss_frame_idx = 0.0
                elif rain_stage == 4:
                    new_state = "crying"
                    if random.randint(1, 10) == 1:
                        px = random.randint(current_arena.left, current_arena.right)
                        py = int(current_arena.top) -20
                        projectiles.append({
                        "type": "PAPER",
                        "rect": pygame.Rect(px, py, 15, 20),
                        "speed_x": random.uniform(-1.0, 1.0),
                        "speed_y": random.uniform(2.5, 4.5)
                        })
                    if rain_stage_timer >= 180:
                        rain_stage = 0
                        rain_stage_timer = 0
                        phase_timer = 0 
        else:
            new_state = "default"
            rain_stage = 0

        if new_state != boss_state:
            boss_state = new_state
            boss_frame_idx = 0.0

    

        if boss_state == "default":


            boss_frame_idx = 0.0

        elif boss_state == "whip_3":

            boss_frame_idx += 0.05

        elif boss_state == "objection":

            boss_frame_idx += 0.10

        else:

            boss_frame_idx += 0.25


        if boss_frame_idx >= len(
            boss_anims[boss_state]):
            boss_frame_idx = 0.0



        screen.fill(BG_COLOR)
        
    
        pygame.draw.rect(screen, WHITE, current_arena, width=4)

        if phase == "ATTACK":
            if skillcheck_active:
                pygame.draw.line(screen, (255, 215, 0), (current_arena.centerx, current_arena.top), (current_arena.centerx, current_arena.bottom), 4)
                pygame.draw.line(screen, WHITE, (bar_x, current_arena.top + 5), (bar_x, current_arena.bottom - 5), 6)

               
                
            for btn in attack_test_buttons:
                is_hovered = btn["rect"].collidepoint(mouse_pos)
                btn_color = HOVER_COLOR if is_hovered else (40, 50, 75)
                pygame.draw.rect(screen, btn_color, btn["rect"], border_radius=6)
                pygame.draw.rect(screen, WHITE, btn["rect"], width=2, border_radius=6)
                txt = small_font.render(btn["name"], True, WHITE)
                screen.blit(txt, txt.get_rect(center=btn["rect"].center))

            for btn in buttons:
                is_hovered = btn["rect"].collidepoint(mouse_pos)
                color = HOVER_COLOR if is_hovered else WHITE
                pygame.draw.rect(screen, color, btn["rect"], width=2, border_radius=5)
                btn_txt = font.render(btn["name"], True, color)
                screen.blit(btn_txt, btn_txt.get_rect(center=btn["rect"].center))
                
            flavor_rnd = font.render(current_flavor, True, WHITE)
            screen.blit(flavor_rnd, flavor_rnd.get_rect(center=(current_arena.centerx, current_arena.centery)))
            
        if hit_effect_timer > 0:
            boss_rect = pygame.Rect(WIDTH//2 - 40, 120 - 40, 80, 80)
            pygame.draw.line(screen, WHITE, (boss_rect.left - 10, boss_rect.top - 10), (boss_rect.right + 10, boss_rect.bottom + 10), 6)
            pygame.draw.line(screen, (255, 100, 100), (boss_rect.left - 5, boss_rect.top), (boss_rect.right, boss_rect.bottom - 5), 3)
            
            dmg_color = HP_YELLOW if last_damage_dealt > 25 else WHITE
            dmg_txt = big_font.render(f"-{last_damage_dealt}", True, dmg_color)
            text_y = boss_rect.centery - (50 - hit_effect_timer) // 2
            screen.blit(dmg_txt, dmg_txt.get_rect(center=(boss_rect.centerx, text_y)))

        if phase == "DEFEND":
            for proj in projectiles:
                if proj["type"] == "NORMAL":
                    pygame.draw.rect(screen, proj["color"], proj["rect"])
                elif proj["type"] == "OBJECTION":

                    if proj.get("warning", 0) > 0:

                        pygame.draw.rect(
                            screen,
                            WHIP_WARNING,
                            proj["rect"],
                            width=3)

                    else:

                        pygame.draw.rect(
                            screen,
                            proj["color"],
                            proj["rect"])
                elif proj["type"] == "PAPER":
                    pygame.draw.rect(screen, PAPER_COLOR, proj["rect"])
                elif proj["type"] == "WHIP":
                    if proj["state"] == "WARNING":
                        pygame.draw.rect(screen, WHIP_WARNING, proj["rect"], width=2)
                    elif proj["state"] == "STRIKE":
                        pygame.draw.rect(screen, WHIP_STRIKE, proj["rect"])
                elif proj["type"] == "SPIN":
                    cx, cy = current_arena.center
                    end_x = cx + math.cos(proj["angle"]) * proj["length"]
                    end_y = cy + math.sin(proj["angle"]) * proj["length"]
                    color = WHIP_WARNING if proj["warmup"] > 0 else WHIP_STRIKE
                    pygame.draw.line(screen, color, (cx, cy), (end_x, end_y), proj["thickness"])
                    pygame.draw.circle(screen, BOSS_COLOR, (cx, cy), 10)

        pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
        draw_player_stats(screen, player_hp, player_max_hp, boss_hp, boss_max_hp, boss_state, boss_frame_idx, boss_flinch_timer)
        
        phoenix_x = 20
        phoenix_y = HEIGHT - 185

        player_is_hit = (
            player_flinch_timer > 0)

        if player_is_hit:

            player_flinch_timer -= 1

            phoenix_x += random.randint(-5, 5)

            phoenix_y += random.randint(-5, 5)

            pygame.draw.rect(
                screen,
                HP_RED,
                current_arena,
                width=5)

        if is_franziska:

            if (
                player_is_hit
                and img_franziska_damage
                is not None):

                current_player_img = (
                    img_franziska_damage)

            elif (
                phoenix_action_timer > 0
                and img_franziska_special
                is not None):

                current_player_img = (
                    img_franziska_special)

            else:

                current_player_img = (
                    img_franziska_default)

                if current_player_img is None:

                    current_player_img = (
                        img_phoenix_idle)

        else:

            if player_is_hit:

                current_player_img = (
                    img_phoenix_damage)

            elif phoenix_action_timer > 0:

                current_player_img = (
                    img_phoenix_attack)

            else:

                current_player_img = (
                    img_phoenix_idle)


        screen.blit(
            current_player_img,
            (
                phoenix_x,
                phoenix_y)
        )

        controls_txt = small_font.render(
            f"[{pygame.key.name(controls['LEFT']).upper()}] Left   "
            f"[{pygame.key.name(controls['RIGHT']).upper()}] Right   "
            f"[{pygame.key.name(controls['UP']).upper()}] Up   "
            f"[{pygame.key.name(controls['DOWN']).upper()}] Down   "
            f"[{pygame.key.name(controls['ACTION']).upper()}] Hit",
            True,
            WHITE)

        screen.blit(
            controls_txt,
            controls_txt.get_rect(
                center=(
                    WIDTH // 2,
                    HEIGHT - 12)
            ))    
        draw_minigame_settings_button(screen, g)

        present_minigame(display, screen)