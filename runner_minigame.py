import pygame
import random
import sys

from config import CARDS, C_COMMON, C_RARE, C_EPIC, C_LEGENDARY, GLOBAL_CONTROLS
from minigame_view import (
    create_minigame_view,
    present_minigame,
    draw_minigame_settings_button,
    minigame_settings_requested,
    run_minigame_settings)
import os

from asset_utils import (
    asset_path,
    load_franziska_sprite)

SPAWN_ROCK_EVENT = pygame.USEREVENT + 1
SPAWN_PIECE_EVENT = pygame.USEREVENT + 2

HORIZON_Y = 50
VANISHING_X = 400
ROAD_TOP_WIDTH = 60
ROAD_BOTTOM_WIDTH = 700
PLAY_AREA_HEIGHT = 450
SCREEN_WIDTH=800
SCREEN_HEIGHT= 550

def get_lane_x(lane_index, y_pos):

    progress = (y_pos - HORIZON_Y) / (PLAY_AREA_HEIGHT - HORIZON_Y)
    current_road_width = ROAD_TOP_WIDTH + progress * (ROAD_BOTTOM_WIDTH - ROAD_TOP_WIDTH)
    left_x = VANISHING_X - (current_road_width / 2)
    lane_width = current_road_width / 3

    return left_x + lane_width * lane_index + (lane_width / 2)

def calculate_speed(y_pos):
    progress = (y_pos - HORIZON_Y) / (PLAY_AREA_HEIGHT - HORIZON_Y)
    progress = max(0.0, min(1.0, progress))
    return 1.2 + (progress ** 1.5) * 8.0

