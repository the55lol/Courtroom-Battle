import os

os.environ["SDL_RENDER_SCALE_QUALITY"] = "linear"

import pygame
import runner_minigame
import cupid_minigame
import manpac_minigame
import boxing_boss
import math
import breakout_boss
from config import GAME_EVENTS
from config import CARDS
from entities import Card
import random
import tutorial
import run_history
from asset_utils import asset_path

from config import (
    W, H, BG, PANEL, BORDER, GOLD, RED, RED_D, GREEN, GREEN_D, BLUE, BLUE_D,
    PURPLE_D, WHITE, GRAY, GRAY_L, ORANGE, CARDS, CW, CH,
    F_BIG, F_MED, F_MED, F_MED, F_TINY_BOLD,
    C_COMMON, C_RARE, C_EPIC, C_LEGENDARY, GLOBAL_CONTROLS, get_card_data,
    RELICS, GAME_EVENTS, F_SML, CARD_UPGRADES,  RELIC_RANDOM_BLACKLIST, HUD_HEIGHT)

from minigame_view import (
    load_display_settings,
    save_display_settings,
    apply_display_settings,
    get_resolution_options,
    get_desktop_resolution,
    present_minigame,
    screen_to_virtual,
    MinigameQuitToMenu,
    MinigameQuitGame
    )

from entities import rrect, txc, lerp, Btn, Card
from game import Game
from audio_settings import (
    load_audio_settings,
    save_audio_settings,
    apply_audio_settings,
    slider_value_from_x)



pygame.init()

if pygame.mixer.get_init():
    pygame.mixer.set_num_channels(
        32)

pygame.key.set_repeat(350, 45)

INITIAL_DISPLAY_SETTINGS = (load_display_settings())

display = apply_display_settings(INITIAL_DISPLAY_SETTINGS)


screen = pygame.Surface((W, H))

pygame.display.set_caption("Courtroom Battle")

try:

    app_icon = pygame.image.load(asset_path("manpac", "img_badge.ico"))

    pygame.display.set_icon(app_icon)

except Exception as exc:

    print("Window icon failed:", exc)

clock = pygame.time.Clock()

TITLE_FONT = pygame.font.SysFont("Impact", 72)

CARD_FONT = pygame.font.SysFont("Georgia", 15)

CARD_KEYWORD_FONT = pygame.font.SysFont("Georgia",15,bold=True)

EVENT_TEXT_FONT = pygame.font.SysFont("Georgia", 20)

EVENT_OPTION_FONT = pygame.font.SysFont("Georgia", 18)

MINIGAME_DISPLAY_NAMES = {
    "HaremRunner": "Card Runner",
    "HaremMaker": "Card Shooter",
    "CardCupid": "Card Shooter",
    "ManPac": "Card ManPac",
    "BoxingBoss": "Godot - Boxing",
    "UndertaleBoss": "Franziska - Bullet Hell"
}

def minigame_display_name(name):
    return MINIGAME_DISPLAY_NAMES.get(name, name)
# PHOENIX COMBAT SPRITES
def load_main_phoenix_image(
    folder,
    filename,
    size=(155, 155),
    flip_x=False):

    path = asset_path(folder, filename)

    try:

        img = pygame.image.load(
            path).convert_alpha()



        visible_bounds = img.get_bounding_rect(
            min_alpha=1)

        if (
            visible_bounds.width > 0
            and visible_bounds.height > 0):

            img = img.subsurface(
                visible_bounds).copy()


        original_w = img.get_width()
        original_h = img.get_height()

        max_w, max_h = size

        scale = min(max_w / original_w, max_h / original_h)

        new_w = max(
            1,
            int(original_w * scale))

        new_h = max(
            1,
            int(original_h * scale))

        img = pygame.transform.smoothscale(
            img,
            (
                new_w,
                new_h)
        )

        if flip_x:

            img = pygame.transform.flip(
                img,
                True,
                False)

        return img

    except Exception as exc:

        print(
            "Could not load main Phoenix image:",
            path,
            exc)

        surf = pygame.Surface(size, pygame.SRCALPHA)

        return surf


MAIN_PHOENIX_IDLE = load_main_phoenix_image(
    "bullethell",
    os.path.join("phoenix", "img_phoneix.png"),
    flip_x=True)

MAIN_PHOENIX_ATTACK = load_main_phoenix_image(
    "bullethell",
    os.path.join("phoenix", "img_phoneix_attack.png")
)

MAIN_PHOENIX_DAMAGE = load_main_phoenix_image(
    "bullethell",
    os.path.join("phoenix", "img_damage.png"))

MAIN_PHOENIX_PROUD = load_main_phoenix_image("runner", "img_proud.png")
# FRANZISKA PLAYER COMBAT SPRITES
MAIN_FRANZISKA_IDLE = load_main_phoenix_image(
    "enemies",
    os.path.join("Franziska von Karma", "franziska_default.png"),
    flip_x=True)

MAIN_FRANZISKA_ATTACK = load_main_phoenix_image(
    "enemies",
    os.path.join("Franziska von Karma", "franziska_attack.png"),
    flip_x=True)

MAIN_FRANZISKA_DAMAGE = load_main_phoenix_image(
    "enemies",
    os.path.join("Franziska von Karma", "franziska_damage.png"),
    flip_x=True)

MAIN_FRANZISKA_SPECIAL = load_main_phoenix_image(
    "enemies",
    os.path.join("Franziska von Karma", "franziska_special.png"),
    flip_x=True)
# ENEMY COMBAT SPRITES
ENEMY_SPRITE_CACHE = {}

ENEMY_SPRITE_MAX_SIZE = (
    190,
    165)


def find_enemy_sprite_path(enemy_name, pose):


    clean_name = str(
        enemy_name).split(" (")[0].strip()

    first_name = (
        clean_name.split()[0]
        if clean_name
        else "")

    enemy_root = asset_path(
        "enemies")

 
    folder_candidates = [
        clean_name,
        first_name
    ]
    if clean_name == "Edgeworth":

        folder_candidates.insert(0, "Miles Edgeworth")

    valid_extensions = (
        ".png",
        ".jpg",
        ".jpeg",
        ".webp")

    for folder_name in folder_candidates:

        if not folder_name:
            continue

        folder_path = os.path.join(enemy_root, folder_name)

        if not os.path.isdir(
            folder_path):
            continue

        folder_first_name = (
            folder_name.split()[0])

        wanted_stem = (
            f"{folder_first_name}_{pose}").lower()

        try:

            filenames = os.listdir(
                folder_path)

        except OSError:
            continue

        for filename in filenames:

            stem, extension = (
                os.path.splitext(
                    filename)
            )

            if (
                stem.lower()
                == wanted_stem
                and extension.lower()
                in valid_extensions):

                return os.path.join(folder_path, filename)

    return None


def get_enemy_sprite(enemy_name, pose="default"):

    cache_key = (
        enemy_name,
        pose)

    if cache_key in ENEMY_SPRITE_CACHE:

        return ENEMY_SPRITE_CACHE[
            cache_key
        ]


    path = find_enemy_sprite_path(enemy_name, pose)



    if (
        path is None
        and pose != "default"):

        path = find_enemy_sprite_path(enemy_name, "default")



    if path is None:

        ENEMY_SPRITE_CACHE[
            cache_key
        ] = None

        return None


    try:

        img = pygame.image.load(
            path).convert_alpha()

        original_w = img.get_width()
        original_h = img.get_height()

        max_w, max_h = (
            ENEMY_SPRITE_MAX_SIZE)

        scale = min(max_w / original_w, max_h / original_h)

        new_w = max(
            1,
            int(
                original_w * scale)
        )

        new_h = max(
            1,
            int(
                original_h * scale)
        )

        img = pygame.transform.smoothscale(
            img,
            (
                new_w,
                new_h)
        )

        ENEMY_SPRITE_CACHE[
            cache_key
        ] = img

        return img

    except Exception as exc:

        print(
            "Enemy sprite failed:",
            enemy_name,
            pose,
            path,
            exc)

        ENEMY_SPRITE_CACHE[
            cache_key
        ] = None

        return None
def txt(surf, s, font, col, x, y):
    surf.blit(font.render(s, True, col), (x, y))

