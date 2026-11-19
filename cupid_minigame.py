import pygame
import random
import sys
import os
from asset_utils import asset_path
from config import CARDS, C_COMMON, C_RARE, C_EPIC, C_LEGENDARY,GLOBAL_CONTROLS
from minigame_view import (
    create_minigame_view,
    present_minigame,
    draw_minigame_settings_button,
    minigame_settings_requested,
    run_minigame_settings)

from asset_utils import (
    load_franziska_sprite)

def run_maker(screen, g):
    ASSET_DIR = asset_path(
        "maker")
    
    
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 700
    display, screen = create_minigame_view(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    TARGET_WIDTH = 80
    TARGET_HEIGHT = 110
    target_speed = 4

    THEMES = {
        "DARK": {
            "BG": (35, 35, 40), "PANEL": (20, 20, 25), "TEXT": (240, 240, 240),
            "PLAYER": (230, 50, 80), "BULLET": (255, 60, 60),
        }
    }
    theme = THEMES["DARK"]
    controls = GLOBAL_CONTROLS["HaremMaker"]
    CARD_ID_COLORS = [
        (70, 150, 255),  
        (70, 210, 120),   
        (175, 100, 255),  
    ]    
    def load_snd(filename):

        path = os.path.join(ASSET_DIR, filename)

        if os.path.exists(path):

            try:

                return pygame.mixer.Sound(
                    path)

            except Exception as exc:

                print(
                    "Maker sound load failed:",
                    path,
                    exc)

        return None
        
    sound_shoot = load_snd("freesound_community-shoot02wav-14562.mp3")
    sound_hit_hero = load_snd("universfield-cinematic-impact-hit-352702.mp3")
    sound_hit_hecate = load_snd("universfield-punch-impact-hit-567196.mp3")
    sound_win = load_snd("freesound_community-success-fanfare-trumpets-6185.mp3")
    sound_lose = load_snd("tuomas_data-wrong-answer-21-199825.mp3")
    
    if sound_shoot: sound_shoot.set_volume(0.5)
    if sound_hit_hero: sound_hit_hero.set_volume(0.6)
    if sound_hit_hecate: sound_hit_hecate.set_volume(0.6)
    def get_card_color(card_name):
        rarity = CARDS.get(card_name, {}).get("rarity", "common")
        if rarity == "common": return C_COMMON
        elif rarity == "rare": return C_RARE
        elif rarity == "epic": return C_EPIC
        elif rarity == "legendary": return C_LEGENDARY
        return C_COMMON

    active_cards = g.reward_pool
    pieces_needed = (
        5
        if "Arcade Token" in getattr(g, "relics", [])
        else 6)
    card_progress = [0, 0, 0]
    completed_cards = set()

    hero_spawn_pool = {
    idx: pieces_needed
    for idx in range(3)
    } 

    player_width, player_height = 60, 60
    is_franziska = (
        str(
            getattr(g, "char_class", "BRUISER")
        ).upper()
        == "ASSASSIN")

    franziska_default_img = (
        load_franziska_sprite(
            "default",
            (90, 90))
        if is_franziska
        else None)

    franziska_damage_img = (
        load_franziska_sprite(
            "damage",
            (90, 90))
        if is_franziska
        else None)

    franziska_special_img = (
        load_franziska_sprite(
            "special",
            (90, 90))
        if is_franziska
        else None)

    player_damage_timer = 0.0
    player_img = None

    player_img_path = os.path.join(ASSET_DIR, "img_phoneix.png")

    if os.path.exists(
        player_img_path):

        try:

            player_img = pygame.image.load(
                player_img_path).convert_alpha()

            player_img = (
                pygame.transform.smoothscale(
                    player_img,
                    (
                        player_width,
                        player_height)
                ))

        except Exception as exc:

            print("Maker Phoenix load failed:", exc)
    font = pygame.font.SysFont("arial", 22, bold=True)
    big_font = pygame.font.SysFont("arial", 54, bold=True)

    targets = []
    bullets = []

    player_x = (SCREEN_WIDTH // 2) - (player_width // 2)
    player_y = 510
    player_speed = 10
    bullet_speed = 12

    clock = pygame.time.Clock()
    last_shot_time = 0
    shoot_cooldown = 800

    start_time = pygame.time.get_ticks()
    time_left = 30 
    state = "GAMEPLAY"
    won_card = None
    win_timer = 2.0

    def get_next_target():
        available_choices = [idx for idx, left in hero_spawn_pool.items() if left > 0]
        if not available_choices:
            return {"type": "hecate"}

        choices_with_hecate = available_choices + ["hecate"]
        weights = [1] * len(available_choices) + [3] 

        selected = random.choices(choices_with_hecate, weights=weights, k=1)[0]

        if selected == "hecate":
            return {"type": "hecate"}
        else:
            hero_spawn_pool[selected] -= 1
            return {"type": selected} 

    for i in range(5):
        rect = pygame.Rect(SCREEN_WIDTH + (i * TARGET_WIDTH), 80, TARGET_WIDTH, TARGET_HEIGHT)
        target_info = get_next_target()
        targets.append({"rect": rect, "type": target_info["type"]})

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        if player_damage_timer > 0:

            player_damage_timer = max(0.0, player_damage_timer - dt)
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
                        g)
                )

                start_time += paused_ms

                if last_shot_time > 0:
                    last_shot_time += paused_ms

                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and state == "GAMEPLAY":
                if event.key == controls["SHOOT"]:
                    current_time = pygame.time.get_ticks()
                    if current_time - last_shot_time > shoot_cooldown:
                        new_bullet = pygame.Rect(player_x + player_width // 2 - 4, player_y, 8, 15)
                        bullets.append(new_bullet)
                        last_shot_time = current_time
                        if sound_shoot: sound_shoot.play()

        if state == "GAMEPLAY":
            elapsed_seconds = (pygame.time.get_ticks() - start_time) // 1000
            time_left = max(0, 30 - elapsed_seconds)

            if time_left <= 0:
                state = "TIMEOUT"

            for target in targets:
                target["rect"].x -= target_speed

            if targets and targets[0]["rect"].right < 0:
                missed = targets.pop(0)
                if missed["type"] != "hecate":
                    hero_spawn_pool[missed["type"]] += 1

            if targets:
                current_x = targets[0]["rect"].x
                for target in targets:
                    target["rect"].x = current_x
                    current_x += TARGET_WIDTH

            last_right = targets[-1]["rect"].right if targets else 0
            while last_right < SCREEN_WIDTH:
                new_rect = pygame.Rect(last_right, 80, TARGET_WIDTH, TARGET_HEIGHT)
                target_info = get_next_target()
                targets.append({"rect": new_rect, "type": target_info["type"]})
                last_right += TARGET_WIDTH

            keys = pygame.key.get_pressed()
            if (
                keys[controls["LEFT"]]
                and player_x > 0):
                player_x -= player_speed

            if (
                keys[controls["RIGHT"]]
                and player_x < SCREEN_WIDTH - player_width):
                player_x += player_speed

            for bullet in bullets[:]:
                bullet_hit = False
                for target in targets[:]:
                    if bullet.colliderect(target["rect"]):
                        hit_type = target["type"]
                        targets.remove(target)
                        bullet_hit = True

                        if hit_type != "hecate":
                            if sound_hit_hero: sound_hit_hero.play()
                            idx = hit_type
                            card_progress[idx] += 1
                            if (card_progress[idx] >= pieces_needed and idx not in completed_cards):
                                completed_cards.add(idx)
                                
                        elif hit_type == "hecate":
                            if sound_hit_hecate: sound_hit_hecate.play()
                            g.php -= 5
                            player_damage_timer = 0.6
                            if g.php <= 0:
                                g.php = 0
                                
                                return "DEAD"

                            possible_victims = [idx for idx, pts in enumerate(card_progress) if pts > 0 and idx not in completed_cards]
                            if possible_victims:
                                victim = random.choice(possible_victims)
                                card_progress[victim] -= 1
                                hero_spawn_pool[victim] += 1
                        break

                if bullet_hit and bullet in bullets:
                    bullets.remove(bullet)

            for bullet in bullets[:]:
                bullet.y -= bullet_speed
                if bullet.y < 0:
                    bullets.remove(bullet)

        # РИСУВАНЕ 
        screen.fill(theme["BG"])

        for target in targets:

            if target["type"] == "hecate":

                pygame.draw.rect(
                    screen,
                    (150, 30, 30),
                    target["rect"],
                    border_radius=5)

                lbl = font.render(
                    "BOMB",
                    True,
                    (255, 255, 255))

            else:

                card_idx = target["type"]

                id_color = CARD_ID_COLORS[
                    card_idx % len(CARD_ID_COLORS)
                ]

                pygame.draw.rect(
                    screen,
                    id_color,
                    target["rect"],
                    border_radius=5)

                lbl = big_font.render(
                    str(card_idx + 1),
                    True,
                    (255, 255, 255))

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                target["rect"],
                2,
                border_radius=5)

            screen.blit(
                lbl,
                lbl.get_rect(
                    center=target["rect"].center)
            )
            # PLAYER SPRITE
            if is_franziska:

                full_victory = (
                    state == "TIMEOUT"
                    and len(completed_cards)
                    == len(active_cards))

                # Победа
                if (
                    full_victory
                    and franziska_special_img
                    is not None):

                    current_player_img = (
                        franziska_special_img)

                # Получила е damage
                elif (
                    player_damage_timer > 0
                    and franziska_damage_img
                    is not None):

                    current_player_img = (
                        franziska_damage_img)

                # Нормално
                else:

                    current_player_img = (
                        franziska_default_img)


                if current_player_img is not None:

                    player_sprite_rect = (
                        current_player_img.get_rect(
                            midbottom=(
                                player_x
                                + player_width // 2,
                                player_y
                                + player_height)
                        ))

                    screen.blit(current_player_img, player_sprite_rect)
            # PHOENIX
            elif player_img is not None:

                screen.blit(
                    player_img,
                    (
                        player_x,
                        player_y)
                )
            # FALLBACK
            else:

                pygame.draw.rect(
                    screen,
                    theme["PLAYER"],
                    (
                        player_x,
                        player_y,
                        player_width,
                        player_height),
                    border_radius=10)       

        for bullet in bullets:
            pygame.draw.rect(screen, theme["BULLET"], bullet, border_radius=3)

        pygame.draw.rect(screen, theme["PANEL"], (0, 590, SCREEN_WIDTH, 110))
        
        timer_color = (255, 70, 70) if time_left <= 10 else theme["TEXT"]
        screen.blit(font.render(f"Time: {time_left}s", True, timer_color), (20, 610))
        screen.blit(font.render(f"HP: {g.php}/{g.pmx}", True, (255, 100, 100)), (20, 640))

        x_offsets = [150, 365, 580]

        for idx in range(3):

            x = x_offsets[idx]

            c_name = active_cards[idx]
            c_prog = card_progress[idx]

            id_color = CARD_ID_COLORS[
                idx % len(CARD_ID_COLORS)
            ]
            # NUMBER BOX
            number_rect = pygame.Rect(x, 610, 34, 34)

            pygame.draw.rect(
                screen,
                id_color,
                number_rect,
                border_radius=5)

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                number_rect,
                2,
                border_radius=5)

            num_txt = font.render(
                str(idx + 1),
                True,
                (255, 255, 255))

            screen.blit(
                num_txt,
                num_txt.get_rect(
                    center=number_rect.center)
            )
            # FULL CARD NAME i PROGRESS
            completed = (
                c_prog >= pieces_needed)

            text_col = (
                (50, 220, 50)
                if completed
                else theme["TEXT"])

            txt = font.render(
                f"{c_name} {c_prog}/{pieces_needed}",
                True,
                text_col)

            screen.blit(
                txt,
                (
                    number_rect.right + 6,
                    616)
            )

        if state == "TIMEOUT":
            if win_timer == 2.0 and sound_lose: sound_lose.play()
            lt = big_font.render("TIME OUT!", True, (255, 70, 70))
            screen.blit(lt, lt.get_rect(center=(SCREEN_WIDTH // 2, 220)))
            win_timer -= dt
            if win_timer <= 0:
               
                won_cards = [active_cards[i] for i in sorted(completed_cards)]
              
                return won_cards

        controls_txt = font.render(
            f"[{pygame.key.name(controls['LEFT']).upper()}] Left   "
            f"[{pygame.key.name(controls['RIGHT']).upper()}] Right   "
            f"[{pygame.key.name(controls['SHOOT']).upper()}] Shoot",
            True,
            (170, 170, 190))

        screen.blit(
            controls_txt,
            controls_txt.get_rect(
                center=(SCREEN_WIDTH // 2, 675))
        )
        draw_minigame_settings_button(screen, g)

        present_minigame(display, screen)

    return None