def run_runner(screen, g):
    text_color = (240, 240, 240)
    ASSET_DIR = asset_path(
        "runner")
    display, screen = create_minigame_view(
        SCREEN_WIDTH,
        SCREEN_HEIGHT)


    def load_image(
        filename,
        size,
        fallback_color):

        path = os.path.join(
            ASSET_DIR,
            filename)

        if os.path.exists(path):

            try:

                img = pygame.image.load(
                    path).convert_alpha()

                return pygame.transform.smoothscale(
                    img,
                    size)

            except Exception as exc:

                print(
                    "Runner image load failed:",
                    path,
                    exc)

        surf = pygame.Surface(
            size,
            pygame.SRCALPHA)

        surf.fill(
            fallback_color)

        return surf


    def load_sound(
        filename,
        volume=1.0):

        path = os.path.join(
            ASSET_DIR,
            filename)

        if not os.path.exists(path):
            return None

        try:

            snd = pygame.mixer.Sound(
                path)

            snd.set_volume(
                volume
                * getattr(g, "sfx_volume", 1.0)
            )

            return snd

        except Exception as exc:

            print(
                "Runner sound load failed:",
                path,
                exc)

            return None

    player_img = load_image(
        "img_phoneix.png",
        (110, 110),
        (255, 200, 0))

    player_damage_img = load_image(
        "img_damage.png",
        (110, 110),
        (255, 80, 80))
    is_franziska = (
        str(
            getattr(g, "char_class", "BRUISER")
        ).upper()
        == "ASSASSIN")

    franziska_default_img = (
        load_franziska_sprite(
            "default",
            (110, 110))
        if is_franziska
        else None)

    franziska_damage_img = (
        load_franziska_sprite(
            "damage",
            (110, 110))
        if is_franziska
        else None)

    franziska_special_img = (
        load_franziska_sprite(
            "special",
            (110, 110))
        if is_franziska
        else None)
    sound_hit = load_sound(
        "universfield-punch-140236.mp3",
        0.6)

    sound_collect = load_sound(
        "driken5482-retro-coin-3-236679.mp3",
        0.6)

    sound_lane = load_sound(
        "freesound_community-cartoon-jump-6462.mp3",
        0.6)

    sound_lose = load_sound(
        "tuomas_data-wrong-answer-21-199825.mp3",
        0.8)
    clock = pygame.time.Clock()
    ASSET_DIR = asset_path(
        "runner")
    font = pygame.font.SysFont("arial", 20, bold=True)
    big_font = pygame.font.SysFont("arial", 40, bold=True)
    controls = GLOBAL_CONTROLS["HaremRunner"]
    bg_color = (35, 35, 40)
    ground_color = (25, 25, 30)
    lane_bg = (45, 45, 55)
    lane_border = (100, 100, 130)
    panel_color = (20, 20, 25)
    text_color = (240, 240, 240)
    CARD_ID_COLORS = [
        (70, 150, 255),   
        (70, 210, 120),   
        (175, 100, 255),  
    ]

    def get_card_color(card_name):
        rarity = CARDS.get(card_name, {}).get("rarity", "common")
        if rarity == "common": return C_COMMON
        elif rarity == "rare": return C_RARE
        elif rarity == "epic": return C_EPIC
        elif rarity == "legendary": return C_LEGENDARY
        return C_COMMON

    def update_runner_sound_volume():

        sfx = getattr(g, "sfx_volume", 1.0)

        if sound_hit:
            sound_hit.set_volume(
                0.6 * sfx)

        if sound_collect:
            sound_collect.set_volume(
                0.6 * sfx)

        if sound_lane:
            sound_lane.set_volume(
                0.6 * sfx)

        if sound_lose:
            sound_lose.set_volume( 
                0.8 * sfx)
    
    current_lane = 1
    PLAYER_Y = 400
    invulnerable_timer = 0.0
    
    reward_cards = g.reward_pool
    if getattr(g, "tutorial_active", False):
        pieces_needed = 5
    else:
        pieces_needed = (
            9
            if "Arcade Token" in getattr(g, "relics", [])
            else 10)
    card_progress = [
        0 for _ in reward_cards
    ]
    completed_cards = set()

    rocks = []
    card_pieces = []
    
    pygame.time.set_timer(SPAWN_ROCK_EVENT, 700)
    pygame.time.set_timer(SPAWN_PIECE_EVENT, 600)
    
    state = "PLAYING"
    won_card = None
    win_timer = 2.0
    
    start_ticks = pygame.time.get_ticks()
    time_left = 30

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        if invulnerable_timer > 0:
            invulnerable_timer -= dt

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
                update_runner_sound_volume()

                start_ticks += paused_ms

                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if state == "PLAYING" and event.type == pygame.KEYDOWN:
                if (
                    event.key == controls["LEFT"]
                    and current_lane > 0):
                    current_lane -= 1
                    if sound_lane:
                        sound_lane.play()

                elif (
                    event.key == controls["RIGHT"]
                    and current_lane < 2):
                    current_lane += 1
                    if sound_lane:
                        sound_lane.play()

            if state == "PLAYING":
                if event.type == SPAWN_ROCK_EVENT:
                    rock_lane = random.choice([0, 1, 2])
                    rocks.append({"lane": rock_lane, "y": HORIZON_Y})

                if event.type == SPAWN_PIECE_EVENT:
                    available_indices = [i for i in range(len(reward_cards)) if card_progress[i] < pieces_needed]
                    if available_indices:
                        piece_lane = random.choice([0, 1, 2])
                        card_idx = random.choice(available_indices)
                        card_pieces.append({"lane": piece_lane, "y": HORIZON_Y, "card_idx": card_idx})

        if state == "PLAYING":
            seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
            time_left = max(0, 30 - seconds_passed)
            
            if time_left <= 0:
                state = "TIMEOUT"

            for rock in rocks[:]:
                rock["y"] += calculate_speed(rock["y"])
                if rock["y"] > PLAY_AREA_HEIGHT + 20:
                    rocks.remove(rock)
                    continue

                if abs(rock["y"] - PLAYER_Y) < 35 and rock["lane"] == current_lane:
                    rocks.remove(rock)
                    if invulnerable_timer <= 0:
                        invulnerable_timer = 1.0
                        if sound_hit:
                            sound_hit.play()
                        g.php -= 5 
                        if g.php <= 0:
                            g.php = 0
                            pygame.time.set_timer(SPAWN_ROCK_EVENT, 0)
                            pygame.time.set_timer(SPAWN_PIECE_EVENT, 0)
                            
                            return "DEAD"

            for piece in card_pieces[:]:
                piece["y"] += calculate_speed(piece["y"])

                if piece["y"] > PLAY_AREA_HEIGHT + 20:
                    card_pieces.remove(piece)
                    continue

                if abs(piece["y"] - PLAYER_Y) < 35 and piece["lane"] == current_lane:
                    idx = piece["card_idx"]

                    card_progress[idx] = min(pieces_needed,card_progress[idx]+1)
                    if sound_collect:
                        sound_collect.play()
                    card_pieces.remove(piece)

                    if (
                        card_progress[idx] >= pieces_needed
                        and idx not in completed_cards):
                        completed_cards.add(idx)
                        if len(completed_cards) == len(reward_cards):
                            state = "TIMEOUT"
                            win_timer = 0.6
        # РИСУВАНЕ
        screen.fill(bg_color)

        pygame.draw.rect(screen, ground_color, (0, HORIZON_Y, 800, PLAY_AREA_HEIGHT - HORIZON_Y))
        top_left = (VANISHING_X - ROAD_TOP_WIDTH // 2, HORIZON_Y)
        top_right = (VANISHING_X + ROAD_TOP_WIDTH // 2, HORIZON_Y)
        bottom_right = (VANISHING_X + ROAD_BOTTOM_WIDTH // 2, PLAY_AREA_HEIGHT)
        bottom_left = (VANISHING_X - ROAD_BOTTOM_WIDTH // 2, PLAY_AREA_HEIGHT)
        pygame.draw.polygon(screen, lane_bg, [top_left, top_right, bottom_right, bottom_left])

        for i in range(1, 3):
            line_top_x = (VANISHING_X - ROAD_TOP_WIDTH // 2) + (ROAD_TOP_WIDTH / 3) * i
            line_bottom_x = (VANISHING_X - ROAD_BOTTOM_WIDTH // 2) + (ROAD_BOTTOM_WIDTH / 3) * i
            pygame.draw.line(screen, lane_border, (line_top_x, HORIZON_Y), (line_bottom_x, PLAY_AREA_HEIGHT), 2)

        for rock in rocks:
            if rock["y"] >= HORIZON_Y:
                rock_x = get_lane_x(rock["lane"], rock["y"])
                progress = (rock["y"] - HORIZON_Y) / (PLAY_AREA_HEIGHT - HORIZON_Y)
                radius = max(6, int(6 + progress * 28))
                pygame.draw.circle(screen, (230, 30, 30), (int(rock_x), int(rock["y"])), radius)

        for piece in card_pieces:

            if piece["y"] >= HORIZON_Y:

                piece_x = get_lane_x(
                    piece["lane"],
                    piece["y"])

                progress = (
                    piece["y"] - HORIZON_Y) / (
                    PLAY_AREA_HEIGHT - HORIZON_Y)

                size = max(
                    14,
                    int(14 + progress * 32))

                rect = pygame.Rect(0, 0, size, size + 8)

                rect.center = (
                    int(piece_x),
                    int(piece["y"]))

                card_idx = piece["card_idx"]

                id_color = CARD_ID_COLORS[
                    card_idx % len(CARD_ID_COLORS)
                ]

                pygame.draw.rect(
                    screen,
                    id_color,
                    rect,
                    border_radius=max(
                        2,
                        size // 6)
                )

                pygame.draw.rect(
                    screen,
                    (245, 245, 245),
                    rect,
                    2,
                    border_radius=max(
                        2,
                        size // 6)
                )
                number_size = max(
                    12,
                    int(size * 0.60))

                number_font = pygame.font.SysFont(
                    "arial",
                    number_size,
                    bold=True)

                number_surf = number_font.render(
                    str(card_idx + 1),
                    True,
                    (255, 255, 255))

                screen.blit(
                    number_surf,
                    number_surf.get_rect(
                        center=rect.center)
                )

        if state != "GAMEOVER" and (invulnerable_timer <= 0 or int(invulnerable_timer * 20) % 2 == 0):
            player_x = get_lane_x(current_lane, PLAYER_Y)
            full_victory = (
                state == "TIMEOUT"
                and len(completed_cards)
                == len(reward_cards))

            if is_franziska:

                if (
                    full_victory
                    and franziska_special_img
                    is not None):

                    current_player_img = (
                        franziska_special_img)

                elif (
                    invulnerable_timer > 0
                    and franziska_damage_img
                    is not None):

                    current_player_img = (
                        franziska_damage_img)

                else:

                    current_player_img = (
                        franziska_default_img
                        or player_img)

            else:

                current_player_img = (
                    player_damage_img
                    if invulnerable_timer > 0
                    else player_img)

            player_rect = current_player_img.get_rect(
                center=(
                    int(player_x),
                    int(PLAYER_Y))
            )

            screen.blit(
                current_player_img,
                player_rect)

        pygame.draw.rect(screen, panel_color, (0, 480, 800, 80))
        
        hp_txt = font.render(f"HP: {g.php}/{g.pmx}", True, (255, 100, 100))
        screen.blit(hp_txt, (20, 490))
        
        timer_col = (255, 80, 80) if time_left <= 10 else text_color
        screen.blit(font.render(f"Time: {time_left}s", True, timer_col), (20, 520))
        
        for i in range(len(reward_cards)):

            c_name = reward_cards[i]
            c_prog = card_progress[i]

            id_color = CARD_ID_COLORS[
                i % len(CARD_ID_COLORS)
            ]
            # NUMBER BOX
            number_rect = pygame.Rect(145 + i * 215, 492, 30, 30)

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
                    center=number_rect.center)
            )
            # FULL CARD NAME i PROGRESS
            completed = (
                c_prog >= pieces_needed)

            name_color = (
                (80, 230, 100)
                if completed
                else text_color)

            label = font.render(
                f"{c_name} {c_prog}/{pieces_needed}",
                True,
                name_color)

            screen.blit(
                label,
                (
                    number_rect.right + 7,
                    496)
            )
        if state == "TIMEOUT":

            if len(completed_cards) == len(reward_cards):
                message = "ALL CARDS COLLECTED!"
                message_color = (50, 220, 50)
            else:
                message = "TIME OUT!"
                message_color = (255, 70, 70)

            wt = big_font.render(
                message,
                True,
                message_color)

            screen.blit(
                wt,
                wt.get_rect(center=(400, 220)))

            win_timer -= dt

            if win_timer <= 0:
                pygame.time.set_timer(
                    SPAWN_ROCK_EVENT,
                    0)

                pygame.time.set_timer(
                    SPAWN_PIECE_EVENT,
                    0)

               

                won_cards = [
                    reward_cards[i]
                    for i in sorted(completed_cards)
                ]

                return won_cards
        controls_txt = font.render(
            f"[{pygame.key.name(controls['LEFT']).upper()}] Left    "
            f"[{pygame.key.name(controls['RIGHT']).upper()}] Right",
            True,
            (170, 170, 190))

        screen.blit(
            controls_txt,
            controls_txt.get_rect(
                center=(400, 540))
        )
        draw_minigame_settings_button(
            screen,
            g)

        present_minigame(
            display,
            screen)
    return None