def hp_bar(surf, cur, mx, x, y, w=170):
    rrect(surf, (55,18,18), (x,y,w,12), 4)
    rrect(surf, GREEN, (x,y,int(w*max(0,cur/mx)),12), 4)
    rrect(surf, BORDER, (x,y,w,12), 4, 1)
    txc(surf, f"{cur}/{mx}", F_MED, WHITE, x+w//2, y+6)
def draw_run_hud(surf, g):

    hud_rect = pygame.Rect(0, H - HUD_HEIGHT, W, HUD_HEIGHT)

    rrect(
        surf,
        (16, 12, 26),
        hud_rect,
        0)

    hud_font = pygame.font.SysFont(
        "Arial",
        16,
        bold=True)

    text_y = H - 24

    total_floors = len(
        getattr(g, "map_data", [])
    )

    if total_floors > 0:
        floor_text = (
            f"FLOOR {g.floor + 1}/{total_floors}")
    else:
        floor_text = (
            f"FLOOR {g.floor + 1}")

    txt(
        surf,
        floor_text,
        hud_font,
        WHITE,
        12,
        text_y)

    txt(
        surf,
        f"HP {g.php}/{g.pmx}",
        hud_font,
        WHITE,
        175,
        text_y)


    hp_ratio = (
        g.php / g.pmx
        if g.pmx > 0
        else 0)

    hp_ratio = max(
        0.0,
        min(1.0, hp_ratio))

    hp_x = 285
    hp_y = H - 13
    hp_w = 130

    rrect(
        surf,
        (55, 18, 18),
        (hp_x, hp_y, hp_w, 7),
        3)

    rrect(surf,RED,(hp_x,hp_y,int(hp_w * hp_ratio),7),3)

    txt(
        surf,
        f"GOLD {getattr(g, 'pgold', 0)}",
        hud_font,
        GOLD,
        460,
        text_y)

    txt(
        surf,
        f"ACT {getattr(g, 'act', 1)}",
        hud_font,
        GOLD,
        610,
        text_y)

def draw_arrow(surf, start, end, color, width=4):
    pygame.draw.line(surf, color, start, end, width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    p1 = (end[0] - 20 * math.cos(angle - math.pi/6), end[1] - 20 * math.sin(angle - math.pi/6))
    p2 = (end[0] - 20 * math.cos(angle + math.pi/6), end[1] - 20 * math.sin(angle + math.pi/6))
    pygame.draw.polygon(surf, color, [end, p1, p2])

def draw_card(surf, name, x, y, mana, selected=False, dragging=False, g=None, in_play_zone=False, target_enemy=None, upgraded=False, upgrade_preview=False):
    d = CARDS[name]
    base_d = get_card_data(name, False)

    d = get_card_data(name, upgraded or upgrade_preview)
    show_upgrade = upgraded or upgrade_preview
    display_cost = d["cost"]

    if (g is not None and hasattr(g, "get_effective_card_cost")and getattr(g, "state", "") == "combat"):

        display_cost = (g.get_effective_card_cost(name, upgraded or upgrade_preview))

    grayed = (
        display_cost > mana)
    sc = 1.08 if dragging else 1.0
    w, h = int(CW*sc), int(CH*sc)
    ox = x - (w-CW)//2; oy = y - (h-CH)//2

    tc = {"attack":RED_D,"skill":BLUE_D,"power":PURPLE_D}[d["type"]]
    rarity = d.get("rarity", "common")

    if grayed:
        bg = (38, 30, 55)
    else:
        if rarity == "common":      bg = (35, 35, 42)
        elif rarity == "rare":      bg = (22, 38, 62)
        elif rarity == "epic":      bg = (48, 22, 60)
        elif rarity == "legendary": bg = (62, 38, 18)
        else:                       bg = PANEL
    
    if rarity == "common": base_border_col = C_COMMON
    elif rarity == "rare": base_border_col = C_RARE
    elif rarity == "epic": base_border_col = C_EPIC
    elif rarity == "legendary": base_border_col = C_LEGENDARY
    else: base_border_col = BORDER

    border_col = GOLD if (selected or dragging) else base_border_col

    rrect(surf, bg, (ox,oy,w,h), 10, 2, border_col)
    rrect(surf, tc, (ox+2,oy+2,w-4,22), 8)

    ccol =  BLUE if not grayed else GRAY
    pygame.draw.circle(surf, ccol, (ox+13,oy+13), 10)
    cost_changed = (
        show_upgrade
        and d.get("cost") != base_d.get("cost"))

    txc(
        surf,
        str(display_cost),
        CARD_FONT,
        GREEN if cost_changed else WHITE,
        ox + 13,
        oy + 13)



    display_name = (
        name + "+"
        if show_upgrade
        else name)

    name_color = (
        GREEN
        if show_upgrade
        else WHITE)

    ns = CARD_FONT.render(
        display_name,
        True,
        name_color)

    surf.blit(
        ns,
        (ox + w//2 - ns.get_width()//2, oy + 4))

    rrect(surf, (22,18,38), (ox+8,oy+30,w-16,80), 5)
    icon = {"attack":"[A]","skill":"[S]","power":"[P]"}[d["type"]]
    txc(surf, icon, F_BIG, GRAY_L, ox+w//2, oy+70)

    base_dmg = d.get("dmg", 0)
    is_attack = (d["type"] == "attack" and base_dmg > 0)
    
    str_bonus = (getattr(g, "pstr", 0)+ getattr(g, "ptmp_str", 0)) if (g is not None and is_attack) else 0
    has_str = str_bonus > 0
    current_dmg = base_dmg + str_bonus
    
    mouse_pos = screen_to_virtual(
        pygame.mouse.get_pos(),
        W,
        H)
    is_vuln_active = False
    
    if g and is_attack:
        if d.get("target_all"):
            is_vuln_active = any(en.get("vuln", 0) > 0 for en in getattr(g, 'enemies', []))
        elif dragging:
            for rect, en in getattr(g, 'enemy_rects', []):
                if rect.collidepoint(mouse_pos) and en.get("vuln", 0) > 0:
                    is_vuln_active = True
                    break
    
    if is_vuln_active:
        vuln_dmg = int(current_dmg * 1.5)
        extra_vuln = vuln_dmg - current_dmg
        current_dmg = vuln_dmg

    keywords = ["vulnerable", "weak", "blitz", "wound","wounds", "strength"]
    space_w = CARD_FONT.size(" ")[0]

    base_dmg = d.get("dmg", 0)
    w_val = d.get("wounds", 0)
    
    combo = (
        getattr(g, "pwounds_combo", 0
)
        if (
            g is not None
            and getattr(g, "state", "") == "combat"
        )
        else 0)
    w_dmg = (w_val + combo) if (w_val > 0 and combo > 0) else 0
    
    total_base = base_dmg + w_dmg
    is_attack = (d["type"] == "attack" and (base_dmg > 0 or w_val > 0))
    
    str_bonus = (getattr(g, "pstr", 0)+ getattr(g, "ptmp_str", 0)) if (g is not None and is_attack) else 0
    has_str = str_bonus > 0
    current_dmg = total_base + str_bonus
    player_is_weak = (
        g is not None
        and getattr(g, "pweak", 0) > 0
        and is_attack)

    if player_is_weak:
        current_dmg = int(current_dmg * 0.75)

    if is_vuln_active:
        current_dmg = int(current_dmg * 1.5)

    changed_upgrade_numbers = set()

    if show_upgrade:

        stats_to_check = [
            "dmg",
            "block",
            "weak",
            "vuln",
            "str",
            "tmp_str",
            "blitz",
            "draw",
            "times"
        ]

        for stat in stats_to_check:

            old_value = base_d.get(stat)
            new_value = d.get(stat)

            if (
                new_value is not None
                and new_value != old_value):
                changed_upgrade_numbers.add(
                    str(new_value))
    wrapped_lines = []

    for original_line in d["desc"].split("\n"):
        words = original_line.split()
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word

            if CARD_FONT.size(test_line)[0] <= w - 18:
                current_line = test_line
            else:
                if current_line:
                    wrapped_lines.append(current_line)
                current_line = word

        if current_line:
            wrapped_lines.append(current_line)



        for i, line in enumerate(wrapped_lines):
            line_col = WHITE if not grayed else GRAY
            line_y = oy + 120 + i * 18
        
            line_text = line
            if is_attack:

                if "dmg" in line and not "Wounds" in line:

                    if player_is_weak:
                        line_text = line.replace(f"{base_dmg} dmg", f"{current_dmg} dmg") 
                        line_col = ORANGE

                    elif is_vuln_active:
                        line_text = line.replace(f"{base_dmg} dmg", f"{current_dmg} dmg")
                        line_col = GREEN

                    elif has_str:
                        line_text = line.replace(f"{base_dmg} dmg", f"{current_dmg} dmg")
                       
                elif "Wounds" in line:
                    if is_vuln_active:
                        line_text = line.replace(f"Wounds {w_val}", f"Wounds {w_val} ({current_dmg} dmg +{extra_vuln})")
                        line_col = ORANGE
                    elif has_str or combo > 0:
                        line_text = line.replace(f"Wounds {w_val}", f"Wounds {w_val} ({current_dmg} dmg)")
                        line_col = ORANGE if combo > 0 else (50, 220, 50)
                    else:
                        line_text = line.replace(f"Wounds {w_val}", f"Wounds {w_val} ({current_dmg} dmg)")
        
            words = line_text.split(" ")
            curr_x = ox + 6
            
            for word in words:

                clean_word = word.strip(
                    ".,!?:").lower()

                is_keyword = (
                    clean_word in keywords)

                font_to_use = (
                    CARD_KEYWORD_FONT
                    if is_keyword
                    else CARD_FONT)

                numeric_word = word.strip(
                    ".,!?:()+")

                is_upgrade_number = (
                    show_upgrade
                    and numeric_word
                    in changed_upgrade_numbers)
                is_strength_damage = (
                    has_str
                    and numeric_word == str(current_dmg)
                    and "dmg" in line_text)
                word_color = (
                    GREEN
                    if is_upgrade_number or is_strength_damage
                    else line_col)
               
                w_surf = font_to_use.render(
                    word,
                    True,
                    word_color)

                surf.blit(
                    w_surf,
                    (curr_x, line_y))

                curr_x += (
                    w_surf.get_width()
                    + space_w)

def load_dev_tab(g, tab):
    g.dev_tab = tab
    g.card_scroll = 0

    if tab == "Relics":
        g.viewing_cards = []
        g.view_title = "DEV MENU - RELICS"
        return

    class_name = tab

    cards = []

    for name, data in CARDS.items():
        card_class = data.get("class", "Any")

        if card_class.lower() == class_name.lower():
            cards.append(Card(name))

    rarity_weights = {
        "common": 0,
        "rare": 1,
        "epic": 2,
        "legendary": 3
    }

    cards.sort(
        key=lambda c: (
            rarity_weights.get(
                CARDS.get(c.name, {}).get("rarity", "common"),
                0),
            CARDS.get(c.name, {}).get("cost", 0),
            c.name)
    )

    g.viewing_cards = cards
    g.view_title = f"DEV MENU - {tab.upper()}"
#  ЕКРАНИ ЗА ИЗБОР И ИМЕНУВАНЕ НА ПРОФИЛИ 

def draw_select_profile(surf, g, mouse):
    surf.fill(BG)

    txc(
        surf,
        "CHOOSE SAVE FILE",
        F_BIG,
        GOLD,
        W // 2,
        100)

    txc(
        surf,
        "Select a save slot to continue or start a new run",
        F_MED,
        GRAY_L,
        W // 2,
        140)

    g.profile_delete_rects = []

    for i, btn in enumerate(g.btn_slots):

        p_info = g.profiles[i]

        p_name = (
            p_info["name"]
            if p_info["name"]
            else f"Slot {i + 1}: [EMPTY]")

        has_save = g.has_save(i)

        status_txt = (
            "Active Run Saved"
            if has_save
            else (
                "Ready for New Run"
                if p_info["name"]
                else "Click to Create")
        )

        btn.label = p_name
        btn.draw(surf, mouse)

        status_col = (
            GREEN
            if has_save
            else GRAY_L)

        txc(
            surf,
            status_txt,
            F_MED,
            status_col,
            btn.rect.centerx,
            btn.rect.bottom - 12)

        if has_save:

            delete_rect = pygame.Rect(btn.rect.right + 15, btn.rect.y + 15, 125, 40)

            hover = delete_rect.collidepoint(mouse)

            rrect(
                surf,
                RED_D if hover else PANEL,
                delete_rect,
                7,
                2,
                RED)

            txc(
                surf,
                "DELETE SAVE",
                F_MED,
                WHITE,
                delete_rect.centerx,
                delete_rect.centery)

            g.profile_delete_rects.append(
                (i, delete_rect))

    if g.profiles[g.current_slot]["name"]:
        g.btn_slot_back.draw(surf, mouse)


def draw_delete_save_confirm(surf, g, mouse):
    surf.fill(BG)

    slot = getattr(g, "delete_save_slot", None)

    profile_name = "Unknown"

    if (
        slot is not None
        and 0 <= slot < len(g.profiles)):
        profile_name = (
            g.profiles[slot].get("name", f"Slot {slot + 1}")
        )

    txc(
        surf,
        "DELETE SAVE FILE?",
        F_BIG,
        RED,
        W // 2,
        180)

    txc(
        surf,
        profile_name,
        F_BIG,
        WHITE,
        W // 2,
        240)

    txc(
        surf,
        "The active run will be permanently deleted.",
        F_MED,
        GRAY_L,
        W // 2,
        290)

    txc(
        surf,
        "Run History and profile name will NOT be deleted.",
        F_MED,
        GOLD,
        W // 2,
        315)

    g.btn_delete_save_yes.draw(surf, mouse)

    g.btn_delete_save_no.draw(surf, mouse)

def draw_name_profile(surf, g, mouse):
    surf.fill(BG)
    txc(surf, f"NAME SAVE FILE {g.naming_slot + 1}", F_BIG, GOLD, W//2, 180)
    txc(surf, "Type your profile name and press ENTER:", F_MED, WHITE, W//2, 240)

    box_rect = pygame.Rect(W//2 - 150, 280, 300, 50)
    rrect(surf, PANEL, box_rect, 8, 2, GOLD)
    txc(surf, g.input_text + "_", F_MED, WHITE, box_rect.centerx, box_rect.centery)

    g.btn_confirm_name.draw(surf, mouse)



def collection_item_unlocked(
    g,
    data,
    class_name):

    required_level = int(
        data.get("unlock_level", 0)
    )


    if required_level <= 0:
        return True

    current_level = g.get_class_level(
        class_name)

    return (
        current_level
        >= required_level)



def draw_locked_collection_card(
    surf,
    x,
    y,
    rarity):

    rarity_colors = {
        "common": C_COMMON,
        "rare": C_RARE,
        "epic": C_EPIC,
        "legendary": C_LEGENDARY
    }

    border_col = rarity_colors.get(rarity, BORDER)

    rect = pygame.Rect(x, y, CW, CH)

    # Напълно черна карта
    rrect(
        surf,
        (8, 8, 10),
        rect,
        10,
        3,
        border_col)

    # Горна лента - също почти черна
    rrect(
        surf,
        (12, 12, 15),
        (
            x + 2,
            y + 2,
            CW - 4,
            22),
        8)

    # Централна неизвестна зона
    rrect(
        surf,
        (3, 3, 5),
        (
            x + 8,
            y + 30,
            CW - 16,
            80),
        5)

    txc(
        surf,
        "?",
        F_BIG,
        GRAY,
        x + CW // 2,
        y + 70)

    txc(
        surf,
        "LOCKED",
        F_MED,
        GRAY,
        x + CW // 2,
        y + 145)

    txc(
        surf,
        "???",
        F_MED,
        GRAY,
        x + CW // 2,
        y + 170)

def draw_start_menu(surf, g, mouse):
    surf.fill(BG)
    txc(surf, "COURTROOM BATTLE", pygame.font.SysFont("Impact", 80), GOLD, W//2, 130)
    
    cur_p = g.profiles[g.current_slot]["name"]
    g.btn_profile.label = f"Profile: {cur_p}"
    g.btn_profile.draw(surf, mouse)
    
    if g.has_save():
        g.btn_continue.draw(surf, mouse)
        g.btn_new_run.draw(surf, mouse)
    else:
        g.btn_start_play.draw(surf, mouse)
        
    g.btn_history.draw(surf, mouse)

    g.btn_collection.draw(surf, mouse)
    g.btn_extras.draw(surf, mouse)
    g.btn_start_set.draw(surf, mouse)

    g.btn_quit_game.draw(surf, mouse)


def draw_collection(
    surf,
    g,
    mouse):

    surf.fill(BG)
    # TITLE
    txc(
        surf,
        "COLLECTION",
        F_BIG,
        GOLD,
        W // 2,
        35)
    # TABS
    tabs = [
        (
            "PHOENIX",
            RED_D),
        (
            "FRANZISKA",
            PURPLE_D),
        (
            "Relics",
            GOLD)
    ]

    tab_w = 190
    tab_h = 40
    gap = 18

    total_width = (
        tab_w * 3
        + gap * 2)

    start_x = (
        W - total_width) // 2

    g.collection_tab_rects = []

    for i, (
        tab_name,
        tab_col) in enumerate(tabs):

        rect = pygame.Rect(
            start_x
            + i * (
                tab_w + gap),
            70,
            tab_w,
            tab_h)

        active = (
            getattr(g, "collection_tab", "Bruiser")
            == tab_name)

        hover = rect.collidepoint(
            mouse)

        if active:
            bg_col = tab_col
            border_col = WHITE

        elif hover:
            bg_col = PANEL
            border_col = tab_col

        else:
            bg_col = PANEL
            border_col = BORDER

        rrect(
            surf,
            bg_col,
            rect,
            7,
            2,
            border_col)

        txc(
            surf,
            tab_name.upper(),
            F_MED,
            WHITE,
            rect.centerx,
            rect.centery)

        g.collection_tab_rects.append(
            (
                tab_name,
                rect)
        )
    # PROGRESS INFO
    active_tab = getattr(g, "collection_tab", "Bruiser")

    if active_tab in (
        "Bruiser",
        "Assassin"):

        level = g.get_class_level(
            active_tab)

        wins = g.get_class_wins(
            active_tab)

        txc(
            surf,
            f"{active_tab.upper()}  |  LEVEL {level}  |  WINS {wins}",
            F_MED,
            GRAY_L,
            W // 2,
            128)
    # SCROLLABLE CONTENT AREA
    content_top = 165
    content_bottom = H - 55

    old_clip = surf.get_clip()

    surf.set_clip(
        pygame.Rect(0, content_top, W, content_bottom - content_top)
    )
    # CARDS
    if active_tab in (
        "Bruiser",
        "Assassin"):

        class_name = active_tab

        card_names = []

        for name, data in CARDS.items():

            card_class = str(
                data.get("class", "Any")
            ).capitalize()


            if card_class in (
                "Any",
                class_name):
                card_names.append(
                    name)

        rarity_order = {
            "common": 0,
            "rare": 1,
            "epic": 2,
            "legendary": 3
        }

        card_names.sort(
            key=lambda name: (
                rarity_order.get(
                    CARDS[name].get("rarity", "common"),
                    0),
                CARDS[name].get("cost", 0),
                name)
        )

        unlocked_count = sum(
            1
            for name in card_names
            if collection_item_unlocked(
                g,
                CARDS[name],
                class_name)
        )

        txc(
            surf,
            f"Cards: {unlocked_count}/{len(card_names)}",
            F_MED,
            GOLD,
            W // 2,
            150)
        # GRID
        cols = 6

        gap_x = 25
        gap_y = 28

        grid_width = (
            cols * CW
            + (
                cols - 1) * gap_x
        )

        grid_x = (
            W - grid_width) // 2
        rows = (
            len(card_names)
            + cols - 1) // cols

        content_height = (
            rows * CH
            + max(0, rows - 1) * gap_y
        )

        visible_height = (
            content_bottom
            - 180)

        min_scroll = min(
            0,
            visible_height
            - content_height)

        g.collection_min_scroll = (
            min_scroll)

        rows = (
            len(card_names)
            + cols - 1) // cols

        content_height = (
            rows * CH
            + max(0, rows - 1) * gap_y
        )

        visible_height = (
            content_bottom
            - 180)

        min_scroll = min(
            0,
            visible_height
            - content_height)

        g.collection_min_scroll = (
            min_scroll)

        start_y = (
            180
            + getattr(g, "collection_scroll", 0)
        )

        for i, name in enumerate(
            card_names):

            row = i // cols
            col = i % cols

            x = (
                grid_x
                + col
                * (
                    CW + gap_x)
            )

            y = (
                start_y
                + row
                * (
                    CH + gap_y)
            )

            if (
                y + CH < 120
                or y > H - 55):
                continue

            data = CARDS[
                name
            ]

            unlocked = (
                collection_item_unlocked(
                    g,
                    data,
                    class_name)
            )

            if unlocked:

                draw_card(
                    surf,
                    name,
                    x,
                    y,
                    99,
                    g=g)

            else:

                draw_locked_collection_card(
                    surf,
                    x,
                    y,
                    data.get("rarity", "common")
                )
    # RELICS
    elif active_tab == "Relics":

        relic_names = list(
            RELICS.keys())

        def relic_sort_key(
            relic_name):

            data = RELICS.get(relic_name, {})

            relic_class = str(
                data.get("class", "Any")
            ).capitalize()

            class_order = {
                "Any": 0,
                "Bruiser": 1,
                "Assassin": 2
            }

            return (
                class_order.get(relic_class, 0),
                int(
                    data.get("unlock_level", 0)
                ),
                relic_name)

        relic_names.sort(
            key=relic_sort_key)

        unlocked_relics = 0

        for relic_name in relic_names:

            data = RELICS.get(relic_name, {})

            relic_class = str(
                data.get("class", "Any")
            ).capitalize()

            if relic_class == "Bruiser":

                unlocked = (
                    collection_item_unlocked(
                        g,
                        data,
                        "Bruiser")
                )

            elif relic_class == "Assassin":

                unlocked = (
                    collection_item_unlocked(
                        g,
                        data,
                        "Assassin")
                )

            else:

                unlocked = True

            if unlocked:
                unlocked_relics += 1

        txc(
            surf,
            f"Relics: {unlocked_relics}/{len(relic_names)}",
            F_MED,
            GOLD,
            W // 2,
            140)
        # RELIC GRID
        cols = 4

        relic_w = 220
        relic_h = 105

        gap_x = 20
        gap_y = 18

        total_width = (
            cols * relic_w
            + (
                cols - 1) * gap_x
        )

        grid_x = (
            W - total_width) // 2

        rows = (
            len(relic_names)
            + cols - 1) // cols

        content_height = (
            rows * relic_h
            + max(0, rows - 1) * gap_y)

        visible_height = (
            content_bottom
            - 175)

        min_scroll = min(
            0,
            visible_height
            - content_height)

        g.collection_min_scroll = (
            min_scroll)

        start_y = (
            175
            + getattr(g, "collection_scroll", 0)
        )

        for i, relic_name in enumerate(
            relic_names):

            row = i // cols
            col = i % cols

            x = (
                grid_x
                + col
                * (
                    relic_w
                    + gap_x)
            )

            y = (
                start_y
                + row
                * (
                    relic_h
                    + gap_y)
            )

            if (
                y + relic_h < 120
                or y > H - 55):
                continue

            data = RELICS.get(relic_name, {})

            relic_class = str(
                data.get("class", "Any")
            ).capitalize()
            # CLASS OUTLINE
            if relic_class == "Bruiser":

                outline_col = RED

                unlocked = (
                    collection_item_unlocked(
                        g,
                        data,
                        "Bruiser")
                )

            elif relic_class == "Assassin":

                outline_col = PURPLE_D

                unlocked = (
                    collection_item_unlocked(
                        g,
                        data,
                        "Assassin")
                )

            else:

                outline_col = GRAY

                unlocked = True

            rect = pygame.Rect(x, y, relic_w, relic_h)

            if not unlocked:
                # LOCKED RELIC
                rrect(
                    surf,
                    (5, 5, 7),
                    rect,
                    8,
                    3,
                    outline_col)

                icon_rect = pygame.Rect(x + 12, y + 18, 55, 55)

                rrect(
                    surf,
                    (2, 2, 3),
                    icon_rect,
                    7,
                    2,
                    outline_col)

                txc(
                    surf,
                    "?",
                    F_BIG,
                    GRAY,
                    icon_rect.centerx,
                    icon_rect.centery)

                txc(
                    surf,
                    "LOCKED",
                    F_MED,
                    GRAY,
                    x + 142,
                    y + 43)

                txc(
                    surf,
                    "???",
                    F_MED,
                    GRAY,
                    x + 142,
                    y + 67)

                continue
            # UNLOCKED RELIC
            hover = rect.collidepoint(
                mouse)

            rrect(
                surf,
                (
                    45,
                    38,
                    55)
                if hover
                else PANEL,
                rect,
                8,
                3,
                outline_col)

            icon_rect = pygame.Rect(x + 10, y + 16, 58, 58)

            rrect(
                surf,
                (60, 40, 20),
                icon_rect,
                7,
                2,
                outline_col)

            txc(
                surf,
                relic_name[0],
                F_BIG,
                outline_col,
                icon_rect.centerx,
                icon_rect.centery)

            txt(
                surf,
                relic_name,
                F_MED,
                WHITE,
                x + 78,
                y + 12)

            desc = data.get("desc", "")

            words = desc.split()

            lines = []
            line = ""

            max_width = (
                relic_w - 88)

            for word in words:

                test = (
                    line
                    + " "
                    + word).strip()

                if (
                    F_MED.size(
                        test)[0]
                    <= max_width):

                    line = test

                else:

                    if line:
                        lines.append(
                            line)

                    line = word

            if line:
                lines.append(
                    line)

            for line_i, line_text in enumerate(
                lines[:4]):

                txt(
                    surf,
                    line_text,
                    F_MED,
                    GRAY_L,
                    x + 78,
                    y
                    + 37
                    + line_i * 15)

    surf.set_clip(
        old_clip)
    # BACK
    g.collection_back_rect = (
        pygame.Rect(W // 2 - 90, H - 45, 180, 34)
    )

    hover = (
        g.collection_back_rect.collidepoint(
            mouse)
    )

    rrect(
        surf,
        RED_D
        if hover
        else PANEL,
        g.collection_back_rect,
        7,
        2,
        RED)

    txc(
        surf,
        "BACK",
        F_MED,
        WHITE,
        g.collection_back_rect.centerx,
        g.collection_back_rect.centery)

def draw_history_build(
    surf,
    g,
    mouse):

    surf.fill(BG)

    history = (
        g.get_history()
        if hasattr(g, "get_history")
        else [])

    index = getattr(g, "history_build_index", 0)

    if not (
        0 <= index < len(history)):

        g.state = "run_history"
        return

    run = history[index]

    final_deck = run.get("final_deck", [])

    relics = run.get("relics", [])
    # TITLE
    txc(
        surf,
        "FINAL BUILD",
        F_BIG,
        GOLD,
        W // 2,
        38)

    txc(
        surf,
        (
            f"{run.get('character', 'Unknown')}  |  "
            f"{run.get('result', 'UNKNOWN')}  |  "
            f"Act {run.get('acts', 1)}"),
        F_MED,
        WHITE,
        W // 2,
        75)
    # PANELS
    deck_panel = pygame.Rect(20, 105, W - 370, H - 175)

    relic_panel = pygame.Rect(W - 330, 105, 310, H - 175)

    rrect(
        surf,
        PANEL,
        deck_panel,
        9,
        2,
        BORDER)

    rrect(
        surf,
        PANEL,
        relic_panel,
        9,
        2,
        BORDER)

    txc(
        surf,
        "FINAL DECK",
        F_MED,
        GOLD,
        deck_panel.centerx,
        deck_panel.top + 22)

    txc(
        surf,
        f"{len(final_deck)} CARDS",
        F_MED,
        GRAY_L,
        deck_panel.centerx,
        deck_panel.top + 45)

    txc(
        surf,
        "RELICS",
        F_MED,
        GOLD,
        relic_panel.centerx,
        relic_panel.top + 22)
    # GROUP DUPLICATE CARDS
    grouped = {}

    for card_data in final_deck:

        if isinstance(card_data, dict):

            name = card_data.get("name", "Unknown")

            upgraded = bool(
                card_data.get("upgraded", False)
            )

        else:


            name = str(card_data)
            upgraded = False

        key = (
            name,
            upgraded)

        grouped[key] = (
            grouped.get(key, 0)
            + 1)

    deck_entries = list(
        grouped.items())

    rarity_order = {
        "common": 0,
        "rare": 1,
        "epic": 2,
        "legendary": 3
    }

    deck_entries.sort(
        key=lambda item: (
            rarity_order.get(
                CARDS.get(item[0][0], {}).get("rarity", "common"),
                0),
            item[0][0])
    )
    # CARD NAME GRID
    g.history_build_card_rects = []

    cols = 3

    gap = 10

    entry_w = (
        deck_panel.width
        - 30
        - gap * (
            cols - 1)
    ) // cols

    entry_h = 34

    start_x = (
        deck_panel.left + 10)

    start_y = (
        deck_panel.top + 70)

    hovered_card = None

    for i, (
        card_key,
        count) in enumerate(
        deck_entries):

        name, upgraded = card_key

        row = i // cols
        col = i % cols

        x = (
            start_x
            + col
            * (
                entry_w + gap)
        )

        y = (
            start_y
            + row * 40)

        rect = pygame.Rect(x, y, entry_w, entry_h)

        hover = rect.collidepoint(
            mouse)

        rarity = CARDS.get(name, {}).get("rarity", "common")

        rarity_col = {
            "common": C_COMMON,
            "rare": C_RARE,
            "epic": C_EPIC,
            "legendary": C_LEGENDARY
        }.get(rarity, BORDER)

        rrect(
            surf,
            (
                55,
                45,
                65)
            if hover
            else (
                28,
                26,
                38),
            rect,
            6,
            2,
            rarity_col)

        display_name = (
            name + "+"
            if upgraded
            else name)

        if count > 1:
            display_name += (
                f" x{count}")

        txc(
            surf,
            display_name,
            F_MED,
            GREEN
            if upgraded
            else WHITE,
            rect.centerx,
            rect.centery)

        g.history_build_card_rects.append(
            (
                rect,
                name,
                upgraded)
        )

        if hover:
            hovered_card = (
                name,
                upgraded)
    # RELICS
    relic_y = (
        relic_panel.top + 52)

    hovered_relic = None

    for i, relic_name in enumerate(
        relics):

        rect = pygame.Rect(relic_panel.left + 12, relic_y + i * 31, relic_panel.width - 24, 27)

        hover = rect.collidepoint(
            mouse)

        rrect(
            surf,
            (
                60,
                45,
                30)
            if hover
            else (
                28,
                26,
                38),
            rect,
            5,
            1,
            GOLD)

        txc(
            surf,
            relic_name,
            F_MED,
            GOLD if hover else WHITE,
            rect.centerx,
            rect.centery)

        if hover:
            hovered_relic = (
                relic_name)
    # CARD HOVER PREVIEW
    if hovered_card:

        name, upgraded = (
            hovered_card)

        preview_x = (
            relic_panel.centerx
            - CW // 2)

        preview_y = (
            H - CH - 85)

        draw_card(
            surf,
            name,
            preview_x,
            preview_y,
            99,
            g=g,
            upgraded=upgraded)
    # RELIC HOVER DESCRIPTION
    elif hovered_relic:

        desc = RELICS.get(hovered_relic, {}).get("desc", "")

        box = pygame.Rect(relic_panel.left + 15, H - 170, relic_panel.width - 30, 80)

        rrect(
            surf,
            (
                20,
                18,
                28),
            box,
            7,
            2,
            GOLD)

        txc(
            surf,
            hovered_relic,
            F_MED,
            GOLD,
            box.centerx,
            box.top + 18)

        words = desc.split()

        lines = []
        line = ""

        for word in words:

            test = (
                line + " " + word).strip()

            if (
                F_SML.size(
                    test)[0]
                <= box.width - 20):
                line = test

            else:

                if line:
                    lines.append(
                        line)

                line = word

        if line:
            lines.append(
                line)

        for line_i, line_text in enumerate(
            lines[:3]):

            txc(
                surf,
                line_text,
                F_SML,
                WHITE,
                box.centerx,
                box.top
                + 42
                + line_i * 15)
    # BACK
    g.history_build_back_rect = (
        pygame.Rect(20, H - 55, 160, 40)
    )

    hover = (
        g.history_build_back_rect.collidepoint(
            mouse)
    )

    rrect(
        surf,
        RED_D
        if hover
        else PANEL,
        g.history_build_back_rect,
        7,
        2,
        RED)

    txc(
        surf,
        "BACK",
        F_MED,
        WHITE,
        g.history_build_back_rect.centerx,
        g.history_build_back_rect.centery)

def draw_abandon_confirm(surf, g, mouse):
    surf.fill(BG)
    txc(surf, "ABANDON CURRENT RUN?", F_BIG, RED, W//2, H//2 - 50)
    txc(surf, "All saved progress for this profile will be lost.", F_MED, WHITE, W//2, H//2)
    g.btn_abandon_yes.draw(surf, mouse)
    g.btn_abandon_no.draw(surf, mouse)

def draw_campfire(surf, g, mouse):
    surf.fill(BG)
    txc(surf, "CAMPFIRE", F_BIG, ORANGE, W//2, 120)
    txc(surf, f"HP: {g.php} / {g.pmx}", F_MED, RED, W//2, 170)
    heal_amount = int(
        g.pmx * 0.30)

    actual_heal = min(
        heal_amount,
        max(0, g.pmx - g.php))

    g.cf_rest.label = (
        f"Rest (heal 30% = +{actual_heal} HP)")    
    g.cf_rest.draw(surf, mouse)

    g.cf_upg.draw(surf, mouse)
    # MOLTEN HAMMER - NO UPGRADES
    if (
        "Molten Hammer"
        in getattr(g, "relics", [])):

        x_rect = g.cf_upg.rect.inflate(14, 14)

        pygame.draw.line(
            surf,
            RED,
            x_rect.topleft,
            x_rect.bottomright,
            10)

        pygame.draw.line(
            surf,
            RED,
            x_rect.topright,
            x_rect.bottomleft,
            10)

    g.cf_leave.draw(surf, mouse)

def draw_campfire_upgrade(surf, g, mouse):

    surf.fill(BG)

    txc(
        surf,
        "UPGRADE A CARD",
        F_BIG,
        ORANGE,
        W // 2,
        40)

    txc(
        surf,
        "Select any card to preview its upgrade.",
        F_MED,
        GRAY_L,
        W // 2,
        72)


    upgradeable_cards = [
        card
        for card in g.deck
        if not card.upgraded
        and card.name in CARD_UPGRADES
    ]


    g.upgrade_card_rects = []

    cols = 4

    start_x = 40
    start_y = 105

    gap_x = 155
    gap_y = 215


    for i, card in enumerate(upgradeable_cards):

        col = i % cols
        row = i // cols

        x = start_x + col * gap_x

        y = (
            start_y
            + row * gap_y
            + getattr(g, "upgrade_scroll", 0))


        if y < -CH or y > H:
            continue


        is_selected = (
            card is getattr(g, "upgrade_selected_card", None)
        )


        draw_card(
            surf,
            card.name,
            x,
            y,
            99,
            selected=is_selected,
            g=g,
            upgraded=False)


        g.upgrade_card_rects.append(
            (
                pygame.Rect(x, y, CW, CH),
                card)
        )


    selected_card = getattr(g, "upgrade_selected_card", None)


    preview_x = W - CW - 55
    preview_y = 190


    if selected_card:

        txc(
            surf,
            "PREVIEW",
            F_MED,
            GREEN,
            preview_x + CW // 2,
            150)


        draw_card(
            surf,
            selected_card.name,
            preview_x,
            preview_y,
            99,
            g=g,
            upgrade_preview=True)

    else:

        txc(
            surf,
            "Select a card",
            F_MED,
            GRAY_L,
            preview_x + CW // 2,
            280)


    g.upgrade_confirm_rect = pygame.Rect(W - 235, H - 115, 190, 45)

    g.upgrade_back_rect = pygame.Rect(W - 235, H - 60, 190, 38)


    can_confirm = (
        selected_card is not None)


    rrect(
        surf,
        GREEN_D if can_confirm else GRAY,
        g.upgrade_confirm_rect,
        8,
        2,
        GREEN if can_confirm else BORDER)

    txc(
        surf,
        "CONFIRM UPGRADE",
        F_MED,
        WHITE,
        g.upgrade_confirm_rect.centerx,
        g.upgrade_confirm_rect.centery)


    rrect(
        surf,
        PANEL,
        g.upgrade_back_rect,
        8,
        2,
        BORDER)

    txc(
        surf,
        "BACK",
        F_MED,
        WHITE,
        g.upgrade_back_rect.centerx,
        g.upgrade_back_rect.centery)
def draw_settings_menu(
    surf,
    g,
    mouse):

    surf.fill(BG)

    txc(
        surf,
        "SETTINGS",
        F_BIG,
        WHITE,
        W // 2,
        70)
    # DISPLAY MODE
    txc(
        surf,
        "DISPLAY MODE",
        F_MED,
        GRAY_L,
        W // 2,
        125)

    g.display_mode_rect = pygame.Rect(W // 2 - 160, 145, 320, 45)

    mode_hover = (
        g.display_mode_rect.collidepoint(
            mouse)
    )

    rrect(
        surf,
        BLUE_D
        if mode_hover
        else PANEL,
        g.display_mode_rect,
        8,
        2,
        BLUE)

    txc(
        surf,
        g.display_mode.upper(),
        F_MED,
        WHITE,
        g.display_mode_rect.centerx,
        g.display_mode_rect.centery)
    # RESOLUTION
    txc(
        surf,
        "RESOLUTION",
        F_MED,
        GRAY_L,
        W // 2,
        215)

    g.display_resolution_rect = (
        pygame.Rect(W // 2 - 160, 235, 320, 45))

    if (
        g.display_mode
        == "Fullscreen"):

        desktop_w, desktop_h = (
            get_desktop_resolution())

        resolution_text = (
            f"DESKTOP "
            f"{desktop_w}x{desktop_h}")

        resolution_border = GRAY

    else:

        res_w, res_h = (
            g.display_resolution)

        resolution_text = (
            f"{res_w}x{res_h}")

        resolution_border = GOLD

    res_hover = (
        g.display_resolution_rect.collidepoint(
            mouse)
        and g.display_mode
        in (
            "Windowed",
            "Borderless")
    )

    rrect(
        surf,
        BLUE_D
        if res_hover
        else PANEL,
        g.display_resolution_rect,
        8,
        2,
        resolution_border)

    txc(
        surf,
        resolution_text,
        F_MED,
        WHITE
        if g.display_mode in (
            "Windowed",
            "Borderless")
        else GRAY_L,
        g.display_resolution_rect.centerx,
        g.display_resolution_rect.centery)
    # APPLY
    g.display_apply_rect = (
        pygame.Rect(W // 2 - 160, 300, 320, 45
)
    )

    apply_hover = (
        g.display_apply_rect.collidepoint(
            mouse)
    )

    rrect(
        surf,
        GREEN_D
        if apply_hover
        else PANEL,
        g.display_apply_rect,
        8,
        2,
        GREEN)

    txc(
        surf,
        "APPLY DISPLAY SETTINGS",
        F_MED,
        WHITE,
        g.display_apply_rect.centerx,
        g.display_apply_rect.centery)
    if getattr(g, "display_restart_notice", False):

        txc(
            surf,
            "Saved - restart required to apply this resolution.",
            F_SML,
            GOLD,
            W // 2,
            355)
    # MUSIC VOLUME
    txc(
        surf,
        f"MUSIC  {int(g.music_volume * 100)}%",
        F_MED,
        WHITE,
        W // 2,
        382)

    g.music_slider_rect = pygame.Rect(W // 2 - 150, 405, 300, 10)

    pygame.draw.rect(
        surf,
        (55, 55, 70),
        g.music_slider_rect,
        border_radius=5)

    music_fill = pygame.Rect(
        g.music_slider_rect.left,
        g.music_slider_rect.top,
        int(
            g.music_slider_rect.width
            * g.music_volume),
        g.music_slider_rect.height)

    pygame.draw.rect(
        surf,
        GREEN,
        music_fill,
        border_radius=5)

    music_knob_x = int(
        g.music_slider_rect.left
        + g.music_slider_rect.width
        * g.music_volume)

    pygame.draw.circle(
        surf,
        WHITE,
        (
            music_knob_x,
            g.music_slider_rect.centery),
        8)
    # SFX VOLUME
    txc(
        surf,
        f"SFX  {int(g.sfx_volume * 100)}%",
        F_MED,
        WHITE,
        W // 2,
        442)

    g.sfx_slider_rect = pygame.Rect(W // 2 - 150, 465, 300, 10)

    pygame.draw.rect(
        surf,
        (55, 55, 70),
        g.sfx_slider_rect,
        border_radius=5)

    sfx_fill = pygame.Rect(
        g.sfx_slider_rect.left,
        g.sfx_slider_rect.top,
        int(
            g.sfx_slider_rect.width
            * g.sfx_volume),
        g.sfx_slider_rect.height)

    pygame.draw.rect(
        surf,
        GOLD,
        sfx_fill,
        border_radius=5)

    sfx_knob_x = int(
        g.sfx_slider_rect.left
        + g.sfx_slider_rect.width
        * g.sfx_volume)

    pygame.draw.circle(
        surf,
        WHITE,
        (
            sfx_knob_x,
            g.sfx_slider_rect.centery),
        8)
    # Останали settings.
    g.btn_set_ctrls.draw(surf, mouse)

    if (
        g.prev_settings_state
        != "start_menu"):

        g.btn_set_quit.draw(surf, mouse)

        g.btn_set_quit_desktop.draw(surf, mouse)

    g.btn_set_back.draw(surf, mouse)

def draw_run_history(surf, g, mouse):
    surf.fill(BG)
    txc(surf, "RUN HISTORY", F_BIG, GOLD, W//2, 40)

    history = g.get_history() if hasattr(g, 'get_history') else []
    if not history:
        txc(surf, "No past runs found for this profile.", F_MED, GRAY_L, W//2, H//2)
        if hasattr(g, 'btn_hist_back'): g.btn_hist_back.draw(surf, mouse)
        return


    rrect(surf, PANEL, (20, 80, 260, H - 160), 8, 2, BORDER)
    for i, run in enumerate(history):
        btn_y = 90 + i * 42
        if btn_y + 38 > H - 80: break 
        
        is_sel = (i == g.selected_history_index)
        b_col = GOLD if is_sel else (GREEN_D if run.get("result") == "VICTORY" else RED_D)
        
        r_rect = pygame.Rect(25, btn_y, 250, 36)
        rrect(surf, b_col, r_rect, 6)
        
        lbl = f"#{len(history)-i} {run.get('result', 'UNKNOWN')} - Fl.{run.get('floors', 0)}"
        txc(surf, lbl, F_MED, WHITE, r_rect.centerx, r_rect.centery)

    rrect(surf, PANEL, (290, 80, W - 310, H - 160), 8, 2, BORDER)
    
    if 0 <= g.selected_history_index < len(history):
        run = history[g.selected_history_index]
        res_col = GREEN if run.get("result") == "VICTORY" else RED
        char_name = run.get("character", "Unknown")
        hero_name = {
            "Bruiser": "Phoenix",
            "BRUISER": "Phoenix",
            "Assassin": "Franziska",
            "ASSASSIN": "Franziska"
        }.get(char_name, char_name)
        floors_reached = run.get("floors", 0)
        

        txc(surf, f"Class: {hero_name} | Result: {run.get('result', '')} | Floors: {floors_reached}/10", F_MED, res_col, 290 + (W-310)//2, 105)


        logs = run.get("log", [])
        

        sorted_logs = sorted(logs, key=lambda x: x.get("floor", 0))

        start_y = 140 + g.history_scroll
        for entry in sorted_logs:
            if 130 <= start_y <= H - 100:
                fl_num = entry.get('floor', '?')
                e_lbl = f"Floor {fl_num}: {entry.get('enemy', 'Unknown')}"
                d_lbl = f"Dmg Dealt: {entry.get('dmg_dealt', 0)} | Dmg Taken: {entry.get('dmg_taken', 0)}"
                mg_lbl = f"Minigame: {minigame_display_name(entry.get('minigame', 'None'))} | Choice: {entry.get('chosen_reward', 'None')}"
                
                txt(surf, e_lbl, F_MED, GOLD, 310, start_y)
                txt(surf, d_lbl, F_MED, WHITE, 310, start_y + 16)
                txt(surf, mg_lbl, F_MED, GRAY_L, 530, start_y + 16)
                pygame.draw.line(surf, BORDER, (300, start_y + 34), (W - 30, start_y + 34), 1)
            start_y += 40

    if hasattr(g, 'btn_hist_back'): g.btn_hist_back.draw(surf, mouse)

def draw_controls_select(surf, g, mouse):
    surf.fill(BG)
    txc(surf, "SELECT MINIGAME", F_BIG, GOLD, W//2, 80)
    
    games = ["HaremMaker", "HaremRunner", "ManPac", "BoxingBoss","UndertaleBoss"]
    btns = []
    sy = 130
    for i, mg in enumerate(games):
        btn = Btn(minigame_display_name(mg), W//2 - 125, sy + i*60, 250, 50, BLUE_D)
        btn.draw(surf, mouse)
        btns.append((btn, mg))
        
    g.btn_set_back.draw(surf, mouse)
    return btns

def draw_controls_menu(surf, g, mouse):
    surf.fill(BG)
    mg = getattr(g, 'selected_minigame_ctrls', 'HaremMaker')
    txc(surf, f"{minigame_display_name(mg)} CONTROLS", F_BIG, GOLD, W//2, 50)
    txc(surf, "Click an action to rebind, press ESC to cancel.", F_MED, GRAY_L, W//2, 90)

    start_y = 150
    g.temp_ctrl_btns = []
    
    actions = GLOBAL_CONTROLS.get(mg, {})
    y = start_y
    
    for action, key_val in actions.items():
        lbl = F_MED.render(f"{action}:", True, WHITE)
        surf.blit(lbl, (W//2 - 150, y + 5))
        
        if g.awaiting_key == (mg, action):
            btn_txt = "PRESS KEY..."
            btn_col = ORANGE
        else:
            btn_txt = pygame.key.name(key_val).upper()
            btn_col = GRAY
        
        btn = Btn(btn_txt, W//2 + 10, y, 150, 30, btn_col)
        btn.draw(surf, mouse)
        g.temp_ctrl_btns.append((btn, mg, action))
        y += 45

    g.btn_set_back.draw(surf, mouse)

def draw_map(surf, g):
    surf.fill(BG)
    scroll_y = getattr(g, 'map_scroll_y', 0)

    pos = screen_to_virtual(
        pygame.mouse.get_pos(),
        W,
        H)
    hovered_node = None

  

        # SKIP TO BOSS
    g.skip_boss_rect = pygame.Rect(W - 170, 55, 160, 40)

    is_skip_hover = (
        g.skip_boss_rect.collidepoint(
            pos)
    )

    rrect(
        surf,
        PURPLE_D
        if is_skip_hover
        else PANEL,
        g.skip_boss_rect,
        r=8,
        bw=2,
        bc=GOLD)

    txc(
        surf,
        "SKIP TO BOSS",
        F_MED,
        WHITE,
        g.skip_boss_rect.centerx,
        g.skip_boss_rect.centery)


 

   
    for f in range(len(g.map_data) - 1):
        for node in g.map_data[f]:
            for nxt_i in node["next_nodes"]:
                nxt_node = g.map_data[f + 1][nxt_i]
                

                is_path = (f, node["idx"]) in g.path_history and (f + 1, nxt_i) in g.path_history
                if is_path:
                    col = GOLD
                    width = 4
                elif getattr(g, 'current_node_idx', None) is not None and f == g.floor and nxt_i in g.map_data[g.floor][g.current_node_idx]["next_nodes"]:
                    col = (100, 220, 255) 
                    width = 3
                else:
                    col = (70, 60, 90) 
                    width = 2
                

                src_y = node["y"] + scroll_y
                dst_y = nxt_node["y"] + scroll_y
                
     
                if -100 <= src_y <= H + 100 or -100 <= dst_y <= H + 100:
                    pygame.draw.line(surf, col, (node["x"], src_y), (nxt_node["x"], dst_y), width)

    # 2. ЧЕРТАНЕ НА NODOVETE
    for f, floor_nodes in enumerate(g.map_data):
        for i, node in enumerate(floor_nodes):
            x = node["x"]
    
            y = node["y"] + scroll_y 
            
    
            if -50 <= y <= H + 50:
                is_edgeworth = (
                    node["type"] == "boss"
                    and node.get("minigame") == "None")

                if is_edgeworth:
                    r = 38
                elif node["type"] == "boss":
                    r = 28
                else:
                    r = 22
                

                is_visited = (f, i) in g.path_history
                is_current = (f == g.floor and i == getattr(g, 'current_node_idx', None))
                
       
                if getattr(g, 'current_node_idx', None) is None:
                    is_selectable = (f == 0) 
                else:
                    curr_node = g.map_data[g.floor][g.current_node_idx]
                    is_selectable = (f == g.floor + 1 and i in curr_node["next_nodes"])

        
                if node["type"] == "boss": bg_col = RED_D
                elif node["type"] == "elite": bg_col = PURPLE_D
                elif node["type"] == "shop": bg_col = GOLD
                elif node["type"] == "campfire": bg_col = GREEN_D
                elif node["type"] == "chest": bg_col = (220, 220, 60) 
                elif node["type"] == "?": bg_col = BLUE_D
                else: bg_col = (120, 40, 40)

       
                if is_selectable:
                    border_col = GREEN
                    bw = 4
                elif is_current:
                    border_col = WHITE
                    bw = 3
                elif is_visited:
                    border_col = GRAY
                    bw = 2
                else:
                    border_col = BORDER
                    bw = 2


                pygame.draw.circle(surf, bg_col, (x, y), r)
                pygame.draw.circle(surf, border_col, (x, y), r, bw)

            
                labels = {"enemy": "E", "elite": "X", "shop": "$", "campfire": "C", "boss": "B", "chest": "R", "?": "?"} # <-- ДОБАВЕН "?"
                txt(surf, labels.get(node["type"], "?"), F_MED, WHITE if node["type"] not in ["shop", "chest"] else BG, x - 7, y - 10)
                # FINAL / OPTIONAL BOSS LABELS
                if node["type"] == "boss":

                    is_final_boss = (
                        node.get("minigame") == "None")

                    if is_final_boss:

                        label_text = "FINAL BOSS"
                        label_color = RED

                    else:

                        label_text = "OPTIONAL BOSS"
                        label_color = GOLD

                    label_y = y - r - 42

                    txc(
                        surf,
                        label_text,
                        F_TINY_BOLD,
                        label_color,
                        x,
                        label_y)

  
                    pygame.draw.line(
                        surf,
                        label_color,
                        (x, label_y + 12),
                        (x, y - r - 6),
                        3)

                    pygame.draw.polygon(
                        surf,
                        label_color,
                        [
                            (x - 6, y - r - 12),
                            (x + 6, y - r - 12),
                            (x, y - r - 4)
                        ])

                if math.hypot(x - pos[0], y - pos[1]) <= r:
                    hovered_node = node

    # HOVER TOOLTIP 
    if hovered_node:
        tx, ty = pos[0] + 15, pos[1] + 15
        box_w, box_h = 270, 150
        if tx + box_w > W: tx = pos[0] - box_w - 10
        if ty + box_h > H: ty = pos[1] - box_h - 10

        rrect(surf, PANEL, (tx, ty, box_w, box_h), r=8, bw=2, bc=BORDER)

        ntype = hovered_node["type"].upper()
        txt(surf, f"Floor {hovered_node['floor'] + 1}: {ntype}", F_TINY_BOLD, GOLD, tx + 10, ty + 10)

        if (hovered_node["type"] in ("enemy", "elite", "boss") and hovered_node.get("enemy")):
            minigame_name = minigame_display_name(hovered_node.get("minigame","Unknown"))

            reward_rarity = hovered_node.get("reward_rarity", "Common")

            rarity_colors = {
                "Common": C_COMMON,
                "Rare": C_RARE,
                "Epic": C_EPIC,
                "Legendary": C_LEGENDARY
            }

            rarity_color = rarity_colors.get(reward_rarity, WHITE)

            txt(
                surf,
                f"Minigame: {minigame_name}",
                F_TINY_BOLD,
                GOLD,
                tx + 10,
                ty + 94)

            txt(
                surf,
                f"Card Reward: {reward_rarity}",
                F_TINY_BOLD,
                rarity_color,
                tx + 10,
                ty + 114)
            enemy_data = hovered_node["enemy"]

            if isinstance(enemy_data, list):
                enemies = enemy_data
            else:
                enemies = [enemy_data]

            names = ", ".join(
                e.get("name", "Enemy")
                for e in enemies)

            total_hp = sum(
                e.get("hp", 0)
                for e in enemies)

            txt(
                surf,
                f"Enemies: {names}",
                F_MED,
                WHITE,
                tx + 10,
                ty + 32)

            txt(
                surf,
                f"Total HP: {total_hp}",
                F_MED,
                WHITE,
                tx + 10,
                ty + 52)

            txt(
                surf,
                f"Count: {len(enemies)}",
                F_MED,
                GREEN,
                tx + 10,
                ty + 72)
            # BOSS CONSEQUENCE
            if hovered_node["type"] == "boss":

                is_final_boss = (
                    hovered_node.get("minigame") == "None")

                if is_final_boss:

                    txt(
                        surf,
                        "FINAL BOSS",
                        F_TINY_BOLD,
                        RED,
                        tx + 10,
                        ty + 132)

                    txt(
                        surf,
                        "Victory ends the run.",
                        F_TINY_BOLD,
                        WHITE,
                        tx + 100,
                        ty + 132)

                else:

                    txt(
                        surf,
                        "OPTIONAL:",
                        F_TINY_BOLD,
                        GOLD,
                        tx + 10,
                        ty + 132)

                    txt(
                        surf,
                        "Win -> Floor 1, keep deck.",
                        F_TINY_BOLD,
                        GREEN,
                        tx + 90,
                        ty + 132)
        elif hovered_node["type"] == "campfire":
            txt(surf, "Rest (Heal 30% HP)", F_MED, WHITE, tx + 10, ty + 35)
            txt(surf, "or Upgrade a Card", F_MED, WHITE, tx + 10, ty + 55)
        elif hovered_node["type"] == "shop":
            txt(surf, "Spend Gold on Cards!", F_MED, WHITE, tx + 10, ty + 40)
        elif hovered_node["type"] == "chest":
            txt(surf, "Free Treasure!", F_MED, GOLD, tx + 10, ty + 40)
        elif hovered_node["type"] == "?":
            txt(surf, "Unknown Event", F_MED, (200, 150, 255), tx + 10, ty + 40)
            txt(surf, "Risk or Reward?", F_MED, WHITE, tx + 10, ty + 60)


def draw_combat(surf, g, mouse):
    global last_hovered_card, hovered_card_time
    rrect(surf, (22,17,38), (0,0,W,H//2-10), 0)
    rrect(surf, PANEL, (0,H//2-10,W,H), 0)
    # COMBAT ANIMATION VISUAL STATE
    player_offset_x = 0
    player_offset_y = 0

    enemy_offsets = {}

    slash_target = None
    slash_enemy = None

    anim = getattr(g, "combat_anim", None)

    if anim:

        now = pygame.time.get_ticks()

        elapsed = (
            now
            - anim.get("started", now))
        # ATTACKER LUNGE
        if elapsed < 85:

            progress = (
                elapsed / 85.0)

            lunge = int(
                28 * progress)

            if anim["attacker"] == "player":

                player_offset_x += (
                    lunge)

            else:

                en = anim.get(
                    "enemy")

                if en:

                    enemy_offsets[
                        id(en)
                    ] = (
                        -lunge,
                        0)
        # TARGET RECOIL
        elif elapsed < 230:

            progress = (
                elapsed - 85) / 145.0

            strength = (
                8
                if anim.get("actual_damage", 0) <= 0
                else 22)

            recoil = int(
                strength
                * (
                    1.0
                    - progress)
            )

            shake = int(
                math.sin(
                    elapsed * 0.18)
                * (
                    3
                    if anim.get("actual_damage", 0) <= 0
                    else 7)
            )

            if anim["target"] == "player":

                player_offset_x -= recoil
                player_offset_y += shake

                slash_target = "player"

            else:

                en = anim.get(
                    "enemy")

                if en:

                    enemy_offsets[
                        id(en)
                    ] = (
                        recoil,
                        shake)

                    slash_target = "enemy"
                    slash_enemy = en
    # РИСУВАНЕ НА ПЛЕЙЪР
    px = 150 + player_offset_x
    py = 245 + player_offset_y
    g.tutorial_player_hp_rect = pygame.Rect(px - 70, py + 2, 140, 12)
    # PLAYER COMBAT SPRITE
    # Phoenix = Bruiser
    # Franziska = Assassin
    is_franziska = (
        str(
            getattr(g, "char_class", "BRUISER")
        ).upper()
        == "ASSASSIN")

    player_name = (
        "Franziska"
        if is_franziska
        else "Phoenix")

    pose = "idle"

    now = pygame.time.get_ticks()

    if (
        now
        < getattr(g, "phoenix_combat_pose_until", 0)):

        pose = getattr(g, "phoenix_combat_pose", "idle")
    # FRANZISKA
    if is_franziska:

        if pose == "damage":

            player_img = (
                MAIN_FRANZISKA_DAMAGE)

        elif pose == "attack":

            player_img = (
                MAIN_FRANZISKA_ATTACK)

        elif pose == "special":

            player_img = (
                MAIN_FRANZISKA_SPECIAL)

        else:

            player_img = (
                MAIN_FRANZISKA_IDLE)
    # PHOENIX
    else:

        if pose == "damage":

            player_img = (
                MAIN_PHOENIX_DAMAGE)

        elif pose == "attack":

            player_img = (
                MAIN_PHOENIX_ATTACK)

        elif pose == "special":
            player_img = (
                MAIN_PHOENIX_PROUD)

        else:

            player_img = (
                MAIN_PHOENIX_IDLE)


    player_rect = player_img.get_rect(
        midbottom=(
            int(px),
            int(py)))

    surf.blit(player_img, player_rect)

    g.player_combat_rect = (
        player_rect.copy())

    txc(
        surf,
        player_name,
        F_MED,
        WHITE,
        px,
        py - 18)
    hp_bar(surf, g.php, g.pmx, px-70, py+2, 140)
    if g.pblock>0:
        pygame.draw.circle(surf, BLUE, (px-88, py+8), 13)
        txc(surf, str(g.pblock), F_MED, WHITE, px-88, py+8)

    sy = py + 24

    if g.pstr > 0:
        txc(surf, f"Strength: +{g.pstr}", F_MED, GREEN, px, sy)
        sy += 14


    if getattr(g, "ptmp_str", 0) > 0:
        txc(surf, f"Tmp Str: +{g.ptmp_str}", F_MED, GREEN, px, sy)
        sy += 14

    if getattr(g, "pweak", 0) > 0:
        txc(surf, f"Weak: {g.pweak}", F_MED, ORANGE, px, sy)
        sy += 14

    if g.pvuln > 0:
        txc(surf, f"Vulnerable: {g.pvuln}", F_MED, ORANGE, px, sy)

    # РИСУВАНЕ НА ВСИЧКИ ВРАГОВЕ
    num_enemies = len(g.enemies)
    enemy_spacing = 180
    start_ex = (W // 2) + 100 - ((num_enemies - 1) * enemy_spacing) // 2

    g.enemy_rects = [] 

    for i, en in enumerate(g.enemies):
        ex = start_ex + i * enemy_spacing
        ey = 225
        off_x, off_y = enemy_offsets.get(
            id(en),
            (0, 0))

        ex += off_x
        ey += off_y
        if i == 0:
            g.tutorial_enemy_hp_rect = pygame.Rect(ex - 85, ey + 2, 170, 12)

            g.tutorial_enemy_intent_rect = pygame.Rect(ex - 70, ey + 48, 140, 24)
        # ENEMY SPRITE
        enemy_pose = "default"

        now = pygame.time.get_ticks()

        if (
            now
            < en.get("sprite_pose_until", 0)):

            enemy_pose = en.get("sprite_pose", "default")


        enemy_img = get_enemy_sprite(en["name"], enemy_pose)


        if enemy_img is not None:

            enemy_sprite_rect = (
                enemy_img.get_rect(
                    midbottom=(
                        int(ex),
                        int(ey - 5))
                ))

            surf.blit(enemy_img, enemy_sprite_rect)

          
            en_rect = enemy_sprite_rect.inflate(12, 8)

        else:

 
            en_rect = pygame.Rect(ex - 40, ey - 80, 80, 78)

            rrect(
                surf,
                (35, 25, 55),
                en_rect,
                10)

            txc(
                surf,
                f"E{i+1}",
                F_MED,
                WHITE,
                en_rect.centerx,
                en_rect.centery)



        g.enemy_rects.append(
            (
                en_rect,
                en)
        )


        txc(
            surf,
            en["name"],
            F_MED,
            WHITE,
            ex,
            max(15, en_rect.top - 13))

        hp_bar(
            surf,
            en["hp"],
            en["max_hp"],
            ex - 85,
            ey + 2,
            170)

        if en.get("block", 0) > 0:
            pygame.draw.circle(
                surf,
                BLUE,
                (ex - 105, ey + 8),
                13)

            txc(
                surf,
                str(en["block"]),
                F_MED,
                WHITE,
                ex - 105,
                ey + 8)

        sy = ey + 24

        if en.get("str", 0) > 0:
            txc(
                surf,
                f"Strength: +{en['str']}",
                F_MED,
                GREEN,
                ex,
                sy)
            sy += 14

        if en.get("weak", 0) > 0:
            txc(
                surf,
                f"Weak: {en['weak']}",
                F_MED,
                ORANGE,
                ex,
                sy)
            sy += 14

        if en.get("vuln", 0) > 0:
            txc(
                surf,
                f"Vulnerable: {en['vuln']}",
                F_MED,
                ORANGE,
                ex,
                sy)
            sy += 14

        if en.get("blitz", 0) > 0:
            txc(
                surf,
                f"Blitz: {en['blitz']} ({en.get('blitz_timer', 0)}t)",
                F_MED,
                ORANGE,
                ex,
                sy)
        # CURRENT INTENT
        pattern = en["pattern"]
        move_key = pattern[
            en["move_i"] % len(pattern)
        ]

        kind, v1, v2 = en["moves"][move_key]

        ilabel = ""
        icol = WHITE

        if kind == "atk":
            total = v1 + en.get("str", 0)

            if en.get("weak", 0) > 0:
                total = int(total * 0.75)

            ilabel = f"Attack {total}"
            icol = (
                ORANGE
                if en.get("weak", 0) > 0
                else RED)

        elif kind == "atk_multi":
            dmg = v1 + en.get("str", 0)

            if en.get("weak", 0) > 0:
                dmg = int(dmg * 0.75)

            ilabel = f"Attack {dmg} x{v2}"
            icol = RED

        elif kind == "blk":
            ilabel = f"Block {v2}"
            icol = BLUE

        elif kind == "buff":
            ilabel = f"Buff +{v2} Str"
            icol = GREEN

        elif kind == "weak_player":
            ilabel = f"Apply {v1} Weak"
            icol = ORANGE

        elif kind == "vuln_player":
            ilabel = f"Apply {v1} Vulnerable"
            icol = ORANGE

        elif kind == "heal":
            ilabel = f"Heal {v1} HP"
            icol = GREEN

        rrect(
            surf,
            PANEL,
            (ex - 70, ey + 48, 140, 24),
            6,
            1,
            icol)

        txc(
            surf,
            f"> {ilabel}",
            F_MED,
            icol,
            ex,
            ey + 60)
        # PROPHET'S EYE
        if (
            hasattr(g, "relics")
            and "Prophet's Eye" in g.relics):
            next_move_key = pattern[
                (en["move_i"] + 1) % len(pattern)
            ]

            n_kind, n_v1, n_v2 = en["moves"][
                next_move_key
            ]

            n_label = ""

            if n_kind == "atk":
                n_total = n_v1 + en.get("str", 0)

                if en.get("weak", 0) > 0:
                    n_total = int(n_total * 0.75)

                n_label = f"Next: Atk {n_total}"

            elif n_kind == "atk_multi":
                n_label = (
                    f"Next: Atk {n_v1} x{n_v2}")

            elif n_kind == "blk":
                n_label = f"Next: Blk {n_v2}"

            elif n_kind == "buff":
                n_label = f"Next: Buff +{n_v2}"

            elif n_kind == "weak_player":
                n_label = f"Next: Weak {n_v1}"

            elif n_kind == "vuln_player":
                n_label = f"Next: Vuln {n_v1}"

            elif n_kind == "heal":
                n_label = f"Next: Heal {n_v1}"

            if i == 0:
                g.tutorial_enemy_next_intent_rect = pygame.Rect(ex - 70, ey + 76, 140, 20)
            rrect(
                surf,
                (20, 20, 30),
                (ex - 70, ey + 76, 140, 20),
                4,
                1,
                GRAY)

            txc(
                surf,
                n_label,
                F_TINY_BOLD,
                GRAY_L,
                ex,
                ey + 86)
    # SLASH HIT EFFECT
    slash_rect = None

    if slash_target == "player":

        slash_rect = getattr(g, "player_combat_rect", None)

    elif (
        slash_target == "enemy"
        and slash_enemy):

        for rect, en in getattr(g, "enemy_rects", []):

            if en is slash_enemy:
                slash_rect = rect
                break


    if slash_rect:

        pygame.draw.line(
            surf,
            WHITE,
            (
                slash_rect.left - 8,
                slash_rect.top - 8),
            (
                slash_rect.right + 8,
                slash_rect.bottom + 8),
            6)

        pygame.draw.line(
            surf,
            (255, 100, 100),
            (
                slash_rect.left,
                slash_rect.top - 4),
            (
                slash_rect.right + 5,
                slash_rect.bottom - 10),
            3)

    g.tutorial_mana_rects = []
    # MANA FEEDBACK WHILE DRAGGING
    not_enough_for_drag = False

    if getattr(g, "drag_card", None):

        dragged_data = get_card_data(g.drag_card.name, g.drag_card.upgraded)

        not_enough_for_drag = (
            g.get_effective_card_cost(
                g.drag_card)
            > g.mana)


    mana_flash = (
        pygame.time.get_ticks()
        // 160) % 2 == 0
    # DRAW MANA ORBS
    for i in range(g.max_mana):

        mana_rect = pygame.Rect(18 + i * 28, H // 2 - 20, 24, 24)

        g.tutorial_mana_rects.append(
            mana_rect)


        if not_enough_for_drag:

            if mana_flash:
                col = RED
            else:
                col = (
                    BLUE
                    if i < g.mana
                    else (55, 20, 25))

        else:

            col = (
                BLUE
                if i < g.mana
                else (35, 35, 60))

        pygame.draw.circle(
            surf,
            col,
            (
                30 + i * 28,
                H // 2 - 8),
            12)

        pygame.draw.circle(
            surf,
            BORDER,
            (
                30 + i * 28,
                H // 2 - 8),
            12,
            2)

        if i < g.mana:

            txc(
                surf,
                str(i + 1),
                F_MED,
                WHITE,
                30 + i * 28,
                H // 2 - 8)


    if g.mana <= 0:
        flash_on = (pygame.time.get_ticks() // 300) % 2 == 0
        warning_col = RED if flash_on else ORANGE

        mana_warning_rect = pygame.Rect(12, H // 2 + 10, 125, 30)

        rrect(
            surf,
            PANEL,
            mana_warning_rect,
            6,
            2,
            warning_col)

        txc(
            surf,
            "0 MANA",
            F_MED,
            warning_col,
            mana_warning_rect.centerx,
            mana_warning_rect.centery)

    for i, (msg,col) in enumerate(g.log_msgs[:5]):
        surf.blit(F_MED.render(msg, True, lerp(col, GRAY, i*0.15)), (W-215, H//2-105+i*17))

    # НОВИ ПОЗИЦИИ НА БУТОНИТЕ
    g.btn_view_draw.label = f"Draw ({len(g.draw_p)})"
    g.btn_view_disc.label = f"Discard ({len(g.disc)})"
    
    g.btn_view_draw.draw(surf, mouse) 
    g.btn_deck.draw(surf, mouse)      
    g.btn_view_disc.draw(surf, mouse) 
    
    g.end_btn.draw(surf, mouse)     

    # РИСУВАНЕ НА КАРТИТЕ
    positions = g.hand_positions()
    # KEEP HAND STILL DURING END-TURN DISCARD
    if (getattr(g, "pending_end_turn_after_discard", False)
        and getattr(g, "end_turn_discard_positions", {})):

        positions = [
            g.end_turn_discard_positions.get(
                id(card),
                (
                    card.x,
                    card.y)
            )
            for card in g.hand
        ]

    drag_card = g.drag_card

    current_hover = None
    hover_index = None
    # FIND TOPMOST CARD UNDER MOUSE
    if drag_card is None:

        for i in range(
            len(g.hand) - 1,
            -1,
            -1):

            card = g.hand[i]

            cx, cy = positions[i]

            if card.collides(
                mouse,
                cx,
                cy):

                current_hover = card
                hover_index = i
                break
    # DRAW NORMAL CARDS FIRST
    for i, card in enumerate(
        g.hand):

        if (
            card is drag_card
            or i == hover_index):
            continue

        cx, cy = positions[i]

        card.x = cx
        card.y = cy

        draw_card(
            surf,
            card.name,
            cx,
            cy,
            g.mana,
            g=g,
            target_enemy=(
                g.enemies[0]
                if g.enemies
                else None),
            upgraded=card.upgraded)
    # DRAW HOVERED CARD LAST / ON TOP
    if hover_index is not None:

        card = g.hand[
            hover_index
        ]

        cx, cy = positions[
            hover_index
        ]

        card.x = cx
        card.y = cy

        draw_card(
            surf,
            card.name,
            cx,
            cy - 20,
            g.mana,
            g=g,
            target_enemy=(
                g.enemies[0]
                if g.enemies
                else None),
            upgraded=card.upgraded)
    
    card_anim = getattr(g, "card_anim", None)

    if card_anim:

        now = pygame.time.get_ticks()

        elapsed = (
            now
            - card_anim["started"])

        duration = max(1, card_anim["duration"])

        t = max(
            0.0,
            min(1.0, elapsed / duration)
        )


        t = (
            t * t
            * (3.0 - 2.0 * t))

        start_x = card_anim["start_x"]
        start_y = card_anim["start_y"]

        target_x = card_anim["target_x"]
        target_y = card_anim["target_y"]

        x = int(
            start_x
            + (
                target_x - start_x) * t
        )

        y = int(
            start_y
            + (
                target_y - start_y) * t
        )

        moving_card = card_anim["card"]

        draw_card(
            surf,
            moving_card.name,
            x,
            y,
            g.mana,
            g=g,
            upgraded=moving_card.upgraded)
    # Tooltip
    if current_hover and not drag_card and g.state == "combat":
        if current_hover == last_hovered_card:
            hovered_card_time += 1/60
        else:
            last_hovered_card = current_hover
            hovered_card_time = 0
            
        if hovered_card_time >= 2.0:
            d = get_card_data(current_hover.name,current_hover.upgraded)
            tips = []
            if "weak" in d or "weak" in d["desc"].lower():
                tips.append(("Weak", "Target deals 25% less attack damage."))
            if "vuln" in d or "vulnerable" in d["desc"].lower() or "vuln" in d["desc"].lower():
                tips.append(("Vulnerable", "Target takes 50% more attack damage."))
            if "blitz" in d or "blitz" in d["desc"].lower():
                tips.append(("Blitz", "Explodes after 3 turns for massive damage."))
            if (
                "str" in d
                or "tmp_str" in d
                or "strength" in d["desc"].lower()
                or " str " in (" " + d["desc"].lower() + " ")):
                tips.append((
                    "Strength",
                    "Each point adds 1 damage to your attack cards."))

            if tips:
                tip_x = current_hover.x + CW + 10
                tip_y = current_hover.y - 20
                tw, th = 240, len(tips) * 50 + 10
                rrect(screen, PANEL, (tip_x, tip_y, tw, th), 5, 2, GOLD)
                
                ty = tip_y + 15
                for title, desc in tips:
                    txt(screen, title, F_MED, GOLD, tip_x + 10, ty)
                    words = desc.split()
                    line1_words = []
                    line2_words = []

                    for word in words:
                        test_line = " ".join(
                            line1_words + [word])

                        if F_MED.size(test_line)[0] < tw - 20:
                            line1_words.append(word)
                        else:
                            line2_words.append(word)

                    line1 = " ".join(line1_words)
                    line2 = " ".join(line2_words)
                    txt(screen, line1, F_MED, WHITE, tip_x + 10, ty + 16)
                    if line2: txt(screen, line2, F_MED, WHITE, tip_x + 10, ty + 30)
                    ty += 45
    else:
        last_hovered_card = None
        hovered_card_time = 0

        # Влачене и стрелка
    # DRAG / MAGNET / TARGETING
    if drag_card:

        d = get_card_data(drag_card.name, drag_card.upgraded)

        needs_target = (
            d["type"] == "attack"
            or "weak" in d
            or "vuln" in d
            or "blitz" in d
            or d.get("trigger_blitz")
            or d.get("double_blitz")
            or "wounds" in d
            or d.get("trigger_wounds")
            or d.get("double_wounds")
            or d.get("draw_per_wound")) and not d.get("target_all", False)

        enough_mana = (
            g.get_effective_card_cost(
                drag_card)
            <= g.mana)

        dx = (
            g.drag_x
            - g.drag_ox)

        dy = (
            g.drag_y
            - g.drag_oy)

        home_y = getattr(g, "drag_home_y", drag_card.y)

  
        lift_distance = (
            home_y - dy)

     
 
        drag_activated = (
            enough_mana
            and lift_distance >= 45)
        # НЯМА MANA ИЛИ ОЩЕ Е В MAGNET ЗОНАТА
        if not drag_activated:

            draw_card(
                surf,
                drag_card.name,
                dx,
                dy,
                g.mana,
                selected=True,
                dragging=True,
                g=g,
                upgraded=drag_card.upgraded)
        # TARGETABLE CARD
        elif needs_target:
            home_x = getattr(g, "drag_home_x", drag_card.x)

            home_y = getattr(g, "drag_home_y", drag_card.y)

            card_x = home_x
            card_y = home_y - 25

            draw_card(
                surf,
                drag_card.name,
                card_x,
                card_y,
                g.mana,
                selected=True,
                dragging=True,
                g=g,
                upgraded=drag_card.upgraded)

            hovered_enemy = None

            for rect, en in getattr(g, "enemy_rects", []):

                if rect.collidepoint(mouse):

                    hovered_enemy = en

                    rrect(
                        surf,
                        (0, 0, 0, 0),
                        rect,
                        10,
                        3,
                        GOLD)

                    break

            arr_col = (
                RED
                if hovered_enemy
                else GOLD)

            draw_arrow(
                surf,
                (
                    card_x + CW // 2,
                    card_y),
                mouse,
                arr_col)
        # NON-TARGET CARD / SPELL
        else:

            in_play_zone = (
                mouse[1]
                < H // 2 - 10)

            zone_col = (
                GREEN
                if in_play_zone
                else GRAY)

            rrect(
                surf,
                (0, 0, 0, 0),
                (
                    80,
                    60,
                    W - 160,
                    H // 2 - 80),
                10,
                2,
                zone_col)

            txc(
                surf,
                "Drop here to play",
                F_MED,
                zone_col,
                W // 2,
                75)

            draw_card(
                surf,
                drag_card.name,
                dx,
                dy,
                g.mana,
                dragging=True,
                g=g,
                in_play_zone=in_play_zone,
                upgraded=drag_card.upgraded)

def draw_pre_minigame(surf, g, mouse):
    rrect(surf, (22,17,38), (0,0,W,H), 0)
    txc(surf, "MINIGAME REWARD", F_BIG, GOLD, W//2, 80)
    txc(surf, "Play the minigame for a chance to win one of these cards:", F_MED, WHITE, W//2, 130)
    
    pool = g.reward_pool
    spacing = 180
    total_w = (len(pool) - 1) * spacing + CW
    start_x = (W - total_w) // 2
    
    for i, card_name in enumerate(pool):
        cx = start_x + i * spacing
        cy = H//2 - 60
        draw_card(surf, card_name, cx, cy, 99, g=g) 
        
    g.btn_mg_confirm.draw(surf, mouse)
    g.btn_mg_skip.draw(surf, mouse)


def draw_shop(surf, g, mouse):
    surf.fill(BG)

    txc(surf, "MERCHANT SHOP", F_BIG, GOLD, W // 2, 35)
    txc(
        surf,
        f"Gold: {getattr(g, 'pgold', 0)}",
        F_MED,
        GOLD,
        W // 2,
        70)
    # CARDS
    visible_cards = g.shop_cards[:4]

    gap = 35
    total_width = len(visible_cards) * CW + max(0, len(visible_cards) - 1) * gap
    start_x = (W - total_width) // 2

    card_y = 110

 
    g.shop_card_rects = []

    for i, item in enumerate(visible_cards):
        x = start_x + i * (CW + gap)

      
        full_rect = pygame.Rect(x, card_y, CW, CH + 42)

        g.shop_card_rects.append(
            (item, full_rect))

        if item.get("bought", False):
            rrect(
                surf,
                (25, 25, 35),
                (x, card_y, CW, CH),
                10,
                2,
                GRAY)

            txc(
                surf,
                "SOLD",
                F_MED,
                GRAY,
                x + CW // 2,
                card_y + CH // 2)

            continue

    
        draw_card(
            surf,
            item["name"],
            x,
            card_y,
            99,
            g=g)

        price = item["price"]
        can_afford = g.pgold >= price

        price_rect = pygame.Rect(x, card_y + CH + 8, CW, 30)

        price_col = GREEN_D if can_afford else RED_D

        rrect(
            surf,
            price_col,
            price_rect,
            6,
            2,
            GOLD if can_afford else RED)

        txc(
            surf,
            f"{price} Gold",
            F_MED,
            WHITE,
            price_rect.centerx,
            price_rect.centery)
    if (
        getattr(g, "tutorial_active", False)
        and getattr(g, "tutorial_room", "") == "shop"):

        g.shop_relic_rects = []

        g.btn_leave_shop.rect.centerx = W // 2
        g.btn_leave_shop.rect.y = H - 60

        g.btn_leave_shop.draw(surf, mouse)

        return
    # RELICS
    relic_title_y = 390

    txc(
        surf,
        "RELICS FOR SALE",
        F_MED,
        GOLD,
        W // 2,
        relic_title_y)

    shop_relics = getattr(g, "shop_relics", [])

    g.shop_relic_rects = []

    relic_w = 250
    relic_h = 95
    relic_gap = 20

    total_relic_w = (
        len(shop_relics) * relic_w
        + max(0, len(shop_relics) - 1) * relic_gap)

    relic_start_x = (W - total_relic_w) // 2
    relic_y = 425

    for i, item in enumerate(shop_relics):
        x = relic_start_x + i * (relic_w + relic_gap)

        rect = pygame.Rect(x, relic_y, relic_w, relic_h)

        g.shop_relic_rects.append(
            (item, rect))

        relic_name = item["name"]
        price = item["price"]

        if item.get("bought", False):
            rrect(
                surf,
                (25, 25, 35),
                rect,
                8,
                2,
                GRAY)

            txc(
                surf,
                "SOLD",
                F_MED,
                GRAY,
                rect.centerx,
                rect.centery)

            continue

        can_afford = g.pgold >= price
        hover = rect.collidepoint(mouse)

        border_col = (
            GOLD if can_afford
            else RED)

        bg_col = (
            (50, 40, 65)
            if hover
            else PANEL)

        rrect(
            surf,
            bg_col,
            rect,
            8,
            2,
            border_col)

        txc(
            surf,
            relic_name,
            F_MED,
            WHITE,
            rect.centerx,
            relic_y + 20)

        desc = RELICS.get(relic_name, {}).get("desc", "")

     
        if len(desc) > 42:
            desc = desc[:39] + "..."

        txc(
            surf,
            desc,
            F_MED,
            GRAY_L,
            rect.centerx,
            relic_y + 47)

        txc(
            surf,
            f"{price} Gold",
            F_MED,
            GOLD if can_afford else RED,
            rect.centerx,
            relic_y + 73)
    # LEAVE
    g.btn_leave_shop.rect.centerx = W // 2
    g.btn_leave_shop.rect.y = H - 60

    g.btn_leave_shop.draw(surf, mouse)

def draw_card_view(surf, g, mouse):
    surf.fill(BG)
    # DEV MENU
    if g.view_mode == "dev":
        scroll_y = g.card_scroll
        txc(
            surf,
            "DEVELOPER MENU",
            F_BIG,
            GOLD,
            W // 2,
            35)

        #  TABS 
        tab_w = 180
        tab_h = 38
        gap = 15

        total_w = tab_w * 3 + gap * 2
        start_x = W//2 - total_w//2

        tabs = [
            ("Bruiser", RED_D),
            ("Assassin", PURPLE_D),
            ("Relics", GOLD)
        ]

        g.dev_tab_rects = []

        for i, (name, col) in enumerate(tabs):
            rect = pygame.Rect(start_x + i * (tab_w + gap), 65, tab_w, tab_h)

            g.dev_tab_rects.append((name, rect))

            active = g.dev_tab == name
            hover = rect.collidepoint(mouse)

            if active:
                bg_col = col
                border_col = WHITE
            elif hover:
                bg_col = lerp(col, WHITE, 0.15)
                border_col = GOLD
            else:
                bg_col = PANEL
                border_col = col

            rrect(
                surf,
                bg_col,
                rect,
                7,
                2,
                border_col)

            txc(
                surf,
                name.upper(),
                F_MED,
                WHITE,
                rect.centerx,
                rect.centery)
        # SCROLLABLE DEV CONTENT AREA
        dev_content_top = 115
        dev_content_bottom = H - 65

        old_clip = surf.get_clip()

        surf.set_clip(pygame.Rect(0, dev_content_top, W, dev_content_bottom - dev_content_top))
        # RELICS TAB
        if g.dev_tab == "Relics":

            txc(
                surf,
                "Click a relic to add/remove it",
                F_MED,
                GRAY_L,
                W//2,
                125 + scroll_y)

            g.dev_relic_rects = []

            relic_names = list(RELICS.keys())

            cols = 4
            box_w = 220
            box_h = 110
            gap_x = 20
            gap_y = 14

            total_grid_w = cols * box_w + (cols - 1) * gap_x
            grid_x = W//2 - total_grid_w//2

            start_y = 155 + g.card_scroll

            for i, relic_name in enumerate(relic_names):

                row = i // cols
                col = i % cols

                x = grid_x + col * (box_w + gap_x)
                y = start_y + row * (box_h + gap_y)

                rect = pygame.Rect(x, y, box_w, box_h)

                g.dev_relic_rects.append(
                    (relic_name, rect))

                owned = relic_name in getattr(g, "relics", [])
                hover = rect.collidepoint(mouse)

                if owned:
                    box_col = (35, 80, 45)
                    border_col = GREEN
                elif hover:
                    box_col = (55, 45, 30)
                    border_col = GOLD
                else:
                    box_col = PANEL
                    border_col = BORDER

                rrect(
                    surf,
                    box_col,
                    rect,
                    8,
                    2,
                    border_col)

                txt(
                    surf,
                    relic_name,
                    F_MED,
                    GREEN if owned else WHITE,
                    x + 10,
                    y + 8)

                if owned:
                    txt(
                        surf,
                        "OWNED - click to remove",
                        F_MED,
                        GREEN,
                        x + 10,
                        y + 29)
                else:
                    txt(
                        surf,
                        "Click to add",
                        F_MED,
                        GOLD,
                        x + 10,
                        y + 29)

                desc = RELICS.get(relic_name, {}).get("desc", "")
                words = desc.split()
                line1 = ""
                line2 = ""

                for word in words:
                    if len(line1 + word) < 30:
                        line1 += word + " "
                    elif len(line2 + word) < 30:
                        line2 += word + " "

                txt(
                    surf,
                    line1.strip(),
                    F_MED,
                    GRAY_L,
                    x + 10,
                    y + 48)

                txt(
                    surf,
                    line2.strip(),
                    F_MED,
                    GRAY_L,
                    x + 10,
                    y + 63)
            surf.set_clip(old_clip)
            g.btn_close_view.draw(surf, mouse)
            return
        # CARD TABS
        txc(
            surf,
            "Click a card to add it to your deck",
            F_MED,
            GRAY_L,
            W//2,
            125 + scroll_y)

        n = len(g.viewing_cards)

        cols = 6
        pad_x = 160
        pad_y = 220

        grid_width = (cols - 1) * pad_x + CW
        start_x = (W - grid_width) // 2
        start_y = 155

        for i, card in enumerate(g.viewing_cards):

            row = i // cols
            col = i % cols

            cx = start_x + col * pad_x
            cy = start_y + row * pad_y + g.card_scroll

            card.x = cx
            card.y = cy

            if -CH <= cy <= H:
                hover = card.collides(mouse, cx, cy)

                draw_card(
                    surf,
                    card.name,
                    cx,
                    cy - (10 if hover else 0),
                    99,
                    selected=hover,
                    g=g,
                    upgraded=card.upgraded)
        surf.set_clip(old_clip)
        g.btn_close_view.draw(surf, mouse)
        return
    # NORMAL CARD VIEW
    title_y = 40 + g.card_scroll
    txc(surf, g.view_title, F_BIG, GOLD, W//2, title_y)

    n = len(g.viewing_cards)

    if n == 0:
        txc(
            surf,
            "Empty",
            F_MED,
            GRAY_L,
            W//2,
            H//2 + g.card_scroll)

    else:
        cols = 6
        pad_x = 160
        pad_y = 220

        grid_width = (cols - 1) * pad_x + CW
        start_x = (W - grid_width) // 2
        start_y = 90

        for i, card in enumerate(g.viewing_cards):

            row = i // cols
            col = i % cols

            cx = start_x + col * pad_x
            cy = start_y + row * pad_y + g.card_scroll

            card.x = cx
            card.y = cy

            if -CH <= cy <= H:
                draw_card(
                    surf,
                    card.name,
                    cx,
                    cy,
                    99,
                    g=g,
                    upgraded=card.upgraded)

    g.btn_close_view.draw(surf, mouse)

def draw_game_over(surf, g, mouse):
    txc(surf, "YOU DIED", F_BIG, RED, W//2, H//2-70)
    txc(surf, f"Reached floor {g.floor+1}", F_MED, GRAY_L, W//2, H//2-20)
    g.restart.draw(surf, mouse)


def draw_level_up(surf, g, mouse):

    surf.fill(BG)

    class_name = str(
        getattr(g, "char_class", "Bruiser")).capitalize()
    hero_name = (
        "Franziska"
        if class_name == "Assassin"
        else "Phoenix")

    old_level = getattr(g, "last_victory_old_level", 0)

    new_level = getattr(g, "last_victory_new_level", old_level)
    # TITLE
    txc(
        surf,
        "LEVEL UP!",
        F_BIG,
        GOLD,
        W // 2,
        42)

    txc(
        surf,
        f"{hero_name.upper()}  LEVEL {old_level} -> {new_level}",
        F_MED,
        GREEN,
        W // 2,
        82)

    txc(
        surf,
        "NEW CONTENT UNLOCKED",
        F_MED,
        WHITE,
        W // 2,
        110)
    # FIND NEW CARDS
    unlocked_cards = []

    for card_name, data in CARDS.items():

        card_class = str(
            data.get("class", "Any")
        ).capitalize()

        unlock_level = int(
            data.get("unlock_level", 0)
        )

        if (
            card_class == class_name
            and unlock_level == new_level):

            unlocked_cards.append(
                card_name)
    # FIND NEW RELICS
    unlocked_relics = []

    for relic_name, data in RELICS.items():

        relic_class = str(
            data.get("class", "Any")
        ).capitalize()

        unlock_level = int(
            data.get("unlock_level", 0)
        )

        if (
            relic_class == class_name
            and unlock_level == new_level):

            unlocked_relics.append(
                relic_name)
    # DRAW UNLOCKED CARDS
    if unlocked_cards:

        txc(
            surf,
            "UNLOCKED CARDS",
            F_MED,
            GOLD,
            W // 2,
            145)

        spacing = 175

        total_width = (
            (len(unlocked_cards) - 1)
            * spacing
            + CW)

        start_x = (
            W - total_width) // 2

        card_y = 175

        for i, card_name in enumerate(
            unlocked_cards):

            card_x = (
                start_x
                + i * spacing)

            draw_card(
                surf,
                card_name,
                card_x,
                card_y,
                99,
                g=g)
    # DRAW UNLOCKED RELICS
    if unlocked_relics:

        relic_title_y = 405


        if not unlocked_cards:
            relic_title_y = 170

        txc(
            surf,
            "UNLOCKED RELICS",
            F_MED,
            GOLD,
            W // 2,
            relic_title_y)

        relic_w = 250
        relic_h = 105
        relic_gap = 20

        total_width = (
            len(unlocked_relics)
            * relic_w
            + max(
                0,
                len(unlocked_relics) - 1)
            * relic_gap)

        start_x = (
            W - total_width) // 2

        relic_y = (
            relic_title_y + 25)

        for i, relic_name in enumerate(
            unlocked_relics):

            x = (
                start_x
                + i
                * (
                    relic_w
                    + relic_gap)
            )

            rect = pygame.Rect(x, relic_y, relic_w, relic_h)

            hover = rect.collidepoint(
                mouse)

            rrect(
                surf,
                PURPLE_D
                if hover
                else PANEL,
                rect,
                9,
                2,
                GOLD)
            # RELIC ICON
            icon_rect = pygame.Rect(x + 10, relic_y + 12, 55, 55)

            rrect(
                surf,
                (60, 40, 20),
                icon_rect,
                8,
                2,
                GOLD)

            txc(
                surf,
                relic_name[0],
                F_BIG,
                GOLD,
                icon_rect.centerx,
                icon_rect.centery)
            # RELIC NAME
            txt(
                surf,
                relic_name,
                F_MED,
                WHITE,
                x + 78,
                relic_y + 12)
            # RELIC DESCRIPTION 
            desc = RELICS.get(relic_name, {}).get("desc", "")

            words = desc.split()

            lines = []
            line = ""

            max_text_width = (
                relic_w - 90)

            for word in words:

                test_line = (
                    line + " " + word).strip()

                if (
                    F_SML.size(
                        test_line)[0]
                    <= max_text_width):

                    line = test_line

                else:

                    if line:
                        lines.append(
                            line)

                    line = word

            if line:
                lines.append(
                    line)

            for line_i, text_line in enumerate(
                lines[:4]):

                txt(
                    surf,
                    text_line,
                    F_SML,
                    GRAY_L,
                    x + 78,
                    relic_y
                    + 38
                    + line_i * 16)
    # NO CONTENT FALLBACK
    if (
        not unlocked_cards
        and not unlocked_relics):

        txc(
            surf,
            "No new content found for this level.",
            F_MED,
            GRAY,
            W // 2,
            H // 2)
    # CONTINUE BUTTON
    g.level_up_continue_rect = pygame.Rect(W // 2 - 130, H - 55, 260, 42)

    hover = (
        g.level_up_continue_rect.collidepoint(
            mouse)
    )

    rrect(
        surf,
        GREEN_D
        if hover
        else PANEL,
        g.level_up_continue_rect,
        8,
        2,
        GREEN)

    txc(
        surf,
        "CONTINUE",
        F_MED,
        WHITE,
        g.level_up_continue_rect.centerx,
        g.level_up_continue_rect.centery)


def draw_win(surf, g, mouse):

    txc(
        surf,
        "VICTORY",
        F_BIG,
        GOLD,
        W // 2,
        H // 2 - 70)

    if getattr(g, "tutorial_room", "") == "tutorial_complete":

        victory_text = (
            "You completed the Spire Tutorial!")

    else:

        victory_text = (
            "You slew the Spire!")

    txc(
        surf,
        victory_text,
        F_MED,
        WHITE,
        W // 2,
        H // 2 - 20)

    txc(
        surf,
        f"HP: {g.php}/{g.pmx}",
        F_MED,
        GREEN,
        W // 2,
        H // 2 + 20)

    g.restart.label = "Play Again"
    g.restart.col = GREEN_D
    g.restart.draw(surf, mouse)

def draw_char_select(surf, g, mouse):

    surf.fill(BG)

    txc(
        surf,
        "SELECT YOUR HERO",
        F_BIG,
        GOLD,
        W // 2,
        85)
    # PROGRESSION DATA
    bruiser_level = g.get_class_level(
        "Bruiser")

    bruiser_wins = g.get_class_wins(
        "Bruiser")

    bruiser_next = g.get_next_level_wins(
        "Bruiser")


    assassin_level = g.get_class_level(
        "Assassin")

    assassin_wins = g.get_class_wins(
        "Assassin")

    assassin_next = g.get_next_level_wins(
        "Assassin")
    # BRUISER
    g.btn_class_1.draw(surf, mouse)

    txc(
        surf,
        "BRUISER",
        F_BIG,
        WHITE,
        g.btn_class_1.rect.centerx,
        g.btn_class_1.rect.top + 27)

    txc(
        surf,
        f"LEVEL {bruiser_level}",
        F_MED,
        GOLD,
        g.btn_class_1.rect.centerx,
        g.btn_class_1.rect.top + 62)

    txc(
        surf,
        f"Wins: {bruiser_wins}",
        F_MED,
        GREEN,
        g.btn_class_1.rect.centerx,
        g.btn_class_1.rect.top + 85)

    if bruiser_level < 5:

        txc(
            surf,
            f"Next Level: {bruiser_next} wins",
            F_MED,
            GRAY_L,
            g.btn_class_1.rect.centerx,
            g.btn_class_1.rect.top + 108)

    else:

        txc(
            surf,
            "MAX LEVEL",
            F_MED,
            GOLD,
            g.btn_class_1.rect.centerx,
            g.btn_class_1.rect.top + 108)

    txc(
        surf,
        "Starts with Bash.",
        F_MED,
        GRAY_L,
        g.btn_class_1.rect.centerx,
        g.btn_class_1.rect.bottom + 18)
    # ASSASSIN
    g.btn_class_2.draw(surf, mouse)

    txc(
        surf,
        "ASSASSIN",
        F_BIG,
        WHITE,
        g.btn_class_2.rect.centerx,
        g.btn_class_2.rect.top + 27)

    txc(
        surf,
        f"LEVEL {assassin_level}",
        F_MED,
        GOLD,
        g.btn_class_2.rect.centerx,
        g.btn_class_2.rect.top + 62)

    txc(
        surf,
        f"Wins: {assassin_wins}",
        F_MED,
        GREEN,
        g.btn_class_2.rect.centerx,
        g.btn_class_2.rect.top + 85)

    if assassin_level < 5:

        txc(
            surf,
            f"Next Level: {assassin_next} wins",
            F_MED,
            GRAY_L,
            g.btn_class_2.rect.centerx,
            g.btn_class_2.rect.top + 108)

    else:

        txc(
            surf,
            "MAX LEVEL",
            F_MED,
            GOLD,
            g.btn_class_2.rect.centerx,
            g.btn_class_2.rect.top + 108)

    txc(
        surf,
        "Master of Weak & Wounds.",
        F_MED,
        GRAY_L,
        g.btn_class_2.rect.centerx,
        g.btn_class_2.rect.bottom + 18)
    # TUTORIAL / BACK
    g.btn_tutorial.draw(surf, mouse)

    txc(
        surf,
        "Learn the basics",
        F_MED,
        GRAY_L,
        g.btn_tutorial.rect.centerx,
        g.btn_tutorial.rect.bottom + 14)

    g.btn_set_back.draw(surf, mouse)

def draw_extras(surf,g,mouse):

    surf.fill(BG)

    txc(
        surf,
        "EXTRAS",
        F_BIG,
        GOLD,
        W // 2,
        55)

    txc(
        surf,
        "PLAY MINIGAME",
        F_MED,
        WHITE,
        W // 2,
        100)

    txc(
        surf,
        "Practice any minigame without affecting your run.",
        F_MED,
        GRAY_L,
        W // 2,
        128)

    games = [
        (
        "HaremRunner",
        "CARD RUNNER"),
        (
        "HaremMaker",
        "CARD SHOOTER"),
        (
        "ManPac",
        "CARD MANPAC"),
        (
            "BoxingBoss",
            "GODOT - BOXING"),
        (
            "UndertaleBoss",
            "FRANZISKA - BULLET HELL")
    ]

    g.extras_minigame_rects = []

    btn_w = 360
    btn_h = 45

    start_y = 165
    gap = 55

    for i, (
        game_id,
        label) in enumerate(games):

        rect = pygame.Rect(W // 2 - btn_w // 2, start_y + i * gap, btn_w, btn_h)

        hover = rect.collidepoint(
            mouse)

        rrect(
            surf,
            PURPLE_D
            if hover
            else PANEL,
            rect,
            8,
            2,
            GOLD if hover else BORDER)

        txc(
            surf,
            label,
            F_MED,
            WHITE,
            rect.centerx,
            rect.centery)

        g.extras_minigame_rects.append(
            (
                game_id,
                rect)
        )

    g.extras_back_rect = pygame.Rect(W // 2 - 90, H - 60, 180, 40)

    hover = (
        g.extras_back_rect.collidepoint(
            mouse)
    )

    rrect(
        surf,
        RED_D
        if hover
        else PANEL,
        g.extras_back_rect,
        7,
        2,
        RED)

    txc(
        surf,
        "BACK",
        F_MED,
        WHITE,
        g.extras_back_rect.centerx,
        g.extras_back_rect.centery)

def draw_relics(surf, g, mouse):

    if not hasattr(g, "relics") or not g.relics:
        return

    start_x = 20
    y = 60
    size = 32

    hovered_relic = None

    for i, relic_name in enumerate(g.relics):

        x = start_x + (i * (size + 10))

        rect = pygame.Rect(x, y, size, size)
        # SECOND CHANCE - USED STATE
        is_used_second_chance = (
            relic_name == "Second Chance"
            and getattr(g, "second_chance_used", False)
        )

        if is_used_second_chance:

            relic_bg = (55, 55, 60)
            relic_border = (110, 110, 120)
            relic_text = (150, 150, 160)

        else:

            relic_bg = (60, 40, 20)
            relic_border = GOLD
            relic_text = WHITE
        # ICON
        rrect(
            surf,
            relic_bg,
            rect,
            6,
            2,
            relic_border)

        txc(
            surf,
            relic_name[0],
            F_MED,
            relic_text,
            x + size // 2,
            y + size // 2)

        if rect.collidepoint(mouse):
            hovered_relic = relic_name
    # TOOLTIP
    if hovered_relic:

        rx = mouse[0] + 15
        ry = mouse[1] + 15

        is_used_second_chance = (
            hovered_relic == "Second Chance"
            and getattr(g, "second_chance_used", False))

        desc = RELICS.get(hovered_relic, {}).get("desc", "Unknown")

        display_name = hovered_relic

        if is_used_second_chance:

            display_name += " (USED)"

            desc = (
                "Already used. "
                "This relic cannot revive you again.")

            title_color = (150, 150, 160)
            desc_color = (130, 130, 140)
            border_color = (110, 110, 120)

        else:

            title_color = GOLD
            desc_color = WHITE
            border_color = GOLD

        box_w = max(
            240,
            F_MED.size(desc)[0] + 20)

        rrect(
            surf,
            PANEL,
            (
                rx,
                ry,
                box_w,
                50),
            5,
            2,
            border_color)

        txt(
            surf,
            display_name,
            F_MED,
            title_color,
            rx + 10,
            ry + 5)

        txt(
            surf,
            desc,
            F_MED,
            desc_color,
            rx + 10,
            ry + 25)

def get_reward_minigame(g):
    mg_type = None

    if getattr(g, "current_node", None):
     
        mg_type = g.current_node.get("minigame")

     
        if not mg_type or mg_type == "None":
            enemy = g.current_node.get("enemy")

            if isinstance(enemy, list) and enemy:
                mg_type = enemy[0].get("mg")

            elif isinstance(enemy, dict):
                mg_type = enemy.get("mg")

    if mg_type not in (
        "HaremRunner",
        "HaremMaker",
        "CardCupid",
        "ManPac"):
        mg_type = "HaremRunner"

    return mg_type

def draw_reward(surf, g, mouse):
    surf.fill(BG)



    if (
        getattr(g, "tutorial_active", False)
        and getattr(g, "tutorial_room", "") == "elite_reward"):

        txc(
            surf,
            "ELITE VICTORY! CLAIM YOUR REWARDS",
            F_BIG,
            GOLD,
            W // 2,
            55)
        # GOLD
        gold_rect = pygame.Rect(W // 2 - 180, 90, 360, 45)

        if not getattr(g, "reward_gold_claimed", False):

            hover = gold_rect.collidepoint(mouse)

            rrect(
                surf,
                GREEN_D if hover else PANEL,
                gold_rect,
                8,
                2,
                GOLD)

            txc(
                surf,
                f"+ {g.reward_gold} Gold",
                F_MED,
                GOLD,
                gold_rect.centerx,
                gold_rect.centery)

        else:

            rrect(
                surf,
                (20, 20, 30),
                gold_rect,
                8,
                1,
                GRAY)

            txc(
                surf,
                "[Gold Claimed]",
                F_MED,
                GRAY,
                gold_rect.centerx,
                gold_rect.centery)
        # RELIC
        relic_rect = pygame.Rect(W // 2 - 180, 145, 360, 45)

        if not getattr(g, "reward_relic_claimed", False):

            hover = relic_rect.collidepoint(mouse)

            rrect(
                surf,
                PURPLE_D if hover else PANEL,
                relic_rect,
                8,
                2,
                GOLD)

            txc(
                surf,
                "Relic: Vampire Fangs",
                F_MED,
                WHITE,
                relic_rect.centerx,
                relic_rect.centery)

        else:

            rrect(
                surf,
                (20, 20, 30),
                relic_rect,
                8,
                1,
                GRAY)

            txc(
                surf,
                "[Vampire Fangs Claimed]",
                F_MED,
                GRAY,
                relic_rect.centerx,
                relic_rect.centery)
        # GUARANTEED CARDS
        txc(
            surf,
            "Card Rewards",
            F_MED,
            WHITE,
            W // 2,
            220)

        card_names = [
            "Ghost Armor",
            "Whirlwind"
        ]

        spacing = 180

        total_w = (
            (len(card_names) - 1)
            * spacing
            + CW)

        start_x = (
            W - total_w) // 2

        card_y = 250

        for i, card_name in enumerate(
            card_names):

            draw_card(
                surf,
                card_name,
                start_x + i * spacing,
                card_y,
                99,
                g=g)

        txc(
            surf,
            "Both cards have been added to your deck.",
            F_MED,
            GREEN,
            W // 2,
            455)
        # CONTINUE
        continue_rect = pygame.Rect(W // 2 - 180, 515, 360, 45)

        rewards_claimed = (
            getattr(g, "reward_gold_claimed", False)
            and getattr(g, "reward_relic_claimed", False))

        rrect(
            surf,
            GREEN_D
            if (
                rewards_claimed
                and continue_rect.collidepoint(mouse))
            else PANEL,
            continue_rect,
            8,
            2,
            GREEN if rewards_claimed else GRAY)

        txc(
            surf,
            "CONTINUE"
            if rewards_claimed
            else "CLAIM GOLD + RELIC",
            F_MED,
            WHITE if rewards_claimed else GRAY_L,
            continue_rect.centerx,
            continue_rect.centery)

        g.tutorial_elite_reward_gold_rect = (
            gold_rect)

        g.tutorial_elite_reward_relic_rect = (
            relic_rect)

        g.tutorial_elite_reward_leave_rect = (
            continue_rect)

        return
    txc(
        surf,
        "VICTORY! CLAIM YOUR REWARDS",
        F_BIG,
        GOLD,
        W // 2,
        55)
    # GOLD
    gold_rect = pygame.Rect(W // 2 - 180, 90, 360, 45)

    if not getattr(g, "reward_gold_claimed", True):
        hover = gold_rect.collidepoint(mouse)

        rrect(
            surf,
            GREEN_D if hover else PANEL,
            gold_rect,
            8,
            2,
            GOLD)

        gold_total = getattr(g, "reward_gold", 0)

        gold_bonus = getattr(g, "reward_gold_bonus", 0)

        if gold_bonus > 0:
            gold_text = (
                f"+ {gold_total} Gold "
                f"(+{gold_bonus})")
        else:
            gold_text = (
                f"+ {gold_total} Gold")

        txc(
            surf,
            gold_text,
            F_MED,
            GOLD,
            gold_rect.centerx,
            gold_rect.centery)

    else:
        rrect(
            surf,
            (20, 20, 30),
            gold_rect,
            8,
            1,
            GRAY)

        txc(
            surf,
            "[Gold Claimed]",
            F_MED,
            GRAY,
            gold_rect.centerx,
            gold_rect.centery)
    # RELIC
    relic_rect = pygame.Rect(W // 2 - 180, 145, 360, 45)

    if getattr(g, "reward_relic", None):

        if not getattr(g, "reward_relic_claimed", True):
            hover = relic_rect.collidepoint(mouse)

            rrect(
                surf,
                PURPLE_D if hover else PANEL,
                relic_rect,
                8,
                2,
                GOLD)

            txc(
                surf,
                f"Relic: {g.reward_relic}",
                F_MED,
                WHITE,
                relic_rect.centerx,
                relic_rect.centery)

        else:
            rrect(
                surf,
                (20, 20, 30),
                relic_rect,
                8,
                1,
                GRAY)

            txc(
                surf,
                "[Relic Claimed]",
                F_MED,
                GRAY,
                relic_rect.centerx,
                relic_rect.centery)
    # POSSIBLE CARD REWARDS
    txc(
        surf,
        "Possible Card Rewards",
        F_MED,
        WHITE,
        W // 2,
        220)

    pool = getattr(g, "reward_pool", [])

    spacing = 180

    if pool:
        total_w = (
            (len(pool) - 1) * spacing
            + CW)

        start_x = (W - total_w) // 2

        card_y = 245

        for i, card_name in enumerate(pool):
            card_x = start_x + i * spacing

            if card_name in CARDS:
                draw_card(
                    surf,
                    card_name,
                    card_x,
                    card_y,
                    99,
                    g=g)

    else:
        txc(
            surf,
            "No card rewards available",
            F_MED,
            GRAY,
            W // 2,
            330)
    # MINIGAME BUTTON
    mg_type = get_reward_minigame(g)

    btn_mg = pygame.Rect(W // 2 - 210, 470, 420, 50)

    btn_skip = pygame.Rect(W // 2 - 180, 535, 360, 40)

    rrect(
        surf,
        BLUE_D if btn_mg.collidepoint(mouse) else PANEL,
        btn_mg,
        8,
        2,
        BLUE)

    txc(
        surf,
        f"Play {minigame_display_name(mg_type)} for Card Reward",
        F_MED,
        WHITE,
        btn_mg.centerx,
        btn_mg.centery)

    rrect(
        surf,
        RED_D if btn_skip.collidepoint(mouse) else PANEL,
        btn_skip,
        8,
        1,
        GRAY)

    txc(
        surf,
        "Skip Card Reward & Return to Map",
        F_MED,
        GRAY_L,
        btn_skip.centerx,
        btn_skip.centery)

def draw_side_boss_reward(surf, g, mouse):

    surf.fill(BG)

    boss_type = getattr(g, "side_boss_reward_type", "")

    relic = getattr(g, "side_boss_reward_relic", "Unknown")

    if boss_type == "BoxingBoss":
        boss_name = "GODOT"

    elif boss_type == "UndertaleBoss":
        boss_name = "FRANZISKA VON KARMA"

    else:
        boss_name = "OPTIONAL BOSS"

    txc(
        surf,
        f"{boss_name} DEFEATED!",
        F_BIG,
        GOLD,
        W // 2,
        80)

    txc(
        surf,
        "CLAIM BOTH REWARDS",
        F_MED,
        GRAY_L,
        W // 2,
        125)
    # GOLD
    gold_rect = pygame.Rect(W // 2 - 220, 170, 440, 65)

    gold_claimed = getattr(g, "side_boss_gold_claimed", False)

    gold_hover = (
        gold_rect.collidepoint(mouse)
        and not gold_claimed)

    rrect(
        surf,
        GREEN_D if gold_hover else PANEL,
        gold_rect,
        10,
        2,
        GRAY if gold_claimed else GOLD)

    txc(
        surf,
        "[100 GOLD CLAIMED]"
        if gold_claimed
        else "+100 GOLD - CLICK TO CLAIM",
        F_MED,
        GRAY if gold_claimed else GOLD,
        gold_rect.centerx,
        gold_rect.centery)
    # RELIC
    relic_rect = pygame.Rect(W // 2 - 260, 270, 520, 150)

    relic_claimed = getattr(g, "side_boss_relic_claimed", False)

    relic_hover = (
        relic_rect.collidepoint(mouse)
        and not relic_claimed)

    rrect(
        surf,
        PURPLE_D if relic_hover else PANEL,
        relic_rect,
        10,
        2,
        GRAY if relic_claimed else GOLD)

    txc(
        surf,
        f"{relic} [CLAIMED]"
        if relic_claimed
        else relic,
        F_BIG,
        GRAY if relic_claimed else WHITE,
        relic_rect.centerx,
        relic_rect.top + 35)

    desc = RELICS.get(relic, {}).get("desc", "")

    txc(
        surf,
        desc,
        F_MED,
        GRAY if relic_claimed else GRAY_L,
        relic_rect.centerx,
        relic_rect.top + 82)

    if not relic_claimed:
        txc(
            surf,
            "CLICK TO CLAIM",
            F_MED,
            GOLD,
            relic_rect.centerx,
            relic_rect.top + 118)
    # CONTINUE
    both_claimed = (
        gold_claimed
        and relic_claimed)

    continue_rect = pygame.Rect(W // 2 - 190, 470, 380, 55)

    hover = (
        both_claimed
        and continue_rect.collidepoint(mouse))

    rrect(
        surf,
        GREEN_D if hover else PANEL,
        continue_rect,
        9,
        2,
        GREEN if both_claimed else GRAY)

    txc(
        surf,
        "START NEXT ACT"
        if both_claimed
        else "CLAIM GOLD + RELIC FIRST",
        F_MED,
        WHITE if both_claimed else GRAY,
        continue_rect.centerx,
        continue_rect.centery)

    g.side_boss_gold_rect = gold_rect
    g.side_boss_relic_rect = relic_rect
    g.side_boss_reward_continue_rect = continue_rect

def draw_chest(surf, g, mouse):
    surf.fill(BG)
    txc(surf, "TREASURE ROOM", F_BIG, GOLD, W//2, 120)
    
    chest_box = pygame.Rect(W//2 - 150, 200, 300, 180)
    rrect(surf, PANEL, chest_box, 12, 3, GOLD)
    

    if not getattr(g, "chest_opened", False):
        txc(surf, "OPEN CHEST", F_BIG, WHITE, W//2, 290)
        g.btn_open_chest.draw(surf, mouse)
    else:

        is_tutorial_chest = (
            getattr(g, "tutorial_active", False)
            and getattr(g, "tutorial_room", "") == "chest")


        if not is_tutorial_chest:
            txc(
                surf,
                f"Found: +{getattr(g, 'chest_gold', 0)} Gold!",
                F_MED,
                GOLD,
                W // 2,
                240)

        relic = getattr(g, "chest_relic", None)

        if relic:
            txc(
                surf,
                f"Found Relic: {relic}",
                F_MED,
                WHITE,
                W // 2,
                280)


        g.btn_leave_chest.draw(surf, mouse)
        
def give_random_event_relic(
    g):

    available_relics = [
        relic_name
        for relic_name in RELICS
        if (
            relic_name
            not in getattr(g, "relics", [])
            and relic_name
            not in RELIC_RANDOM_BLACKLIST
            and g.is_relic_unlocked(
                relic_name)
        )
    ]

    if not available_relics:

        g.add_log(
            "Event: no available Relics.")

        return None

    relic_name = random.choice(
        available_relics)

    g.add_relic(
        relic_name)

    g.add_log(
        f"Event: gained relic "
        f"'{relic_name}'.")

    return relic_name

def main():

    global screen, display

    g = Game()
    g.draw_settings_menu = draw_settings_menu
    audio_settings = (
        load_audio_settings())

    g.music_volume = (
        audio_settings[
            "music_volume"
        ])

    g.sfx_volume = (
        audio_settings[
            "sfx_volume"
        ])

    apply_audio_settings(g.music_volume, g.sfx_volume)
    Btn.click_callback = lambda: g.play_sfx("universfield-computer-mouse-click-352734", 0.40)
    g.display_mode = (
        INITIAL_DISPLAY_SETTINGS.get("mode", "Windowed")
    )

    g.display_resolutions = (
        get_resolution_options())

    saved_resolution = tuple(
        INITIAL_DISPLAY_SETTINGS.get(
            "resolution",
            (W, H)))

    if (
        saved_resolution
        in g.display_resolutions):
        g.display_resolution = (
            saved_resolution)

    else:
        g.display_resolution = (
            g.display_resolutions[0])
    show_title_screen = True

    global hovered_card_time, last_hovered_card
    hovered_card_time = 0
    last_hovered_card = None
    running = True
    map_enter_btn = None
    ctrl_select_btns = None
    dragging_audio_slider = None

    while running:
        if show_title_screen:
            screen.fill((12, 9, 20))

            txc(
                screen,
                "COURTROOM BATTLE",
                TITLE_FONT,
                GOLD,
                W // 2,
                H // 2 - 60)

            if (pygame.time.get_ticks() // 500) % 2 == 0:
                txc(
                    screen,
                    "PRESS ANY KEY TO CONTINUE...",
                    F_MED,
                    WHITE,
                    W // 2,
                    H // 2 + 50)

            current_display = (
                pygame.display.get_surface())

            if current_display is not None:
                display = current_display
            present_minigame(display, screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type in (
                    pygame.KEYDOWN,
                    pygame.MOUSEBUTTONDOWN):
                    show_title_screen = False

            clock.tick(60)
            continue

        if g.state == "play_minigame":

            minigame_name = getattr(g, "minigame_type", "HaremRunner")

            result = None

            try:

                if minigame_name == "HaremRunner":

                    result = (
                        runner_minigame.run_runner(screen, g)
                    )

                elif minigame_name in (
                    "HaremMaker",
                    "CardCupid"):

                    result = (
                        cupid_minigame.run_maker(screen, g)
                    )

                elif minigame_name == "ManPac":

                    result = (
                        manpac_minigame.run_manpac(screen, g)
                    )

                elif minigame_name == "BoxingBoss":

                    result = (
                        boxing_boss.run_boxing_boss(screen, g)
                    )

                elif minigame_name == "UndertaleBoss":

                    result = (
                        breakout_boss.run_undertale_boss(screen, g)
                    )
            # SAVE & QUIT TO MENU FROM MINIGAME
            except MinigameQuitToMenu:
                pygame.mixer.stop()
                pygame.mixer.music.stop()
                if not getattr(g, "practice_minigame", False):

                    g.save_run()

                g.practice_minigame = False

                g.reset()

                g.state = "start_menu"

                display = (
                    pygame.display.get_surface())

                continue
            # SAVE & QUIT GAME FROM MINIGAME
            except MinigameQuitGame:
                pygame.mixer.stop()
                pygame.mixer.music.stop()
                if not getattr(g, "practice_minigame", False):

                    g.save_run()

                running = False

                break
            # EXTRAS / PRACTICE MODE
            if getattr(g, "practice_minigame", False):

                g.practice_minigame = False
                g.reset()
                g.state = "extras"

                continue

            if result == "DEAD":

                if g.try_revive():

                    
                    g.state = "map"

                else:
                    g.php = 0
                    g.delete_save()

                    g.play_sfx("tuomas_data-wrong-answer-21-199825", 0.80)
                    g.state = "game_over"
                    g.save_run_to_history("DEFEAT")
            elif result == "WIN":
                if minigame_name in ["BoxingBoss", "UndertaleBoss"]:
                    g.on_side_boss_defeated(minigame_name)
                else:
                    g.take_reward(result)
            elif isinstance(result, list):

                if result:

                    g.history_add_cards(
                        result)
                    for card_name in result:
                        g.deck.append(
                            Card(card_name))

                        g.log(f"Minigame reward: {card_name}", GOLD)

                    if g.current_run_log:
                        last_log = g.current_run_log[-1]

                        if isinstance(last_log, dict):
                            last_log["chosen_reward"] = ", ".join(result)

                # TUTORIAL RUNNER FINISHED
                if (
                    getattr(g, "tutorial_active", False)
                    and getattr(g, "tutorial_room", "") == "runner"):
                    g.tutorial_room = "shop_map_intro"
                    g.tutorial_shop_map_step = 0
                    g.state = "map"

                else:
                    if result:
                        g.state = "map"
                    else:
                        g.skip_reward()

            elif result:
                g.take_reward(result)

            else:
                g.skip_reward()

            continue

        mouse = screen_to_virtual(
            pygame.mouse.get_pos(),
            W,
            H)
        if g.state == "combat":
            g.update_card_animations()
            g.update_combat_animations()
        if g.state == "select_profile":
            draw_select_profile(
                screen,
                g,
                mouse)

        elif g.state == "delete_save_confirm":
            draw_delete_save_confirm(
                screen,
                g,
                mouse)   
        elif g.state == "name_profile":
            draw_name_profile(screen, g, mouse)
        elif g.state == "tutorial_prompt":
            tutorial.draw_tutorial_prompt(screen,g,mouse)
        elif g.state == "start_menu":
            draw_start_menu(screen, g, mouse)
        elif g.state == "collection":
            draw_collection(screen,g,mouse)
        elif g.state == "extras":
            draw_extras(screen,g,mouse)
        elif g.state == "abandon_confirm":
            draw_abandon_confirm(screen, g, mouse)
        elif g.state == "char_select":
            draw_char_select(screen, g, mouse)
        elif g.state == "settings_menu":
            draw_settings_menu(screen, g, mouse)
        elif g.state == "run_history":
            run_history.draw_run_history(screen, g, mouse)
        elif g.state == "history_build":
            draw_history_build(screen,g,mouse)
        elif g.state == "controls_select":
            ctrl_select_btns = draw_controls_select(screen, g, mouse)
        elif g.state == "controls_menu":
            draw_controls_menu(screen, g, mouse)
        elif g.state == "view_cards":
            draw_card_view(screen, g, mouse)
        
        else:
            screen.fill(BG)
            if g.state == "map":
                map_enter_btn = draw_map(screen, g)
                tutorial.draw_map_overlay(screen, g, mouse)

            elif g.state == "campfire":
                draw_campfire(screen, g, mouse)
                tutorial.draw_campfire_overlay(screen,g,mouse)
            elif g.state == "campfire_upgrade":
                draw_campfire_upgrade(screen, g, mouse)
                tutorial.draw_upgrade_overlay(screen,g,mouse)
            elif g.state == "reward":
                draw_reward(screen, g, mouse)
                tutorial.draw_reward_overlay(screen, g, mouse)
            elif g.state == "side_boss_reward":
                draw_side_boss_reward(screen,g,mouse)
            elif g.state == "chest":
                draw_chest(screen, g, mouse)
                tutorial.draw_chest_overlay(screen,g,mouse)
            elif g.state == "combat":
                draw_combat(screen, g, mouse)
                tutorial.draw_combat_overlay(screen, g, mouse)
                tutorial.draw_elite_overlay(screen,g,mouse)
                tutorial.draw_boss_overlay(screen, g, mouse)
            elif g.state == "shop":

                draw_shop(
                    screen,
                    g,
                    mouse)

                tutorial.draw_shop_overlay(
                    screen,
                    g,
                    mouse)          

            elif g.state == "event":

                screen.fill((20, 20, 30))
            
                ev_data = GAME_EVENTS[g.current_event_key]
                # EVENT TITLE
                txc(
                    screen,
                    ev_data["title"],
                    F_BIG,
                    GOLD,
                    W // 2,
                    90)
                # EVENT DESCRIPTION
                event_text = ev_data["text"]

                words = event_text.split()

                event_lines = []
                current_line = ""

                for word in words:

                    test_line = (
                        current_line + " " + word).strip()

                    if (
                        EVENT_TEXT_FONT.size(
                            test_line)[0]
                        <= 760):
                        current_line = test_line

                    else:

                        if current_line:
                            event_lines.append(
                                current_line)

                        current_line = word

                if current_line:
                    event_lines.append(
                        current_line)


                event_text_start_y = 155

                for line_i, line_text in enumerate(
                    event_lines[:4]):

                    txc(
                        screen,
                        line_text,
                        EVENT_TEXT_FONT,
                        WHITE,
                        W // 2,
                        event_text_start_y
                        + line_i * 28)
            
                g.event_buttons = []
                start_y = 300
                for i, opt in enumerate(ev_data["options"]):
                    btn_w, btn_h = 520, 64
                    btn_x = W//2 - btn_w//2
                    btn_y = start_y + i * 82
                
                    rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

                    required_gold = int(
                        opt.get(
                            "cost",
                            opt.get("gold_loss", 0)
                        ))

                    disabled = (
                        required_gold > getattr(g, "pgold", 0)
                    )


                    if (
                        opt.get("action")
                        == "gain_relic_pay_gold"
                        and opt.get("relic")
                        in getattr(g, "relics", [])
                    ):
                        disabled = True

                    g.event_buttons.append({
                        "rect": rect,
                        "opt": opt,
                        "disabled": disabled
                    })

                    is_hover = (
                        rect.collidepoint(
                            mouse)
                        and not disabled)
                    if disabled:

                        button_bg = (
                            28,
                            28,
                            35)

                        button_border = GRAY

                    else:

                        button_bg = (
                            (70, 70, 90)
                            if is_hover
                            else (40, 40, 60))

                        button_border = (
                            GOLD
                            if is_hover
                            else GRAY)

                    rrect(
                        screen,
                        button_bg,
                        (
                            btn_x,
                            btn_y,
                            btn_w,
                            btn_h),
                        10,
                        2,
                        button_border)
                    label_color = (
                        GRAY
                        if disabled
                        else WHITE)
                    label = opt["label"]

                    words = label.split()

                    lines = []
                    line = ""

                    for word in words:

                        test = (
                            line + " " + word).strip()

                        if (EVENT_OPTION_FONT.size(test)[0]> btn_w - 30):

                            if line:
                                lines.append(line)

                            line = word

                        else:
                            line = test

                    if line:
                        lines.append(line)


                    if len(lines) == 1:

                        txc(
                            screen,
                            lines[0],
                            EVENT_OPTION_FONT,
                            label_color,
                            btn_x + btn_w // 2,
                            btn_y + btn_h // 2)

                    else:

                        start_text_y = (
                            btn_y
                            + btn_h // 2
                            - ((len(lines) - 1) * 10))

                        for line_i, text_line in enumerate(
                            lines[:3]):

                            txc(
                                screen,
                                text_line,
                                EVENT_OPTION_FONT,
                                label_color,
                                btn_x + btn_w // 2,
                                start_text_y
                                + line_i * 20)



            elif g.state == "pre_minigame":
                draw_pre_minigame(screen, g, mouse)
            
            elif g.state == "game_over":
                draw_game_over(
                    screen,
                    g,
                    mouse)

            elif g.state == "level_up":
                draw_level_up(
                    screen,
                    g,
                    mouse)

            elif g.state == "win":
                draw_win(
                    screen,
                    g,
                    mouse)

            normal_run_screens = (
                "map",
                "campfire",
                "reward",
                "pre_minigame",
                "shop",
                "chest",
                "event")

            if g.state in normal_run_screens:

                g.btn_deck.label = (
                    f"Deck: {len(g.deck)}")

                g.btn_deck.draw(screen, mouse)

                if not getattr(g, "tutorial_active", False):

                    g.btn_ingame_set.draw(screen, mouse)

                g.btn_dev.draw(screen, mouse)

            elif g.state == "combat":
                g.btn_ingame_set.draw(screen, mouse)

                g.btn_dev.draw(screen, mouse)

            hud_states = (
                "map",
                "combat",
                "campfire",
                "reward",
                "pre_minigame",
                "shop",
                "chest",
                "event")

            if g.state in hud_states:
                draw_run_hud(screen, g)

            if g.state in ("map", "combat", "campfire", "reward", "pre_minigame", "shop", "chest","event"):
                draw_relics(screen, g, mouse)


        present_minigame(display, screen)

        for event in pygame.event.get():
            if hasattr(event, "pos"):

                event.pos = (
                    screen_to_virtual(
                        event.pos,
                        W,
                        H)
                )
            if event.type == pygame.QUIT: 
                running = False
            if (
                event.type == pygame.KEYDOWN
                and g.state == "controls_menu"
                and g.awaiting_key is not None):
                mg, action = g.awaiting_key

                if event.key == pygame.K_ESCAPE:
                    g.awaiting_key = None

                else:
                    GLOBAL_CONTROLS[mg][action] = event.key
                    g.awaiting_key = None

                continue
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                if g.state == "map":
                    scroll_speed = 60
                    if event.button == 4: 
                        g.map_scroll_y += scroll_speed
                    elif event.button == 5: 
                        g.map_scroll_y -= scroll_speed
                    g.map_scroll_y = max(0, min(g.map_scroll_y, 1950))
                
                elif g.state == "view_cards":
                    scroll_speed = 60
                    if event.button == 4: 
                        g.card_scroll += scroll_speed
                    elif event.button == 5: 
                        g.card_scroll -= scroll_speed
                    
              
                    g.card_scroll = min(0, g.card_scroll)
                    
                    cols = 6
                    pad_y = 220
                    if g.view_mode == "dev" and getattr(g, "dev_tab", "") == "Relics":
                        num_cards = len(RELICS)
                        cols = 4
                        pad_y = 124
                    else:
                        num_cards = len(g.viewing_cards)
                        cols = 6


                    rows = (
                        num_cards + cols - 1) // cols

                    if g.view_mode == "dev":

                        if getattr(g, "dev_tab", "") == "Relics":

                            content_start_y = 155
                            item_height = 124

                        else:

                            content_start_y = 155
                            item_height = 220

                        visible_bottom = H - 65
                        visible_height = (
                            visible_bottom
                            - content_start_y)

                        content_height = (
                            rows * item_height)

                        max_scroll = min(
                            0,
                            visible_height
                            - content_height)

                        g.card_scroll = max(
                            max_scroll,
                            min(0, g.card_scroll)
                        )

                    else:

                        total_height = (
                            90
                            + rows * pad_y)

                        if total_height > H - 100:

                            max_scroll = -(
                                total_height
                                - (H - 100))

                            g.card_scroll = max(max_scroll, g.card_scroll)

                        else:

                            g.card_scroll = 0

                elif g.state == "collection":

                    scroll_speed = 60

                    if event.button == 4:
                        g.collection_scroll += scroll_speed

                    elif event.button == 5:
                        g.collection_scroll -= scroll_speed

                    min_scroll = getattr(g, "collection_min_scroll", 0)

                    g.collection_scroll = max(
                        min_scroll,
                        min(0, g.collection_scroll)
                    )

                elif g.state == "campfire_upgrade":

                    scroll_speed = 60

                    if event.button == 4:
                        g.upgrade_scroll += scroll_speed

                    elif event.button == 5:
                        g.upgrade_scroll -= scroll_speed

                    g.upgrade_scroll = min(0, g.upgrade_scroll)

                    upgradeable_count = len([
                        c for c in g.deck
                        if not c.upgraded
                        and c.name in CARD_UPGRADES
                    ])

                    cols = 4
                    rows = (
                        upgradeable_count + cols - 1) // cols

                    total_height = (
                        105
                        + rows * 215)

                    visible_height = H - 120

                    if total_height > visible_height:
                        max_scroll = -(
                            total_height
                            - visible_height)

                        g.upgrade_scroll = max(max_scroll, g.upgrade_scroll)

                    else:
                        g.upgrade_scroll = 0

            if (
                event.type
                == pygame.MOUSEMOTION
                and g.state
                == "settings_menu"
                and dragging_audio_slider
                is not None):

                pos = event.pos

                if (
                    dragging_audio_slider
                    == "music"):

                    g.music_volume = (
                        slider_value_from_x(pos[0], g.music_slider_rect)
                    )

                elif (
                    dragging_audio_slider
                    == "sfx"):

                    g.sfx_volume = (
                        slider_value_from_x(pos[0], g.sfx_slider_rect)
                    )

                apply_audio_settings(g.music_volume, g.sfx_volume)

                continue


            if (
                event.type
                == pygame.MOUSEBUTTONUP
                and event.button == 1
                and dragging_audio_slider
                is not None):

                save_audio_settings(g.music_volume, g.sfx_volume)

                dragging_audio_slider = None

                continue


            elif event.type == pygame.KEYDOWN:
                # ВЪВЕЖДАНЕ НА ИМЕ НА ПРОФИЛА
                if g.state == "name_profile":
                    if event.key in (
                        pygame.K_RETURN,
                        pygame.K_KP_ENTER):
                        g.confirm_profile_name()
                    elif event.key == pygame.K_BACKSPACE:
                        g.input_text = g.input_text[:-1]
                    elif len(g.input_text) < 15 and event.unicode.isprintable():
                        g.input_text += event.unicode
                    continue

                if g.state == "view_cards":
                    if event.key == pygame.K_UP:
                        g.card_scroll += 50
                    elif event.key == pygame.K_DOWN:
                        g.card_scroll -= 50
                    
                    g.card_scroll = min(0, g.card_scroll)
                    if (
                        g.view_mode == "dev"
                        and getattr(g, "dev_tab", "") == "Relics"):

                        cols = 4
                        pad_y = 124
                        num_items = len(RELICS)

                    else:

                        cols = 6
                        pad_y = 220
                        num_items = len(g.viewing_cards)


                    rows = (
                        num_items + cols - 1) // cols

                    total_height = (
                        155
                        + rows * pad_y)
                   
                    
                    if total_height > H - 100:
                        g.card_scroll = max(-(total_height - (H - 100)), g.card_scroll)
                    else:
                        g.card_scroll = 0

                
                if event.key == pygame.K_ESCAPE:
                    # TUTORIAL
                    if getattr(g, "tutorial_active", False):
                        pass
                    # SETTINGS -> RETURN
                    elif g.state == "settings_menu":

                        g.state = (
                            g.prev_settings_state)

                    elif g.state == "controls_menu":

                        g.awaiting_key = None
                        g.state = "controls_select"

                    elif g.state == "controls_select":

                        g.state = "settings_menu"
                    # NORMAL RUN -> SETTINGS
                    elif g.state in (
                        "map",
                        "combat",
                        "campfire",
                        "campfire_upgrade",
                        "reward",
                        "side_boss_reward",
                        "chest",
                        "pre_minigame",
                        "shop",
                        "event"):

                        g.prev_settings_state = (
                            g.state)

                        g.state = (
                            "settings_menu")
                    # DECK / CARD VIEW
                    elif g.state == "view_cards":

                        g.close_card_view()
                    # OTHER MENUS
                    elif g.state == "collection":

                        g.collection_scroll = 0
                        g.state = "start_menu"

                    elif g.state == "extras":

                        g.state = "start_menu"

                    elif g.state == "char_select":

                        g.state = "start_menu"

                    elif g.state == "history_build":

                        g.state = "run_history"

                    elif g.state == "run_history":

                        g.state = "start_menu"

                    elif (
                        g.state == "select_profile"
                        and g.profiles[
                            g.current_slot
                        ]["name"]):

                        g.state = "start_menu"

                if (g.state == "combat" and event.key == pygame.K_e and not g.drag_card):
                    if (getattr(g, "tutorial_active", False)and getattr(g, "tutorial_room", "") == "first_enemy"and getattr(g, "tutorial_step", 0) not in (9, 14)):
                            pass
                    
                    else:
                        g.end_turn()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                settings_states = (
                    "map",
                    "combat",
                    "campfire",
                    "campfire_upgrade",
                    "reward",
                    "side_boss_reward",
                    "chest",
                    "pre_minigame",
                    "shop",
                    "event")

                if (
                    not getattr(g, "tutorial_active", False)
                    and g.state
                    in settings_states
                    and g.btn_ingame_set.hit(
                        pos)
                ):

                    g.prev_settings_state = (
                        g.state)

                    g.state = (
                        "settings_menu")

                    continue

                if (g.state == "combat" and tutorial.handle_combat_click(g, pos)):continue
                if (g.state == "map" and tutorial.handle_map_click( g, pos )):continue
                if (g.state == "reward" and tutorial.handle_elite_reward_click(g, pos)):
                   continue
                # ИМЕ НА ПРОФИЛА
            
                if g.state == "select_profile":

                    delete_clicked = False

                    for slot_idx, rect in getattr(g, "profile_delete_rects", []):

                        if rect.collidepoint(pos):
                            g.delete_save_slot = slot_idx
                            g.state = "delete_save_confirm"

                            delete_clicked = True
                            break

                    if delete_clicked:
                        continue

                    # NORMAL SAVE SLOT CLICK
                    for i, btn in enumerate(g.btn_slots):

                        if btn.hit(pos):
                            g.select_slot(i)
                            break

                    # BACK BUTTON
                    if (
                        g.profiles[g.current_slot]["name"]
                        and g.btn_slot_back.hit(pos)):
                        g.state = "start_menu"

                    continue


                elif g.state == "delete_save_confirm":

                    if g.btn_delete_save_yes.hit(pos):

                        slot = getattr(g, "delete_save_slot", None)

                        if slot is not None:
                            g.delete_profile_slot(slot)

                        g.delete_save_slot = None
                        g.state = "select_profile"

                    elif g.btn_delete_save_no.hit(pos):

                        g.delete_save_slot = None
                        g.state = "select_profile"

                    continue


              

                elif g.state == "name_profile":
                    if g.btn_confirm_name.hit(pos):
                        g.confirm_profile_name()
                elif g.state == "tutorial_prompt":

                    tutorial.handle_tutorial_prompt(g, pos)

                    continue
                elif g.state == "tutorial_runner_ready":
                    tutorial.draw_runner_ready(
                        screen,
                        g,
                        mouse)
                # МЕНЮТА 
                elif g.state == "start_menu":

                    if g.btn_profile.hit(pos):
                        g.state = "select_profile"

                    elif (hasattr(g, "btn_history") and g.btn_history.hit(pos)):
                        g.selected_history_index = 0
                        g.history_scroll = 0
                        g.state = "run_history"
                    elif (hasattr(g,"btn_collection")and g.btn_collection.hit(pos)):
                        g.collection_tab = "Bruiser"
                        g.collection_scroll = 0
                        g.state = "collection"
                    elif (hasattr(g,"btn_extras") and g.btn_extras.hit(pos)):
                        g.state = "extras"
                    elif g.has_save():

                        if g.btn_continue.hit(pos):
                            g.load_run()

                        elif g.btn_new_run.hit(pos):
                            g.state = "abandon_confirm"

                    else:

                        if g.btn_start_play.hit(pos):
                            g.state = "char_select"

                    if g.btn_start_set.hit(pos):
                        g.prev_settings_state = g.state
                        g.state = "settings_menu"

                    elif (
                        hasattr(g, "btn_quit_game")
                        and g.btn_quit_game.hit(pos)):
                        running = False

                elif g.state == "collection":

                    # BACK
                    if (getattr(g, "collection_back_rect", None) and g.collection_back_rect.collidepoint(pos)):

                        g.state = "start_menu"
                        g.collection_scroll = 0

                        continue

                    # TABS
                    for tab_name, rect in getattr(g, "collection_tab_rects", []):

                        if rect.collidepoint(
                            pos):

                            g.collection_tab = (
                                tab_name)

                            g.collection_scroll = 0

                            break

                    continue

                elif g.state == "history_build":

                    if getattr(g, "history_build_back_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):

                        g.state = "run_history"

                    continue

                elif g.state == "extras":

                    if getattr(g, "extras_back_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):

                        g.state = "start_menu"
                        continue

                    for game_id, rect in getattr(g, "extras_minigame_rects", []):

                        if rect.collidepoint(pos):
                            # PRACTICE SETUP
                            g.practice_minigame = True

                            g.tutorial_active = False

                            g.php = 70
                            g.pmx = 70

                            g.relics = []
                            practice_cards = [
                                name
                                for name, data
                                in CARDS.items()
                                if (
                                    name not in (
                                        "Strike",
                                        "Defend")
                                    and data.get(
                                        "type") in (
                                        "attack",
                                        "skill",
                                        "power"))]

                            if len(
                                practice_cards) >= 3:

                                g.reward_pool = random.sample(practice_cards, 3)

                            else:

                                g.reward_pool = (
                                    practice_cards[:3])

                            g.minigame_type = (
                                game_id)

                            g.state = (
                                "play_minigame")

                            break

                    continue
                elif g.state == "run_history":

                    run_history.handle_run_history_click(g, pos)

                    continue

                elif g.state == "abandon_confirm":
                    if g.btn_abandon_yes.hit(pos):
                        g.delete_save()
                        g.state = "char_select"
                    elif g.btn_abandon_no.hit(pos):
                        g.state = "start_menu"

                elif g.state == "view_cards":

                    if g.btn_close_view.hit(pos):
                        g.close_card_view()
                    elif g.view_mode == "dev":

                        clicked_tab = False
                        for tab_name, rect in getattr(g, "dev_tab_rects", []):
                            if rect.collidepoint(pos):
                                g.play_sfx("universfield-computer-mouse-click-352734", 0.40)

                                load_dev_tab(g, tab_name)
                                clicked_tab = True
                                break

                        if not clicked_tab:
                            if g.dev_tab == "Relics":
                                for relic_name, rect in getattr(g, "dev_relic_rects", []):
                                    if rect.collidepoint(pos):
                                        g.play_sfx("universfield-computer-mouse-click-352734", 0.40)
                                        if not hasattr(g, "relics"):
                                            g.relics = []
                                        if relic_name in g.relics:
                                            g.relics.remove(relic_name)

                                            if hasattr(g, "log"):
                                                g.log(f"DEV removed relic: {relic_name}", RED)
                                        else:
                                            g.add_relic(relic_name)
                                            
                                            g.log(f"DEV added relic: {relic_name}", GOLD)
                                        break
                            else:
                                 for c in reversed(g.viewing_cards):
                                     if c.collides(pos, c.x, c.y):
                                         g.play_sfx("universfield-computer-mouse-click-352734", 0.40
)
                                         g.deck.append(Card(c.name))
                                        
                                         if hasattr(g, "log"):
                                             g.log(f"DEV added card: {c.name}", GOLD)
                                         break

                elif g.state == "level_up":

                    level_up_rect = getattr(g, "level_up_continue_rect", None)

                    if (level_up_rect and level_up_rect.collidepoint(pos)):

                        g.state = "win"

                    continue

                elif g.state == "char_select":

                    if g.btn_class_1.hit(pos):
                        g.start_run("BRUISER")
                        g.state = "map"

                    elif g.btn_class_2.hit(pos):
                        g.start_run("ASSASSIN")
                        g.state = "map"

                    elif g.btn_tutorial.hit(pos):
                        tutorial.start_tutorial(g)

                    elif g.btn_set_back.hit(pos):
                        g.state = "start_menu"

                elif g.state == "settings_menu":
                    # DISPLAY MODE
                    if getattr(g, "music_slider_rect", pygame.Rect(0, 0, 0, 0)).inflate(0, 20).collidepoint(pos):
                        g.play_sfx("universfield-computer-mouse-click-352734", 0.40)
                        dragging_audio_slider = ("music")

                        g.music_volume = (slider_value_from_x(pos[0], g.music_slider_rect))

                        apply_audio_settings(g.music_volume, g.sfx_volume)
                        g.play_sfx("universfield-computer-mouse-click-352734", 0.40)


                    elif getattr(g, "sfx_slider_rect", pygame.Rect(0, 0, 0, 0)).inflate(0, 20).collidepoint(pos):

                        dragging_audio_slider = ("sfx")

                        g.sfx_volume = (slider_value_from_x(pos[0], g.sfx_slider_rect))

                        apply_audio_settings(g.music_volume, g.sfx_volume)
                    # DISPLAY MODE
                    elif getattr(g, "display_mode_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
                        g.play_sfx("universfield-computer-mouse-click-352734", 0.40)
                        display_modes = [
                            "Windowed",
                            "Borderless",
                            "Fullscreen"
                        ]

                        try:

                            mode_index = (
                                display_modes.index(
                                    g.display_mode)
                            )

                        except ValueError:

                            mode_index = 0

                        g.display_mode = ( 
                            display_modes[
                                (mode_index + 1)
                                % len(display_modes)
                            ])
                    # RESOLUTION
                    elif (
                        getattr(g, "display_resolution_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos)
                        and g.display_mode
                        in (
                            "Windowed",
                            "Borderless")
                    ):
                        g.play_sfx("universfield-computer-mouse-click-352734", 0.40)
                        options = (
                            g.display_resolutions)

                        try:

                            current_index = (
                                options.index(
                                    g.display_resolution)
                            )

                        except ValueError:

                            current_index = 0

                        next_index = (
                            current_index + 1) % len(options)

                        g.display_resolution = (
                            options[next_index])
                    # APPLY DISPLAY
                    elif getattr(g, "display_apply_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
                        g.play_sfx("universfield-computer-mouse-click-352734", 0.40)
                        new_settings = {
                            "mode": (
                                g.display_mode),
                            "resolution": list(
                                g.display_resolution)
                        }
                        save_display_settings(
                            new_settings)
                        g.display_restart_notice = True
                    # NORMAL SETTINGS
                    elif g.btn_set_ctrls.hit(pos):

                        g.state = (
                            "controls_select")

                    elif (
                        g.prev_settings_state
                        != "start_menu"):

                        if g.btn_set_quit.hit(
                            pos):

                            g.save_run()
                            g.reset()

                        elif (hasattr(g, "btn_set_quit_desktop")and g.btn_set_quit_desktop.hit(pos)):

                            g.save_run()
                            running = False

                    if g.btn_set_back.hit(
                        pos):

                        g.state = (
                            g.prev_settings_state)  
                elif g.state == "controls_select":
                    if g.btn_set_back.hit(pos): 
                        g.state = "settings_menu"
                    elif ctrl_select_btns:
                        for btn, mg in ctrl_select_btns:
                            if btn.hit(pos):
                                g.selected_minigame_ctrls = mg
                                g.state = "controls_menu"

                elif g.state == "controls_menu":
                    if g.btn_set_back.hit(pos): 
                        g.awaiting_key = None
                        g.state = "controls_select"
                    else:
                        for btn, mg, action in g.temp_ctrl_btns:
                            if btn.hit(pos):
                                g.awaiting_key = (mg, action)

                elif g.state == "side_boss_reward":

                    if getattr(g, "side_boss_gold_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):

                        g.claim_side_boss_gold()

                    elif getattr(g, "side_boss_relic_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):

                        g.claim_side_boss_relic()

                    elif getattr(g, "side_boss_reward_continue_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):

                        if (
                            getattr(g, "side_boss_gold_claimed", False)
                            and getattr(g, "side_boss_relic_claimed", False)
                        ):
                            g.claim_side_boss_reward()

                    continue
                if g.state == "campfire_upgrade":
                    if tutorial.handle_upgrade_click(g,pos):
                        continue
                    for rect, card in getattr(g, "upgrade_card_rects", []):

                        if rect.collidepoint(pos):


                            g.upgrade_selected_card = card

                            break


                    if getattr(g, "upgrade_confirm_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):

                        if getattr(g, "upgrade_selected_card", None) is not None:

                            g.confirm_campfire_upgrade()


                    elif getattr(g, "upgrade_back_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):

                        g.upgrade_selected_card = None
                        g.state = "campfire"


                    continue                
                # ИН-ГЕЙМ СЪСТОЯНИЯ 
                if g.state in ("map", "combat", "campfire", "reward", "pre_minigame", "shop", "chest","event"):
                    if g.btn_deck.hit(pos):
                        g.open_card_view(g.deck, "YOUR DECK")
                    elif g.btn_ingame_set.hit(pos):
                        g.prev_settings_state = g.state
                        g.state = "settings_menu"
                    elif hasattr(g, 'btn_dev') and g.btn_dev.hit(pos):
                        g.prev_state = g.state
                        g.view_mode = "dev"
                        g.dev_tab = "Bruiser"
                        g.card_scroll = 0
                        g.state = "view_cards"

                        load_dev_tab(g, "Bruiser")
                    
                    elif g.state == "map":
                        click_pos = event.pos
                        scroll_y = getattr(g, 'map_scroll_y', 0)

                        # Клик на SKIP TO BOSS
                        skip_rect = getattr(g, "skip_boss_rect", pygame.Rect(W - 170, 55, 160, 40))

                        if skip_rect.collidepoint(
                            click_pos):
                            boss_prep_floor = len(g.map_data) - 2
                            fire_node = g.map_data[boss_prep_floor][0]
                            g.enter_node(fire_node["floor"], fire_node["idx"])
                            g.map_scroll_y = max(0, min((H // 2) - fire_node["y"], 1950))
                            continue

                        selectable_nodes = []
                        if getattr(g, 'current_node_idx', None) is None:
                            selectable_nodes = g.map_data[0]
                        else:
                            target_floor = g.floor + 1
                            if target_floor < len(g.map_data):
                                curr_node = g.map_data[g.floor][g.current_node_idx]
                                for nxt_idx in curr_node["next_nodes"]:
                                    selectable_nodes.append(g.map_data[target_floor][nxt_idx])

                        clicked = False
                        for node in selectable_nodes:
                            nx = node["x"]
                            ny = node["y"] + scroll_y
                            is_edgeworth = (
                                node["type"] == "boss"
                                and node.get("minigame") == "None")

                            if is_edgeworth:
                                r = 40
                            elif node["type"] == "boss":
                                r = 30
                            else:
                                r = 25

                            if math.hypot(click_pos[0] - nx, click_pos[1] - ny) <= r:
                                g.enter_node(node["floor"], node["idx"])
                                g.map_scroll_y = max(0, min((H // 2) - node["y"], 1950))
                                clicked = True
                                break
                    
                    elif g.state == "campfire":
                        if tutorial.handle_campfire_click(g,pos):
                            continue
                        if g.cf_rest.hit(pos):   
                            g.cf_do_rest()
                        elif g.cf_upg.hit(pos): 
                            g.cf_do_upgrade()
                        elif g.cf_leave.hit(pos): 
                            g._leave_campfire()

                    elif g.state == "reward":

                        gold_rect = pygame.Rect(W // 2 - 180, 90, 360, 45)

                        relic_rect = pygame.Rect(W // 2 - 180, 145, 360, 45)

                        btn_mg = pygame.Rect(W // 2 - 210, 470, 420, 50)

                        btn_skip = pygame.Rect(W // 2 - 180, 535, 360, 40)

                        if (
                            gold_rect.collidepoint(pos)
                            and not getattr(g, "reward_gold_claimed", True)
                        ):

                            g.pgold += getattr(g, "reward_gold", 0)

                            g.reward_gold_claimed = True

                            g.log(f"Claimed {g.reward_gold} Gold.", GOLD)

                            tutorial.on_reward_gold_claimed(g)

                        elif (
                            getattr(g, "reward_relic", None)
                            and relic_rect.collidepoint(pos)
                            and not getattr(g, "reward_relic_claimed", True)
                        ):

                            relic = g.reward_relic

                            if not hasattr(g, "relics"):
                                g.relics = []

                            if relic not in g.relics:
                                g.add_relic(relic)

                            g.reward_relic_claimed = True

                            g.log(f"Claimed relic: {relic}.", GOLD)

                        elif btn_mg.collidepoint(pos):

                            if tutorial.can_start_reward_minigame(g):

                                g.minigame_type = (
                                    get_reward_minigame(g))

                                if g.run_history_events:

                                    entry = (
                                        g.run_history_events[-1])

                                    entry[
                                        "minigame_status"
                                    ] = "PLAYED"

                                    entry[
                                        "minigame"
                                    ] = g.minigame_type

                                print("STARTING MINIGAME:",minigame_display_name ( g.minigame_type))

                                if (
                                    getattr(g, "tutorial_active", False)
                                    and getattr(g, "tutorial_room", "") == "reward"
                                ):

                                    g.tutorial_room = (
                                        "runner")

                                g.state = "play_minigame"

                        elif btn_skip.collidepoint(pos):

                            if not getattr(g, "tutorial_active", False):
                                g.skip_reward()


                    elif g.state == "event":
                        print("Кликнато е в event екран!") 
                        if hasattr(g, "event_buttons"):
                            for btn in g.event_buttons:
                                if (
                                    btn["rect"].collidepoint(
                                        event.pos)
                                    and not btn.get("disabled", False)
                                    and not getattr(g, "event_resolved", False)
                                ):
                                    opt = btn["opt"]
                                    action = opt["action"]

                                    print(f"Натиснат е бутон: {opt['label']}")
                                    g.event_resolved = True

                                    if not hasattr(g, "relics"):
                                        g.relics = []
                                
                                # Прост Релик
                                    if action == "gain_relic_simple":
                                        r_name = opt["relic"]
                                        if r_name not in g.relics: g.add_relic(r_name)
                                        g.add_log(f"Евент: Получи релик '{r_name}'.")
                                    elif (
                                        action
                                        == "lose_hp_gain_random_relic"):

                                        relic_name = (
                                            give_random_event_relic(
                                                g)
                                        )

                                        if relic_name is not None:

                                            g.php = max(
                                                1,
                                                g.php
                                                - opt.get("hp_loss", 10)
                                            )

                                            g.add_log(
                                                "Mysterious Shrine: "
                                                "lost 10 HP.")
                                    # Релик + Wounds
                                    elif action == "gain_relic_and_strikes":

                                        r_name = opt[
                                            "relic"
                                        ]

                                        if (
                                            r_name
                                            not in g.relics):
                                            g.add_relic(
                                                r_name)

                                        strike_count = opt.get("strikes", 1)

                                        for _ in range(
                                            strike_count):

                                            g.deck.append(
                                                Card(
                                                    "Strike")
                                            )

                                        g.add_log(
                                            f"Event: gained '{r_name}' "
                                            f"and added {strike_count} "
                                            f"Strike card(s).")

                                    #  Vampire Fangs 
                                    elif action == "gain_vampire_fangs":
                                        if "Vampire Fangs" not in g.relics: g.add_relic("Vampire Fangs")
                                        g.pmx = max(10, int(g.pmx * 0.8))
                                        g.php = min(g.php, g.pmx)
                                        g.add_log("Евент: Получи Vampire Fangs, но загуби 20% Max HP.")

                                        # Full Heal - Gold 
                                    elif action == "full_heal_lose_gold":

                                        cost = opt.get("cost", 40)

                                        if g.pgold >= cost:

                                            g.pgold -= cost
                                            g.php = g.pmx

                                            g.add_log(
                                                f"Event: fully healed "
                                                f"for {cost} Gold.")

                                        # Upgrade random card
                                    elif (
                                        action
                                        == "upgrade_random_cards_lose_hp"):

                                        g.php = max(
                                            1,
                                            g.php
                                            - opt.get("hp_loss", 12)
                                        )

                                        upgradable = [
                                            card
                                            for card in g.deck
                                            if (
                                                hasattr(card, "upgraded")
                                                and not card.upgraded
                                                and card.name
                                                in CARD_UPGRADES)
                                        ]

                                        random.shuffle(
                                            upgradable)

                                        selected_cards = (
                                            upgradable[
                                                :opt.get("count", 2)
                                            ])

                                        for card in selected_cards:

                                            card.do_upgrade()

                                        g.add_log(
                                            f"Molten Forge: "
                                            f"upgraded "
                                            f"{len(selected_cards)} "
                                            f"card(s), lost 12 HP.")

                                    #  Mind Glass
                                    elif action == "gain_mind_glass":
                                        if "Mind Glass" not in g.relics: g.add_relic("Mind Glass")
                                        g.pmx = max(10, g.pmx - 10)
                                        g.php = min(g.php, g.pmx)
                                        g.add_log("Евент: Получи Mind Glass (+1 Draw).")

                                    # Remove 1 Strike AND 1 Defend
                                    elif action == "remove_two_basic_cards":

                                        removed_cards = []

                                        for target_name in ("Strike", "Defend"):

                                            for i, card in enumerate(g.deck):

                                                c_name = (
                                                    card.name
                                                    if hasattr(card, "name")
                                                    else str(card))

                             
                                                clean_name = c_name.rstrip("+")

                                                if clean_name == target_name:

                                                    g.deck.pop(i)

                                                    removed_cards.append(
                                                        target_name)

                                                    break

                                        if removed_cards:
                                            g.add_log(
                                                "Евент: Премахна "
                                                + " и ".join(removed_cards)
                                                + ".")

                                    elif action == "half_max_hp_upgrade_all":

                                        # Half Max HP
                                        g.pmx = max(1, g.pmx // 2)

          
                                        g.php = min(g.php, g.pmx)

                                        upgraded_count = 0

                                        for card in g.deck:

                                            if (
                                                card.name in CARD_UPGRADES
                                                and not card.upgraded):
                                                card.do_upgrade()
                                                upgraded_count += 1

                                        g.add_log(
                                            f"Forbidden Knowledge: "
                                            f"Max HP halved. "
                                            f"Upgraded {upgraded_count} cards.")
                                    # Relic за Gold

                                    elif action == "gain_relic_pay_gold":

                                        cost = opt.get("cost", 50)

                                        if g.pgold >= cost:

                                            r_name = opt[
                                                "relic"
                                            ]

                                            if (
                                                r_name
                                                not in g.relics):

                                                g.pgold -= cost

                                                g.add_relic(
                                                    r_name)

                                                g.add_log(
                                                    f"Event: bought "
                                                    f"'{r_name}' "
                                                    f"for {cost} Gold.")

                                    # Relic - HP
                                    elif action == "gain_relic_lose_hp":
                                        g.php -= opt.get("hp_loss", 15)
                                        if g.php < 1: g.php = 1
                                        r_name = opt["relic"]
                                        if r_name not in g.relics: g.add_relic(r_name)
                                        g.add_log(f"Евент: Взе '{r_name}'.")

                                    # Steal Merchant
                                    elif action == "steal_merchant":
                                        g.pgold += opt.get("gold", 40)
                                        g.php -= opt.get("hp_loss", 15)
                                        if g.php < 1: g.php = 1
                                        rares = [cn for cn, cd in CARDS.items() if cd.get("rarity","").lower() == "rare"]
                                        if rares: g.deck.append(Card(random.choice(rares)))
                                        g.add_log("Евент: Ограби търговеца!")

                                    # Gamble 
                                    elif action == "gamble_gold_or_damage":
                                        if random.random() < 0.5:
                                            g.pgold += opt.get("gold", 120)
                                            g.add_log("Евент: Спечели залога!")
                                        else:
                                            g.php -= opt.get("damage", 15)
                                            if g.php < 1: g.php = 1
                                            g.add_log("Евент: Загуби залога!")

                                    # Duplicate best card 
                                    elif (
                                        action
                                        == "upgrade_random_card_lose_hp"):

                                        upgradable = [
                                            card
                                            for card in g.deck
                                            if (
                                                hasattr(card, "upgraded"
)
                                                and not card.upgraded
                                                and card.name
                                                in CARD_UPGRADES)
                                        ]

                                        if upgradable:

                                            chosen_card = random.choice(
                                                upgradable)

                                            chosen_card.do_upgrade()

                                            g.php = max(
                                                1,
                                                g.php
                                                - opt.get("hp_loss", 10
)
                                            )

                                            g.add_log(
                                                f"Cursed Mirror: "
                                                f"upgraded "
                                                f"'{chosen_card.name}', "
                                                f"lost 10 HP.")

                                        else:

                                            g.add_log(
                                                "Cursed Mirror: "
                                                "no cards can be upgraded.")



                                    elif action == "gain_max_hp_and_heal":

                                        cost = opt.get("cost", 0
)

                                        if g.pgold >= cost:

                                            g.pgold -= cost

                                            max_hp_gain = opt.get("max_hp_gain",12)

                                            hp_gain = opt.get("hp_gain", 12)

                                            g.pmx += max_hp_gain

                                            g.php = min(g.pmx, g.php + hp_gain)

                                            g.add_log(
                                                f"Mutagen Lab: "
                                                f"+{max_hp_gain} Max HP, "
                                                f"healed {hp_gain} HP.")

                                    # Gold & Damage
                                    elif action == "gold_and_damage":
                                        g.pgold += opt.get("gold", 80)
                                        g.php -= opt.get("hp_loss", 10)
                                        if g.php < 1: g.php = 1
                                        g.add_log("Евент: Взе злато, но понесе щети.")

                                        # Забавяне на враговете
                                    elif action == "pay_gold_leave":

                                        cost = opt.get("cost",30)

                                        if g.pgold >= cost:
                                            g.pgold -= cost
                                            g.add_log(f"Event: paid " f"{cost} Gold.")

                                    elif action == "gain_random_relic":

                                       give_random_event_relic(g)

                                g.state = "map"
                                break
                    

                    elif g.state == "combat":
                        if g.btn_view_draw.hit(pos):
                            g.open_card_view(g.draw_p, "DRAW PILE")
                        elif g.btn_view_disc.hit(pos):
                            g.open_card_view(g.disc, "DISCARD PILE")
                        elif (g.end_btn.hit(pos) and not g.drag_card):
                           
                            if (
                                getattr(g, "tutorial_active", False)
                                and getattr(g, "tutorial_room", "") == "first_enemy"
                                and getattr(g, "tutorial_step", 0) not in (9, 14)):
                                pass

                            else:
                                g.end_turn()
                        else:
                            positions = g.hand_positions()
                            for i in range(len(g.hand) - 1,-1,-1):
                                card = g.hand[i]
                                cx, cy = positions[i]
                                if card.collides(pos, cx, cy):
                                    g.play_sfx("universfield-computer-mouse-click-352734", 0.40)

                                    g.drag_card = card

                                    g.drag_ox = (pos[0] - cx)

                                    g.drag_oy = (pos[1] - cy)

                                    g.drag_x = pos[0]
                                    g.drag_y = pos[1]

                                   
                                    g.drag_home_x = cx
                                    g.drag_home_y = cy

                                    break
                    
                    elif g.state == "shop":

                        if tutorial.handle_shop_click(g,event.pos):
                            continue
                        if (hasattr(g, "btn_leave_shop") and g.btn_leave_shop.hit(event.pos)):
                            g.state = "map"

                        else:
                            # CARD PURCHASES
                            card_clicked = False

                            for item, rect in getattr(g,"shop_card_rects",[]):
                                if (rect.collidepoint(event.pos) and not item.get("bought", False)):
                                    card_clicked = True

                                    if g.pgold >= item["price"]:
                                        g.pgold -= item["price"]
                                        item["bought"] = True

                                        g.deck.append(Card(item["name"]))

                                        g.add_log(
                                            f"Bought {item['name']} "
                                            f"for {item['price']} Gold")

                                    break
                            # RELIC PURCHASES
                            if not card_clicked:

                                for item, rect in getattr(g,"shop_relic_rects",[]):
                                    if (rect.collidepoint(event.pos) and not item.get("bought", False)):
                                        if g.pgold >= item["price"]:
                                            g.pgold -= item["price"]
                                            item["bought"] = True

                                            g.add_relic(item["name"])

                                            g.add_log(
                                                f"Bought relic "
                                                f"{item['name']} "
                                                f"for {item['price']} Gold")

                                        break

                    elif g.state == "chest":
                        if tutorial.handle_chest_click(g, pos):
                            continue

                        if not getattr(g, 'chest_opened', False):
                             if hasattr(g, 'btn_open_chest') and g.btn_open_chest.hit(event.pos):
                                 if hasattr(g, 'open_chest'):
                                     g.open_chest()
                        else:
                            if hasattr(g, 'btn_leave_chest') and g.btn_leave_chest.hit(event.pos):
                                 g.state = "map"

                    elif g.state == "pre_minigame":
                        if g.btn_mg_confirm.hit(pos):
                            g.state = "play_minigame"
                            
                            
                        elif g.btn_mg_skip.hit(pos):
                            g.state = "map" 

                # КРАЙ НА ИГРАТА
                elif g.state in ("game_over", "win"):
                    if g.restart.hit(pos): g.reset()

            elif event.type == pygame.MOUSEMOTION:
                if g.drag_card:
                        d = get_card_data(g.drag_card.name, g.drag_card.upgraded)

                        enough_mana = (g.get_effective_card_cost(g.drag_card)<= g.mana)

                        home_x = getattr(g,"drag_home_x",g.drag_card.x)

                        home_y = getattr(g,"drag_home_y",g.drag_card.y)

  
                        wanted_x = (event.pos[0]- g.drag_ox)

                        wanted_y = (event.pos[1]- g.drag_oy)
                        # НЯМА ДОСТАТЪЧНО MANA
                        if not enough_mana:


                            magnet_x = max(home_x - 35,min(home_x + 35,wanted_x))

                            magnet_y = max(home_y - 40,min(home_y + 15, wanted_y))

                            g.drag_x = ( magnet_x + g.drag_ox)

                            g.drag_y = ( magnet_y + g.drag_oy)
                        # ИМА MANA 
                        else:

                            g.drag_x = event.pos[0]
                            g.drag_y = event.pos[1]

            elif (event.type == pygame.MOUSEBUTTONUP and event.button == 1):

                if (g.drag_card and g.state == "combat"):

                    card = g.drag_card

                    d = get_card_data(card.name,card.upgraded)

                    enough_mana = (g.get_effective_card_cost(card)<= g.mana)

                    needs_target = (
                        d["type"] == "attack"
                        or "weak" in d
                        or "vuln" in d
                        or "blitz" in d
                        or d.get("trigger_blitz")
                        or d.get("double_blitz")
                        or "wounds" in d
                        or d.get("trigger_wounds")
                        or d.get("double_wounds")
                        or d.get("draw_per_wound")) and not d.get("target_all", False)

                    current_y = ( g.drag_y - g.drag_oy)
                    home_y = getattr(g, "drag_home_y",card.y)
                    lift_distance = (home_y - current_y)
                    drag_activated = (enough_mana and lift_distance >= 45)

                    if drag_activated:

                        if needs_target:

                            for rect, en in getattr(g,"enemy_rects",[]):

                                if rect.collidepoint(event.pos):

                                    g.play_card(card,target_enemy=en)

                                    break

                        else:

                            if (event.pos[1]< H // 2 - 10):
                                g.play_card(card)

                    g.drag_card = None

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()