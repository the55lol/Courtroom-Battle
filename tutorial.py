import pygame
import os

from asset_utils import asset_path
from entities import Card, rrect, txc
from config import (
    W, H,
    PANEL, BORDER,
    GOLD, WHITE, GRAY_L,
    GREEN, GREEN_D,
    RED, RED_D,
    BLUE, BLUE_D,
    F_BIG, F_MED, F_MED, F_MED,
     ORANGE)


GUIDE_NAME = "von Karma"
TUTORIAL_TEXT_FONT = pygame.font.SysFont("Georgia", 21)
# PROFILE TUTORIAL PROMPT
def load_tutorial_portrait(
    game_folder,
    relative_path,
    size=(120, 120),
    flip_x=False):

    try:

        path = asset_path(game_folder, relative_path)

        img = pygame.image.load(
            path)

        visible_bounds = img.get_bounding_rect(
            min_alpha=1)

        if (
            visible_bounds.width > 0
            and visible_bounds.height > 0):
            img = img.subsurface(
                visible_bounds).copy()

        img = pygame.transform.smoothscale(img, size)

        if flip_x:
            img = pygame.transform.flip(
                img,
                True,
                False)

        return img

    except Exception as exc:

        print(
            "Tutorial portrait load failed:",
            game_folder,
            relative_path,
            exc)

        return None

GUIDE_PORTRAIT = load_tutorial_portrait(
    "enemies",
    os.path.join("Manfred von Karma", "manfred_default.png"),
    (70, 70),
    flip_x=False)


def draw_guide_identity(surf, box):

    portrait_center_x = (
        box.x + 55)

    portrait_center_y = (
        box.centery + 10)

    if GUIDE_PORTRAIT is not None:

        portrait_rect = (
            GUIDE_PORTRAIT.get_rect(
                center=(
                    portrait_center_x,
                    portrait_center_y)
            ))

        surf.blit(GUIDE_PORTRAIT, portrait_rect)

    
    txc(
        surf,
        GUIDE_NAME,
        F_MED,
        GOLD,
        portrait_center_x,
        box.y + 10)


