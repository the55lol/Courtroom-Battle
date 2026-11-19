import pygame
import random
import math
import os
from config import GLOBAL_CONTROLS
from minigame_view import (
    create_minigame_view,
    present_minigame,
    draw_minigame_settings_button,
    minigame_settings_requested,
    run_minigame_settings
)
from asset_utils import (
    asset_path,
    load_franziska_sprite
)

def run_boxing_boss(screen, g):
 
    old_width, old_height = screen.get_size()
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    display, screen = create_minigame_view(
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )
    
    clock = pygame.time.Clock()
    FPS = 60
    ASSET_DIR = asset_path(
        "boxingboss"
    )

    DIFFICULTIES = {
        "HARD": {"damage": 15, "name": "HARD"}
    }
    current_difficulty = "HARD"

   
    THEMES = {
        "DARK": {
            "BG": (35, 35, 40),
            "PANEL": (20, 20, 25),
            "TEXT": (240, 240, 240),
            "TITLE": (255, 80, 120),
            "BTN_MAIN": (180, 40, 80),
            "BTN_HOVER": (220, 60, 100),
            "BORDER": (80, 80, 100),
        }
    }
    current_theme = "DARK"
    theme = THEMES[current_theme]

    # Шрифтове 
    font_dmg = pygame.font.SysFont("Impact", 40, bold=True)
    font_ui = pygame.font.SysFont("Arial", 20, bold=True)
    small_font = pygame.font.SysFont("arial", 16, bold=True)
    big_font = pygame.font.SysFont("arial", 54, bold=True)
    huge_font = pygame.font.SysFont("Impact", 120, bold=True)

    # Звуци 
    def load_sound(
        filename,
        volume=1.0
    ):

        full_path = os.path.join(
            ASSET_DIR,
            filename
        )

        if os.path.exists(
            full_path
        ):

            try:

                sound = pygame.mixer.Sound(
                    full_path
                )

                sound.set_volume(
                    volume
                )

                return sound

            except Exception as exc:

                print(
                    "Could not load boxing sound:",
                    full_path,
                    exc
                )

        return None

    sound_defeat        = load_sound("defeat.wav", 0.33)
    sound_victory       = load_sound("victory.wav", 0.33)
    sound_objection     = load_sound("objection_phoenix.wav", 0.33)
    sound_deskslam      = load_sound("sfx-deskslam.wav", 0.33)
    sound_realization   = load_sound("sfx-realization.wav", 0.33)
    sound_swing         = load_sound("sfx-swing.wav", 0.33)
    sound_damage2       = load_sound("sfx-damage2.wav", 0.33)
    sound_block_boss    = load_sound("block_boss.wav", 0.33)
    sound_stab2         = load_sound("sfx-stab2.wav", 0.33) 
    sound_damage1       = load_sound("sfx-damage1.wav", 0.33) 
    sound_stab          = load_sound("sfx-stab.wav", 0.33) 
    sound_bell          = load_sound("boxing_bell.wav", 0.5)
    sound_block_phoenix = load_sound("block_phoenix.wav", 1.0) 

    TARGET_BOSS_HEIGHT_CORR = 250
    TARGET_PLAYER_HEIGHT = 200

    def load_proportional_image(
        filename,
        target_height,
        placeholder_color
    ):

        full_path = os.path.join(
            ASSET_DIR,
            filename
        )

        if os.path.exists(
            full_path
        ):

            try:

                image = pygame.image.load(
                    full_path
                ).convert_alpha()

                orig_w, orig_h = (
                    image.get_size()
                )

                target_w = int(
                    orig_w
                    * (
                        target_height
                        / orig_h
                    )
                )

                return pygame.transform.smoothscale(
                    image,
                    (
                        target_w,
                        target_height
                    )
                )

            except pygame.error as exc:

                print(
                    "Could not load boxing image:",
                    full_path,
                    exc
                )

        # Fallbac
        surf = pygame.Surface(
            (
                150,
                target_height
            )
        )

        surf.fill(
            placeholder_color
        )

        return surf

    def load_defeat_frames(
        prefix,
        height
    ):

        frames = []
        i = 1

        while True:

            filename = (
                f"{prefix}_{i}.png"
            )

            full_path = os.path.join(
                ASSET_DIR,
                filename
            )

            if os.path.exists(
                full_path
            ):

                frames.append(
                    load_proportional_image(
                        filename,
                        height,
                        (
                            200,
                            200,
                            200
                        )
                    )
                )

                i += 1

            else:

                break

        if not frames:

            frames.append(
                load_proportional_image(
                    "placeholder",
                    height,
                    (
                        100,
                        100,
                        100
                    )
                )
            )

        return frames

    img_godot_normal = load_proportional_image("img_godot_normal.png", TARGET_BOSS_HEIGHT_CORR, (200, 50, 50))
    img_godot_face = load_proportional_image("img_godot_face.png", TARGET_BOSS_HEIGHT_CORR, (255, 150, 150))
    img_godot_stomach = load_proportional_image("img_godot_stomach.png", TARGET_BOSS_HEIGHT_CORR, (150, 50, 50))
    godot_defeat_frames = load_defeat_frames("img_godot_defeat", TARGET_BOSS_HEIGHT_CORR)

    img_phoenix_normal = load_proportional_image("img_phoenix_normal.png", TARGET_PLAYER_HEIGHT, (50, 100, 180))
    img_phoenix_down = load_proportional_image("img_phoenix_down.png", TARGET_PLAYER_HEIGHT, (80, 80, 120))
    img_phoenix_hit = load_proportional_image("img_phoenix_hit.png", TARGET_PLAYER_HEIGHT, (150, 80, 80))
    img_phoenix_lose = load_proportional_image("img_phoenix_lose.png", TARGET_PLAYER_HEIGHT, (50, 50, 50))
    is_franziska = (
        str(
            getattr(
                g,
                "char_class",
                "BRUISER"
            )
        ).upper()
        == "ASSASSIN"
    )

    img_franziska_normal = (
        load_franziska_sprite(
            "default",
            (
                TARGET_PLAYER_HEIGHT,
                TARGET_PLAYER_HEIGHT
            )
        )
        if is_franziska
        else None
    )

    img_franziska_damage = (
        load_franziska_sprite(
            "damage",
            (
                TARGET_PLAYER_HEIGHT,
                TARGET_PLAYER_HEIGHT
            )
        )
        if is_franziska
        else None
    )

    img_franziska_special = (
        load_franziska_sprite(
            "special",
            (
                TARGET_PLAYER_HEIGHT,
                TARGET_PLAYER_HEIGHT
            )
        )
        if is_franziska
        else None
    )
    #profile
    BOSS_PROFILES = {
        "HARD": {
            "name": "Godot (HARD)",
            "damage": 15,
            "sprites": {"normal": img_godot_normal, "face": img_godot_face, "stomach": img_godot_stomach, "defeat": godot_defeat_frames},
            "attacks": ["arc_left", "arc_right", "forward_center", "forward_left", "forward_right"],
            "attack_delay": (90, 150),     
            "guard_switch_chance": 60,     
            "tell_duration": 50,           
            "attack_duration": 20          
        }
    }

    #Colors
    BOSS_EXHAUSTED_COLOR = (50, 100, 200) 
    BOSS_FIST_COLOR = (220, 50, 50)       
    WARNING_COLOR = (255, 200, 50)        
    PLAYER_FIST_COLOR = (48, 82, 137)     
    PLAYER_HP_COLOR = (50, 220, 50)
    STAMINA_COLOR = (255, 200, 50) 
    SUPER_COLOR = (100, 255, 100)
    BOSS_HP_COLOR = (220, 50, 50)

    cfg = GLOBAL_CONTROLS["BoxingBoss"]

    controls = {
        "PUNCH_LEFT": [
            cfg["PUNCH_L"]
        ],

        "PUNCH_RIGHT": [
            cfg["PUNCH_R"]
        ],

        "DODGE_LEFT": [
            cfg["DODGE_L"]
        ],

        "DODGE_RIGHT": [
            cfg["DODGE_R"]
        ],

        "BLOCK": [
            cfg["BLOCK"]
        ],

        "AIM_HIGH": [
            cfg["AIM_UP"]
        ],

        "SUPER_PUNCH": [
            cfg["SUPER"]
        ]
    }

    # инициализация
    BOSS_DAMAGE = DIFFICULTIES[current_difficulty]["damage"]
    PLAYER_MAX_HP = g.pmx
    PLAYER_MAX_STAMINA = 15
    BOSS_MAX_HP = 300
    PUNCH_DURATION = 10
    COOLDOWN_FRAMES = 15  
    DODGE_DURATION = 30 

    player_stamina = PLAYER_MAX_STAMINA
    player_stun_timer = player_cooldown = player_offset_x = dodge_timer = 0
    player_flinch_x = player_flinch_y = player_flinch_timer = 0
    is_blocking = False
    player_hit_reaction = None 
    punch_timers = {"left": {"time": 0, "height": "low"}, "right": {"time": 0, "height": "low"}}

    successful_hits = 0

    boss_hp = BOSS_MAX_HP
    boss_state = "IDLE"
    boss_next_state = "IDLE"
    boss_attack_type = boss_attack_type_tell = boss_attack_type_real = ""
    boss_timer = 60
    boss_guard = "low"
    boss_misses = exhausted_hits = 0
    boss_flinch_x = boss_flinch_y = boss_flinch_timer = boss_image_timer = 0
    boss_visual_state = "normal"
    last_hit_side = last_player_punch = None
    ai_memory = {"low": {"low": 1, "high": 1}, "high": {"low": 1, "high": 1}}

    floating_texts = [] 

    game_state = "COUNTDOWN"
    countdown_timer = 180
    win_anim_timer = 0
    
   
    # GODOT BOSS MUSIC
    pygame.mixer.music.stop()

    music_file = None

    for ext in (
        ".mp3",
        ".wav",
        ".ogg"
    ):

        candidate = os.path.join(
            ASSET_DIR,
            "apollo_pursuit" + ext
        )

        if os.path.exists(
            candidate
        ):

            music_file = candidate
            break


    if music_file:

        try:


            # GODOT MUSIC след звънеца


            pygame.mixer.music.stop()

            music_file = None

            for ext in (
                ".mp3",
                ".wav",
                ".ogg"
            ):

                candidate = os.path.join(
                    ASSET_DIR,
                    "apollo_pursuit" + ext
                )

                if os.path.exists(
                    candidate
                ):

                    music_file = candidate
                    break

            music_started = False

        except Exception as exc:

            print(
                "Could not load Godot music:",
                exc
            )

    running = True
    while running:
        dt = clock.tick(FPS)
        boss_prof = BOSS_PROFILES[current_difficulty]

        keys = pygame.key.get_pressed()
        is_aiming_high = any(keys[k] for k in controls["AIM_HIGH"])

        for event in pygame.event.get():
            if minigame_settings_requested(
                event,
                g,
                SCREEN_WIDTH,
                SCREEN_HEIGHT
            ):

                display, _ = (
                    run_minigame_settings(
                        display,
                        screen,
                        g
                    )
                )

       
                is_blocking = False

                continue
         
            if event.type == pygame.QUIT:
               
                return "DEAD"
                

            if ( event.type == pygame.KEYDOWN and game_state == "FIGHT" and player_stun_timer <= 0):
                if any(event.key == k for k in controls["BLOCK"]):
                    if dodge_timer <= 0 and punch_timers["left"]["time"] == 0 and punch_timers["right"]["time"] == 0:
                        is_blocking = True

                if not is_blocking and dodge_timer <= 0 and punch_timers["left"]["time"] == 0 and punch_timers["right"]["time"] == 0:
                    if any(event.key == k for k in controls["DODGE_LEFT"]):
                        player_offset_x = -150
                        dodge_timer = DODGE_DURATION
                    elif any(event.key == k for k in controls["DODGE_RIGHT"]):
                        player_offset_x = 150
                        dodge_timer = DODGE_DURATION

                if not is_blocking and dodge_timer <= 0 and player_cooldown <= 0:
                    player_punched = False
                    punch_side = None
                    is_super_punch = False

                    if any(event.key == k for k in controls["SUPER_PUNCH"]) and successful_hits >= 10:
                        punch_side, is_super_punch, player_punched = "right", True, True
                        punch_timers[punch_side]["time"] = PUNCH_DURATION
                        punch_timers[punch_side]["height"] = "high"
                    elif any(event.key == k for k in controls["PUNCH_LEFT"]): 
                        punch_side, player_punched = "left", True
                        punch_timers[punch_side]["time"] = PUNCH_DURATION
                        punch_timers[punch_side]["height"] = "high" if is_aiming_high else "low"
                    elif any(event.key == k for k in controls["PUNCH_RIGHT"]): 
                        punch_side, player_punched = "right", True
                        punch_timers[punch_side]["time"] = PUNCH_DURATION
                        punch_timers[punch_side]["height"] = "high" if is_aiming_high else "low"

                    if player_punched:
                        player_cooldown = COOLDOWN_FRAMES 
                        hit_successful = False
                        target_height = punch_timers[punch_side]["height"]

                        if is_super_punch:
                            hit_successful = True
                            successful_hits = 0 
                        else:
                            if boss_state == "IDLE" and last_player_punch is not None:
                                prob_low = ai_memory[last_player_punch]["low"]
                                prob_high = ai_memory[last_player_punch]["high"]
                                if prob_low > prob_high: boss_guard = "low"
                                elif prob_high > prob_low: boss_guard = "high"
                                else: boss_guard = random.choice(["low", "high"])

                            if last_player_punch is not None:
                                ai_memory[last_player_punch][target_height] += 1
                            last_player_punch = target_height

                            if boss_state == "EXHAUSTED":
                                hit_successful = True
                                exhausted_hits -= 1
                                if exhausted_hits <= 0:
                                    boss_state = "IDLE"
                                    boss_timer = 90
                                    boss_misses = 0
                            elif boss_state in ["TELL", "ATTACK"]:
                                hit_successful = True 
                            elif boss_state == "IDLE":
                                if target_height != boss_guard:
                                    hit_successful = True 
                                    boss_guard = target_height 
                                else:
                                    hit_successful = False 

                        if hit_successful:
                            if is_super_punch:
                                current_player_damage = 40
                                if sound_objection: sound_objection.play() 
                            else:
                                current_player_damage = 15 if target_height == "high" else 10
                                if target_height == "high": 
                                    if sound_damage1: sound_damage1.play() 
                                else: 
                                    if sound_stab2: sound_stab2.play()

                            if successful_hits < 10:
                                successful_hits += 1
                                if successful_hits == 10:
                                    if sound_realization: sound_realization.play() 
                        
                            boss_hp -= current_player_damage 
                            boss_misses = 0 

                            if boss_hp <= 0: 
                                boss_hp = 0
                                game_state = "WIN" 
                                pygame.mixer.music.stop()
                                
                            floating_texts.append({
                                "text": f"-{current_player_damage}", "x": 400 + random.randint(-30, 30), 
                                "y": 140, "timer": 40, "color": (100, 255, 100) 
                            })
                            
                            boss_image_timer = 30 
                            last_hit_side = punch_side 
                            boss_flinch_timer = 15
                            
                            if target_height == "high":
                                boss_visual_state = "face" 
                                multiplier = 1.5 if is_super_punch else 1.0
                                boss_flinch_x = (40 * multiplier) if punch_side == "left" else (-40 * multiplier)
                                boss_flinch_y = -30 * multiplier  
                            else:
                                boss_visual_state = "stomach" 
                                boss_flinch_x = 0
                                boss_flinch_y = -40
                        else:
                            if sound_block_boss: sound_block_boss.play()
                            boss_flinch_timer = 8  
                            if target_height == "high":
                                boss_flinch_x = 12 if punch_side == "left" else -12   
                                boss_flinch_y = -5
                            else:
                                boss_flinch_x = 0
                                boss_flinch_y = -10

                        player_stamina -= 1
                        if player_stamina <= 0:
                            player_stun_timer = 120 
                            is_blocking = False
                            floating_texts.append({"text": "STUNNED!", "x": 400, "y": 300, "timer": 60, "color": (255, 50, 50)})

            if event.type == pygame.KEYUP:
                if any(event.key == k for k in controls["BLOCK"]):
                    is_blocking = False

        if game_state == "COUNTDOWN":

            countdown_timer -= 1

            if countdown_timer == 60:

            
                if sound_bell:
                    sound_bell.play()

           
                if (
                    music_file
                    and not music_started
                ):

                    try:

                        pygame.mixer.music.load(
                            music_file
                        )

                        pygame.mixer.music.set_volume(
                            getattr(
                                g,
                                "music_volume",
                                0.30
                            )
                        )

                        pygame.mixer.music.play(
                            -1
                        )

                        music_started = True

                    except Exception as exc:

                        print(
                            "Could not start Godot music:",
                            exc
                        )

            elif countdown_timer <= 0:

                game_state = "FIGHT"
                
        elif game_state == "FIGHT":
            if player_stun_timer > 0:
                player_stun_timer -= 1
                if player_stun_timer <= 0: player_stamina = 10 

            if dodge_timer > 0:
                dodge_timer -= 1
                if dodge_timer <= 0: player_offset_x = 0

            if player_flinch_timer > 0:
                player_flinch_timer -= 1
                player_flinch_x, player_flinch_y = int(player_flinch_x * 0.8), int(player_flinch_y * 0.8)
            else: player_flinch_x, player_flinch_y = 0, 0

            if boss_flinch_timer > 0:
                boss_flinch_timer -= 1
                boss_flinch_x, boss_flinch_y = int(boss_flinch_x * 0.8), int(boss_flinch_y * 0.8)
            else: boss_flinch_x, boss_flinch_y = 0, 0

            if boss_image_timer > 0:
                boss_image_timer -= 1
                if boss_image_timer <= 0: boss_visual_state = "normal" 

            if player_cooldown > 0: player_cooldown -= 1
            
            for key in punch_timers:
                if punch_timers[key]["time"] > 0: punch_timers[key]["time"] -= 1

            # ЛОГИКА НА БОС
            boss_timer -= 1
            
            if boss_state == "IDLE":
                if random.randint(1, boss_prof["guard_switch_chance"]) == 1: 
                    boss_guard = "low" if boss_guard == "high" else "high"
                if boss_timer <= 0:
                    boss_attack_type = random.choice(boss_prof["attacks"])
                    if boss_attack_type == "swing_logic":
                        boss_attack_type_tell = random.choice(["arc_left", "arc_right"])
                    else:
                        boss_attack_type_tell = "forward_center" if boss_attack_type == "forward_center" else boss_attack_type
                        
                    boss_state = "TELL"
                    boss_timer = boss_prof["tell_duration"]  
                    boss_next_state = "IDLE"
                
            elif boss_state == "TELL" and boss_timer <= 0:
                if boss_attack_type == "swing_logic":
                    boss_attack_type_real = "forward_center"
                else:
                    boss_attack_type_real = boss_attack_type_tell
                    
                boss_state = "ATTACK"
                boss_timer = boss_prof["attack_duration"]  
                
                if boss_attack_type_tell in ["arc_left", "arc_right"]:
                    if sound_swing: sound_swing.play()
                elif boss_attack_type_real in ["forward_left", "forward_right"]:
                    if sound_stab: sound_stab.play()
                
            elif boss_state == "ATTACK":
                if boss_timer == 5 and boss_attack_type_real == "forward_center":
                    if sound_deskslam: sound_deskslam.play()

                would_hit = False
                if current_difficulty == "HARD":
                    if boss_attack_type_real == "arc_left" and player_offset_x > -150: would_hit = True
                    elif boss_attack_type_real == "arc_right" and player_offset_x < 150: would_hit = True
                    elif boss_attack_type_real == "forward_center" and player_offset_x == 0: would_hit = True
                    elif boss_attack_type_real == "forward_left" and player_offset_x == -150: would_hit = True
                    elif boss_attack_type_real == "forward_right" and player_offset_x == 150: would_hit = True

                if boss_timer == 5:
                    if would_hit:
                        if is_blocking:
                            boss_misses += 1
                            if sound_block_phoenix: sound_block_phoenix.play()
                            
                            player_flinch_timer = 8
                            if boss_attack_type_real == "arc_left": player_flinch_x, player_flinch_y = 15, 10
                            elif boss_attack_type_real == "arc_right": player_flinch_x, player_flinch_y = -15, 10
                            else: player_flinch_x, player_flinch_y = 0, 15
                            
                            boss_next_state = "EXHAUSTED" if boss_misses >= 3 else "IDLE"
                            if boss_next_state == "EXHAUSTED": exhausted_hits = random.randint(2, 3) 

                            player_stamina -= 1
                            if player_stamina <= 0:
                                player_stun_timer = 120 
                                is_blocking = False
                                floating_texts.append({"text": "STUNNED!", "x": 400, "y": 300, "timer": 60, "color": (255, 50, 50)})
                        else:
                            g.php -= BOSS_DAMAGE
                            if sound_damage2: sound_damage2.play()

                            if g.php <= 0: 
                                g.php = 0
                                game_state = "GAMEOVER" 
                                boss_visual_state = "normal" 
                                pygame.mixer.music.stop()
                                
                            boss_next_state, boss_misses = "IDLE", 0 
                            
                            player_flinch_timer = 15
                            if boss_attack_type_real == "arc_left":
                                player_flinch_x, player_flinch_y = 50, 30
                                player_hit_reaction = "left_arm"
                            elif boss_attack_type_real == "arc_right":
                                player_flinch_x, player_flinch_y = -50, 30
                                player_hit_reaction = "right_arm"
                            else:
                                player_flinch_x, player_flinch_y = 0, 50
                                player_hit_reaction = "down"

                            floating_texts.append({"text": f"-{BOSS_DAMAGE}", "x": 400 + random.randint(-30, 30), "y": 380, "timer": 40, "color": (255, 50, 50)})
                    else:
                        boss_misses += 1
                        boss_next_state = "EXHAUSTED" if boss_misses >= 3 else "IDLE"
                        if boss_next_state == "EXHAUSTED": exhausted_hits = random.randint(2, 3) 

                if boss_timer <= 0:
                    boss_state = boss_next_state
                    boss_timer = 180 if boss_state == "EXHAUSTED" else random.randint(*boss_prof["attack_delay"])
                    
            elif boss_state == "EXHAUSTED" and boss_timer <= 0:
                boss_state, boss_timer, boss_misses = "IDLE", random.randint(*boss_prof["attack_delay"]), 0
                player_stamina = PLAYER_MAX_STAMINA 

        for ft in floating_texts: 
            ft["y"] -= 1.5; ft["timer"] -= 1    
        floating_texts = [ft for ft in floating_texts if ft["timer"] > 0]

        # draw screen
        screen.fill(theme["BG"])

        # boss tqlo
        boss_body_y_base = 160 + boss_flinch_y
        boss_body_y = boss_body_y_base

        if boss_state == "TELL" and boss_attack_type_tell == "forward_center": boss_body_y -= 30 
        elif boss_state == "ATTACK" and boss_attack_type_real == "forward_center":
            progress = (boss_prof["attack_duration"] - boss_timer) / float(boss_prof["attack_duration"])
            boss_body_y = boss_body_y_base - 30 + (progress * 60)

        if game_state == "WIN":
            frame_idx = min(win_anim_timer // 6, len(boss_prof["sprites"]["defeat"]) - 1)
            current_sprite = boss_prof["sprites"]["defeat"][frame_idx]
        else:
            if boss_visual_state == "face":
                current_sprite_base = boss_prof["sprites"]["face"]
                current_sprite = pygame.transform.flip(current_sprite_base, True, False) if last_hit_side == "left" else current_sprite_base
            elif boss_visual_state == "stomach":
                current_sprite_base = boss_prof["sprites"]["stomach"]
                current_sprite = pygame.transform.flip(current_sprite_base, True, False) if last_hit_side == "right" else current_sprite_base
            else:
                current_sprite = boss_prof["sprites"]["normal"]

        temp_surf = current_sprite.copy()
        if boss_state == "EXHAUSTED" and game_state == "FIGHT":
            temp_surf.fill((100, 150, 255), special_flags=pygame.BLEND_RGB_MULT)

        boss_final_x = 400 + boss_flinch_x - (temp_surf.get_width() // 2)
        offset_y = 60 
        boss_final_y = boss_body_y - offset_y 
        screen.blit(temp_surf, (boss_final_x, boss_final_y))

        # Boss ruce
        if game_state not in ["WIN", "GAMEOVER", "COUNTDOWN"]:
            if boss_guard == "high": base_left, base_right = [370, boss_body_y + 10], [430, boss_body_y + 10]
            else: base_left, base_right = [370, boss_body_y + 180], [430, boss_body_y + 180]

            boss_left_fist, boss_right_fist = list(base_left), list(base_right)
            b_left_color, b_right_color = BOSS_FIST_COLOR, BOSS_FIST_COLOR

            if boss_state == "EXHAUSTED":
                boss_left_fist, boss_right_fist = [300, boss_body_y + 120], [500, boss_body_y + 120]
            elif boss_state == "TELL":
                if boss_attack_type_tell == "arc_left": b_left_color, boss_left_fist, boss_right_fist = WARNING_COLOR, [260, boss_body_y_base], [520, boss_body_y_base]
                elif boss_attack_type_tell == "arc_right": b_right_color, boss_left_fist, boss_right_fist = WARNING_COLOR, [280, boss_body_y_base], [540, boss_body_y_base]
                elif boss_attack_type_tell == "forward_left": b_left_color, boss_left_fist = WARNING_COLOR, [280, boss_body_y_base - 40] 
                elif boss_attack_type_tell == "forward_right": b_right_color, boss_right_fist = WARNING_COLOR, [520, boss_body_y_base - 40]
                elif boss_attack_type_tell == "forward_center": boss_left_fist, boss_right_fist = [280, boss_body_y_base], [520, boss_body_y_base]
                    
            elif boss_state == "ATTACK":
                progress = (boss_prof["attack_duration"] - boss_timer) / float(boss_prof["attack_duration"])
                vis_type = boss_attack_type_real
                
                if vis_type == "arc_left":
                    b_left_color, boss_right_fist = WARNING_COLOR, [520, boss_body_y_base] 
                    boss_left_fist = [260 + progress * 300, boss_body_y_base + progress * 200 + math.sin(progress * math.pi) * 100]
                elif vis_type == "arc_right":
                    b_right_color, boss_left_fist = WARNING_COLOR, [280, boss_body_y_base] 
                    boss_right_fist = [540 - progress * 300, boss_body_y_base + progress * 200 + math.sin(progress * math.pi) * 100]
                elif vis_type == "forward_left":
                    b_left_color, boss_left_fist = WARNING_COLOR, [280 + progress * -30, boss_body_y_base - 40 + progress * 350] 
                elif vis_type == "forward_right":
                    b_right_color, boss_right_fist = WARNING_COLOR, [520 + progress * 30, boss_body_y_base - 40 + progress * 350]
                elif vis_type == "forward_center":
                    b_left_color = b_right_color = WARNING_COLOR 
                    boss_left_fist, boss_right_fist = [280, boss_body_y_base + progress * 200], [520, boss_body_y_base + progress * 200]

            pygame.draw.circle(screen, b_left_color, (int(boss_left_fist[0] + boss_flinch_x), int(boss_left_fist[1])), 40)
            pygame.draw.circle(screen, b_right_color, (int(boss_right_fist[0] + boss_flinch_x), int(boss_right_fist[1])), 40)

        # Player
        player_body_y = 380
        is_jumping = False
        if (punch_timers["left"]["time"] > 0 and punch_timers["left"]["height"] == "high") or \
           (punch_timers["right"]["time"] > 0 and punch_timers["right"]["height"] == "high"):
            is_jumping = True

        if is_jumping: player_body_y -= 80 
        player_body_y += player_flinch_y
        
        if is_franziska:

            if (
                game_state == "WIN"
                and img_franziska_special
                is not None
            ):

                current_player_sprite = (
                    img_franziska_special
                )

            elif (
                (
                    player_flinch_timer > 0
                    or game_state == "GAMEOVER"
                )
                and img_franziska_damage
                is not None
            ):

                current_player_sprite = (
                    img_franziska_damage
                )

            else:

                current_player_sprite = (
                    img_franziska_normal
                    or img_phoenix_normal
                )

        else:

            if game_state == "GAMEOVER":

                current_player_sprite = (
                    img_phoenix_lose
                )

            elif (
                player_flinch_timer > 0
                and player_hit_reaction
            ):

                if (
                    player_hit_reaction
                    == "right_arm"
                ):

                    current_player_sprite = (
                        img_phoenix_hit
                    )

                elif (
                    player_hit_reaction
                    == "left_arm"
                ):

                    current_player_sprite = (
                        pygame.transform.flip(
                            img_phoenix_hit,
                            True,
                            False
                        )
                    )

                else:

                    current_player_sprite = (
                        img_phoenix_down
                    )

            else:

                current_player_sprite = (
                    img_phoenix_normal
                )

        p_surf = current_player_sprite.copy()
        if player_stun_timer > 0 and game_state == "FIGHT":
            p_surf.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_MULT)

        player_final_x = 400 + player_offset_x + player_flinch_x - (p_surf.get_width() // 2)
        screen.blit(p_surf, (player_final_x, player_body_y))

        # Ръце на играч
        if game_state not in ["WIN", "GAMEOVER", "COUNTDOWN"]:
            if is_blocking:
                left_fist_x, right_fist_x = 380 + player_offset_x, 420 + player_offset_x
                left_fist_y, right_fist_y = player_body_y + 50, player_body_y + 50 
            else:
                left_fist_x, right_fist_x = 360 + player_offset_x, 440 + player_offset_x
                left_fist_y, right_fist_y = player_body_y + 130, player_body_y + 130 

                if punch_timers["left"]["time"] > 0: 
                    left_fist_x -= 20
                    left_fist_y -= 220 if punch_timers["left"]["height"] == "high" else 170
                if punch_timers["right"]["time"] > 0: 
                    right_fist_x += 20
                    right_fist_y -= 220 if punch_timers["right"]["height"] == "high" else 170

            left_fist_x += player_flinch_x
            left_fist_y += player_flinch_y
            right_fist_x += player_flinch_x
            right_fist_y += player_flinch_y

            pygame.draw.circle(screen, PLAYER_FIST_COLOR, (int(left_fist_x), int(left_fist_y)), 35)
            pygame.draw.circle(screen, PLAYER_FIST_COLOR, (int(right_fist_x), int(right_fist_y)), 35)

        for ft in floating_texts:
            txt_surf = font_dmg.render(ft["text"], True, ft["color"])
            txt_surf.set_alpha(min(255, ft["timer"] * 10))
            screen.blit(txt_surf, txt_surf.get_rect(center=(ft["x"], int(ft["y"]))))

        #UI БАРОВЕ
        pygame.draw.rect(screen, theme["BORDER"], (200, 20, 400, 20), border_radius=5)
        pygame.draw.rect(screen, BOSS_HP_COLOR, (200, 20, (boss_hp / BOSS_MAX_HP) * 400, 20), border_radius=5)
        boss_hp_text = font_ui.render(f"{max(0, int(boss_hp))}/{BOSS_MAX_HP}",True,theme["TEXT"])
        screen.blit(boss_hp_text,boss_hp_text.get_rect(center=(400,30)))
        screen.blit(font_ui.render(f"Misses: {boss_misses}/3", True, theme["TEXT"]), (200, 45))

        pygame.draw.rect(screen, theme["BORDER"], (20, 535, 300, 20), border_radius=5)
        pygame.draw.rect(screen, PLAYER_HP_COLOR, (20, 535, (g.php / PLAYER_MAX_HP) * 300, 20), border_radius=5)
        player_hp_text = font_ui.render(f"{max(0, int(g.php))}/{PLAYER_MAX_HP}",True,theme["TEXT"])

        screen.blit(
            player_hp_text,
            player_hp_text.get_rect(
                center=(
                    170,
                    545
                )
            )
        )        
        stamina_text = font_ui.render(f"Stamina: {player_stamina} / {PLAYER_MAX_STAMINA}", True, STAMINA_COLOR)
        screen.blit(stamina_text, (20, 560))

        if successful_hits == 10:
            super_text = font_ui.render(f"Super Punch: 10/10 (READY!)", True, SUPER_COLOR)
        else:
            super_text = font_ui.render(f"Super Punch: {successful_hits}/10", True, (200, 200, 200))
        screen.blit(super_text, (220, 560))

        #COUNTDOWN OVERLAY
        if game_state == "COUNTDOWN":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            if countdown_timer > 120: c_text = "3"
            elif countdown_timer > 60: c_text = "2"
            elif countdown_timer > 0: c_text = "1"
            else: c_text = "START!"
            
            color = (255, 200, 50) if c_text != "START!" else (100, 255, 100)
            txt_surf = huge_font.render(c_text, True, color)
            screen.blit(txt_surf, txt_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)))

        # КРАЙ НА ИГРАТА
        if game_state == "WIN":
            win_text = big_font.render("YOU DEFEATED THE BOSS!", True, (100, 255, 100))
            screen.blit(win_text, win_text.get_rect(center=(SCREEN_WIDTH // 2, 280)))
            
            if win_anim_timer == 1 and sound_victory: sound_victory.play()
            
            win_anim_timer += 1
            if win_anim_timer > 120:
            
                return "WIN"

        elif game_state == "GAMEOVER":
            lose_text = big_font.render("GAME OVER", True, (255, 70, 70))
            screen.blit(lose_text, lose_text.get_rect(center=(SCREEN_WIDTH // 2, 280)))
            
            if win_anim_timer == 1 and sound_defeat: sound_defeat.play()

            win_anim_timer += 1
            if win_anim_timer > 120:

                return "DEAD"
        # CONTROLS PANEL


        controls_panel = pygame.Rect(
            545,
            475,
            245,
            115
        )

        panel_surface = pygame.Surface(
            controls_panel.size,
            pygame.SRCALPHA
        )

        panel_surface.fill(
            (15, 15, 20, 210)
        )

        screen.blit(
            panel_surface,
            controls_panel.topleft
        )

        pygame.draw.rect(
            screen,
            theme["BORDER"],
            controls_panel,
            2,
            border_radius=8
        )

        control_lines = [
            f"[{pygame.key.name(cfg['PUNCH_L']).upper()}] Left Punch",
            f"[{pygame.key.name(cfg['PUNCH_R']).upper()}] Right Punch",
            f"[{pygame.key.name(cfg['DODGE_L']).upper()} / {pygame.key.name(cfg['DODGE_R']).upper()}] Dodge",
            f"[{pygame.key.name(cfg['BLOCK']).upper()}] Block",
            f"[{pygame.key.name(cfg['AIM_UP']).upper()}] Aim High",
            f"[{pygame.key.name(cfg['SUPER']).upper()}] Super"
        ]

        for i, line in enumerate(control_lines):

            txt = small_font.render(
                line,
                True,
                theme["TEXT"]
            )

            screen.blit(
                txt,
                (
                    controls_panel.x + 10,
                    controls_panel.y + 8 + i * 17
                )
            )
        draw_minigame_settings_button(
            screen,
            g
        )
        present_minigame(
            display,
            screen
        )

    return None