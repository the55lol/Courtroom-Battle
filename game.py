import random
import json
import os
import tutorial
import pygame

from config import (
    W, H, MAP_NODES, BOSSES, ELITES, ENEMIES, EASY_ENEMIES, CARDS, 
    WHITE, RED, BLUE, BLUE_D, ORANGE, GOLD, GREEN, GREEN_D, PURPLE_D, GRAY, RED_D, CW, CH, GAME_EVENTS, 
    get_card_data, CARD_UPGRADES,RELICS, RELIC_RANDOM_BLACKLIST, HUD_HEIGHT)
from entities import Card, Btn
from asset_utils import asset_path

class Game:
    def __init__(self):
        self.btn_class_1 = Btn("PHOENIX", W//2 - 220, H//2 - 50, 200, 150, RED_D)
        self.btn_class_2 = Btn("FRANZISKA", W//2 + 20, H//2 - 50, 200, 150, PURPLE_D)
        self.btn_tutorial = Btn("PLAY TUTORIAL", W//2 - 110, H//2 + 130, 220, 45, BLUE_D)

        self.cf_rest = Btn("Rest (heal 30%)", W//2-110, 240, 220, 42, GREEN_D)
        self.cf_upg  = Btn("Upgrade a card",  W//2-110, 296, 220, 42, PURPLE_D)
        self.cf_leave= Btn("Leave", W//2-60,  352, 120, 38, GRAY)
        
        # БУТОНИ ЗА БИТКА

        self.end_btn = Btn("End Turn [E]", W - 150, H//2 - 25, 135, 40, GREEN_D)
        self.restart = Btn("Play Again", W//2 - 80, H//2 + 70, 160, 48, RED_D)
        

        bottom_btn_y = H - HUD_HEIGHT - 42

        self.btn_view_draw = Btn(
            "Draw Pile",
            10,
            bottom_btn_y,
            105,
            36,
            BLUE_D)

        self.btn_deck = Btn(
            "Deck",
            125,
            bottom_btn_y,
            80,
            36,
            PURPLE_D)

        self.btn_view_disc = Btn(
            "Discard",
            W - 115,
            bottom_btn_y,
            105,
            36,
            (80, 80, 100))
        self.btn_close_view = Btn("BACK", W//2 - 60, H - 60, 120, 40, RED_D)
        
        self.btn_mg_confirm = Btn("PLAY MINIGAME", W//2 - 170, H - 150, 160, 45, GREEN_D)
        self.btn_mg_skip    = Btn("SKIP (SAFE)",   W//2 + 10,  H - 150, 160, 45, RED_D)
        
        # БУТОНИ ЗА ГЛАВНИТЕ МЕНЮТА
        self.btn_profile    = Btn("Profile: Empty", 10, 10, 180, 35, PURPLE_D)
        self.btn_continue   = Btn("CONTINUE RUN", W//2 - 110, H//2 - 110, 220, 42, GREEN_D)
        self.btn_new_run    = Btn("NEW RUN", W//2 - 110, H//2 - 55, 220, 42, RED_D)
        self.btn_start_play = Btn("PLAY", W//2 - 110, H//2 - 55, 220, 42, GREEN_D)
        self.btn_history = Btn(
            "RUN HISTORY",
            W//2 - 110,
            H//2,
            220,
            42,
            BLUE_D)

        self.btn_collection = Btn(
            "COLLECTION",
            W//2 - 110,
            H//2 + 55,
            220,
            42,
            GOLD)

        self.btn_extras = Btn(
            "EXTRAS",
            W//2 - 110,
            H//2 + 110,
            220,
            42,
            PURPLE_D)

        self.btn_start_set = Btn(
            "SETTINGS",
            W//2 - 110,
            H//2 + 165,
            220,
            42,
            GRAY)

        self.btn_quit_game = Btn(
            "QUIT GAME",
            W//2 - 110,
            H//2 + 220,
            220,
            42,
            RED_D)
        self.btn_hist_back  = Btn("BACK", 20, H - 60, 120, 40, RED_D)
        

        self.btn_abandon_yes = Btn("YES", W//2 - 110, H//2 + 50, 100, 40, RED_D)
        self.btn_abandon_no  = Btn("NO", W//2 + 10, H//2 + 50, 100, 40, GRAY)
        self.btn_set_ctrls = Btn(
            "MINIGAME CONTROLS",
            W // 2 - 150,
            490,
            300,
            50,
            BLUE_D)

        self.btn_set_quit = Btn(
            "SAVE & QUIT TO MENU",
            W // 2 - 125,
            550,
            250,
            48,
            RED_D)

        self.btn_set_quit_desktop = Btn(
            "SAVE & QUIT GAME",
            W // 2 - 125,
            610,
            250,
            48,
            RED_D)

        self.btn_set_back = Btn(
            "BACK",
            W // 2 - 100,
            H - 100,
            200,
            50,
            RED_D)


        self.btn_ingame_set = Btn(
            "SETTINGS",
            W - 105,
            10,
            95,
            35,
            GRAY)


        self.btn_leave_shop = Btn("LEAVE SHOP", W // 2 - 80, H - 75, 160, 42, GRAY)
        self.shop_cards = []
        self.reward_pool = []
        self.current_node = None
        self.current_run_log = []
        self.combat_dmg_dealt = 0
        self.combat_dmg_taken = 0

        self.selected_history_index = 0
        self.history_scroll = 0
        
        self.btn_slots = [
            Btn("", W//2 - 160, 200 + i * 90, 320, 70, BLUE_D) for i in range(3)
        ]
        self.btn_slot_back = Btn("BACK", W//2 - 80, H - 90, 160, 42, RED_D)
        self.btn_delete_save_yes = Btn(
            "DELETE",
            W // 2 - 150,
            370,
            130,
            45,
            RED_D)

        self.btn_delete_save_no = Btn(
            "CANCEL",
            W // 2 + 20,
            370,
            130,
            45,
            GRAY)

        self.delete_save_slot = None
        self.btn_confirm_name = Btn("CONFIRM", W//2 - 80, H//2 + 60, 160, 45, GREEN_D)

        self.viewing_cards = []
        self.view_title = ""
        self.prev_state = ""
        self.enemies = []
        self.btn_dev = Btn("DEV: CARDS", 10, 10, 110, 35, (200, 100, 0))
        self.view_mode = "view"
        self.dev_tab = "Bruiser"
        self.dev_relic_rects = []


        self.prev_settings_state = "start_menu"
        self.awaiting_key = None
        self.selected_minigame_ctrls = "HaremMaker"

        self.card_scroll = 0

        self.collection_tab = "Bruiser"
        self.collection_scroll = 0
        self.collection_tab_rects = []
        self.collection_back_rect = None    

        self.current_slot = 0
        self.profiles = self.load_profiles()
        self.naming_slot = None
        self.input_text = ""
        self.sfx_cache = {}

        self.reset()

    def play_sfx(
        self,
        sound_stem,
        base_volume=1.0):

        if not pygame.mixer.get_init():
            return

        if not hasattr(self, "sfx_cache"
):
            self.sfx_cache = {}
        if sound_stem not in self.sfx_cache:

            sfx_dir = asset_path(
                "sfx")

            sound_path = None
            wanted_stems = {
                sound_stem.lower()
            }
            if os.path.isdir(
                sfx_dir):

                for filename in os.listdir(
                    sfx_dir):

                    stem, ext = os.path.splitext(
                        filename)
                    wanted_stems = {
                        sound_stem.lower()
                    }

                    if sound_stem.lower() == "sfx-stab1":
                        wanted_stems.add(
                            "sfx-stab")
                    if (
                        stem.lower()
                        == sound_stem.lower()
                        and ext.lower()
                        in (
                            ".wav",
                            ".ogg",
                            ".mp3")
                    ):

                        sound_path = os.path.join(sfx_dir, filename
)

                        break

            if sound_path is None:

                print("SFX not found:", sound_stem
)

                self.sfx_cache[
                    sound_stem
                ] = None

            else:

                try:

                    self.sfx_cache[
                        sound_stem
                    ] = pygame.mixer.Sound(
                        sound_path)

                except Exception as exc:

                    print(
                        "SFX load failed:",
                        sound_path,
                        exc)

                    self.sfx_cache[
                        sound_stem
                    ] = None


        sound = self.sfx_cache.get(
            sound_stem)

        if sound is None:
            return

        volume = (
            base_volume
            * getattr(self, "sfx_volume", 1.0
)
        )

        sound.set_volume(
            max(
                0.0,
                min(1.0, volume
)
            ))

        sound.play()
    # ПРОФИЛИ И СЕЙВОВЕ
    def load_profiles(self):

        profiles = None

        if os.path.exists(
            "profiles.json"):

            try:

                with open(
                    "profiles.json",
                    "r",
                    encoding="utf-8") as f:

                    profiles = json.load(f)

            except:
                profiles = None


        if not isinstance(profiles, list
):

            profiles = [
                {"name": ""}
                for _ in range(3)
            ]


        while len(profiles) < 3:

            profiles.append({
                "name": ""
            })


        for profile in profiles:

            profile.setdefault("name", ""
)

            profile.setdefault("tutorial_choice_made", False
)

            profile.setdefault(
                "class_wins",
                {
                    "Bruiser": 0,
                    "Assassin": 0
                })

            profile[
                "class_wins"
            ].setdefault("Bruiser", 0
)

            profile[
                "class_wins"
            ].setdefault("Assassin", 0
)


        return profiles
    # CLASS PROGRESSION
    def _ensure_profile_progression(self, slot=None):

        if slot is None:
            slot = self.current_slot

        if not (
            0 <= slot < len(self.profiles)):
            return

        profile = self.profiles[slot]

        if "class_wins" not in profile:
            profile["class_wins"] = {
                "Bruiser": 0,
                "Assassin": 0
            }

        else:

            profile["class_wins"].setdefault("Bruiser", 0
)

            profile["class_wins"].setdefault("Assassin", 0
)


    def get_class_wins(self, class_name=None
):

        self._ensure_profile_progression()

        if class_name is None:
            class_name = getattr(self, "char_class", "Bruiser"
)

        class_name = str(
            class_name).capitalize()

        return int(
            self.profiles[
                self.current_slot
            ]["class_wins"].get(class_name, 0
)
        )


    def get_class_level(self, class_name=None
):

        wins = self.get_class_wins(
            class_name)

        if wins >= 15:
            return 5

        if wins >= 10:
            return 4

        if wins >= 6:
            return 3

        if wins >= 3:
            return 2

        if wins >= 1:
            return 1

        return 0


    def get_next_level_wins(self, class_name=None
):

        level = self.get_class_level(
            class_name)

        if level >= 5:
            return None


        return level + 1


    def record_class_victory(self):

        self._ensure_profile_progression()

        class_name = str(
            getattr(self, "char_class", "Bruiser"
)
        ).capitalize()

        old_level = self.get_class_level(
            class_name)

        self.profiles[
            self.current_slot
        ]["class_wins"][class_name] += 1

        new_level = self.get_class_level(
            class_name)

        self.save_profiles()

        return old_level, new_level


    def is_card_unlocked(self, card_name
):

        data = CARDS.get(card_name, {}
)

        card_class = str(
            data.get("class", "Any"
)
        ).capitalize()

        current_class = str(
            getattr(self, "char_class", "Bruiser"
)
        ).capitalize()

 
        if (
            card_class != "Any"
            and card_class != current_class):
            return False

        required_level = int(
            data.get("unlock_level", 0
)
        )

        return (
            self.get_class_level(
                current_class)
            >= required_level)


    def is_relic_unlocked(self, relic_name
):

        data = RELICS.get(relic_name, {}
)

        relic_class = str(
            data.get("class", "Any"
)
        ).capitalize()

        current_class = str(
            getattr(self, "char_class", "Bruiser"
)
        ).capitalize()

        if (
            relic_class != "Any"
            and relic_class != current_class):
            return False

        required_level = int(
            data.get("unlock_level", 0
)
        )

        return (
            self.get_class_level(
                current_class)
            >= required_level)
    def save_profiles(self):
        with open("profiles.json", "w", encoding="utf-8") as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=2)

    def get_save_filename(self, slot=None):
        if slot is None:
            slot = self.current_slot
        return f"save_slot_{slot}.json"

    def has_save(self, slot=None):
        return os.path.exists(self.get_save_filename(slot))

    def delete_save(self, slot=None):
        fn = self.get_save_filename(slot)
        if os.path.exists(fn):
            os.remove(fn)


    def delete_profile_slot(self, slot):

        if slot < 0 or slot >= len(self.profiles):
            return

 
        save_file = self.get_save_filename(slot)

        if os.path.exists(save_file):
            os.remove(save_file)


        history_file = f"history_slot_{slot}.json"

        if os.path.exists(history_file):
            os.remove(history_file)


        self.profiles[slot] = {
            "name": "",
            "tutorial_choice_made": False,

            "class_wins": {
                "Bruiser": 0,
                "Assassin": 0
            }
        }

        self.save_profiles()

        if slot == self.current_slot:
            self.naming_slot = None
            self.input_text = ""
    

    def select_slot(self, slot_idx):
        self.current_slot = slot_idx
        p_name = self.profiles[slot_idx]["name"]
        if not p_name:
            self.naming_slot = slot_idx
            self.input_text = f"Player {slot_idx + 1}"
            self.state = "name_profile"
        else:
            self.state = "start_menu"

    def confirm_profile_name(self):
        if self.naming_slot is not None:

            name = (
                self.input_text.strip()
                or f"Player {self.naming_slot + 1}")

            slot = self.naming_slot

            self.profiles[slot]["name"] = name
            self.profiles[slot][
                "class_wins"
            ] = {
                "Bruiser": 0,
                "Assassin": 0
            }
            self.profiles[slot][
                "tutorial_choice_made"
            ] = False

            self.save_profiles()

            self.current_slot = slot
            self.naming_slot = None

            self.state = "tutorial_prompt"

    def save_run(self):
        actual_state = self.state
        if actual_state in ("settings_menu", "controls_select", "controls_menu", "view_cards"):
            actual_state = self.prev_settings_state if actual_state == "settings_menu" else self.prev_state

        data = {
            "char_class": getattr(self, "char_class", "Bruiser"),
            "floor": getattr(self, "floor", 0),
            "relics": getattr(self, "relics", []),
            "php": self.php,
            "pmx": self.pmx,
            "pblock": getattr(self, "pblock", 0),
            "pstr": getattr(self, "pstr", 0),
            "pvuln": getattr(self, "pvuln", 0),
            "ptmp_str": getattr(self, "ptmp_str", 0),
            "pwounds_combo": getattr(self, "pwounds_combo", 0),
            "state": actual_state,
            "minigame_type": getattr(self, "minigame_type", None),
            "current_node_idx": getattr(self, "current_node_idx", None),
            "map_scroll_y": getattr(self, "map_scroll_y", 0),

            "deck": [{"name": c.name, "upgraded": c.upgraded} for c in self.deck],
            "map_data": getattr(self, "map_data", []),
            "path_history": getattr(self,"path_history",[]),
            "current_node": getattr(self, "current_node", None),
            "reward_pool": getattr(self, "reward_pool", []),
            "event_pool": getattr(self, "event_pool", []),
            "current_event_key": getattr(self, "current_event_key", None),
            "current_run_log": getattr(self, "current_run_log", []),
            "pgold": getattr(self, "pgold", 99),
            "normal_enemy_fights": getattr(self,"normal_enemy_fights",0),
            "second_chance_used": getattr(self,"second_chance_used",False)
        }

        if actual_state == "combat":
            data["enemies"] = self.enemies
            data["turn"] = getattr(self, "turn", 1
)

            data["mana"] = self.mana
            data["max_mana"] = self.max_mana
            data["draw_p"] = [{"name": c.name, "upgraded": c.upgraded} for c in self.draw_p]
            data["hand"] = [{"name": c.name, "upgraded": c.upgraded} for c in self.hand]
            data["disc"] = [{"name": c.name, "upgraded": c.upgraded} for c in self.disc]
            data["evuln"] = getattr(self, "evuln", 0)
            data["eweak"] = getattr(self, "eweak", 0)
            data["eblitz"] = getattr(self, "eblitz", 0)
            data["eblitz_timer"] = getattr(self, "eblitz_timer", 0)

        with open(self.get_save_filename(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
    def load_run(self):
        fn = self.get_save_filename()
        if not os.path.exists(fn): return
        with open(fn, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.char_class = data.get("char_class", "Bruiser")
        self.floor = data.get("floor", 0)
        self.php = data.get("php", 70)
        self.pmx = data.get("pmx", 70)
        self.pblock = data.get("pblock", 0)
        self.pstr = data.get("pstr", 0)
        self.pvuln = data.get("pvuln", 0)
        self.ptmp_str = data.get("ptmp_str", 0)
        self.pwounds_combo = data.get("pwounds_combo", 0)
        self.state = data.get("state", "map")
        self.minigame_type = data.get(
            "minigame_type")

        if (
            self.state == "play_minigame"
            and not self.minigame_type):
            self.state = "map"
        self.map_data = data.get("map_data", [])
        self.path_history = [tuple(item)for item in data.get("path_history",[])]
        if not hasattr( self, "path_history"):self.path_history = []
        self.relics = data.get("relics", [])
        self.current_node = data.get("current_node")
        self.current_node_idx = data.get("current_node_idx")
        self.map_scroll_y = data.get("map_scroll_y", 0)
        self.reward_pool = data.get("reward_pool", [])
        self.event_pool = data.get("event_pool", [])
        self.current_event_key = data.get("current_event_key")
        self.current_run_log = data.get("current_run_log", [])
        self.normal_enemy_fights = data.get("normal_enemy_fights",0)
        self.pgold = data.get("pgold", 99)
        self.second_chance_used = data.get("second_chance_used",False)
        self.deck = []
        for cd in data.get("deck", []):
            c = Card(cd["name"])
            c.upgraded = cd["upgraded"]
            self.deck.append(c)

        if self.state == "combat":
            self.enemies = data.get("enemies", [])
            self.turn = data.get("turn", 1)
            self.mana = data.get("mana", 3)
            self.max_mana = data.get("max_mana", 3)
            self.evuln = data.get("evuln", 0)
            self.eweak = data.get("eweak", 0)
            self.eblitz = data.get("eblitz", 0)
            self.eblitz_timer = data.get("eblitz_timer", 0)

            self.draw_p = []
            for cd in data.get("draw_p", []):
                c = Card(cd["name"])
                c.upgraded = cd["upgraded"]
                self.draw_p.append(c)

            self.hand = []
            for cd in data.get("hand", []):
                c = Card(cd["name"])
                c.upgraded = cd["upgraded"]
                self.hand.append(c)

            self.disc = []
            for cd in data.get("disc", []):
                c = Card(cd["name"])
                c.upgraded = cd["upgraded"]
                self.disc.append(c)

        self.drag_card = None
        self.map_scroll_y = 0
        self.log_msgs = []
        self.log("Run loaded successfully.", GREEN)

    def reset(self):
        self.hand = []
        self.deck = []
        self.floor = 0
        self.php = 0; self.pmx = 0
        self.pstr = 0
        self.ptmp_str = 0
        self.pblock = 0
        self.pvuln = 0
        self.pweak = 0
        self.pwounds_combo = 0
        self.log_msgs = []
        self.prev_settings_state = "start_menu"
        self.awaiting_key = None
        self.selected_minigame_ctrls = "HaremMaker"
        self.card_scroll = 0
        self.drag_card = None
        self.draw_p = []       
        self.disc = []         
        self.reward_pool = []  
        self.current_node = None 
        self.mana = 3          
        self.max_mana = 3
        self.turn = 1
        self.enemies = []
        
        self.barbed_wounds = 0
        self.normal_enemy_fights = 0
        self.run_history_events = []
        self.active_history_index = None
        # CARD COMBAT ANIMATIONS
        self.combat_anim_queue = []
        self.combat_anim = None
        self.pending_enemy_turn_finish = False
        self.phoenix_combat_pose = "idle"
        self.phoenix_combat_pose_until = 0
        # CARD MOVE ANIMATIONS
        self.card_anim_queue = []
        self.card_anim = None

        self.pending_end_turn_after_discard = False

        self.end_turn_discard_positions = {}

        self.reshuffle_active = False
        self.reshuffle_next_tick = 0
        self.pending_draw_after_reshuffle = 0

        p_name = self.profiles[self.current_slot]["name"]
        if not p_name:
            self.state = "select_profile"
        else:
            self.state = "start_menu"

    def start_run(self, char_class="Bruiser"):
        # LEAVING TUTORIAL STATE
        self.tutorial_active = False
        self.tutorial_room = ""

        self.tutorial_step = 0
        self.tutorial_map_step = 0

        self.card_anim_queue = []
        self.card_anim = None

        self.combat_anim_queue = []
        self.combat_anim = None

        self.pending_end_turn_after_discard = False
        self.pending_enemy_turn_finish = False

        self.end_turn_discard_positions = {}

        self.reshuffle_active = False
        self.pending_draw_after_reshuffle = 0
        self.delete_save() 
        self.char_class = char_class
        self.floor = 0
        self.current_run_log = []
        self.run_history_events = []
        self.active_history_index = None


        self.php = 70; self.pmx = 70
        self.pblock = 0; self.pstr = 0; self.pvuln = 0
        self.pweak = 0
        self.pvuln = 0
        self.pgold = 99
        self.ptmp_str = 0  
        self.pwounds_combo = 0 
        self.mana = 3
        self.max_mana = 3
        self.pweak = 0
        self.second_chance_used = False
        self.evuln = 0; self.eweak = 0  
        self.eblitz = 0; self.eblitz_timer = 0
        if char_class == "BRUISER":
            self.relics = ["Prophet's Eye"]

        else:  
            self.relics = ["Prosecutor's Badge"]
        if char_class == "BRUISER":
            starting_cards = ["Strike", "Strike", "Strike", "Strike", "Strike", "Defend", "Defend", "Defend", "Defend", "Bash"]
        else:  # ASSASSIN
            starting_cards = ["Strike", "Strike", "Strike", "Strike", "Defend", "Defend", "Defend", "Defend", "Scratch", "Blood Price"]

        self.drag_card = None
        self.current_node = None
        self.generate_map()
        self.state = "map"
        self.deck = [Card(c) for c in starting_cards]
        self.act = 1
        self.defeated_bosses = []
    


    def on_side_boss_defeated(self, boss_mg_name):
        self.history_finish_encounter(
            "VICTORY")

        self.side_boss_reward_type = boss_mg_name

        self.side_boss_reward_gold = 100
        self.side_boss_gold_claimed = False
        self.side_boss_relic_claimed = False

        if boss_mg_name == "BoxingBoss":
            self.side_boss_reward_relic = "Second Chance"

        elif boss_mg_name == "UndertaleBoss":
            self.side_boss_reward_relic = "Perfect Verdict"

        else:
            self.side_boss_reward_relic = None

        self.state = "side_boss_reward"

    def claim_side_boss_gold(self):

        if getattr(self, "side_boss_gold_claimed", False):
            return

        self.pgold += getattr(self, "side_boss_reward_gold", 100)

        self.side_boss_gold_claimed = True

        self.log("Optional Boss reward: +100 Gold!", GOLD)


    def claim_side_boss_relic(self):
        if getattr(self, "side_boss_relic_claimed", False):
            return

        relic = getattr(self, "side_boss_reward_relic", None)

        if relic and relic not in self.relics:
            self.add_relic(relic)

        self.side_boss_relic_claimed = True

        if relic:
            self.log(f"Optional Boss reward: {relic}!", GOLD)
    def claim_side_boss_reward(self):

        if not getattr(self, "side_boss_gold_claimed", False):
            return

        if not getattr(self, "side_boss_relic_claimed", False):
            return

        boss_name = getattr(self, "side_boss_reward_type", None)

        if not boss_name:
            return

        relic = getattr(self, "side_boss_reward_relic", None)
        # MARK BOSS AS DEFEATED
        if not hasattr(self, "defeated_bosses"):
            self.defeated_bosses = []

        if boss_name not in self.defeated_bosses:
            self.defeated_bosses.append(
                boss_name)
        # NEXT ACT
        if not hasattr(self, "act"):
            self.act = 1

        self.act += 1

        self.add_log(
            f"Optional Boss defeated! "
            f"+100 Gold, gained {relic}. "
            f"Returning to Floor 1.")

        self.generate_map()
        # CLEANUP REWARD STATE
        self.side_boss_reward_type = None
        self.side_boss_reward_relic = None
        self.side_boss_reward_gold = 0

        self.side_boss_gold_claimed = False
        self.side_boss_relic_claimed = False

        self.state = "map"

    def open_card_view(self, cards, title, mode="view"):
        self.prev_state = self.state
        rarity_weights = {"common": 0, "rare": 1, "epic": 2, "legendary": 3}
        
        self.viewing_cards = sorted(
            cards,
            key=lambda c: (
                rarity_weights.get(CARDS.get(c.name, {}).get("rarity", "common"), 0),
                CARDS.get(c.name, {}).get("cost", 0),
                c.name)
        )
        self.view_title = title
        self.view_mode = mode
        self.card_scroll = 0
        self.state = "view_cards"
        
    def close_card_view(self):
        self.state = self.prev_state

    def generate_map(self):
        """Генерира карта с 21 етажа (0-20), единствен campfire на етаж 19 и оставащите босове на етаж 20."""
        num_floors = 21
        num_cols = 7
        self.map_data = []
        self.floor = 0
        self.current_node_idx = None
        self.path_history = []
        self.map_scroll_y = 0 

        if not hasattr(self, 'act'): self.act = 1
        if not hasattr(self, 'defeated_bosses'): self.defeated_bosses = []

        act_scale = 1.0 + (self.act - 1) * 0.3

        start_y = H - 120
        y_step = 110 

        padding = 120
        usable_w = W - 2 * padding
        col_spacing = usable_w // (num_cols - 1)
        col_x = [padding + i * col_spacing for i in range(num_cols)]

        num_paths = random.choice([4, 5])
        start_cols = sorted(random.sample(range(num_cols), num_paths))
        paths = [[c] for c in start_cols]

        for f in range(num_floors - 3):
            prev_col_next = -1
            for p_idx in range(len(paths)):
                curr_c = paths[p_idx][-1]
                candidates = [curr_c - 1, curr_c, curr_c + 1]
                valid = [c for c in candidates if 0 <= c < num_cols and c >= prev_col_next]
                if not valid: valid = [c for c in candidates if 0 <= c < num_cols]
                next_c = random.choice(valid)
                paths[p_idx].append(next_c)
                prev_col_next = next_c

        floor_nodes_grid = []
        for f in range(num_floors - 2):
            y = int(start_y - f * y_step)
            cols_on_floor = sorted(list(set(p[f] for p in paths)))
            nodes_dict = {}

            for idx, c in enumerate(cols_on_floor):
                x = col_x[c] + random.randint(-8, 8) 

                if f == 0: ntype = "enemy" 
                elif f == 10: ntype = "chest" 
                else:
                    choices = ["enemy", "enemy", "?", "?", "elite", "shop", "campfire","campfire","campfire"]
                    if f < 4: choices = ["enemy", "enemy", "?", "shop", "campfire","campfire"]
                
                    parent_types = []
                    if f > 0:
                        for p in paths:
                            if p[f] == c:  
                                prev_c = p[f-1]
                                parent_types.append(floor_nodes_grid[f-1][prev_c]["type"])
                    has_good_parent = any(pt in ["shop", "campfire", "chest", "?"] for pt in parent_types)
                    if has_good_parent:
                        choices = [x for x in choices if x not in ["shop", "campfire", "?"]]
                        if not choices: choices = ["enemy"]
                
                    ntype = random.choice(choices)

                
                enemy_info = None

                mg = random.choice([
                    "HaremMaker",
                    "HaremRunner",
                    "ManPac"
                ])

                reward_rarity = "Common"

                if ntype in ("enemy", "elite"):

                    if ntype == "elite":

                        encounter_template = random.choice(
                            ELITES)

                        reward_rarity = random.choice([
                            "Epic",
                            "Legendary"
                        ])

                    else:
                        if f < 4:
                            encounter_template = random.choice(
                                EASY_ENEMIES)
                        else:
                            encounter_template = random.choice(
                                ENEMIES)

                        reward_rarity = random.choice([
                            "Common",
                            "Rare",
                            "Epic"
                        ])

                    if isinstance(encounter_template, dict):
                        encounter_template = [encounter_template]

                    enemy_info = []

                    for original_enemy in encounter_template:

                        e_dict = dict(original_enemy)

                        base_hp = int(
                            e_dict.get("hp", 45)
                            * act_scale)

                        moves = e_dict.get(
                            "moves",
                            {"Attack 5": ("atk", 5, 0)})

                        scaled_moves = {}

                        for move_name, move_data in moves.items():

                            kind, v1, v2 = move_data

                            if kind in ("atk", "atk_multi"):
                                scaled_v1 = int(
                                    v1 * act_scale)
                            else:
                                scaled_v1 = v1

                            scaled_moves[move_name] = (
                                kind,
                                scaled_v1,
                                v2)

                        enemy_info.append({
                            "name": e_dict.get("name", "Enemy"),
                            "hp": base_hp,
                            "max_hp": base_hp,
                            "mg": mg,
                            "rarity": reward_rarity,
                            "pattern": list(
                                e_dict.get("pattern", ["Attack 5"])
                            ),
                            "moves": scaled_moves
                        })

                nodes_dict[c] = {
                    "floor": f,
                    "idx": idx,
                    "col": c,
                    "type": ntype,
                    "minigame": mg,
                    "reward_rarity": reward_rarity,
                    "enemy": enemy_info,
                    "x": x,
                    "y": y,
                    "next_nodes": []
                }

            floor_nodes_grid.append(nodes_dict)
        y_camp = int(start_y - (num_floors - 2) * y_step)
        y_boss = int(start_y - (num_floors - 1) * y_step)
        boss_nodes = []

        #  ФИНАЛЕН БОС 
        boss1_dict = next(
            (
                boss
                for boss in BOSSES
                if boss.get("name") == "Edgeworth"),
            BOSSES[0])
        
        b_moves = boss1_dict.get("moves", {"Attack 10": ("atk", 10, 0)})
        if isinstance(b_moves, list):
            formatted = {}
            for m in b_moves:
                formatted[m["name"]] = (m.get("kind", "atk"), m.get("v1", 10), m.get("v2", 0))
            b_moves = formatted

        card_boss_hp = int(boss1_dict.get("hp", 200) * act_scale)
        boss_cards = {
            "floor": num_floors - 1, "idx": 0, "type": "boss", "minigame": "None",
            "enemy": {
                "name": f"Edgeworth (FINAL BOSS - Act {self.act})",
                "hp": card_boss_hp, "max_hp": card_boss_hp,
                "mg": "None", "type": "normal_boss", "rarity": "Legendary",
                "pattern": boss1_dict.get("pattern", ["Attack 10"]),
                "moves": b_moves
            },
            "x": 0, "y": y_boss, "next_nodes": []
        }
        boss_nodes.append(boss_cards)

        #  БОКСИНГ БОС (Godot)
        if "BoxingBoss" not in self.defeated_bosses:
            boxing_hp = int(180 * act_scale)
            boss_boxing = {
                "floor": num_floors - 1, "idx": len(boss_nodes), "type": "boss", "minigame": "BoxingBoss",
                "enemy": {
                    "name": "Godot (Boxing Boss)", "hp": boxing_hp, "max_hp": boxing_hp,
                    "mg": "BoxingBoss", "type": "boxing_boss", "rarity": "Legendary",
                    "pattern": ["Attack 10"], "moves": {"Attack 10": ("atk", 10, 0)}
                },
                "x": 0, "y": y_boss, "next_nodes": []
            }
            boss_nodes.append(boss_boxing)

        # UNDERTALE БОС (Franziska
        if "UndertaleBoss" not in self.defeated_bosses:
            undertale_hp = int(200 * act_scale)
            boss_undertale = {
                "floor": num_floors - 1, "idx": len(boss_nodes), "type": "boss", "minigame": "UndertaleBoss",
                "enemy": {
                    "name": "Franziska (Undertale Boss)", "hp": undertale_hp, "max_hp": undertale_hp,
                    "mg": "UndertaleBoss", "type": "undertale_boss", "rarity": "Legendary",
                    "pattern": ["Attack 10"], "moves": {"Attack 10": ("atk", 10, 0)}
                },
                "x": 0, "y": y_boss, "next_nodes": []
            }
            boss_nodes.append(boss_undertale)

        edgeworth = boss_nodes[0]

        edgeworth["x"] = W // 2

        optional_bosses = boss_nodes[1:]

        if len(optional_bosses) == 2:

            optional_bosses[0]["x"] = W // 2 - 250
            optional_bosses[1]["x"] = W // 2 + 250

        elif len(optional_bosses) == 1:
            optional_bosses[0]["x"] = W // 2 + 250
        campfire_node = {
            "floor": num_floors - 2, "idx": 0, "col": num_cols // 2,
            "type": "campfire", "minigame": "None", "enemy": None,
            "x": W // 2, "y": y_camp,
            "next_nodes": [b["idx"] for b in boss_nodes]
        }

        for f in range(num_floors - 3):
            curr_floor_dict = floor_nodes_grid[f]
            next_floor_dict = floor_nodes_grid[f + 1]
            for p in paths:
                src_node = curr_floor_dict[p[f]]
                dst_node = next_floor_dict[p[f + 1]]
                if dst_node["idx"] not in src_node["next_nodes"]:
                    src_node["next_nodes"].append(dst_node["idx"])

        floor18_dict = floor_nodes_grid[num_floors - 3]
        for c, node in floor18_dict.items():
            node["next_nodes"] = [0]

        self.map_data = []
        for f in range(num_floors - 2):
            self.map_data.append(list(floor_nodes_grid[f].values()))

        self.map_data.append([campfire_node])
        self.map_data.append(boss_nodes)  

    def add_relic(self, relic_name):
        """Добавя релик и изпълнява еднократния му pickup ефект."""

        if not hasattr(self, "relics"):
            self.relics = []

        if relic_name in self.relics:
            return False

        self.relics.append(relic_name)

    # ONE-TIME PICKUP EFFECTS

        if relic_name == "Ancient Coin":
            self.pgold += 50
            self.log("Ancient Coin: +50 Gold!", GOLD)
        return True


    def enter_node(self, floor_idx, node_idx):
        """Влизане в избрания възел от разклонената карта."""
        self.floor = floor_idx
        self.current_node_idx = node_idx
        if not hasattr(self, 'path_history'):
            self.path_history = []
        self.path_history.append((floor_idx, node_idx))
        
        node = self.map_data[floor_idx][node_idx]
        self.current_node = node
        ntype = node["type"]

      
        if ntype in ("enemy", "elite", "boss"):
            raw_enemy_data = node.get("enemy")

            if isinstance(raw_enemy_data, list):
                first_enemy = (
                    raw_enemy_data[0]
                    if raw_enemy_data
                    else {})
            else:
                first_enemy = raw_enemy_data or {}
            mg_type = first_enemy.get("mg")
            if mg_type in ["BoxingBoss", "UndertaleBoss"]:

                self.current_enemy = dict(first_enemy)
                self.combat_dmg_dealt = 0
                self.combat_dmg_taken = 0

                self.history_start_encounter(
                    node,
                    [first_enemy],
                    allow_replay=False)
                self.state = "play_minigame"
                self.minigame_type = mg_type
                
                self.log(f"BOSS FIGHT: {first_enemy['name']}!", RED)               
                self.save_run()

                return

            self.state = "combat"

            self.turn = 1
            self.combat_dmg_dealt = 0
            self.combat_dmg_taken = 0
            self.thunder_heart_used = False
            self.execution_mark_used = False

            self.capacitor_core_used = False
            self.blood_needle_used = False

            self.blitz_applied_this_turn = 0
            self.storm_engine_triggered = False

            self.wound_cards_this_turn = 0
            self.bloodletter_triggered = False
            self.max_mana = 3
            self.mana = self.max_mana

            self.pstr = 0
            self.pblock = 0
            self.pvuln = 0
            self.ptmp_str = 0
            # PROSECUTOR'S BADGE
            if (
                self.turn == 1
                and "Prosecutor's Badge"
                in getattr(self, "relics", [])):

                self.pblock += 4
                self.pstr += 1

                self.log(
                    "Prosecutor's Badge: "
                    "+4 Block, +1 Strength.",
                    GOLD)

            self.pweak = 0
            self.pvuln = 0



            if "Demon Horn" in getattr(self, "relics", []):
                self.pstr += 1
                self.log("Demon Horn: +1 Strength.", ORANGE)

            # Mana Crystal: +1 Max Mana
            if "Mana Crystal" in getattr(self, "relics", []):
                self.max_mana += 1
                self.mana = self.max_mana
                self.log("Mana Crystal: +1 Max Mana.", BLUE)

            # Molten Hammer: +1 Max Mana
            if "Molten Hammer" in getattr(self, "relics", []):
                self.max_mana += 1
                self.mana = self.max_mana
                self.log("Molten Hammer: +1 Max Mana.", ORANGE)

            # Mutated Blood: +2 Strength, -3 HP
            if "Mutated Blood" in getattr(self, "relics", []):
                self.pstr += 2
                self.php = max(1, self.php - 3)
                self.log("Mutated Blood: +2 Strength, -3 HP.", RED)

            if "Iron Core" in getattr(self, "relics", []):
                self.pblock += 4
                self.log("Iron Core: +4 Block.", BLUE)
            if not getattr(self, 'deck', None):
                self.deck = [Card("Strike") for _ in range(5)] + [Card("Defend") for _ in range(5)]


            self.draw_p = []
            for c in self.deck:
                
                    if isinstance(c, str):
                        self.draw_p.append(Card(c))
                    elif hasattr(c, 'name'):
                        new_card = Card(c.name)
                        new_card.upgraded = c.upgraded
                        self.draw_p.append(new_card)
                    else:
                        self.draw_pile.append(c)

            random.shuffle(self.draw_p)
            self.hand = []
            self.disc = []
            self.mana = getattr(self, 'max_mana', 3)
            is_scripted_tutorial_fight = (
                getattr(self, "tutorial_active", False)
                and getattr(self, "tutorial_room", "") == "first_enemy")

            if not is_scripted_tutorial_fight:
                self.draw_cards(5)
            raw_enemies = node.get("enemy", [])

            if isinstance(raw_enemies, dict):
                raw_enemies = [raw_enemies]


            self.enemies = []

            for raw_enemy in raw_enemies:

                en = dict(raw_enemy)

                en["max_hp"] = en.get(
                    "max_hp",
                    en.get("hp", 30))

                en["hp"] = en["max_hp"]

                en["block"] = 0
                en["str"] = 0
                en["weak"] = 0
                en["vuln"] = 0
                en["blitz"] = 0
                en["blitz_timer"] = 0

                en["turn"] = 0
                en["move_i"] = 0

                self.enemies.append(en)


            self.history_start_encounter(
                node,
                self.enemies,
                allow_replay=False)             

            if "Toxic Gland" in getattr(self, "relics", []):

                for en in self.enemies:
                    en["weak"] += 1

                self.log("Toxic Gland: enemies start with 1 Weak.", GREEN)


            if self.enemies:
                self.current_enemy = self.enemies[0]


            self.log(f"Encounter started: {len(self.enemies)} enemy/enemies!", ORANGE)
            tutorial.on_enter_combat(self)
            if self.enemies:
                self.current_enemy = self.enemies[0]
            self.save_run()
 

        elif ntype == "campfire":
            self.state = "campfire"
        elif ntype == "shop":
            if hasattr(self, 'enter_shop'):
                self.enter_shop()
            elif hasattr(self, 'generate_shop'):
                self.generate_shop()
                self.state = "shop"
            else:
                self.state = "shop"
        elif ntype == "chest":
            self.chest_opened = False
            self.chest_gold = random.randint(50, 100)
           
            avail_relics = [
                r
                for r in RELICS.keys()
                if (
                    r not in getattr(self, "relics", [])
                    and r not in RELIC_RANDOM_BLACKLIST
                    and self.is_relic_unlocked(
                        r)
                )
            ]
            self.chest_relic = random.choice(avail_relics) if avail_relics else None
            self.btn_open_chest = Btn("OPEN CHEST", W // 2 - 90, H // 2 + 30, 180, 45, GOLD)
            self.btn_leave_chest = Btn("Leave", W//2 - 60, 400, 120, 42, GRAY)
            self.state = "chest"
        elif node["type"] == "?":
            self.state = "event"
            
            if not getattr(self, "event_pool", []):
                    self.event_pool = list(GAME_EVENTS.keys())
                    random.shuffle(self.event_pool)

            self.current_event_key = self.event_pool.pop()

            self.event_resolved = False
            self.add_log("Влезе в събитие: " + GAME_EVENTS[self.current_event_key]["title"])

            self.save_run()

    def open_chest(self):
        if not getattr(self, "chest_opened", False):
            self.chest_opened = True

            self.pgold += getattr(self, "chest_gold", 0)

            if getattr(self, "chest_relic", None):
                self.add_relic(self.chest_relic)


    def start_combat_with_node(self, node):
        self.current_node = node
        self.enemies = []
        self.combat_dmg_dealt = 0
        self.combat_dmg_taken = 0
        enemy_list = node["enemy"] 
        for en in enemy_list:
            new_enemy = dict(en) 
            new_enemy["max_hp"] = new_enemy["hp"]
            new_enemy["block"] = 0
            new_enemy["str"] = 0
            new_enemy["vuln"] = 0
            new_enemy["weak"] = 0
            new_enemy["blitz"] = 0
            new_enemy["blitz_timer"] = 0
            new_enemy["move_i"] = 0
            self.enemies.append(new_enemy)

        self.pblock = 0; self.pvuln = 0; self.ptmp_str = 0
        self.pweak = 0
        self.draw_p = self.deck.copy()
        random.shuffle(self.draw_p)
        self.hand = []
        self.disc = []
        self.mana = 3
        self.max_mana = 3
        self.drag_card = None
        if "Demon Horn" in self.relics:
            self.pstr += 1
        if "Mana Crystal" in self.relics:
            self.max_mana += 1
            self.mana += 1
        if "Toxic Gland" in self.relics:
            for en in self.enemies:
                en["weak"] += 1
                
        self._start_turn()
        self.state = "combat"
        

    def _start_turn(self):

        self.mana = self.max_mana
        self.pblock = 0
        self.ptmp_str = 0
        # PROGRESSION RELIC TURN RESET
        self.capacitor_core_used = False
        self.blood_needle_used = False

        self.blitz_applied_this_turn = 0
        self.storm_engine_triggered = False

        self.wound_cards_this_turn = 0
        self.bloodletter_triggered = False

        self.barbed_wounds = 0
        # LEVEL 5 START-OF-TURN RELICS
        if (
            "Infinite Voltage"
            in getattr(self, "relics", [])
        ):

            for en in getattr(self, "enemies", []):

                if en.get("hp", 0) > 0:

                    self.apply_blitz(en, 5)

            self.log("Infinite Voltage activated.", PURPLE_D)

        if (
            "Blood Moon"
            in getattr(self, "relics", [])
        ):

            for en in getattr(self, "enemies", []):

                if en.get("hp", 0) > 0:

                    self.apply_wounds(en, 2)

            self.log("Blood Moon activated.", RED)
        # TUTORIAL / NORMAL DRAW
        scripted_turn = (
            tutorial.prepare_scripted_turn(
                self)
        )

        if not scripted_turn:

            draw_count = (
                6
                if (
                    "Mind Glass"
                    in getattr(self, "relics", [])
                )
                else 5)

            self.draw_cards(
                draw_count)
        # HOURGLASS
        if (
            "Hourglass of Fate"
            in getattr(self, "relics", [])
            and self.turn % 3 == 0):

            self.mana += 2

            self.draw_cards(
                2)

            self.log(
                "Hourglass of Fate: +2 Mana, draw 2!",
                GOLD)

        self.log(f"Turn start. Mana: {self.mana}", WHITE)

        self.pwounds_combo = 0

        tutorial.on_turn_started(
            self)

    def draw_cards(self, n):

        remaining = n

        while remaining > 0:
            # DRAW PILE EMPTY -> RESHUFFLE
            if not self.draw_p:

                if not self.disc:
                    break

                self.start_reshuffle(
                    remaining)

                return
            # NORMAL DRAW
            card = self.draw_p.pop()

            self.queue_draw_card(
                card)

            remaining -= 1

            
    def hand_positions(self):
        n = len(self.hand)
        if n == 0: return []
        spacing = 100
        total_w = (n-1)*spacing + CW
        start_x = (W - total_w)//2
        return [(start_x + i*spacing, H - CH - 15) for i in range(n)]
    # CARD MOVE ANIMATIONS
    def card_animation_busy(self):
        return bool(
            self.card_anim
            or self.card_anim_queue
            or self.reshuffle_active)


    def queue_draw_card(self, card):

        self.card_anim_queue.append({
            "type": "draw",
            "card": card,
            "started": None,
            "duration": 220,

            "start_x": 10,
            "start_y": H - 80,

            "target_x": None,
            "target_y": None
        })


    def queue_discard_card(
        self,
        card,
        start_x,
        start_y):

        self.card_anim_queue.append({
            "type": "discard",
            "card": card,
            "started": None,
            "duration": 200,

            "start_x": start_x,
            "start_y": start_y,

            "target_x": W - CW - 10,
            "target_y": H - 80
        })


    def start_reshuffle(self, draw_after):

        if not self.disc:
            return

        self.reshuffle_active = True

        self.reshuffle_next_tick = (
            pygame.time.get_ticks())

        self.pending_draw_after_reshuffle = (
            draw_after)

    def update_card_animations(self):

        if self.state != "combat":

            self.card_anim = None
            self.card_anim_queue = []
            self.pending_end_turn_after_discard = False

            return


        now = pygame.time.get_ticks()
        # DISCARD -> DRAW RESHUFFLE
        if self.reshuffle_active:

            if (
                now
                >= self.reshuffle_next_tick):

                if self.disc:

                    card = self.disc.pop()

                    self.draw_p.append(
                        card)
                    self.reshuffle_next_tick = (
                        now + 70)

                else:

                    random.shuffle(
                        self.draw_p)

                    self.reshuffle_active = False

                    amount = (
                        self.pending_draw_after_reshuffle)

                    self.pending_draw_after_reshuffle = 0
                    if amount > 0:

                        self.draw_cards(
                            amount)

            return
        # START NEXT CARD
        if (
            self.card_anim is None
            and self.card_anim_queue):

            self.card_anim = (
                self.card_anim_queue.pop(0))

            self.card_anim["started"] = now
            # DISCARD STARTS NOW
            if (
                self.card_anim["type"]
                == "discard"):

                card = self.card_anim[
                    "card"
                ]

                if card in self.hand:

                    self.hand.remove(
                        card)
            if self.card_anim["type"] == "draw":

                future_count = (
                    len(self.hand) + 1)

                spacing = 100

                total_w = (
                    (future_count - 1)
                    * spacing
                    + CW)

                start_x = (
                    W - total_w) // 2

                self.card_anim[
                    "target_x"
                ] = (
                    start_x
                    + (
                        future_count - 1) * spacing
                )

                self.card_anim[
                    "target_y"
                ] = (
                    H - CH - 15)


        anim = self.card_anim
        # NOTHING MOVING
        if anim is None:

            if (
                self.pending_end_turn_after_discard):

                self.pending_end_turn_after_discard = False

                self.end_turn_discard_positions = {}

                self._continue_end_turn()

            return


        elapsed = (
            now - anim["started"])


        if elapsed >= anim["duration"]:

            card = anim["card"]
            if anim["type"] == "draw":

                self.hand.append(
                    card)


            elif anim["type"] == "discard":

                self.disc.append(
                    card)


            self.card_anim = None
            if (
                self.state == "combat"
                and not self.card_anim_queue
                and not self.reshuffle_active
            ):
                self.save_run()
    # CARD COMBAT HIT ANIMATIONS
    def queue_combat_hit(
        self,
        attacker,
        target,
        raw_damage,
        enemy=None,
        action="Attack"):
        self.combat_anim_queue.append({
            "attacker": attacker,
            "target": target,
            "raw_damage": raw_damage,
            "enemy": enemy,
            "action": action,
            "started": None,
            "damage_applied": False,
            "actual_damage": 0,
            "blocked": 0
        })


    def combat_animation_busy(self):
        return bool(
            self.combat_anim
            or self.combat_anim_queue)


    def _apply_combat_animation_damage(self, anim):

        raw = anim["raw_damage"]
        enemy = anim.get("enemy")
        # PLAYER -> ENEMY
        if anim["target"] == "enemy":

            if not enemy or enemy["hp"] <= 0:
                return

            block_before = enemy.get("block", 0)

            actual = max(0, raw - block_before)

            blocked = min(block_before, raw)

            enemy["block"] = max(0, block_before - raw)

            enemy["hp"] -= actual

            self.combat_dmg_dealt += actual

            anim["actual_damage"] = actual
            anim["blocked"] = blocked

            if actual > 0:
                self.play_sfx("sfx-stab2", 0.70)
                self.set_enemy_pose(
                    enemy,
                    "damage",
                    850)
            elif (
                raw > 0
                and blocked >= raw):

                self.play_sfx("sfx-smack", 0.75)            

            self.history_record_step(
                actor="player",
                source="Player",
                action=anim.get("action", "Attack"),
                target=enemy.get("name", "Enemy"),
                kind="damage",
                value=actual)
            self.log(f"Dealt {actual} dmg to {enemy['name']}.", RED)
        # ENEMY -> PLAYER
        elif anim["target"] == "player":

            block_before = self.pblock

            actual = max(0, raw - block_before)

            blocked = min(block_before, raw)

            self.pblock = max(0, block_before - raw)

            # Tutorial Payne safety.
            if (
                getattr(self, "tutorial_active", False)
                and getattr(self, "tutorial_room", "") == "elite"
            ):
                actual = min(
                    actual,
                    max(0, self.php - 10)
                )

            self.php -= actual
            self.combat_dmg_taken += actual

            anim["actual_damage"] = actual
            anim["blocked"] = blocked
            if actual > 0:

                self.play_sfx("sfx-stab", 0.70)
                self.phoenix_combat_pose = (
                    "damage")

                self.phoenix_combat_pose_until = (
                    pygame.time.get_ticks()
                    + 900)      
            elif (
                raw > 0
                and blocked >= raw):

                self.play_sfx("sfx-smack", 0.75)
            self.history_record_step(
                actor="enemy",
                source=(
                    enemy.get("name", "Enemy")
                    if enemy
                    else "Enemy"),
                action=anim.get("action", "Attack"),
                target="Player",
                kind="damage",
                value=actual)
            # Mirror Shield
            if (
                blocked > 0
                and enemy
                and "Mirror Shield"
                in getattr(self, "relics", [])):
                enemy["hp"] -= 4
                self.combat_dmg_dealt += 4
                self.play_sfx("sfx-stab2", 0.70)
                self.log(f"Mirror Shield reflected 4 dmg to {enemy['name']}!", BLUE)

            if enemy:
                self.log(f"{enemy['name']} dealt {actual} dmg.", RED)


    def update_combat_animations(self):

            if self.state != "combat":
                self.combat_anim = None
                self.combat_anim_queue = []
                self.pending_enemy_turn_finish = False
                return

            now = pygame.time.get_ticks()
            # START NEXT HIT
            if (
                self.combat_anim is None
                and self.combat_anim_queue):

                self.combat_anim = (
                    self.combat_anim_queue.pop(0))

                self.combat_anim["started"] = now
                if (
                    self.combat_anim.get(
                        "attacker") == "enemy"
                ):

                    attacking_enemy = (
                        self.combat_anim.get(
                            "enemy")
                    )

                    if attacking_enemy:

                        self.set_enemy_pose(
                            attacking_enemy,
                            "attack",
                            700)

            anim = self.combat_anim

            if anim is None:

                if self.pending_enemy_turn_finish:

                    self.pending_enemy_turn_finish = False

                    self.enemies = [
                        e
                        for e in self.enemies
                        if e["hp"] > 0
                    ]

                    if self.php <= 0:

                        if self.try_revive():

             
                            self.turn += 1

                            self._start_turn()

                            return

                        self.php = 0
                        self.delete_save()
                        self.play_sfx("tuomas_data-wrong-answer-21-199825", 0.80)
                        self.state = "game_over"

                        self.save_run_to_history(
                            "DEFEAT")

                        return

                    if not self.enemies:
                        self._win_combat()
                        return

                    self.turn += 1
                    self._start_turn()

                return

            elapsed = (
                now - anim["started"])

            if (
                elapsed >= 85
                and not anim[
                    "damage_applied"
                ]):

                anim[
                    "damage_applied"
                ] = True

                self._apply_combat_animation_damage(
                    anim)

            if elapsed >= 300:

                self.combat_anim = None

                self.enemies = [
                    e
                    for e in self.enemies
                    if e["hp"] > 0
                ]
                if (
                    not self.enemies
                    and not self.pending_enemy_turn_finish
                    and self.php > 0):
                    self._win_combat()
    # PROGRESSION RELIC HELPERS
    def get_effective_card_cost(self, card_or_name, upgraded=False):

        if hasattr(card_or_name, "name"):
            name = card_or_name.name
            upgraded = getattr(card_or_name, "upgraded", upgraded)
        else:
            name = card_or_name

        d = get_card_data(name, upgraded)

        if not d:
            return 999

        cost = d.get("cost", 0)

        is_blitz_card = (
            "blitz" in d
            or d.get("trigger_blitz")
            or d.get("double_blitz"))

        if (
            is_blitz_card
            and "Capacitor Core"
            in getattr(self, "relics", [])
            and not getattr(self, "capacitor_core_used", False)):
            cost = max(0, cost - 1)

        is_wound_card = (
            "wounds" in d
            or d.get("trigger_wounds")
            or d.get("double_wounds")
            or d.get("draw_per_wound"))

        if (
            is_wound_card
            and "Blood Needle"
            in getattr(self, "relics", [])
            and not getattr(self, "blood_needle_used", )):
            cost = max(0, cost - 1)

        return cost


    def apply_blitz(self, en, amount):

        if amount <= 0:
            return 0

        if (
            "Overcharged Coil"
            in getattr(self, "relics", [])):
            amount += 2

        en["blitz"] = (
            en.get("blitz", 0)
            + amount)

        if (
            en.get("blitz_timer", 0)
            <= 0):
            en["blitz_timer"] = 3

        self.blitz_applied_this_turn = (
            getattr(self, "blitz_applied_this_turn", 0)
            + amount)

        self.log(f"Blitz +{amount} to {en['name']}.", PURPLE_D)

        if (
            "Storm Engine"
            in getattr(self, "relics", [])
            and not getattr(self, "storm_engine_triggered", False)
            and self.blitz_applied_this_turn >= 10):

            self.storm_engine_triggered = True

            self.draw_cards(1)

            self.log("Storm Engine: drew 1 card!", GOLD)

        return amount


    def detonate_blitz(self, en):

        amount = en.get("blitz", 0)

        if amount <= 0:
            return

        original_amount = amount

        if (
            "Thunder Heart"
            in getattr(self, "relics", [])
            and not getattr(self, "thunder_heart_used", False)):

            amount *= 2
            self.thunder_heart_used = True

            self.log("Thunder Heart doubled the Blitz detonation!", GOLD)

        en["hp"] -= amount
        self.play_sfx("sfx-stab2", 0.70)
        self.combat_dmg_dealt += amount

        self.log(f"Blitz detonated on {en['name']}! {amount} dmg.", PURPLE_D)

        if (
            "Static Shield"
            in getattr(self, "relics", [])):

            self.pblock += 4

            self.log("Static Shield: +4 Block.", BLUE)

        if (
            "Chain Reactor"
            in getattr(self, "relics", [])):

            other_enemies = [
                other
                for other in self.enemies
                if (
                    other is not en
                    and other.get("hp", 0) > 0)
            ]

            if other_enemies:

                other = random.choice(
                    other_enemies)

                spread = max(1, original_amount // 2)

                self.apply_blitz(other, spread)

                self.log(f"Chain Reactor spread {spread} Blitz to {other['name']}.", PURPLE_D)

        en["blitz"] = 0
        en["blitz_timer"] = 0


    def apply_wounds(self, en, amount):

        if amount <= 0:
            return 0

        if (
            "Serrated Ring"
            in getattr(self, "relics", [])):
            amount += 1

        if (
            "Crimson Edge"
            in getattr(self, "relics", [])):
            amount += 2

        en["wounds"] = (
            en.get("wounds", 0)
            + amount)

        self.log(f"Wounds +{amount} to {en['name']}.", RED)

        return amount


    def trigger_wounds(self, en):

        wounds = en.get("wounds", 0)

        if wounds <= 0:
            return

        damage = wounds

        if (
            "Executioner's Mark"
            in getattr(self, "relics", [])
            and not getattr(self, "execution_mark_used", False)
        ):

            damage *= 2
            self.execution_mark_used = True

            self.log("Executioner's Mark doubled the Wound trigger!", GOLD)

        en["hp"] -= damage
        self.play_sfx("sfx-stab2", 0.70)
        en["wounds"] = max(0, wounds - 1)

        self.combat_dmg_dealt += damage

        self.log(f"Wounds triggered for {damage} dmg on {en['name']}!", RED)

        if (
            "Open Vein"
            in getattr(self, "relics", [])):

            self.pblock += 4

            self.log("Open Vein: +4 Block.", BLUE)




    def play_card(
        self,
        card,
        target_enemy=None):

        if (
            self.combat_animation_busy()
            or self.card_animation_busy()):
            return

        if card not in self.hand:
            return

        if not tutorial.can_play_card(self, card):
            return

        d = get_card_data(card.name, card.upgraded)

        if not d:
            return

        actual_cost = (
            self.get_effective_card_cost(
                card)
        )

        if actual_cost > self.mana:
            return
        # PLAYER CARD REACTION i SFX
        is_franziska = (
            str(
                getattr(self, "char_class", "BRUISER")
            ).upper()
            == "ASSASSIN")


        if d.get("type") == "attack":

            self.phoenix_combat_pose = (
                "attack")

            # Franziska attack / whip
            if is_franziska:

                self.play_sfx("sfx-whip", 0.75)


        else:

            self.phoenix_combat_pose = (
                "special")

            # Franziska Skill / Power
            if is_franziska:

                self.play_sfx("sfx-fwasshing", 0.70)
            # Phoenix Skill / Power
            else:

                self.play_sfx("sfx-saveblip", 0.70)


        self.phoenix_combat_pose_until = (
            pygame.time.get_ticks()
            + 1100)
        # CARD TYPE FLAGS
        is_blitz_card = (
            "blitz" in d
            or d.get("trigger_blitz")
            or d.get("double_blitz"))

        is_wound_card = (
            "wounds" in d
            or d.get("trigger_wounds")
            or d.get("double_wounds")
            or d.get("draw_per_wound"))
        # PAY MANA
        self.mana -= actual_cost

        if (
            is_blitz_card
            and "Capacitor Core"
            in getattr(self, "relics", [])
            and not getattr(self, "capacitor_core_used", False)
        ):
            self.capacitor_core_used = True

        if (
            is_wound_card
            and "Blood Needle"
            in getattr(self, "relics", [])
            and not getattr(self, "blood_needle_used", False)
        ):
            self.blood_needle_used = True
        # BLOODLETTER
        if is_wound_card:

            self.wound_cards_this_turn = (
                getattr(self, "wound_cards_this_turn", 0)
                + 1)

            if (
                "Bloodletter"
                in getattr(self, "relics", [])
                and not getattr(self, "bloodletter_triggered", False)
                and self.wound_cards_this_turn >= 3):

                self.bloodletter_triggered = True

                self.draw_cards(1)

                self.log("Bloodletter: drew 1 card!", RED)
        # DISCARD ANIMATION
        start_x = getattr(card, "x", W // 2)

        start_y = getattr(card, "y", H - CH - 15)

        self.hand.remove(
            card)

        self.queue_discard_card(
            card,
            start_x,
            start_y)
        # ATTACK HEAL RELICS
        if d.get("type") == "attack":

            if (
                "Vampire Cloak"
                in getattr(self, "relics", [])):

                old_hp = self.php

                self.php = min(self.pmx, self.php + 1)

                if self.php > old_hp:
                    self.log("Vampire Cloak healed 1 HP.", GREEN)

            if (
                "Vampire Fangs"
                in getattr(self, "relics", [])):

                old_hp = self.php

                self.php = min(self.pmx, self.php + 2)

                if self.php > old_hp:
                    self.log("Vampire Fangs healed 2 HP.", GREEN)
        # PLAYER EFFECTS
        block = d.get("block", 0)

        if block > 0:

            self.pblock += block

            self.log(f"{card.name}: gained {block} block.", BLUE)

            self.history_record_step(
                actor="player",
                source="Player",
                action=card.name,
                target="Player",
                kind="block",
                value=block)

        if d.get(
            "wounds_retaliation"):

            self.barbed_wounds = max(
                getattr(self, "barbed_wounds", 0),
                d["wounds_retaliation"])
        # WOUND COMBO
        wound_value = d.get("wounds", 0)

        wound_combo_damage = 0

        if wound_value > 0:

            effective_wounds = wound_value

            if (
                "Serrated Ring"
                in getattr(self, "relics", [])):
                effective_wounds += 1

            if (
                "Crimson Edge"
                in getattr(self, "relics", [])):
                effective_wounds += 2

            wound_combo_damage = (
                effective_wounds
                + getattr(self, "pwounds_combo", 0)
            )

            self.pwounds_combo += (
                effective_wounds)

        base_dmg = d.get("dmg", 0)
        if wound_value > 0:
            base_dmg += (
                wound_combo_damage)

        times = d.get("times", 1)

        target_all = d.get("target_all", False)
        # TARGET EFFECTS
        def hit_enemy(en):

            if (
                en is None
                or en.get("hp", 0) <= 0):
                return
            # DAMAGE
            if base_dmg > 0:

                for _ in range(times):

                    raw = (
                        base_dmg
                        + self.pstr
                        + self.ptmp_str)

                    if (
                        getattr(self, "pweak", 0) > 0
                    ):
                        raw = int(
                            raw * 0.75)

                    if (
                        en.get("vuln", 0) > 0
                    ):
                        raw = int(
                            raw * 1.5)

                    self.queue_combat_hit(
                        attacker="player",
                        target="enemy",
                        raw_damage=raw,
                        enemy=en,
                        action=card.name)
            # DEBUFFS
            if "vuln" in d:

                en["vuln"] = (
                    en.get("vuln", 0)
                    + d["vuln"])

                self.log(f"Vuln +{d['vuln']} to {en['name']}.", ORANGE)

            if "weak" in d:

                en["weak"] = (
                    en.get("weak", 0)
                    + d["weak"])

                self.log(f"Weak +{d['weak']} to {en['name']}.", ORANGE)
            # BLITZ
            if "blitz" in d:

                self.apply_blitz(en, d["blitz"])

            if (
                d.get("trigger_blitz")
                and en.get("blitz", 0) > 0):

                self.detonate_blitz(
                    en)

            if (
                d.get("double_blitz")
                and en.get("blitz", 0) > 0):

                en["blitz"] *= 2

                self.log(f"Blitz doubled on {en['name']}!", PURPLE_D)
            # WOUNDS
            if "wounds" in d:

                self.apply_wounds(en, d["wounds"])

            if (
                d.get("trigger_wounds")
                and en.get("wounds", 0) > 0):

                self.trigger_wounds(
                    en)

            if (
                d.get("double_wounds")
                and en.get("wounds", 0) > 0):

                en["wounds"] *= 2

                self.log(f"Wounds doubled on {en['name']}!", RED)

            if (
                d.get("draw_per_wound")
                and en.get("wounds", 0) > 0):

                amount = (
                    en["wounds"]
                    * d.get("draw_per_wound", 1)
                )

                amount = min(
                    amount,
                    d.get("max_draw", amount)
                )

                self.draw_cards(
                    amount)

                self.log(
                    f"Blood Scent drew {amount} card(s).",
                    GREEN)
        # APPLY TO TARGET
        if target_all:

            for en in list(
                self.enemies):
                hit_enemy(en)

        elif target_enemy:

            hit_enemy(
                target_enemy)

        elif self.enemies:

            hit_enemy(
                self.enemies[0])
        # PLAYER BUFFS
        if "str" in d:

            self.pstr += d["str"]

            self.log(f"+{d['str']} Str perm.", ORANGE)

        if "tmp_str" in d:

            self.ptmp_str += d[
                "tmp_str"
            ]

            self.log(f"+{d['tmp_str']} Str temp.", ORANGE)

        if "draw" in d:

            self.draw_cards(
                d["draw"])

        self.enemies = [
            e
            for e in self.enemies
            if e.get("hp", 0) > 0
        ]

        if (
            not self.enemies
            and not self.combat_animation_busy()
            and self.state == "combat"):

            self._win_combat()
            return

        tutorial.on_card_played(self, card)


    def end_turn(self):

        if (
            self.card_animation_busy()
            or self.combat_animation_busy()):
            return

        if not tutorial.can_end_turn(self):
            return

        tutorial.on_end_turn(self)
        # FREEZE CURRENT HAND POSITIONS
        positions = self.hand_positions()

        cards_to_discard = list(
            self.hand)

        self.end_turn_discard_positions = {}

        for i, card in enumerate(
            cards_to_discard):

            if i < len(positions):
                start_x, start_y = (
                    positions[i])
            else:
                start_x = W // 2
                start_y = H - CH - 15

            self.end_turn_discard_positions[
                id(card)
            ] = (
                start_x,
                start_y)

            self.queue_discard_card(
                card,
                start_x,
                start_y)


        if cards_to_discard:

            self.pending_end_turn_after_discard = True
            return

        self._continue_end_turn()

    def _continue_end_turn(self):

        if (
            self.php <= 0
            or len(self.enemies) <= 0):
            return

        # PLAYER DEBUFF DURATIONS
        if getattr(self, "pweak", 0) > 0:
            self.pweak -= 1

        if getattr(self, "pvuln", 0) > 0:
            self.pvuln -= 1

        self._enemy_turn()
        self.enemies = [
            e for e in self.enemies
            if e["hp"] > 0
        ]

        if self.state != "combat":
            return

        if not self.enemies:
            self._win_combat()
            return

        if self.combat_animation_busy():
            self.pending_enemy_turn_finish = True
            return

        if self.php > 0:
            self.turn += 1
            self._start_turn()
    def set_enemy_pose(
        self,
        enemy,
        pose,
        duration=900):

        if not enemy:
            return

        enemy["sprite_pose"] = (
            pose)

        enemy["sprite_pose_until"] = (
            pygame.time.get_ticks()
            + duration)
    def _enemy_turn(self):
        for en in list(self.enemies):
            en["block"] = 0 
            
            if en.get("blitz", 0) > 0:

                en["blitz_timer"] -= 1

                if en["blitz_timer"] <= 0:

                    self.detonate_blitz(
                        en)

                    if en["hp"] <= 0:
                        continue

            pattern  = en["pattern"]
            move_key = pattern[en["move_i"] % len(pattern)]
            kind, v1, v2 = en["moves"][move_key]
            en["move_i"] += 1
            if kind in (
                "blk",
                "buff",
                "weak_player",
                "vuln_player",
                "heal"):
                self.play_sfx("sfx-guilty", 0.70)
                self.set_enemy_pose(
                    en,
                    "special",
                    1000)
            if kind == "atk":

                raw = (
                    v1
                    + en.get("str", 0)
                )

                if en.get("weak", 0) > 0:

                    raw = int(
                        raw * 0.75)

                if self.pvuln > 0:

                    raw = int(
                        raw * 1.5)

                self.queue_combat_hit(
                    attacker="enemy",
                    target="player",
                    raw_damage=raw,
                    enemy=en,
                    action=move_key)
            elif kind == "blk":
                en["block"] += v2
                self.log(f"{en['name']} gained {v2} block.", BLUE)
            elif kind == "buff":
                en["str"] += v2
                self.log(f"{en['name']} gained +{v2} Strength.", GREEN)
            elif kind == "weak_player":
                self.pweak += v1
                self.log(f"{en['name']} applied {v1} Weak.", ORANGE)
            elif kind == "vuln_player":
                self.pvuln += v1
                self.log(f"{en['name']} applied {v1} Vulnerable.", ORANGE)
            elif kind == "heal":
                old_hp = en["hp"]
                en["hp"] = min(en["max_hp"], en["hp"] + v1)

                healed = en["hp"] - old_hp
                self.log(f"{en['name']} healed {healed} HP.", GREEN)
            elif kind == "atk_multi":

                hits = max(1, v2)

                for _ in range(hits):

                    raw = (
                        v1
                        + en.get("str", 0)
                    )

                    if en.get("weak", 0) > 0:
                        raw = int(
                            raw * 0.75)

                    if self.pvuln > 0:
                        raw = int(
                            raw * 1.5)

                    self.queue_combat_hit(
                        attacker="enemy",
                        target="player",
                        raw_damage=raw,
                        enemy=en)

            if en["weak"] > 0: en["weak"] -= 1
            if en["vuln"] > 0: en["vuln"] -= 1

            if self.php <= 0:
                if self.try_revive():
                    return
                self.php = 0
                self.delete_save()

                self.state = "game_over"
                self.save_run_to_history("DEFEAT")
                return

        self.enemies = [e for e in self.enemies if e["hp"] > 0]


    def _win_combat(self):
        from config import RELICS
        self.log("Won combat!", GOLD)
        if tutorial.handle_combat_win(self):
            return
        self.history_finish_encounter(
            "VICTORY")
        if "Bloody Tooth" in getattr(self, "relics", []):
            self.php = min(self.pmx, self.php + 2)
            self.log("Bloody Tooth healed 2 HP!", GREEN)
        node_type = self.current_node.get("type") if self.current_node else "enemy"
        if node_type == "enemy":

            self.normal_enemy_fights = getattr(self, "normal_enemy_fights", 0) + 1
        if node_type == "enemy":
            gold_won = random.randint(10, 20)
        elif node_type == "elite":
            gold_won = random.randint(25, 35)
        else: 
            gold_won = random.randint(50, 80)
        self.reward_gold = gold_won
        self.reward_gold_bonus = 0

        if "Golden Idol" in getattr(self, "relics", []):
            boosted_gold = int(
                gold_won * 1.5)

            self.reward_gold_bonus = (
                boosted_gold - gold_won)

            self.reward_gold = boosted_gold

        self.reward_gold_claimed = False
        available_relics = [
            r
            for r in RELICS.keys()
            if (
                r not in getattr(self, "relics", [])
                and r not in RELIC_RANDOM_BLACKLIST
                and self.is_relic_unlocked(
                    r)
            )
        ]
        if available_relics and node_type == "elite":
            self.reward_relic = random.choice(available_relics)
        else:
            self.reward_relic = None
        self.reward_relic_claimed = False
        self.pstr = 0
        self.ptmp_str = 0
        self.pweak = 0
        self.pvuln = 0

        if self.floor == len(self.map_data) - 1:

            old_level, new_level = (
                self.record_class_victory())

            self.last_victory_old_level = (
                old_level)

            self.last_victory_new_level = (
                new_level)

            self.did_level_up = (
                new_level > old_level)

            self.delete_save()

            self.save_run_to_history(
                "VICTORY")
            self.play_sfx("freesound_community-success-fanfare-trumpets-6185", 0.85)
            if self.did_level_up:
                self.state = "level_up"
            else:
                self.state = "win"

            return

        # CARD REWARD GENERATION
        rarity = "common"

        if self.current_node:
            enemy_data = self.current_node.get("enemy")

            rarity = "common"

            if self.current_node:

                rarity = str(
                    self.current_node.get("reward_rarity", "Common")
                ).lower()

        if rarity not in (
            "common",
            "rare",
            "epic",
            "legendary"):
            rarity = "common"
        # CLASS FILTER
        player_class = str(
            getattr(self, "char_class", "")).lower()

        valid_cards = [
            name
            for name in CARDS.keys()
            if (
                name not in (
                    "Strike",
                    "Defend")
                and self.is_card_unlocked(
                    name)
            )
        ]

        same_rarity = [
            name
            for name in valid_cards
            if CARDS[name].get("rarity", "common").lower() == rarity
        ]

        reward_cards = []

        if same_rarity:
            take_count = min(
                3,
                len(same_rarity))

            reward_cards.extend(
                random.sample(same_rarity, take_count)
            )
        if len(reward_cards) < 3:

            remaining = [
                name
                for name in valid_cards
                if name not in reward_cards
            ]

            random.shuffle(remaining)

            reward_cards.extend(
                remaining[
                    :3 - len(reward_cards)
                ])


        self.reward_pool = reward_cards
        if self.run_history_events:

            entry = self.run_history_events[-1]

            entry["reward_options"] = list(
                self.reward_pool)

            entry["minigame"] = (
                self.current_node.get("minigame", "None")
                if self.current_node
                else "None")

        print(
            "REWARD DEBUG |",
            "class =", player_class,
            "| rarity =", rarity,
            "| pool =", self.reward_pool)

        en_list = self.current_node.get("enemy", []) if self.current_node else []
        en_names = ", ".join([e["name"] for e in en_list]) if isinstance(en_list, list) else str(en_list)

        self.current_run_log.append({
            "floor": self.floor + 1,
            "enemy": en_names,
            "dmg_dealt": getattr(self, "combat_dmg_dealt", 0),
            "dmg_taken": getattr(self, "combat_dmg_taken", 0),
            "minigame": self.current_node.get("minigame", "None") if self.current_node else "None",
            "reward_pool": list(self.reward_pool),
            "chosen_reward": None
        })
        self.pwounds_combo = 0
        self.barbed_wounds = 0


        self.state = "reward"

    def take_reward(self, name):

        self.deck.append(
            Card(name))

        self.history_add_cards(
            [name])
        if self.run_history_events:

            entry = self.run_history_events[-1]

            entry["reward_choice"] = name

        self.log(f"Added {name} to deck.", GOLD)

        self.state = "map"

        if self.current_run_log:
            last_log = self.current_run_log[-1]

            if isinstance(last_log, dict):
                last_log[
                    "chosen_reward"
                ] = name

    def skip_reward(self):

        if self.run_history_events:

            entry = self.run_history_events[-1]

            entry["reward_choice"] = "SKIPPED"
            if entry.get(
                "minigame_status") != "PLAYED":

                entry[
                    "minigame_status"
                ] = "SKIPPED"

        self.log("Skipped minigame/reward.", GRAY)

        self.state = "map"

        if (
            self.current_run_log
            and isinstance(self.current_run_log[-1], dict)
        ):
            self.current_run_log[-1][
                "chosen_reward"
            ] = "Skipped"
    
    def cf_do_rest(self):

        heal_amount = int(
            self.pmx * 0.30)

        old_hp = self.php

        self.php = min(self.pmx, self.php + heal_amount)

        actual_heal = (
            self.php - old_hp)

        self.log(f"Rested at Campfire. Healed {actual_heal} HP.", GREEN)

        self._leave_campfire()
    def cf_do_upgrade(self):

        if "Molten Hammer" in getattr(self, "relics", []):
            self.log("Molten Hammer prevents Campfire upgrades!", RED)
            return

        upgradeable = [
            card
            for card in self.deck
            if not card.upgraded
            and card.name in CARD_UPGRADES
        ]

        if not upgradeable:
            self.log("No cards available to upgrade.", GRAY)
            return

        self.upgrade_selected_card = None
        self.upgrade_scroll = 0

        self.state = "campfire_upgrade"

    def confirm_campfire_upgrade(self):

        card = getattr(self, "upgrade_selected_card", None)

        if card is None:
            return

        if card.upgraded:
            return

        if card.name not in CARD_UPGRADES:
            return


        card.do_upgrade()

        self.log(f"Upgraded {card.name}!", GREEN)
        if "Heavy Anvil" in getattr(self, "relics", []):

            healed = min(10, self.pmx - self.php)
            self.php = min(self.pmx, self.php + 10)
            self.log(f"Heavy Anvil healed {healed} HP.", GREEN)


        self.upgrade_selected_card = None

        self._leave_campfire()


    def _leave_campfire(self):
        self.state = "map"
    def enter_shop(self):

        if (
            getattr(self, "tutorial_active", False)
            and getattr(self, "tutorial_room", "") == "runner_complete"):
            tutorial.setup_shop(self)
            return

        self.shop_cards = []
        valid_cards = [
            name
            for name in CARDS.keys()
            if (
                name not in (
                    "Strike",
                    "Defend")
                and self.is_card_unlocked(
                    name)
            )
        ]
        
            
        chosen = random.sample(valid_cards, min(4, len(valid_cards)))
        
        for name in chosen:
            rarity = CARDS[name].get("rarity", "common")
            base_price = {"common": 45, "rare": 75, "epic": 110, "legendary": 160}.get(rarity, 50)
            price = int(base_price * random.uniform(0.9, 1.1))
            if "Greed Goblet" in getattr(self, 'relics', []):
                price = int(price * 0.6)
            self.shop_cards.append({
                "name": name,
                "price": price,
                "bought": False
            })
        
        available_relics = [
            r
            for r in RELICS.keys()
            if (
                r not in getattr(self, "relics", [])
                and r not in RELIC_RANDOM_BLACKLIST
                and self.is_relic_unlocked(
                    r)
            )
        ]
        chosen_relics = random.sample(available_relics, min(3, len(available_relics)))
        self.shop_relics = []
        for r_name in chosen_relics:
            price = random.randint(140, 180)

            if "Greed Goblet" in getattr(self, "relics", []):
                price = int(price * 0.6)

            self.shop_relics.append({
                "name": r_name,
                "price": price,
                "bought": False
            })
        
        self.btn_leave_shop = Btn("LEAVE SHOP", W // 2 - 80, H - 55, 160, 40, GRAY)
        self.state = "shop"

    def start_combat(self, enemy):
        self.start_combat_with_node({"enemy": [enemy]})

    def try_revive(self):

        if (
            "Second Chance"
            not in getattr(self, "relics", [])):
            return False

        if getattr(self, "second_chance_used", False):
            return False

        self.second_chance_used = True

        self.php = max(1, self.pmx // 2)

        self.log("Second Chance revived you at 50% HP!", GREEN)

        return True

    def intent_label(self):

        if not self.enemies:
            return ""

        en = self.enemies[0]

        pattern = en["pattern"]

        move_key = pattern[
            en["move_i"] % len(pattern)
        ]

        kind, v1, v2 = en["moves"][
            move_key
        ]

        if kind == "atk":

            raw = (
                v1
                + en.get("str", 0)
            )

            if en.get("weak", 0) > 0:

                raw = int(
                    raw * 0.75)

            return f"Attack {raw}"

        elif kind == "atk_multi":

            raw = (
                v1
                + en.get("str", 0)
            )

            if en.get("weak", 0) > 0:

                raw = int(
                    raw * 0.75)

            return (
                f"Attack {raw} x{v2}")

        elif kind == "blk":
            return f"Block {v2}"

        elif kind == "buff":
            return f"Buff +{v2} Str"

        elif kind == "weak_player":
            return f"Apply {v1} Weak"

        elif kind == "vuln_player":
            return (
                f"Apply {v1} Vulnerable")

        elif kind == "heal":
            return f"Heal {v1}"

        return ""
    # NEW RUN HISTORY 
    def history_start_encounter(
        self,
        node,
        enemies,
        allow_replay=True):

        if getattr(self, "tutorial_active", False):
            return

        if not hasattr(self, "run_history_events"):
            self.run_history_events = []

        names = []

        for en in enemies:

            if isinstance(en, dict):
                names.append(
                    en.get("name", "Enemy")
                )

        enemy_name = (
            ", ".join(names)
            if names
            else "Enemy")

        entry = {
            "floor": getattr(self, "floor", 0) + 1,

            "act": getattr(self, "act", 1),

            "node_type": node.get("type", "enemy"),

            "enemy": enemy_name,

            "minigame": node.get("minigame", "None"),

            "result": "IN PROGRESS",

            "dmg_dealt": 0,
            "dmg_taken": 0,

            "reward_options": [],
            "reward_choice": None,

            "minigame_status": "NOT PLAYED",

            "cards": []
        }

        self.run_history_events.append(
            entry)

        self.active_history_index = (
            len(
                self.run_history_events) - 1
        )


    def history_record_step(
        self,
        actor,
        action,
        target="",
        kind="action",
        value=0,
        detail="",
        source=""):
        return
        return

        index = getattr(self, "active_history_index", None)

        if index is None:
            return

        if not (
            0 <= index
            < len(
                getattr(self, "run_history_events", [])
            )):
            return

        entry = self.run_history_events[
            index
        ]
        if entry.get(
            "minigame") in (
            "BoxingBoss",
            "UndertaleBoss"):
            return




    def history_finish_encounter(self, result):

        index = getattr(self, "active_history_index", None)

        if index is None:
            return

        if not (
            0 <= index
            < len(
                getattr(self, "run_history_events", [])
            )):
            return

        entry = self.run_history_events[
            index
        ]

        entry["result"] = result

        entry["dmg_dealt"] = getattr(self, "combat_dmg_dealt", 0)

        entry["dmg_taken"] = getattr(self, "combat_dmg_taken", 0)

        self.active_history_index = None


    def history_add_cards(self, cards):

        if not cards:
            return

        if not getattr(self, "run_history_events", []):
            return

        entry = self.run_history_events[-1]

        if isinstance(cards, str):
            cards = [cards]

        for card in cards:

            if card not in entry["cards"]:
                entry["cards"].append(
                    card)

    def save_run_to_history(self, result):

        history_file = (
            f"history_slot_"
            f"{self.current_slot}.json")

        history = []

        if os.path.exists(
            history_file):

            try:

                with open(
                    history_file,
                    "r",
                    encoding="utf-8") as f:

                    history = json.load(f)

            except:
                history = []

        run_entry = {
            "version": 3,

            "result": result,

            "character": getattr(self, "char_class", "Bruiser"),

            "floors": getattr(self, "floor", 0) + 1,

            "acts": getattr(self, "act", 1),
            # FINAL BUILD
            "final_deck": [
                {
                    "name": card.name,
                    "upgraded": getattr(card, "upgraded", False)
                }
                for card in getattr(self, "deck", [])
            ],

            "relics": list(
                getattr(self, "relics", [])
            ),

            "path": list(
                getattr(self, "run_history_events", [])
            )
        }

        history.insert(0, run_entry)

        history = history[:15]

        with open(
            history_file,
            "w",
            encoding="utf-8") as f:

            json.dump(
                history,
                f,
                ensure_ascii=False,
                indent=2)

    def get_history(self):
        history_file = f"history_slot_{self.current_slot}.json"
        if os.path.exists(history_file):
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return []
    def add_log(self, text):
        if not hasattr(self, 'current_run_log'):
            self.current_run_log = []
        self.current_run_log.append(text)

    
    def log(self, msg, col):
        self.log_msgs.insert(0, (msg, col))
        if len(self.log_msgs) > 20: self.log_msgs.pop()