def draw_tutorial_prompt(surf, g, mouse):
    surf.fill((18, 15, 28))

    txc(
        surf,
        "PLAY THE TUTORIAL?",
        F_BIG,
        GOLD,
        W // 2,
        130)

    txc(
        surf,
        "Would you like to learn the basics before your first run?",
        F_MED,
        WHITE,
        W // 2,
        200)

    txc(
        surf,
        "You can skip it if you already know how the game works.",
        F_MED,
        GRAY_L,
        W // 2,
        235)

    yes_rect = pygame.Rect(W // 2 - 220, 310, 200, 55)

    no_rect = pygame.Rect(W // 2 + 20, 310, 200, 55)

    rrect(
        surf,
        GREEN_D if yes_rect.collidepoint(mouse) else PANEL,
        yes_rect,
        8,
        2,
        GREEN)

    rrect(
        surf,
        RED_D if no_rect.collidepoint(mouse) else PANEL,
        no_rect,
        8,
        2,
        RED)

    txc(
        surf,
        "PLAY TUTORIAL",
        F_MED,
        WHITE,
        yes_rect.centerx,
        yes_rect.centery)

    txc(
        surf,
        "SKIP",
        F_MED,
        WHITE,
        no_rect.centerx,
        no_rect.centery)

    g.tutorial_yes_rect = yes_rect
    g.tutorial_no_rect = no_rect


def handle_tutorial_prompt(g, pos):

    if getattr(g, "tutorial_yes_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):

        mark_tutorial_choice(g)
        start_tutorial(g)

        return True

    if getattr(g, "tutorial_no_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):

        mark_tutorial_choice(g)

        g.tutorial_active = False
        g.state = "start_menu"

        return True

    return False


def mark_tutorial_choice(g):

    if (
        hasattr(g, "profiles")
        and 0 <= g.current_slot < len(g.profiles)):
        g.profiles[g.current_slot][
            "tutorial_choice_made"
        ] = True

        g.save_profiles()
# START TUTORIAL
def start_tutorial(g):

    g.tutorial_active = True
    g.card_anim_queue = []
    g.card_anim = None

    g.combat_anim_queue = []
    g.combat_anim = None

    g.pending_end_turn_after_discard = False
    g.pending_enemy_turn_finish = False

    g.end_turn_discard_positions = {}

    g.reshuffle_active = False
    g.pending_draw_after_reshuffle = 0
    g.tutorial_room = "map_intro"
    g.tutorial_map_step = 0
    g.tutorial_step = 0
    g.tutorial_defends_played = 0
    g.char_class = "BRUISER"
    g.php = 70
    g.pmx = 70
    g.pgold = 0
    g.pblock = 0
    g.pstr = 0
    g.pvuln = 0
    g.ptmp_str = 0
    g.mana = 3
    g.max_mana = 3
    g.relics = []
    g.deck = (
        [Card("Strike") for _ in range(5)]
        + [Card("Defend") for _ in range(4)]
        + [Card("Bash")])

    generate_first_tutorial_map(g)
# FIRST TUTORIAL MAP
def generate_first_tutorial_map(g):

    enemy = {
        "name": "Marvin Grossberg",

        "hp": 23,
        "max_hp": 23,

        "mg": "HaremRunner",
        "rarity": "common",
        "pattern": [
            "Attack 10",
            "Block 5",
            "Attack 5",
            "Block 5"
        ],

        "moves": {
            "Attack 10": (
                "atk",
                10,
                0),

            "Block 5": (
                "blk",
                0,
                5),

            "Attack 5": (
                "atk",
                5,
                0)
        }
    }

    enemy_node = {
        "floor": 0,
        "idx": 0,
        "col": 3,

        "type": "enemy",
        "minigame": "HaremRunner",

        "enemy": enemy,

        "x": W // 2,
        "y": H // 2,

        "next_nodes": [0]
    }
    shop_node = {
    "floor": 1,
    "idx": 0,
    "col": 3,

    "type": "shop",
    "minigame": None,

    "x": W // 2,
    "y": H // 2 - 150,

    "next_nodes": [0]
    }
    campfire_node = {
        "floor": 2,
        "idx": 0,
        "col": 3,

        "type": "campfire",
        "minigame": None,

        "x": W // 2,
        "y": H // 2 - 300,

        "next_nodes": [0]
    }
    chest_node = {
    "floor": 3,
    "idx": 0,
    "col": 3,

    "type": "chest",
    "minigame": None,

    "x": W // 2,
    "y": H // 2 - 450,

    "next_nodes": [0]
    }

    elite_enemy = {
        "name": "Winston Payne",

        "hp": 58,
        "max_hp": 58,

        "mg": "HaremRunner",
        "rarity": "epic",

        "pattern": [
            "Double Objection",
            "Prosecutor's Confidence",
            "Double Objection",
             "Prosecutor's Confidence",

        ],

        "moves": {
            "Prosecutor's Confidence": (
                "buff",
                0,
                3),

            "Double Objection": (
                "atk_multi",
                8,
                2),

            "Case Preparation": (
                "blk",
                0,
                10),

            "Desperate Argument": (
                "atk",
                11,
                0)
        }
    }


    elite_node = {
        "floor": 4,
        "idx": 0,
        "col": 3,

        "type": "elite",
        "minigame": "HaremRunner",
        "reward_rarity": "Epic",

        "enemy": elite_enemy,

        "x": W // 2,
        "y": H // 2 - 600,

        "next_nodes": [0]
    }
    rest_campfire_node = {
        "floor": 5,
        "idx": 0,
        "col": 3,

        "type": "campfire",
        "minigame": None,

        "x": W // 2,
        "y": H // 2 - 750,

        "next_nodes": [0]
    }

    boss_enemy = {
        "name": "Manfred von Karma",

        "hp": 170,
        "max_hp": 170,

        "mg": "HaremRunner",
        "rarity": "legendary",

        "pattern": [
            "Perfect Opening",
            "Relentless Objection",
            "Absolute Defense",
            "Final Argument"
        ],

        "moves": {
            "Perfect Opening": (
                "buff",
                0,
                2),

            "Relentless Objection": (
                "atk_multi",
                8,
                2),

            "Absolute Defense": (
                "blk",
                0,
                14),

            "Final Argument": (
                "atk",
                16,
                0)
        }
    }


    boss_node = {
        "floor": 6,
        "idx": 0,
        "col": 3,

        "type": "boss",
        "minigame": "HaremRunner",
        "reward_rarity": "legendary",

        "enemy": boss_enemy,

        "x": W // 2,
        "y": H // 2 - 900,

        "next_nodes": []
    }
    g.map_data = [
        [enemy_node],
        [shop_node],
        [campfire_node],
        [chest_node],
        [elite_node],
        [rest_campfire_node],
        [boss_node]
    ]

    g.floor = 0

    g.current_node = None
    g.current_node_idx = None

    g.path_history = []

    g.map_scroll_y = 0

    g.state = "map"
# TUTORIAL MAP INTRO
def get_map_dialogue(g):

    step = getattr(g, "tutorial_map_step", 0)

    dialogues = {

        0: (
            "Welcome to the game. "
            "This is your Tutorial Map."),

        1: (
            "In an actual run, the map will be much larger. "
            "You'll travel upward and choose between different paths, "
            "enemies and rooms."),

        2: (
            "Every journey starts somewhere. "
            "Yours starts here. "
            "Click the highlighted node to begin.")
    }

    return dialogues.get(step, "")


def continue_map_dialogue(g):

    step = getattr(g, "tutorial_map_step", 0)

    if step == 0:
        g.tutorial_map_step = 1

    elif step == 1:
        g.tutorial_map_step = 2

def draw_map_overlay(surf, g, mouse):

    if not getattr(g, "tutorial_active", False):
        return

    room = getattr(g, "tutorial_room", "")

    if room not in (
        "map_intro",
        "shop_map_intro",
        "campfire_map_intro",
        "chest_map_intro",
        "elite_map_intro",
        "rest_campfire_map_intro",
        "boss_map_intro"):
        return
    # SHOP MAP INTRO
    if room == "shop_map_intro":

        step = getattr(g, "tutorial_shop_map_step", 0)
        if (
            step == 2
            and len(getattr(g, "map_data", [])) > 1
            and g.map_data[1]):
            node = g.map_data[1][0]

            scroll_y = getattr(g, "map_scroll_y", 0)

            node_x = node["x"]
            node_y = node["y"] + scroll_y

            pygame.draw.circle(
                surf,
                BLUE,
                (
                    int(node_x),
                    int(node_y)),
                34,
                4)

            pygame.draw.polygon(
                surf,
                GOLD,
                [
                    (
                        node_x,
                        node_y - 38),
                    (
                        node_x - 12,
                        node_y - 56),
                    (
                        node_x + 12,
                        node_y - 56)
                ])

            txc(
                surf,
                "SHOP",
                F_MED,
                GOLD,
                node_x,
                node_y - 75)

        dialogue = get_shop_map_dialogue(g)

        box = pygame.Rect(W // 2 - 330, H - 210, 660, 95)

        rrect(
            surf,
            (25, 22, 38),
            box,
            10,
            2,
            GOLD)

        draw_guide_identity(surf, box)

        words = dialogue.split()

        lines = []
        line = ""

        for word in words:

            test = (
                line + " " + word).strip()

            if TUTORIAL_TEXT_FONT.size(test)[0] > 500:

                if line:
                    lines.append(line)

                line = word

            else:
                line = test

        if line:
            lines.append(line)

        for i, text in enumerate(
            lines[:3]):
            surf.blit(
                F_MED.render(
                    text,
                    True,
                    WHITE),
                (
                    box.x + 110,
                    box.y + 15 + i * 18)
            )

        if step in (0, 1):

            cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

            rrect(
                surf,
                BLUE_D
                if cont_rect.collidepoint(mouse)
                else PANEL,
                cont_rect,
                5,
                1,
                BLUE)

            txc(
                surf,
                "CONTINUE",
                F_MED,
                WHITE,
                cont_rect.centerx,
                cont_rect.centery)

            g.tutorial_shop_map_continue_rect = (
                cont_rect)

        else:
            g.tutorial_shop_map_continue_rect = None

        return
    step = getattr(g, "tutorial_map_step", 0)
    # CAMPFIRE MAP INTRO
    if room == "campfire_map_intro":

        step = getattr(g, "tutorial_campfire_map_step", 0)

        if (
            step == 2
            and len(getattr(g, "map_data", [])) > 2
            and g.map_data[2]):

            node = g.map_data[2][0]

            scroll_y = getattr(g, "map_scroll_y", 0)

            node_x = node["x"]
            node_y = node["y"] + scroll_y

            pygame.draw.circle(
                surf,
                GOLD,
                (
                    int(node_x),
                    int(node_y)),
                34,
                4)

            pygame.draw.polygon(
                surf,
                GOLD,
                [
                    (
                        node_x,
                        node_y - 38),
                    (
                        node_x - 12,
                        node_y - 56),
                    (
                        node_x + 12,
                        node_y - 56)
                ])

            txc(
                surf,
                "CAMPFIRE",
                F_MED,
                GOLD,
                node_x,
                node_y - 75)

        dialogue = get_campfire_map_dialogue(g)

        box = pygame.Rect(W // 2 - 330, H - 210, 660, 95)

        rrect(
            surf,
            (25, 22, 38),
            box,
            10,
            2,
            GOLD)

        draw_guide_identity(surf, box)

        words = dialogue.split()

        lines = []
        line = ""

        for word in words:

            test = (
                line + " " + word).strip()

            if TUTORIAL_TEXT_FONT.size(test)[0] > 500:

                if line:
                    lines.append(line)

                line = word

            else:
                line = test

        if line:
            lines.append(line)

        for i, text in enumerate(
            lines[:3]):
            surf.blit(
                F_MED.render(
                    text,
                    True,
                    WHITE),
                (
                    box.x + 110,
                    box.y + 15 + i * 18)
            )

        if step in (0, 1):

            cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

            rrect(
                surf,
                BLUE_D
                if cont_rect.collidepoint(mouse)
                else PANEL,
                cont_rect,
                5,
                1,
                BLUE)

            txc(
                surf,
                "CONTINUE",
                F_MED,
                WHITE,
                cont_rect.centerx,
                cont_rect.centery)

            g.tutorial_campfire_map_continue_rect = (
                cont_rect)

        else:
            g.tutorial_campfire_map_continue_rect = None

        return
    # CHEST MAP INTRO
    if room == "chest_map_intro":

        step = getattr(g, "tutorial_chest_map_step", 0)

        if (
            step == 2
            and len(getattr(g, "map_data", [])) > 3
            and g.map_data[3]):

            node = g.map_data[3][0]

            scroll_y = getattr(g, "map_scroll_y", 0 )

            node_x = node["x"]
            node_y = node["y"] + scroll_y

            pygame.draw.circle(
                surf,
                GOLD,
                (
                    int(node_x),
                    int(node_y)),
                34,
                4)

            pygame.draw.polygon(
                surf,
                GOLD,
                [
                    (
                        node_x,
                        node_y - 38),
                    (
                        node_x - 12,
                        node_y - 56),
                    (
                        node_x + 12,
                        node_y - 56)
                ])

            txc(
                surf,
                "TREASURE",
                F_MED,
                GOLD,
                node_x,
                node_y - 75)

        dialogue = get_chest_map_dialogue(g)

        box = pygame.Rect(W // 2 - 330, H - 210, 660, 95)

        rrect(
            surf,
            (25, 22, 38),
            box,
            10,
            2,
            GOLD)

        draw_guide_identity(surf, box)

        words = dialogue.split()

        lines = []
        line = ""

        for word in words:

            test = (
                line + " " + word).strip()

            if TUTORIAL_TEXT_FONT.size(test)[0] > 500:

                if line:
                    lines.append(line)

                line = word

            else:
                line = test

        if line:
            lines.append(line)

        for i, text in enumerate(lines[:3]):

            surf.blit(
                F_MED.render(
                    text,
                    True,
                    WHITE),
                (
                    box.x + 110,
                    box.y + 15 + i * 18)
            )

        if step in (0, 1):

            cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

            rrect(
                surf,
                BLUE_D
                if cont_rect.collidepoint(mouse)
                else PANEL,
                cont_rect,
                5,
                1,
                BLUE)

            txc(
                surf,
                "CONTINUE",
                F_MED,
                WHITE,
                cont_rect.centerx,
                cont_rect.centery)

            g.tutorial_chest_map_continue_rect = (
                cont_rect)

        else:
            g.tutorial_chest_map_continue_rect = None

        return
    # ELITE MAP INTRO
    if room == "elite_map_intro":

        step = getattr(g, "tutorial_elite_map_step", 0)

        if (
            step == 3
            and len(getattr(g, "map_data", [])) > 4
            and g.map_data[4]):

            node = g.map_data[4][0]

            scroll_y = getattr(g, "map_scroll_y", 0)

            node_x = node["x"]
            node_y = node["y"] + scroll_y

            pygame.draw.circle(
                surf,
                GOLD,
                (
                    int(node_x),
                    int(node_y)),
                36,
                4)

            pygame.draw.polygon(
                surf,
                GOLD,
                [
                    (
                        node_x,
                        node_y - 40),
                    (
                        node_x - 12,
                        node_y - 58),
                    (
                        node_x + 12,
                        node_y - 58)
                ])

            txc(
                surf,
                "ELITE",
                F_MED,
                GOLD,
                node_x,
                node_y - 78)

        dialogue = get_elite_map_dialogue(g)

        box = pygame.Rect(W // 2 - 330, H - 210, 660, 95)

        rrect(
            surf,
            (25, 22, 38),
            box,
            10,
            2,
            GOLD)

        draw_guide_identity(surf, box)

        words = dialogue.split()
        lines = []
        line = ""

        for word in words:

            test = (
                line + " " + word).strip()

            if TUTORIAL_TEXT_FONT.size(test)[0] > 500:

                if line:
                    lines.append(line)

                line = word

            else:
                line = test

        if line:
            lines.append(line)

        for i, text in enumerate(
            lines[:3]):
            surf.blit(
                F_MED.render(
                    text,
                    True,
                    WHITE),
                (
                    box.x + 110,
                    box.y + 15 + i * 18)
            )

        if step < 3:

            cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

            rrect(
                surf,
                BLUE_D
                if cont_rect.collidepoint(mouse)
                else PANEL,
                cont_rect,
                5,
                1,
                BLUE)

            txc(
                surf,
                "CONTINUE",
                F_MED,
                WHITE,
                cont_rect.centerx,
                cont_rect.centery)

            g.tutorial_elite_map_continue_rect = (
                cont_rect)

        else:
            g.tutorial_elite_map_continue_rect = None

        return
    # SECOND CAMPFIRE MAP INTRO
    if room == "rest_campfire_map_intro":

        step = getattr(g, "tutorial_rest_campfire_map_step", 0)

        if (
            step == 3
            and len(getattr(g, "map_data", [])) > 5
            and g.map_data[5]):

            node = g.map_data[5][0]

            scroll_y = getattr(g, "map_scroll_y", 0)

            node_x = node["x"]
            node_y = node["y"] + scroll_y

            pygame.draw.circle(
                surf,
                GOLD,
                (
                    int(node_x),
                    int(node_y)),
                34,
                4)

            pygame.draw.polygon(
                surf,
                GOLD,
                [
                    (
                        node_x,
                        node_y - 38),
                    (
                        node_x - 12,
                        node_y - 56),
                    (
                        node_x + 12,
                        node_y - 56)
                ])

            txc(
                surf,
                "CAMPFIRE",
                F_MED,
                GOLD,
                node_x,
                node_y - 75)

        dialogue = get_rest_campfire_map_dialogue(g)

        box = pygame.Rect(W // 2 - 330, H - 210, 660, 95)

        rrect(
            surf,
            (25, 22, 38),
            box,
            10,
            2,
            GOLD)

        draw_guide_identity(surf, box)

        words = dialogue.split()

        lines = []
        line = ""

        for word in words:

            test = (
                line + " " + word).strip()

            if TUTORIAL_TEXT_FONT.size(test)[0] > 500:

                if line:
                    lines.append(line)

                line = word

            else:
                line = test

        if line:
            lines.append(line)

        for i, text in enumerate(
            lines[:3]):

            surf.blit(
                F_MED.render(
                    text,
                    True,
                    WHITE),
                (
                    box.x + 110,
                    box.y + 15 + i * 18)
            )

        if step < 3:

            cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

            rrect(
                surf,
                BLUE_D
                if cont_rect.collidepoint(mouse)
                else PANEL,
                cont_rect,
                5,
                1,
                BLUE)

            txc(
                surf,
                "CONTINUE",
                F_MED,
                WHITE,
                cont_rect.centerx,
                cont_rect.centery)

            g.tutorial_rest_campfire_map_continue_rect = (
                cont_rect)

        else:
            g.tutorial_rest_campfire_map_continue_rect = None

        return
    # BOSS MAP INTRO
    if room == "boss_map_intro":

        step = getattr(g, "tutorial_boss_map_step", 0)

        if (
            step == 5
            and len(getattr(g, "map_data", [])) > 6
            and g.map_data[6]):

            node = g.map_data[6][0]

            scroll_y = getattr(g, "map_scroll_y", 0)

            node_x = node["x"]
            node_y = node["y"] + scroll_y

            pygame.draw.circle(
                surf,
                GOLD,
                (
                    int(node_x),
                    int(node_y)),
                40,
                4)

            pygame.draw.polygon(
                surf,
                GOLD,
                [
                    (
                        node_x,
                        node_y - 44),
                    (
                        node_x - 13,
                        node_y - 64),
                    (
                        node_x + 13,
                        node_y - 64)
                ])

            txc(
                surf,
                "FINAL BOSS",
                F_MED,
                GOLD,
                node_x,
                node_y - 85)

        dialogue = get_boss_map_dialogue(g)

        box = pygame.Rect(W // 2 - 330, H - 210, 660, 95)

        rrect(
            surf,
            (25, 22, 38),
            box,
            10,
            2,
            GOLD)

        draw_guide_identity(surf, box)

        words = dialogue.split()

        lines = []
        line = ""

        for word in words:

            test = (
                line + " " + word).strip()

            if TUTORIAL_TEXT_FONT.size(test)[0] > 500:

                if line:
                    lines.append(line)

                line = word

            else:
                line = test

        if line:
            lines.append(line)

        for i, text in enumerate(
            lines[:3]):

            surf.blit(
                F_MED.render(
                    text,
                    True,
                    WHITE),
                (
                    box.x + 110,
                    box.y + 15 + i * 18)
            )

        if step < 5:

            cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

            rrect(
                surf,
                BLUE_D
                if cont_rect.collidepoint(mouse)
                else PANEL,
                cont_rect,
                5,
                1,
                BLUE)

            txc(
                surf,
                "CONTINUE",
                F_MED,
                WHITE,
                cont_rect.centerx,
                cont_rect.centery)

            g.tutorial_boss_map_continue_rect = cont_rect

        else:
            g.tutorial_boss_map_continue_rect = None

        return
    # HIGHLIGHT FIRST NODE
    if (
        step == 2
        and getattr(g, "map_data", None)
        and g.map_data[0]):

        node = g.map_data[0][0]

        scroll_y = getattr(g, "map_scroll_y", 0)

        node_x = node["x"]
        node_y = (
            node["y"]
            + scroll_y)
        pygame.draw.circle(
            surf,
            GOLD,
            (
                int(node_x),
                int(node_y)),
            34,
            4)
        pygame.draw.polygon(
            surf,
            GOLD,
            [
                (
                    node_x,
                    node_y - 38),
                (
                    node_x - 12,
                    node_y - 56),
                (
                    node_x + 12,
                    node_y - 56)
            ])

        txc(
            surf,
            "START HERE",
            F_MED,
            GOLD,
            node_x,
            node_y - 75)
    # GUIDE DIALOGUE
    dialogue = get_map_dialogue(g)

    if not dialogue:
        return

    box = pygame.Rect(W // 2 - 330, H - 210, 660, 95)

    rrect(
        surf,
        (25, 22, 38),
        box,
        10,
        2,
        GOLD)

    draw_guide_identity(surf, box)

    words = dialogue.split()

    lines = []
    line = ""

    for word in words:

        test = (
            line + " " + word).strip()

        if TUTORIAL_TEXT_FONT.size(test)[0] > 500:

            if line:
                lines.append(line)

            line = word

        else:
            line = test

    if line:
        lines.append(line)

    for i, text in enumerate(
        lines[:3]):

        surf.blit(
            F_MED.render(
                text,
                True,
                WHITE),
            (
                box.x + 110,
                box.y + 15 + i * 18)
        )
    if step in (0, 1):

        cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

        rrect(
            surf,
            BLUE_D
            if cont_rect.collidepoint(mouse)
            else PANEL,
            cont_rect,
            5,
            1,
            BLUE)

        txc(
            surf,
            "CONTINUE",
            F_MED,
            WHITE,
            cont_rect.centerx,
            cont_rect.centery)

        g.tutorial_map_continue_rect = (
            cont_rect)

    else:

        g.tutorial_map_continue_rect = None

def handle_map_click(g, pos):
    room = getattr(g, "tutorial_room", "")


    if room == "boss_map_intro":

        step = getattr(g, "tutorial_boss_map_step", 0)

        cont_rect = getattr(g, "tutorial_boss_map_continue_rect", None)

        if (
            cont_rect
            and cont_rect.collidepoint(pos)):
            continue_boss_map_dialogue(g)
            return True

        if (
            step == 5
            and len(getattr(g, "map_data", [])) > 6
            and g.map_data[6]):

            node = g.map_data[6][0]

            scroll_y = getattr(g, "map_scroll_y", 0)

            node_x = node["x"]
            node_y = node["y"] + scroll_y

            distance = (
                (
                    pos[0] - node_x) ** 2
                +
                (
                    pos[1] - node_y) ** 2
            ) ** 0.5

            if distance <= 35:

                g.tutorial_room = "boss"
                g.tutorial_boss_step = 0

                g.enter_node(node["floor"], node["idx"])

                return True

        return True
    if room == "rest_campfire_map_intro":

        step = getattr(g, "tutorial_rest_campfire_map_step", 0)

        cont_rect = getattr(g, "tutorial_rest_campfire_map_continue_rect", None)

        if (
            cont_rect
            and cont_rect.collidepoint(pos)):
            continue_rest_campfire_map_dialogue(g)
            return True

        if (
            step == 3
            and len(getattr(g, "map_data", [])) > 5
            and g.map_data[5]):

            node = g.map_data[5][0]

            scroll_y = getattr(g, "map_scroll_y", 0)

            node_x = node["x"]
            node_y = node["y"] + scroll_y

            distance = (
                (
                    pos[0] - node_x) ** 2
                +
                (
                    pos[1] - node_y) ** 2
            ) ** 0.5

            if distance <= 30:

                g.tutorial_room = "rest_campfire"
                g.tutorial_rest_campfire_step = 0

                g.enter_node(node["floor"], node["idx"])

                return True

        return True
    if room == "elite_map_intro":

        step = getattr(g, "tutorial_elite_map_step", 0)

        cont_rect = getattr(g, "tutorial_elite_map_continue_rect", None)

        if (
            cont_rect
            and cont_rect.collidepoint(pos)):
            continue_elite_map_dialogue(g)
            return True

        if (
            step == 3
            and len(getattr(g, "map_data", [])) > 4
            and g.map_data[4]):

            node = g.map_data[4][0]

            scroll_y = getattr(g, "map_scroll_y", 0)

            node_x = node["x"]
            node_y = node["y"] + scroll_y

            distance = (
                (
                    pos[0] - node_x) ** 2
                +
                (
                    pos[1] - node_y) ** 2
            ) ** 0.5

            if distance <= 32:

                g.tutorial_room = "elite"
                g.tutorial_elite_step = 0

                g.enter_node(node["floor"], node["idx"])

                return True

        return True
    if room == "chest_map_intro":

        step = getattr(g, "tutorial_chest_map_step", 0)

        cont_rect = getattr(g, "tutorial_chest_map_continue_rect", None)

        if (
            cont_rect
            and cont_rect.collidepoint(pos)):
            continue_chest_map_dialogue(g)
            return True

        if (
            step == 2
            and len(getattr(g, "map_data", [])) > 3
            and g.map_data[3]):

            node = g.map_data[3][0]

            scroll_y = getattr(g, "map_scroll_y", 0)

            node_x = node["x"]
            node_y = node["y"] + scroll_y

            distance = (
                (
                    pos[0] - node_x) ** 2
                +
                (
                    pos[1] - node_y) ** 2
            ) ** 0.5

            if distance <= 30:

                g.tutorial_room = "chest"
                g.tutorial_chest_step = 0

                g.enter_node(node["floor"], node["idx"])
                g.chest_gold = 0
                g.chest_relic = "Prophet's Eye"
                g.chest_opened = False

                return True

        return True
    if room == "campfire_map_intro":

        step = getattr(g, "tutorial_campfire_map_step", 0)

        cont_rect = getattr(g, "tutorial_campfire_map_continue_rect", None)

        if (
            cont_rect
            and cont_rect.collidepoint(pos)):
            continue_campfire_map_dialogue(g)
            return True

        if (
            step == 2
            and len(getattr(g, "map_data", [])) > 2
            and g.map_data[2]):

            node = g.map_data[2][0]

            scroll_y = getattr(g, "map_scroll_y", 0)

            node_x = node["x"]
            node_y = node["y"] + scroll_y

            distance = (
                (
                    pos[0] - node_x) ** 2
                +
                (
                    pos[1] - node_y) ** 2
            ) ** 0.5

            if distance <= 30:

                g.tutorial_room = "campfire"
                g.tutorial_campfire_step = 0

                g.enter_node(node["floor"], node["idx"])

                return True

        return True
    if room == "shop_map_intro":

        step = getattr(g, "tutorial_shop_map_step", 0)

        cont_rect = getattr(g, "tutorial_shop_map_continue_rect", None)

        if (
            cont_rect
            and cont_rect.collidepoint(pos)):
            continue_shop_map_dialogue(g)
            return True

        if (
            step == 2
            and len(getattr(g, "map_data", [])) > 1
            and g.map_data[1]):
            node = g.map_data[1][0]

            scroll_y = getattr(g, "map_scroll_y", 0)

            node_x = node["x"]
            node_y = node["y"] + scroll_y

            distance = (
                (
                    pos[0] - node_x) ** 2
                +
                (
                    pos[1] - node_y) ** 2
            ) ** 0.5

            if distance <= 30:
                g.tutorial_room = "runner_complete"
                g.enter_node(node["floor"], node["idx"])

                return True

        return True
    if not getattr(g, "tutorial_active", False):
        return False

    if getattr(g, "tutorial_room", "") != "map_intro":
        return False

    step = getattr(g, "tutorial_map_step", 0)
    # CONTINUE
    cont_rect = getattr(g, "tutorial_map_continue_rect", None)

    if (
        cont_rect
        and cont_rect.collidepoint(pos)):

        continue_map_dialogue(g)
        return True
    # FIRST NODE
    if (
        step == 2
        and getattr(g, "map_data", None)
        and g.map_data[0]):

        node = g.map_data[0][0]

        scroll_y = getattr(g, "map_scroll_y", 0)

        node_x = node["x"]
        node_y = (
            node["y"]
            + scroll_y)

        distance = (
            (
                pos[0] - node_x) ** 2
            +
            (
                pos[1] - node_y) ** 2
        ) ** 0.5

        if distance <= 30:
            g.tutorial_room = "first_enemy"

            g.enter_node(node["floor"], node["idx"])

            return True

    return True
# COMBAT SETUP
def on_enter_combat(g):

    if not getattr(g, "tutorial_active", False):
        return

    if getattr(g, "tutorial_room", "") == "elite":

        g.tutorial_elite_step = 0
        return

    if getattr(g, "tutorial_room", "") == "boss":

        g.tutorial_boss_step = 0
        return

    if getattr(g, "tutorial_room", "") != "first_enemy":
        return

    g.turn = 1

    g.max_mana = 3
    g.mana = 3

    g.pblock = 0

    g.tutorial_step = 0
    g.tutorial_defends_played = 0
    # SCRIPTED TURN 1
    #
    # 2 Defends
    # 3 Strikes
    g.hand = [
        Card("Defend"),
        Card("Defend"),
        Card("Strike"),
        Card("Strike"),
        Card("Strike")
    ]
    g.draw_p = [
        Card("Strike"),
        Card("Defend"),
        Card("Defend")
    ]

    g.disc = []

    g.drag_card = None
# SCRIPTED TURN 2
def prepare_scripted_turn(g):

    if not getattr(g, "tutorial_active", False):
        return False

    if getattr(g, "tutorial_room", "") != "first_enemy":
        return False

    if g.turn != 2:
        return False

    # Turn 2:
    #
    # Bash -> Strike
    #
    # Bash = 2 Mana
    # Strike = 1 Mana

    g.hand = [
        Card("Bash"),
        Card("Strike")
    ]

    g.tutorial_step = 10
    g.tutorial_vulnerable_hover_done = False
    g.tutorial_vulnerable_hover_start = None
    return True
# ALLOWED ACTIONS
def can_play_card(g, card):

    if not getattr(g, "tutorial_active", False):
        return True

    if getattr(g, "tutorial_room", "") != "first_enemy":
        return True
    if getattr(g, "turn", 1) >= 3:

        if getattr(g, "tutorial_step", 0) < 16:
            g.tutorial_step = 16

        return True

    step = getattr(g, "tutorial_step", 0)
    if step in (
        0, 1, 2, 3, 4,
        6, 7,
        10, 12,
        15):
        return False

 
    if step == 5:
        return card.name == "Defend"

 
    if step == 8:
        return card.name == "Strike"

 
    if step == 9:
        return False

    
    # Bash
    if step == 11:

        return (
            card.name == "Bash"
            and getattr(g, "tutorial_vulnerable_hover_done", False)
        )
    # Strike след Vulnerable.
    if step == 13:
        return card.name == "Strike"

    
    if step == 14:
        return False

 
    if step >= 16:
        return True

    return False

def on_card_played(g, card):

    if not getattr(g, "tutorial_active", False):
        return

    if getattr(g, "tutorial_room", "") != "first_enemy":
        return

    step = getattr(g, "tutorial_step", 0)
    # TWO DEFENDS
    if (
        step == 5
        and card.name == "Defend"):

        g.tutorial_defends_played += 1

        if g.tutorial_defends_played >= 2:
        
            g.tutorial_step = 6

        return
    # TURN 1 STRIKE
    if (
        step == 8
        and card.name == "Strike"):
        g.tutorial_step = 9
        return
    # BASH
    if (
        step == 11
        and card.name == "Bash"):
        g.tutorial_step = 12
        return
    # VULNERABLE STRIKE
    if (
        step == 13
        and card.name == "Strike"):
        g.tutorial_step = 14
        return

def can_end_turn(g):

    if not getattr(g, "tutorial_active", False):
        return True
    # FINAL BOSS
    if getattr(g, "tutorial_room", "") == "boss":

        return getattr(g, "tutorial_boss_step", 0) >= 4
    # ELITE
    if getattr(g, "tutorial_room", "") == "elite":

        return getattr(g, "tutorial_elite_step", 0) >= 6
    # FIRST ENEMY
    if getattr(g, "tutorial_room", "") != "first_enemy":
        return True

    step = getattr(g, "tutorial_step", 0)
    if getattr(g, "turn", 1) >= 3:

        if getattr(g, "tutorial_step", 0) < 16:
            g.tutorial_step = 16

        return True
    return (
        step in (9, 14)
        or step >= 16)

def on_end_turn(g):

    if not getattr(g, "tutorial_active", False):
        return

    if getattr(g, "tutorial_room", "") != "first_enemy":
        return

    if g.tutorial_step == 14:
        g.tutorial_step = 15

def on_turn_started(g):

    if not getattr(g, "tutorial_active", False):
        return

    if getattr(g, "tutorial_room", "") != "first_enemy":
        return

    if (
        getattr(g, "turn", 1) >= 3
        and getattr(g, "tutorial_step", 0) < 16):
        g.tutorial_step = 16
# DIALOGUE
def get_dialogue(g):

    step = getattr(g, "tutorial_step", 0)

    if (
        step == 11
        and getattr(g, "tutorial_vulnerable_hover_done", False)
    ):
        return (
            "Good. Hovering over cards can explain effects "
            "such as Vulnerable, Weak, Blitz and Strength. "
            "Now play Bash on the enemy.")
    dialogues = {

        0: (
            "Hey. Looks like this is your first fight. "
            "I'll show you how this works."),

        1: (
            "This is your Health. "
            "If your Health reaches 0, you lose."),

        2: (
            "This is the enemy's Health. "
            "Reduce it to 0 to win the fight."),

        3: (
            "This is the enemy's Intent. "
            "It shows what they plan to do next. "
            "Right now, this enemy plans to attack for 10 damage."),

        4: (
            "Playing cards costs Mana. "
            "The number in the top-left corner of a card "
            "shows how much Mana it costs."),

        5: (
            "Both Defend cards cost 1 Mana. "
            "Play both of them before the enemy attacks."),

        6: (
            "This is your Block. "
            "Block absorbs incoming attack damage. "
            "Your two Defends gave you enough Block for this attack."),

        7: (
            "These circles are your Mana. "
            "You started the turn with 3 Mana. "
            "After playing two Defends, you have 1 Mana left."),

        8: (
            "Strike costs 1 Mana. "
            "Use your remaining Mana to attack the enemy."),

        9: (
            "You're out of Mana for this turn. "
            "Press End Turn to let the enemy act."),

        10: (
            "A new turn restores your Mana. "
            "This time, the enemy plans to gain 5 Block."),

        11: (
            "You drew Bash, which applies Vulnerable. "
            "Hover over the card for a moment to learn what Vulnerable does. "
            "Whenever you don't recognize an effect, hover over it for more information."),

        12: (
            "Vulnerable makes the target take 50% more attack damage."),

        13: (
            "You still have 1 Mana. "
            "Use Strike while the enemy is Vulnerable."),

        14: (
            "Good. End your turn."),

        15: (
            "That's the basics. "
            "Now defeat the enemy however you like.")
    }

    return dialogues.get(step, "")


def step_has_continue(step):

    return step in (
        0,
        1,
        2,
        3,
        4,
        6,
        7,
        10,
        12,
        15)


def continue_dialogue(g):

    step = getattr(g, "tutorial_step", 0)

    transitions = {
        0: 1,
        1: 2,
        2: 3,
        3: 4,
        4: 5,

        6: 7,
        7: 8,

        10: 11,
        12: 13,

        15: 16
    }

    if step in transitions:
        g.tutorial_step = transitions[step]
# DRAW OVERLAY
def draw_combat_overlay(surf, g, mouse):

    if not getattr(g, "tutorial_active", False):
        return

    if getattr(g, "tutorial_room", "") != "first_enemy":
        return

    step = getattr(g, "tutorial_step", 0)
    def highlight_rect(
        rect,
        color=GOLD,
        padding=8,
        width=4):
        if rect is None:
            return

        pygame.draw.rect(
            surf,
            color,
            rect.inflate(padding, padding),
            width,
            border_radius=8)


    def down_arrow(
        x,
        y,
        color=GOLD):
        pygame.draw.polygon(
            surf,
            color,
            [
                (x, y + 14),
                (x - 10, y),
                (x + 10, y)
            ])
    # PLAYER HP
    if step == 1:

        rect = getattr(g, "tutorial_player_hp_rect", None)

        highlight_rect(
            rect,
            GREEN,
            14)

        if rect:
            down_arrow(
                rect.centerx,
                rect.top - 25,
                GREEN)
    # ENEMY HP
    elif step == 2:

        rect = getattr(g, "tutorial_enemy_hp_rect", None)

        highlight_rect(
            rect,
            RED,
            14)

        if rect:
            down_arrow(
                rect.centerx,
                rect.top - 25,
                RED)
    # ENEMY INTENT
    elif step == 3:

        rect = getattr(g, "tutorial_enemy_intent_rect", None)

        highlight_rect(
            rect,
            ORANGE,
            12)

        if rect:
            down_arrow(
                rect.centerx,
                rect.top - 25,
                ORANGE)
    # CARD MANA COST
    elif step == 4:

        positions = g.hand_positions()

        for i, card in enumerate(g.hand):

            if card.name != "Defend":
                continue

            if i >= len(positions):
                continue

            x, y = positions[i]

            hovered = card.collides(
                mouse,
                x,
                y)

            visual_y = (
                y - 20
                if hovered
                else y)

            pygame.draw.circle(
                surf,
                GOLD,
                (
                    x + 13,
                    visual_y + 13),
                16,
                3)
    # PLAYER BLOCK
    elif step == 6:

        rect = getattr(g, "tutorial_player_block_rect", None)

        highlight_rect(
            rect,
            BLUE,
            10)

        if rect:
            down_arrow(
                rect.centerx,
                rect.top - 28,
                BLUE)
    # MANA
    elif step == 7:

        mana_rects = getattr(g, "tutorial_mana_rects", [])

        if mana_rects:

            combined = mana_rects[0].copy()

            for rect in mana_rects[1:]:
                combined.union_ip(rect)

            highlight_rect(
                combined,
                BLUE,
                12)

            down_arrow(
                combined.centerx,
                combined.top - 28,
                BLUE)
    # CARD HIGHLIGHTS
    positions = g.hand_positions()
    # TEACH CARD KEYWORD HOVER
    if step == 11:

        bash_hovered = False

        for i, card in enumerate(g.hand):

            if (
                card.name != "Bash"
                or i >= len(positions)):
                continue

            x, y = positions[i]

            if card.collides(
                mouse,
                x,
                y):
                bash_hovered = True
                break

        if bash_hovered:

            if getattr(g, "tutorial_vulnerable_hover_start", None) is None:

                g.tutorial_vulnerable_hover_start = (
                    pygame.time.get_ticks())

            elif (
                pygame.time.get_ticks()
                - g.tutorial_vulnerable_hover_start
                >= 2100):

                g.tutorial_vulnerable_hover_done = True

        else:

            g.tutorial_vulnerable_hover_start = None
    highlight_names = []

    if step == 5:
        highlight_names = ["Defend"]

    elif step == 8:
        highlight_names = ["Strike"]

    elif step == 11:
        highlight_names = ["Bash"]

    elif step == 13:
        highlight_names = ["Strike"]

    for i, card in enumerate(g.hand):

        if i >= len(positions):
            continue

        if card.name not in highlight_names:
            continue

        x, y = positions[i]
        card_hovered = card.collides(
            mouse,
            x,
            y)

        visual_y = (
            y - 20
            if card_hovered
            else y)

        center_x = x + 60
        label_rect = pygame.Rect(center_x - 35, visual_y - 34, 70, 22)

        rrect(
            surf,
            (45, 35, 15),
            label_rect,
            6,
            2,
            GOLD)

        txc(
            surf,
            ("HOVER"if (step == 11 and not getattr(g,"tutorial_vulnerable_hover_done",False))else "PLAY"),
            F_MED,
            GOLD,
            label_rect.centerx,
            label_rect.centery)
        arrow_tip = (
            center_x,
            visual_y - 2)

        arrow_left = (
            center_x - 9,
            visual_y - 13)

        arrow_right = (
            center_x + 9,
            visual_y - 13)

        pygame.draw.polygon(
            surf,
            GOLD,
            [
                arrow_tip,
                arrow_left,
                arrow_right
            ])
    # ENEMY HIGHLIGHT
    if step in (
        8,
        11,
        13):

        for rect, enemy in getattr(g, "enemy_rects", []):
            pygame.draw.rect(
                surf,
                RED,
                rect.inflate(16, 16),
                4,
                border_radius=10)
    # END TURN HIGHLIGHT
    if step in (
        9,
        14):

        pygame.draw.rect(
            surf,
            GOLD,
            g.end_btn.rect.inflate(8, 8),
            4,
            border_radius=8)
    # DIALOGUE PANEL
    dialogue = get_dialogue(g)

    if not dialogue:
        return

    box = pygame.Rect(W // 2 - 330, H // 2 + 5, 660, 90)

    rrect(
        surf,
        (25, 22, 38),
        box,
        10,
        2,
        GOLD)

    draw_guide_identity(surf, box)
    words = dialogue.split()

    lines = []
    line = ""

    for word in words:

        test = (
            line + " " + word).strip()

        if TUTORIAL_TEXT_FONT.size(test)[0] > 500:
            lines.append(line)
            line = word
        else:
            line = test

    if line:
        lines.append(line)

    for i, text in enumerate(
        lines[:3]):
        surf.blit(
            F_MED.render(
                text,
                True,
                WHITE),
            (
                box.x + 110,
                box.y + 15 + i * 18)
        )
    # CONTINUE BUTTON
    if step_has_continue(step):

        cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

        rrect(
            surf,
            BLUE_D
            if cont_rect.collidepoint(mouse)
            else PANEL,
            cont_rect,
            5,
            1,
            BLUE)

        txc(
            surf,
            "CONTINUE",
            F_MED,
            WHITE,
            cont_rect.centerx,
            cont_rect.centery)

        g.tutorial_continue_rect = cont_rect

    else:
        g.tutorial_continue_rect = None


def handle_combat_click(g, pos):

    if not getattr(g, "tutorial_active", False):
        return False

    room = getattr(g, "tutorial_room", "")
    # FINAL BOSS COMBAT
    if room == "boss":

        step = getattr(g, "tutorial_boss_step", 0)

        if step < 4:

            rect = getattr(g, "tutorial_boss_continue_rect", None)

            if (
                rect
                and rect.collidepoint(pos)):
                continue_boss_dialogue(g)

            return True

        return False
    # ELITE COMBAT
    if room == "elite":

        step = getattr(g, "tutorial_elite_step", 0)

        if step < 6:

            rect = getattr(g, "tutorial_elite_continue_rect", None)

            if (
                rect
                and rect.collidepoint(pos)):
                continue_elite_dialogue(g)

            return True

        return False
    # FIRST ENEMY COMBAT
    if room == "first_enemy":

        rect = getattr(g, "tutorial_continue_rect", None)

        if (
            rect
            and rect.collidepoint(pos)):
            continue_dialogue(g)
            return True

        return False

    return False
# FIRST ENEMY DEFEATED
def handle_combat_win(g):

    if not getattr(g, "tutorial_active", False):
        return False
    # FINAL TUTORIAL BOSS DEFEATED
    if getattr(g, "tutorial_room", "") == "boss":

        g.tutorial_active = False
        g.tutorial_room = "tutorial_complete"
        g.state = "win"

        return True
    # TUTORIAL ELITE DEFEATED
    if getattr(g, "tutorial_room", "") == "elite":
        g.pstr = 0
        g.ptmp_str = 0
        g.pblock = 0
        g.pvuln = 0
        g.pweak = 0
        # Двете карти са гарантирани.
        g.deck.append(
            Card("Ghost Armor"))

        g.deck.append(
            Card("Whirlwind"))

        # Scripted Elite reward.
        g.reward_pool = [
            "Ghost Armor",
            "Whirlwind"
        ]

        g.reward_gold = 80
        g.reward_gold_claimed = False

        g.reward_relic = "Vampire Fangs"
        g.reward_relic_claimed = False

        g.tutorial_room = "elite_reward"

        g.state = "reward"

        return True

    if getattr(g, "tutorial_room", "") != "first_enemy":
        return False

    g.tutorial_room = "reward"
    g.tutorial_reward_step = 0

    g.reward_pool = [
        "Strike",
        "Defend"
    ]

    g.reward_gold = 70
    g.reward_gold_claimed = False

    g.reward_relic = None
    g.reward_relic_claimed = True

    g.minigame_type = "HaremRunner"

    g.state = "reward"

    return True

def on_reward_gold_claimed(g):

    if not getattr(g, "tutorial_active", False):
        return

    if getattr(g, "tutorial_room", "") != "reward":
        return

    g.tutorial_reward_step = 1


def can_start_reward_minigame(g):

    if not getattr(g, "tutorial_active", False):
        return True

    if getattr(g, "tutorial_room", "") != "reward":
        return True
    return getattr(g, "tutorial_reward_step", 0) >= 1

def draw_reward_overlay(surf, g, mouse):

    if not getattr(g, "tutorial_active", False):
        return

    room = getattr(g, "tutorial_room", "")
    # ELITE SCRIPTED REWARD
    if room == "elite_reward":

        step = getattr(g, "tutorial_elite_reward_step", 0)

        dialogue = get_elite_reward_dialogue(g)

        box = pygame.Rect(W // 2 - 340, H - 130, 680, 105)

        rrect(
            surf,
            (25, 22, 38),
            box,
            10,
            2,
            GOLD)

        draw_guide_identity(surf, box)

        words = dialogue.split()
        lines = []
        line = ""

        for word in words:

            test = (
                line + " " + word).strip()

            if TUTORIAL_TEXT_FONT.size(test)[0] > 500:

                if line:
                    lines.append(line)

                line = word

            else:
                line = test

        if line:
            lines.append(line)

        for i, text in enumerate(
            lines[:4]):

            surf.blit(
                F_MED.render(
                    text,
                    True,
                    WHITE),
                (
                    box.x + 110,
                    box.y + 12 + i * 18)
            )

        if step < 5:

            cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

            rrect(
                surf,
                BLUE_D
                if cont_rect.collidepoint(mouse)
                else PANEL,
                cont_rect,
                5,
                1,
                BLUE)

            txc(
                surf,
                "CONTINUE",
                F_MED,
                WHITE,
                cont_rect.centerx,
                cont_rect.centery)

            g.tutorial_elite_reward_continue_rect = (
                cont_rect)

        else:

            leave_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

            rrect(
                surf,
                GREEN_D
                if leave_rect.collidepoint(mouse)
                else PANEL,
                leave_rect,
                5,
                1,
                GREEN)

            txc(
                surf,
                "CONTINUE",
                F_MED,
                WHITE,
                leave_rect.centerx,
                leave_rect.centery)

            g.tutorial_elite_reward_leave_rect = (
                leave_rect)

        return

    if room != "reward":
        return
    step = getattr(g, "tutorial_reward_step", 0)
    # STEP 0 - TAKE GOLD
    if step == 0:

        gold_rect = pygame.Rect(W // 2 - 180, 90, 360, 45)

        pygame.draw.rect(
            surf,
            GOLD,
            gold_rect.inflate(10, 10),
            4,
            border_radius=10)

        dialogue = (
            "Winning battles gives you rewards. "
            "First, take the Gold you earned.")
    # STEP 1 - PLAY MINIGAME
    else:

        minigame_rect = pygame.Rect(W // 2 - 210, 470, 420, 50)

        pygame.draw.rect(
            surf,
            GOLD,
            minigame_rect.inflate(10, 10),
            4,
            border_radius=10)

        dialogue = (
            "These are your possible card rewards: Strike and Defend. "
            "In Card Runner, collect 5 matching pieces to earn a card. "
            "You can earn one, both, or neither. "
        )
    # GUIDE BOX
    box = pygame.Rect(W // 2 - 340, H - 105, 680, 105)

    rrect(
        surf,
        (25, 22, 38),
        box,
        10,
        2,
        GOLD)

    draw_guide_identity(surf, box)

    words = dialogue.split()

    lines = []
    line = ""

    for word in words:

        test = (
            line + " " + word).strip()

        if TUTORIAL_TEXT_FONT.size(test)[0] > 500:
            lines.append(line)
            line = word
        else:
            line = test

    if line:
        lines.append(line)

    for i, text in enumerate(lines[:4]):

        surf.blit(
            F_MED.render(
                text,
                True,
                WHITE),
            (
                box.x + 110,
                box.y + 15 + i * 20)
        )
# TEMP SCREEN BEFORE RUNNER
def draw_runner_ready(surf, g, mouse):

    surf.fill(
        (18, 15, 28))

    txc(
        surf,
        "COMBAT COMPLETE",
        F_BIG,
        GOLD,
        W // 2,
        150)

    txc(
        surf,
        "Next: learn how to earn cards through Card Runner.",
        F_MED,
        WHITE,
        W // 2,
        230)

    txc(
        surf,
        "Tutorial rewards: Strike + Defend",
        F_MED,
        GRAY_L,
        W // 2,
        275)

    txc(
        surf,
        "Each card will require 5 pieces.",
        F_MED,
        GRAY_L,
        W // 2,
        305)

    txc(
        surf,
        "We'll connect this screen to the Runner next.",
        F_MED,
        GOLD,
        W // 2,
        350)
# TUTORIAL SHOP
def setup_shop(g):

    g.tutorial_room = "shop"
    g.tutorial_shop_step = 0
    g.tutorial_shop_wrong_card = None

    g.shop_cards = [
        {
            "name": "Inflame",
            "price": 70,
            "bought": False
        },
        {
            "name": "Clothesline",
            "price": 95,
            "bought": False
        },
        {
            "name": "Carnage",
            "price": 120,
            "bought": False
        },
        {
            "name": "Bludgeon",
            "price": 160,
            "bought": False
        }
    ]
    g.shop_relics = []
    g.shop_relic_rects = []

    g.state = "shop"

def get_shop_map_dialogue(g):

    step = getattr(g, "tutorial_shop_map_step", 0)

    dialogues = {

        0: (
            "That icon is a Shop. "
            "Shops let you spend the Gold you earn during your journey."),

        1: (
            "You'll find cards and other useful things in Shops. "
            "For now, let's see what this one has to offer."),

        2: (
            "Click the highlighted Shop node to enter.")
    }

    return dialogues.get(step, "")


def continue_shop_map_dialogue(g):

    step = getattr(g, "tutorial_shop_map_step", 0)

    if step == 0:
        g.tutorial_shop_map_step = 1

    elif step == 1:
        g.tutorial_shop_map_step = 2

def get_shop_dialogue(g):

    step = getattr(g, "tutorial_shop_step", 0)

    wrong_card = getattr(g, "tutorial_shop_wrong_card", None)

    if step == 2 and wrong_card:

        return (
            f"{wrong_card} is too expensive for you right now. "
            "You only have 70 Gold. "
            "Look for something you can actually afford.")

    dialogues = {

        0: (
            "This is a Shop. "
            "Shops let you spend Gold to add new cards to your deck."),

        1: (
            "You currently have 70 Gold. "
            "Conveniently, one of these cards costs exactly 70."),

        2: (
            "Inflame costs 70 Gold. "
            "Buy it."),

        3: (
            "Nice. Inflame is now part of your deck. "
            "It increases your Strength for the rest of a combat, "
            "making your attacks deal more damage."),

        4: (
            "That's all you need here. "
            "Leave the Shop and continue your journey.")
    }

    return dialogues.get(step, "")

def continue_shop_dialogue(g):

    step = getattr(g, "tutorial_shop_step", 0)

    if step == 0:
        g.tutorial_shop_step = 1

    elif step == 1:
        g.tutorial_shop_step = 2

    elif step == 3:
        g.tutorial_shop_step = 4
def draw_shop_overlay(surf, g, mouse):

    if not getattr(g, "tutorial_active", False):
        return

    if getattr(g, "tutorial_room", "") != "shop":
        return

    step = getattr(g, "tutorial_shop_step", 0)
    # GOLD HIGHLIGHT
    if step == 1:

        gold_rect = pygame.Rect(W // 2 - 85, 52, 170, 38)

        pygame.draw.rect(
            surf,
            GOLD,
            gold_rect,
            3,
            border_radius=8)
    # INFLAME HIGHLIGHT
    if step == 2:

        for item, rect in getattr(g, "shop_card_rects", []):

            if item["name"] == "Inflame":

                pygame.draw.rect(
                    surf,
                    GOLD,
                    rect.inflate(10, 10),
                    4,
                    border_radius=10)

                pygame.draw.polygon(
                    surf,
                    GOLD,
                    [
                        (
                            rect.centerx,
                            rect.top - 5),
                        (
                            rect.centerx - 10,
                            rect.top - 22),
                        (
                            rect.centerx + 10,
                            rect.top - 22)
                    ])

                break
    # LEAVE HIGHLIGHT
    if step == 4:

        pygame.draw.rect(
            surf,
            GOLD,
            g.btn_leave_shop.rect.inflate(8, 8),
            4,
            border_radius=8)
    # DIALOGUE
    dialogue = get_shop_dialogue(g)

    if not dialogue:
        return

    box = pygame.Rect(W // 2 - 340, H - 215, 680, 105)

    rrect(
        surf,
        (25, 22, 38),
        box,
        10,
        2,
        GOLD)

    draw_guide_identity(surf, box)

    words = dialogue.split()

    lines = []
    line = ""

    for word in words:

        test = (
            line + " " + word).strip()

        if TUTORIAL_TEXT_FONT.size(test)[0] > 500:

            if line:
                lines.append(line)

            line = word

        else:
            line = test

    if line:
        lines.append(line)

    for i, text in enumerate(
        lines[:4]):
        surf.blit(
            F_MED.render(
                text,
                True,
                WHITE),
            (
                box.x + 110,
                box.y + 15 + i * 18)
        )
    # CONTINUE
    if step in (0, 1, 3):

        cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

        rrect(
            surf,
            BLUE_D
            if cont_rect.collidepoint(mouse)
            else PANEL,
            cont_rect,
            5,
            1,
            BLUE)

        txc(
            surf,
            "CONTINUE",
            F_MED,
            WHITE,
            cont_rect.centerx,
            cont_rect.centery)

        g.tutorial_shop_continue_rect = (
            cont_rect)

    else:

        g.tutorial_shop_continue_rect = None

def handle_shop_click(g, pos):

    if not getattr(g, "tutorial_active", False):
        return False

    if getattr(g, "tutorial_room", "") != "shop":
        return False

    step = getattr(g, "tutorial_shop_step", 0)
    # CONTINUE
    cont_rect = getattr(g, "tutorial_shop_continue_rect", None)

    if (
        cont_rect
        and cont_rect.collidepoint(pos)):
        continue_shop_dialogue(g)
        return True
    # BUY CARD
    if step == 2:

        for item, rect in getattr(g, "shop_card_rects", []):

            if not rect.collidepoint(pos):
                continue

            if item.get("bought", False):
                return True

            # Правилната карта
            if item["name"] == "Inflame":

                if g.pgold >= 70:

                    g.pgold -= 70
                    item["bought"] = True

                    g.deck.append(
                        Card("Inflame"))

                    g.add_log(
                        "Bought Inflame for 70 Gold")

                    g.tutorial_shop_wrong_card = None
                    g.tutorial_shop_step = 3

                return True
            g.tutorial_shop_wrong_card = (
                item["name"])

            return True
        return True
    # LEAVE
    if step == 4:

        if (
            hasattr(g, "btn_leave_shop")
            and g.btn_leave_shop.hit(pos)):
            g.tutorial_room = "campfire_map_intro"
            g.tutorial_campfire_map_step = 0
            g.state = "map"

            return True

        return True

    return True
# CAMPFIRE MAP INTRO
def get_campfire_map_dialogue(g):

    step = getattr(g, "tutorial_campfire_map_step", 0)

    dialogues = {

        0: (
            "Up ahead is a Campfire. "
            "Campfires give you a chance to prepare for future fights."),

        1: (
            "They can be used in different ways. "
            "For now, we're going to improve the card you just bought."),

        2: (
            "Click the highlighted Campfire to continue.")
    }

    return dialogues.get(step, "")


def continue_campfire_map_dialogue(g):

    step = getattr(g, "tutorial_campfire_map_step", 0)

    if step == 0:
        g.tutorial_campfire_map_step = 1

    elif step == 1:
        g.tutorial_campfire_map_step = 2
# CAMPFIRE TUTORIAL
def get_campfire_dialogue(g):

    step = getattr(g, "tutorial_campfire_step", 0)

    dialogues = {

        0: (
            "This is a Campfire. "
            "Campfires give you several ways to prepare before moving on."),

        1: (
            "One option is upgrading a card. "
            "Upgraded cards are stronger versions of cards already in your deck."),

        2: (
            "You just bought Inflame. "
            "Let's make it stronger. "
            "Click Upgrade a Card.")
    }

    return dialogues.get(step, "")


def continue_campfire_dialogue(g):

    step = getattr(g, "tutorial_campfire_step", 0)

    if step == 0:
        g.tutorial_campfire_step = 1

    elif step == 1:
        g.tutorial_campfire_step = 2

def draw_campfire_overlay(surf, g, mouse):

    if not getattr(g, "tutorial_active", False):
        return

    room = getattr(g, "tutorial_room", "")
    # SECOND CAMPFIRE - REST
    if room == "rest_campfire":

        step = getattr(g, "tutorial_rest_campfire_step", 0)

        if step == 2:

            pygame.draw.rect(
                surf,
                GOLD,
                g.cf_rest.rect.inflate(10, 10),
                4,
                border_radius=8)

            pygame.draw.polygon(
                surf,
                GOLD,
                [
                    (
                        g.cf_rest.rect.centerx,
                        g.cf_rest.rect.top - 4),
                    (
                        g.cf_rest.rect.centerx - 10,
                        g.cf_rest.rect.top - 22),
                    (
                        g.cf_rest.rect.centerx + 10,
                        g.cf_rest.rect.top - 22)
                ])

        dialogue = get_rest_campfire_dialogue(g)

        box = pygame.Rect(W // 2 - 340, H - 135, 680, 95)

        rrect(
            surf,
            (25, 22, 38),
            box,
            10,
            2,
            GOLD)

        draw_guide_identity(surf, box)

        words = dialogue.split()
        lines = []
        line = ""

        for word in words:

            test = (
                line + " " + word).strip()

            if TUTORIAL_TEXT_FONT.size(test)[0] > 500:

                if line:
                    lines.append(line)

                line = word

            else:
                line = test

        if line:
            lines.append(line)

        for i, text in enumerate(
            lines[:3]):

            surf.blit(
                F_MED.render(
                    text,
                    True,
                    WHITE),
                (
                    box.x + 110,
                    box.y + 15 + i * 18)
            )

        if step < 2:

            cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

            rrect(
                surf,
                BLUE_D
                if cont_rect.collidepoint(mouse)
                else PANEL,
                cont_rect,
                5,
                1,
                BLUE)

            txc(
                surf,
                "CONTINUE",
                F_MED,
                WHITE,
                cont_rect.centerx,
                cont_rect.centery)

            g.tutorial_rest_campfire_continue_rect = (
                cont_rect)

        else:
            g.tutorial_rest_campfire_continue_rect = None

        return
    # FIRST CAMPFIRE - UPGRADE
    if room != "campfire":
        return

    step = getattr(g, "tutorial_campfire_step", 0)
    # UPGRADE BUTTON
    if step == 2:

        pygame.draw.rect(
            surf,
            GOLD,
            g.cf_upg.rect.inflate(10, 10),
            4,
            border_radius=8)

        pygame.draw.polygon(
            surf,
            GOLD,
            [
                (
                    g.cf_upg.rect.centerx,
                    g.cf_upg.rect.top - 4),
                (
                    g.cf_upg.rect.centerx - 10,
                    g.cf_upg.rect.top - 22),
                (
                    g.cf_upg.rect.centerx + 10,
                    g.cf_upg.rect.top - 22)
            ])

    dialogue = get_campfire_dialogue(g)

    if not dialogue:
        return

    box = pygame.Rect(W // 2 - 340, H - 135, 680, 95)

    rrect(
        surf,
        (25, 22, 38),
        box,
        10,
        2,
        GOLD)

    draw_guide_identity(surf, box)

    words = dialogue.split()

    lines = []
    line = ""

    for word in words:

        test = (
            line + " " + word).strip()

        if TUTORIAL_TEXT_FONT.size(test)[0] > 500:

            if line:
                lines.append(line)

            line = word

        else:
            line = test

    if line:
        lines.append(line)

    for i, text in enumerate(
        lines[:3]):

        surf.blit(
            F_MED.render(
                text,
                True,
                WHITE),
            (
                box.x + 110,
                box.y + 15 + i * 18)
        )

    if step in (0, 1):

        cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

        rrect(
            surf,
            BLUE_D
            if cont_rect.collidepoint(mouse)
            else PANEL,
            cont_rect,
            5,
            1,
            BLUE)

        txc(
            surf,
            "CONTINUE",
            F_MED,
            WHITE,
            cont_rect.centerx,
            cont_rect.centery)

        g.tutorial_campfire_continue_rect = cont_rect

    else:
        g.tutorial_campfire_continue_rect = None

def handle_campfire_click(g, pos):

    if not getattr(g, "tutorial_active", False):
        return False
    if getattr(g, "tutorial_room", "") == "rest_campfire":

        step = getattr(g, "tutorial_rest_campfire_step", 0)

        cont_rect = getattr(g, "tutorial_rest_campfire_continue_rect", None)

        if (
            cont_rect
            and cont_rect.collidepoint(pos)):
            continue_rest_campfire_dialogue(g)
            return True

        if (
            step == 2
            and g.cf_rest.hit(pos)):

            g.cf_do_rest()

            g.tutorial_room = "boss_map_intro"
            g.tutorial_boss_map_step = 0


            return True
        return True

    if getattr(g, "tutorial_room", "") != "campfire":
        return False

    step = getattr(g, "tutorial_campfire_step", 0)

    cont_rect = getattr(g, "tutorial_campfire_continue_rect", None)

    if (
        cont_rect
        and cont_rect.collidepoint(pos)):
        continue_campfire_dialogue(g)
        return True

    if (
        step == 2
        and g.cf_upg.hit(pos)):

        g.tutorial_room = "campfire_upgrade"
        g.tutorial_upgrade_step = 0

        g.cf_do_upgrade()

        return True


    return True

def get_upgrade_dialogue(g):

    step = getattr(g, "tutorial_upgrade_step", 0)

    dialogues = {

        0: (
            "Here you can choose a card from your deck to upgrade. "
            "Find the Inflame you bought at the Shop."),

        1: (
            "Look at the preview. "
            "Inflame normally gives 2 Strength. "
            "After upgrading, it gives 3."),

        2: (
            "Confirm the upgrade.")
    }

    return dialogues.get(step, "")

def draw_upgrade_overlay(surf, g, mouse):

    if not getattr(g, "tutorial_active", False):
        return

    if getattr(g, "tutorial_room", "") != "campfire_upgrade":
        return

    step = getattr(g, "tutorial_upgrade_step", 0)
    # FIND INFLAME
    if step == 0:

        for rect, card in getattr(g, "upgrade_card_rects", []):

            if card.name == "Inflame":

                pygame.draw.rect(
                    surf,
                    GOLD,
                    rect.inflate(10, 10),
                    4,
                    border_radius=10)

                break
    # CONFIRM BUTTON
    elif step == 2:

        rect = getattr(g, "upgrade_confirm_rect", None)

        if rect:

            pygame.draw.rect(
                surf,
                GOLD,
                rect.inflate(8, 8),
                4,
                border_radius=8)

    dialogue = get_upgrade_dialogue(g)

    box = pygame.Rect(20, H - 115, 550, 85)

    rrect(
        surf,
        (25, 22, 38),
        box,
        10,
        2,
        GOLD)

    draw_guide_identity(surf, box)

    words = dialogue.split()

    lines = []
    line = ""

    for word in words:

        test = (
            line + " " + word).strip()

        if F_MED.size(test)[0] > 390:

            if line:
                lines.append(line)

            line = word

        else:
            line = test

    if line:
        lines.append(line)

    for i, text in enumerate(
        lines[:3]):
        surf.blit(
            F_MED.render(
                text,
                True,
                WHITE),
            (
                box.x + 110,
                box.y + 15 + i * 18)
        )
    if step == 1:

        cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

        rrect(
            surf,
            BLUE_D
            if cont_rect.collidepoint(mouse)
            else PANEL,
            cont_rect,
            5,
            1,
            BLUE)

        txc(
            surf,
            "CONTINUE",
            F_MED,
            WHITE,
            cont_rect.centerx,
            cont_rect.centery)

        g.tutorial_upgrade_continue_rect = (
            cont_rect)

    else:
        g.tutorial_upgrade_continue_rect = None

def handle_upgrade_click(g, pos):

    if not getattr(g, "tutorial_active", False):
        return False

    if getattr(g, "tutorial_room", "") != "campfire_upgrade":
        return False

    step = getattr(g, "tutorial_upgrade_step", 0)
    # SELECT INFLAME
    if step == 0:

        for rect, card in getattr(g, "upgrade_card_rects", []):

            if (
                rect.collidepoint(pos)
                and card.name == "Inflame"):

                g.upgrade_selected_card = card
                g.tutorial_upgrade_step = 1

                return True
        return True
    # PREVIEW CONTINUE
    if step == 1:

        cont_rect = getattr(g, "tutorial_upgrade_continue_rect", None)

        if (
            cont_rect
            and cont_rect.collidepoint(pos)):
            g.tutorial_upgrade_step = 2
            return True

        return True
    # CONFIRM
    if step == 2:

        confirm_rect = getattr(g, "upgrade_confirm_rect", None)

        if (
            confirm_rect
            and confirm_rect.collidepoint(pos)):

            g.confirm_campfire_upgrade()
            g.tutorial_room="chest_map_intro"
            g.tutorial_chest_map_step = 0


            return True

        return True

    return True
# CHEST MAP INTRO
def get_chest_map_dialogue(g):

    step = getattr(g, "tutorial_chest_map_step", 0)

    dialogues = {
        0: (
            "That is a Treasure Chest. "
            "Treasure rooms contain valuable rewards and cost nothing to enter."),

        1: (
            "Chests are one of the ways you can find powerful Relics "
            "during a run."),

        2: (
            "Click the highlighted Chest and let's see what's inside.")
    }

    return dialogues.get(step, "")


def continue_chest_map_dialogue(g):

    step = getattr(g, "tutorial_chest_map_step", 0)

    if step == 0:
        g.tutorial_chest_map_step = 1

    elif step == 1:
        g.tutorial_chest_map_step = 2
# CHEST TUTORIAL
def get_chest_dialogue(g):

    step = getattr(g, "tutorial_chest_step", 0)

    dialogues = {

        0: (
            "This is a Treasure Room. "
            "Unlike Shops, the rewards you find here are free."),

        1: (
            "Open the Chest and take what's inside."),

        2: (
            "You found a Relic: Prophet's Eye."),

        3: (
            "There are various ways to obtain Relics during a run. "
            "Some give small advantages, while others can completely "
            "change how you play."),

        4: (
            "Prophet's Eye lets you see the enemy's next Intent in advance. "
            "That should make what's coming next a little easier."),

        5: (
            "That's everything here. Continue your journey.")
    }

    return dialogues.get(step, "")

def continue_chest_dialogue(g):

    step = getattr(g, "tutorial_chest_step", 0)

    if step == 0:
        g.tutorial_chest_step = 1

    elif step == 2:
        g.tutorial_chest_step = 3

    elif step == 3:
        g.tutorial_chest_step = 4

    elif step == 4:
        g.tutorial_chest_step = 5

def draw_chest_overlay(surf, g, mouse):

    if not getattr(g, "tutorial_active", False):
        return

    if getattr(g, "tutorial_room", "") != "chest":
        return

    step = getattr(g, "tutorial_chest_step", 0)
    # OPEN CHEST
    if (
        step == 1
        and hasattr(g, "btn_open_chest")):

        pygame.draw.rect(
            surf,
            GOLD,
            g.btn_open_chest.rect.inflate(10, 10),
            4,
            border_radius=8)
    # LEAVE
    if (
        step == 5
        and hasattr(g, "btn_leave_chest")):

        pygame.draw.rect(
            surf,
            GOLD,
            g.btn_leave_chest.rect.inflate(10, 10),
            4,
            border_radius=8)

    dialogue = get_chest_dialogue(g)

    if not dialogue:
        return
    box = pygame.Rect(W // 2 - 340, H - 200, 680, 105)

    rrect(
        surf,
        (25, 22, 38),
        box,
        10,
        2,
        GOLD)

    draw_guide_identity(surf, box)

    words = dialogue.split()

    lines = []
    line = ""

    for word in words:

        test = (
            line + " " + word).strip()

        if F_MED.size(test)[0] > 500:

            if line:
                lines.append(line)

            line = word

        else:
            line = test

    if line:
        lines.append(line)

    for i, text in enumerate(
        lines[:4]):

        surf.blit(
            F_MED.render(
                text,
                True,
                WHITE),
            (
                box.x + 110,
                box.y + 15 + i * 18)
        )

    if step in (0, 2, 3, 4):

        cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

        rrect(
            surf,
            BLUE_D
            if cont_rect.collidepoint(mouse)
            else PANEL,
            cont_rect,
            5,
            1,
            BLUE)

        txc(
            surf,
            "CONTINUE",
            F_MED,
            WHITE,
            cont_rect.centerx,
            cont_rect.centery)

        g.tutorial_chest_continue_rect = (
            cont_rect)

    else:
        g.tutorial_chest_continue_rect = None

def handle_chest_click(g, pos):

    if not getattr(g, "tutorial_active", False):
        return False

    if getattr(g, "tutorial_room", "") != "chest":
        return False

    step = getattr(g, "tutorial_chest_step", 0)

    cont_rect = getattr(g, "tutorial_chest_continue_rect", None)

    if (
        cont_rect
        and cont_rect.collidepoint(pos)):
        continue_chest_dialogue(g)
        return True
    # OPEN
    if (
        step == 1
        and hasattr(g, "btn_open_chest")
        and g.btn_open_chest.hit(pos)):

        g.open_chest()

        g.tutorial_chest_step = 2

        return True
    # LEAVE
    if (
        step == 5
        and hasattr(g, "btn_leave_chest")
        and g.btn_leave_chest.hit(pos)):

        g.tutorial_room = "elite_map_intro"
        g.tutorial_elite_map_step = 0
        g.state = "map"

        return True
    return True
# ELITE MAP INTRO
def get_elite_map_dialogue(g):

    step = getattr(g, "tutorial_elite_map_step", 0)

    dialogues = {

        0: (
            "That skull marks an Elite encounter. "
            "Elites are stronger and more dangerous than ordinary enemies."),

        1: (
            "Winston Payne may not look intimidating, "
            "but he can strengthen himself, defend, "
            "and attack multiple times."),

        2: (
            "This is where your new Relic becomes useful. "
            "Prophet's Eye reveals the enemy's next Intent."),

        3: (
            "Watch his pattern carefully. "
            "Click the highlighted Elite when you're ready.")
    }

    return dialogues.get(step, "")


def continue_elite_map_dialogue(g):

    step = getattr(g, "tutorial_elite_map_step", 0)

    if step < 3:
        g.tutorial_elite_map_step += 1
# ELITE COMBAT TUTORIAL
def get_elite_dialogue(g):

    step = getattr(g, "tutorial_elite_step", 0)

    dialogues = {

        0: (
            "This is an Elite. "
            "Unlike Grossberg, Payne has a much more dangerous pattern."),

        1: (
            "Before we continue, there is one more important part of combat: "
            "your Draw Pile."),

        2: (
            "At the start of combat, your deck is shuffled into the Draw Pile. "
            "Normally, you draw 5 cards at the start of each turn."),

        3: (
            "Cards you play go into the Discard Pile. "
            "Any cards left in your hand are also discarded when you end your turn."),

        4: (
            "When your Draw Pile is empty, your Discard Pile is shuffled "
            "and becomes your new Draw Pile."),

        5: (
            "Now use everything you've learned and defeat Winston Payne.")
    }

    return dialogues.get(step, "")
# SECOND CAMPFIRE MAP INTRO
def get_rest_campfire_map_dialogue(g):

    step = getattr(g, "tutorial_rest_campfire_map_step", 0)

    dialogues = {

        0: (
            "That was a much tougher fight. "
            "Elites can leave you badly injured even when you win."),

        1: (
            "Fortunately, there's another Campfire ahead. "
            "Last time we used one to upgrade a card."),

        2: (
            "This time, we'll use it to recover some Health."),

        3: (
            "Click the highlighted Campfire.")
    }

    return dialogues.get(step, "")


def continue_rest_campfire_map_dialogue(g):

    step = getattr(g, "tutorial_rest_campfire_map_step", 0)

    if step < 3:
        g.tutorial_rest_campfire_map_step += 1



def continue_elite_dialogue(g):

    step = getattr(g, "tutorial_elite_step", 0)

    if step < 6:
        g.tutorial_elite_step += 1

def draw_elite_overlay(surf, g, mouse):

    if not getattr(g, "tutorial_active", False):
        return

    if getattr(g, "tutorial_room", "") != "elite":
        return

    step = getattr(g, "tutorial_elite_step", 0)
    # DRAW PILE
    if step in (1, 2):

        pygame.draw.rect(
            surf,
            GOLD,
            g.btn_view_draw.rect.inflate(10, 10),
            4,
            border_radius=8)
    # DISCARD PILE
    elif step == 3:

        pygame.draw.rect(
            surf,
            GOLD,
            g.btn_view_disc.rect.inflate(10, 10),
            4,
            border_radius=8)
    # DRAW + DISCARD / RESHUFFLE
    elif step == 4:

        pygame.draw.rect(
            surf,
            GOLD,
            g.btn_view_draw.rect.inflate(10, 10),
            4,
            border_radius=8)

        pygame.draw.rect(
            surf,
            GOLD,
            g.btn_view_disc.rect.inflate(10, 10),
            4,
            border_radius=8)
   

    dialogue = get_elite_dialogue(g)

    if not dialogue:
        return

    box = pygame.Rect(W // 2 - 330, H // 2 + 5, 660, 90)

    rrect(
        surf,
        (25, 22, 38),
        box,
        10,
        2,
        GOLD)

    draw_guide_identity(surf, box)

    words = dialogue.split()

    lines = []
    line = ""

    for word in words:

        test = (
            line + " " + word).strip()

        if F_MED.size(test)[0] > 500:

            if line:
                lines.append(line)

            line = word

        else:
            line = test

    if line:
        lines.append(line)

    for i, text in enumerate(
        lines[:4]):
        surf.blit(
            F_MED.render(
                text,
                True,
                WHITE),
            (
                box.x + 110,
                box.y + 15 + i * 18)
        )

    if step < 6:

        cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

        rrect(
            surf,
            BLUE_D
            if cont_rect.collidepoint(mouse)
            else PANEL,
            cont_rect,
            5,
            1,
            BLUE)

        txc(
            surf,
            "CONTINUE",
            F_MED,
            WHITE,
            cont_rect.centerx,
            cont_rect.centery)

        g.tutorial_elite_continue_rect = (
            cont_rect)

    else:
        g.tutorial_elite_continue_rect = None

# SECOND CAMPFIRE - REST TUTORIAL
def get_rest_campfire_dialogue(g):

    step = getattr(g, "tutorial_rest_campfire_step", 0)

    dialogues = {

        0: (
            "You took some damage against Payne. "
            "Campfires can also be used to recover Health."),

        1: (
            "Rest restores 30% of your maximum Health."),

        2: (
            "You already improved your deck earlier. "
            "This time, choose Rest.")
    }

    return dialogues.get(step, "")


def continue_rest_campfire_dialogue(g):

    step = getattr(g, "tutorial_rest_campfire_step", 0)

    if step < 2:
        g.tutorial_rest_campfire_step += 1
# BOSS MAP INTRO
def get_boss_map_dialogue(g):

    step = getattr(g, "tutorial_boss_map_step", 0)

    dialogues = {

        0: (
            "You've learned the fundamentals."),

        1: (
            "Now there is only one thing left to test."),

        2: (
            "Whether you can use everything you've learned "
            "against a truly dangerous opponent."),

        3: (
            "Your final opponent is Manfred von Karma."),

        4: (
            "Defeat him, and your training is complete."),

        5: (
            "Click the highlighted Boss when you're ready.")
    }

    return dialogues.get(step, "")


def continue_boss_map_dialogue(g):

    step = getattr(g, "tutorial_boss_map_step", 0)

    if step < 5:
        g.tutorial_boss_map_step += 1
# FINAL BOSS COMBAT
def get_boss_dialogue(g):

    step = getattr(g, "tutorial_boss_step", 0)

    dialogues = {

        0: (
            "This is your final test."),

        1: (
            "Manfred can strengthen himself, defend heavily, "
            "and attack multiple times."),

        2: (
            "Prophet's Eye will help you anticipate his pattern, "
            "but the decisions are yours."),

        3: (
            "Use everything you've learned and defeat Manfred von Karma.")
    }

    return dialogues.get(step, "")


def continue_boss_dialogue(g):

    step = getattr(g, "tutorial_boss_step", 0)

    if step < 4:
        g.tutorial_boss_step += 1


def draw_boss_overlay(surf, g, mouse):

    if not getattr(g, "tutorial_active", False):
        return

    if getattr(g, "tutorial_room", "") != "boss":
        return

    step = getattr(g, "tutorial_boss_step", 0)
    if step >= 4:
        return

    dialogue = get_boss_dialogue(g)

    box = pygame.Rect(W // 2 - 330, H // 2 + 5, 660, 90)

    rrect(
        surf,
        (25, 22, 38),
        box,
        10,
        2,
        RED)

    draw_guide_identity(surf, box)

    words = dialogue.split()

    lines = []
    line = ""

    for word in words:

        test = (
            line + " " + word).strip()

        if F_MED.size(test)[0] > 480:

            if line:
                lines.append(line)

            line = word

        else:
            line = test

    if line:
        lines.append(line)

    for i, text in enumerate(
        lines[:4]):

        surf.blit(
            F_MED.render(
                text,
                True,
                WHITE),
            (
                box.x + 150,
                box.y + 15 + i * 18)
        )

    cont_rect = pygame.Rect(box.right - 125, box.bottom - 33, 105, 25)

    rrect(
        surf,
        BLUE_D
        if cont_rect.collidepoint(mouse)
        else PANEL,
        cont_rect,
        5,
        1,
        BLUE)

    txc(
        surf,
        "CONTINUE",
        F_MED,
        WHITE,
        cont_rect.centerx,
        cont_rect.centery)

    g.tutorial_boss_continue_rect = cont_rect
# ELITE SCRIPTED REWARD
def get_elite_reward_dialogue(g):

    step = getattr(g, "tutorial_elite_reward_step", 0)

    dialogues = {

        0: (
            "Elite enemies are dangerous, but their rewards are usually stronger."),

        1: (
            "For defeating Payne, you'll receive two new cards: "
            "Ghost Armor and Whirlwind."),

        2: (
            "Ghost Armor gives you a large amount of Block, "
            "while Whirlwind attacks multiple times."),

        3: (
            "You also earned a Relic: Vampire Fangs."),

        4: (
            "Vampire Fangs heals you for 2 HP whenever you play an Attack card."),

        5: (
            "These rewards are yours. Continue to the next Campfire.")
    }

    return dialogues.get(step, "")

def continue_elite_reward_dialogue(g):

    step = getattr(g, "tutorial_elite_reward_step", 0)

    if step < 5:
        g.tutorial_elite_reward_step += 1

def handle_elite_reward_click(g, pos):

    if not getattr(g, "tutorial_active", False):
        return False

    if getattr(g, "tutorial_room", "") != "elite_reward":
        return False
    # CLAIM GOLD
    gold_rect = getattr(g, "tutorial_elite_reward_gold_rect", None)

    if (
        gold_rect
        and gold_rect.collidepoint(pos)
        and not getattr(g, "reward_gold_claimed", False)):

        g.pgold += getattr(g, "reward_gold", 0)

        g.reward_gold_claimed = True

        g.log(f"Claimed {g.reward_gold} Gold.", GOLD)

        return True
    # CLAIM VAMPIRE FANGS
    relic_rect = getattr(g, "tutorial_elite_reward_relic_rect", None)

    if (
        relic_rect
        and relic_rect.collidepoint(pos)
        and not getattr(g, "reward_relic_claimed", False)):

        if "Vampire Fangs" not in getattr(g, "relics", []):
            g.add_relic(
                "Vampire Fangs")

        g.reward_relic_claimed = True

        g.log("Claimed relic: Vampire Fangs.", GOLD)

        return True
    leave_rect = getattr(g, "tutorial_elite_reward_leave_rect", None)

    if (
        leave_rect
        and leave_rect.collidepoint(pos)
        and getattr(g, "reward_gold_claimed", False)
        and getattr(g, "reward_relic_claimed", False)):

        g.tutorial_room = (
            "rest_campfire_map_intro")

        g.tutorial_rest_campfire_map_step = 0

        g.state = "map"

        return True

    return True