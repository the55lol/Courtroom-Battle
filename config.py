import pygame

pygame.init()
W, H = 1024, 768
CW, CH = 140, 200  

HUD_HEIGHT = 32
F_BIG  = pygame.font.SysFont("Georgia", 28, bold=True)
F_MED  = pygame.font.SysFont("Georgia", 19)
F_MED   = pygame.font.SysFont("Georgia", 14)
F_MED = pygame.font.SysFont("Georgia", 12)
F_TINY_BOLD = pygame.font.SysFont("Georgia", 12, bold=True)
F_SML       = pygame.font.SysFont("Georgia", 16)

BG       = (18, 14, 28)
PANEL    = (30, 24, 48)
BORDER   = (80, 60, 110)
GOLD     = (210, 170, 60)
RED      = (190, 55, 55)
RED_D    = (110, 25, 25)
GREEN    = (55, 175, 85)
GREEN_D  = (25, 100, 45)
BLUE     = (55, 115, 205)
BLUE_D   = (25, 55, 125)
PURPLE   = (130, 55, 195)
PURPLE_D = (70, 25, 110)
WHITE    = (235, 225, 215)
GRAY     = (95, 85, 115)
GRAY_L   = (155, 145, 165)
ORANGE   = (215, 135, 35)
C_COMMON    = (150, 150, 150)  # Сив
C_RARE      = (55, 115, 205)   # Син
C_EPIC      = (150, 50, 200)   # Лилав
C_LEGENDARY = (255, 140, 0)

CARDS = {
    #  COMMON
    "Strike": {"cost": 1, "type": "attack", "desc": "Deal 6 dmg.", "dmg": 6, "block": 0, "rarity": "common"},
    "Defend": {"cost": 1, "type": "skill", "desc": "Gain 5 block.", "dmg": 0, "block": 5, "rarity": "common"},
    "Pommel": {"cost": 1, "type": "attack", "desc": "Deal 9 dmg.", "dmg": 9, "block": 0, "rarity": "common"},
    "Shrug": {"cost": 1, "type": "skill", "desc": "Gain 8 block.", "dmg": 0, "block": 8, "rarity": "common","class": "Bruiser"},
    "Iron Wave": {"cost": 1, "type": "attack", "desc": "Deal 5 dmg.\nGain 5 block.", "dmg": 5, "block": 5, "rarity": "common"},
    "Clash": {"cost": 0, "type": "attack", "desc": "Deal 14 dmg.", "dmg": 14, "block": 0, "rarity": "common"},

    # RARE 
    "Bash": {"cost": 2, "type": "attack", "desc": "Deal 8 dmg.\nApply 2 Vulnerable.", "dmg": 8, "block": 0, "vuln": 2, "rarity": "rare","class": "Bruiser"},
    "Thunder": {"cost": 1, "type": "attack", "desc": "Deal 4 dmg.\nApply 1 Vulnerable.", "dmg": 4, "block": 0, "vuln": 1, "rarity": "rare","class": "Bruiser"},
    "Flex": {"cost": 0, "type": "skill", "desc": "Gain 3\nTemp Str.", "dmg": 0, "block": 0, "tmp_str": 3, "rarity": "rare","class": "Bruiser"},
    "Ghost Armor": {"cost": 1, "type": "skill", "desc": "Gain 10 block.", "dmg": 0, "block": 10, "rarity": "rare","class": "Bruiser"},
    "Clothesline": {"cost": 2, "type": "attack", "desc": "Deal 12 dmg.\nApply 2 Weak.", "dmg": 12, "block": 0, "weak": 2, "rarity": "rare","class": "Bruiser"},

    #  EPIC
    "Uppercut": {"cost": 2, "type": "attack", "desc": "Deal 5 dmg.\n1 Weak.\n1 Vulnerable.", "dmg": 5, "block": 0, "weak": 1, "vuln": 1, "rarity": "epic","class": "Bruiser"},
    "Carnage": {"cost": 2, "type": "attack", "desc": "Deal 20 dmg.", "dmg": 20, "block": 0, "rarity": "epic","class": "Bruiser"},
    "Inflame": {"cost": 1, "type": "power", "desc": "Gain 2 Str\npermanent.", "dmg": 0, "block": 0, "str": 2, "rarity": "epic","class": "Bruiser"},
    

    # LEGENDARY 
    "Demon Form": {"cost": 3, "type": "power", "desc": "Gain 4 Str\npermanent.", "dmg": 0, "block": 0, "str": 4, "rarity": "legendary","class": "Bruiser"},
    "Bludgeon": {"cost": 3, "type": "attack", "desc": "Deal 32 dmg.", "dmg": 32, "block": 0, "rarity": "legendary","class": "Bruiser"},
    "Barricade": {"cost": 3, "type": "skill", "desc": "Gain 30 block.", "dmg": 0, "block": 30, "rarity": "legendary","class": "Bruiser"},


    # BLITZ КАРТИ 
    "Blitz Strike": {"cost": 1, "type": "attack", "desc": "Deal 5 dmg.\nApply 5 Blitz.", "dmg": 5, "block": 0, "blitz": 5, "rarity": "common","class": "Bruiser"},
    "Patient Spark": {"cost": 0, "type": "skill", "desc": "Apply 6 Blitz.", "dmg": 0, "block": 0, "blitz": 6, "rarity": "common","class": "Bruiser"},
    "Blitz Shield": {"cost": 1, "type": "skill", "desc": "Gain 5 block.\nApply 4 Blitz.", "dmg": 0, "block": 5, "blitz": 4, "rarity": "common","class": "Bruiser"},
    "Quick Blitz": {"cost": 0, "type": "skill", "desc": "Apply 5 Blitz.", "dmg": 0, "block": 0, "blitz": 5, "rarity": "common","class": "Bruiser"},
    "Blitz Wall": {"cost": 2, "type": "skill", "desc": "Gain 7 block.\nApply 15 Blitz.", "dmg": 0, "block": 7, "blitz": 15, "rarity": "rare","class": "Bruiser"},
    "Blitzkrieg": {"cost": 2, "type": "attack", "desc": "Deal 6 dmg.\nApply 12 Blitz.", "dmg": 6, "block": 0, "blitz": 12, "rarity": "epic","class": "Bruiser"},
    "Detonate": {"cost": 1, "type": "skill", "desc": "Trigger Blitz\nimmediately.", "dmg": 0, "block": 0,"blitz": 5, "trigger_blitz": True, "rarity": "legendary","class": "Bruiser"},
    "Catalyst": {"cost": 1, "type": "skill", "desc": "Double the\nenemy's Blitz.", "dmg": 0, "block": 0, "double_blitz": True, "rarity": "rare","class": "Bruiser"},
    "Chain Blitz": {"cost": 1, "type": "attack", "desc": "Deal 3 dmg.\n3 Blitz.\nDraw 1 card.", "dmg": 3, "block": 0, "blitz": 3, "draw": 1, "rarity": "rare","class": "Bruiser"},

    "Cleave": {"cost": 1, "type": "attack", "desc": "Deal 8 dmg to ALL enemies.", "dmg": 8, "block": 0, "target_all": True, "rarity": "common","class": "Bruiser"},
    "Shockwave": {"cost": 2, "type": "skill", "desc": "Apply 3 Weak and\n3 Vulnerable to ALL enemies.", "dmg": 0, "block": 0, "weak": 3, "vuln": 3, "target_all": True, "rarity": "epic","class": "Bruiser"},
    "Whirlwind": {"cost": 2, "type": "attack", "desc": "Deal 5 dmg 3 times\nTo ALL enemies.", "dmg": 5, "times": 3, "block": 0, "target_all": True, "rarity": "common","class": "Bruiser"},

    # BRUISER PROGRESSION CARDS

    # LEVEL 1
    "Static Jab": {
        "cost": 1,
        "type": "attack",
        "desc": "Deal 6 dmg.\nApply 4 Blitz.",
        "dmg": 6,
        "block": 0,
        "blitz": 4,
        "rarity": "common",
        "class": "Bruiser",
        "unlock_level": 1
    },

    "Charge Up": {
        "cost": 0,
        "type": "skill",
        "desc": "Apply 5 Blitz.\nDraw 1 card.",
        "dmg": 0,
        "block": 0,
        "blitz": 5,
        "draw": 1,
        "rarity": "rare",
        "class": "Bruiser",
        "unlock_level": 1
    },


    # LEVEL 2
    "Voltage Guard": {
        "cost": 1,
        "type": "skill",
        "desc": "Gain 9 block.\nApply 5 Blitz.",
        "dmg": 0,
        "block": 9,
        "blitz": 5,
        "rarity": "rare",
        "class": "Bruiser",
        "unlock_level": 2
    },

    "Heavy Current": {
        "cost": 2,
        "type": "attack",
        "desc": "Deal 12 dmg.\nApply 8 Blitz.",
        "dmg": 12,
        "block": 0,
        "blitz": 8,
        "rarity": "rare",
        "class": "Bruiser",
        "unlock_level": 2
    },


    # LEVEL 3
    "Feedback Loop": {
        "cost": 1,
        "type": "skill",
        "desc": "Double enemy Blitz.\nDraw 1 card.",
        "dmg": 0,
        "block": 0,
        "double_blitz": True,
        "draw": 1,
        "rarity": "epic",
        "class": "Bruiser",
        "unlock_level": 3
    },


    # LEVEL 4
    "Thunder Verdict": {
        "cost": 2,
        "type": "attack",
        "desc": "Deal 14 dmg.\nApply 12 Blitz.",
        "dmg": 14,
        "block": 0,
        "blitz": 12,
        "rarity": "epic",
        "class": "Bruiser",
        "unlock_level": 4
    },

    "Overload": {
        "cost": 1,
        "type": "skill",
        "desc": "Apply 10 Blitz.\nTrigger Blitz immediately.",
        "dmg": 0,
        "block": 0,
        "blitz": 10,
        "trigger_blitz": True,
        "rarity": "legendary",
        "class": "Bruiser",
        "unlock_level": 4
    },

    "Final Discharge": {
        "cost": 3,
        "type": "attack",
        "desc": "Deal 20 dmg.\nApply 15 Blitz.\nDraw 1 card.",
        "dmg": 20,
        "block": 0,
        "blitz": 15,
        "draw": 1,
        "rarity": "legendary",
        "class": "Bruiser",
        "unlock_level": 4
    },





    
    #ASSASSIN CARDS 

 # COMMON
 "Scratch": {"cost": 1, "type": "attack", "desc": "Deal 3 dmg.\nApply 1 Wound.", "dmg": 3, "block": 0, "wounds": 1, "rarity": "common","class": "Assassin"},
 "Spiked Shield": {"cost": 1, "type": "skill", "desc": "Gain 5 block.\nApply 1 Wound.", "dmg": 0, "block": 5, "wounds": 1, "rarity": "common","class": "Assassin"},
 "Blood Price": {"cost": 0, "type": "skill", "desc": "Apply 1 Wound.", "dmg": 0, "block": 0, "wounds": 1, "rarity": "common","class": "Assassin"},
 "Dodge": {"cost": 1, "type": "skill", "desc": "Gain 6 block.\nApply 1 Weak.", "dmg": 0, "block": 6, "weak": 1, "rarity": "common","class": "Assassin"},
 "Swift Blade": {"cost": 0, "type": "attack", "desc": "Deal 3 dmg.\nDraw 1 card.", "dmg": 3, "block": 0, "draw": 1, "rarity": "common","class": "Assassin"},

 # RARE
 "Barbed Armor": {"cost": 2, "type": "skill", "desc": "Gain 15 block.\nWhen attacked this turn,\napply 1 Wound.", "dmg": 0, "block": 15, "wounds_retaliation": 1, "rarity": "rare","class": "Assassin"},
 "Toxic Flask": {"cost": 1, "type": "skill", "desc": "Apply 4 Wounds.", "dmg": 0, "block": 0, "wounds": 4, "rarity": "rare","class": "Assassin"},
 "Hamstring": {"cost": 2, "type": "attack", "desc": "Deal 7 dmg.\nApply 2 Weak.", "dmg": 7, "block": 0, "weak": 2, "rarity": "rare","class": "Assassin"},
 "Acrobatics": {"cost": 1, "type": "skill", "desc": "Gain 4 block.\nDraw 2 cards.", "dmg": 0, "block": 4, "draw": 2, "rarity": "rare","class": "Assassin"},

 # EPIC
 "Blood Scent": {
    "cost": 1,
    "type": "skill",
    "desc": "Draw up to 3 cards\nbased on enemy Wounds.",
    "dmg": 0,
    "block": 0,
    "draw_per_wound": 1,
    "max_draw": 3,
    "rarity": "epic",
    "class": "Assassin"
},
 "Butcher": {"cost": 2, "type": "attack", "desc": "Deal 5 dmg.\nApply 4 Wounds.", "dmg": 5, "block": 0, "wounds": 4, "rarity": "epic","class": "Assassin"},
 "Crippling Strike": {"cost": 2, "type": "attack", "desc": "Deal 8 dmg.\nApply 2 Wounds\nand 2 Weak.", "dmg": 8, "block": 0, "wounds": 2, "weak": 2, "rarity": "epic","class": "Assassin"},
 "Rupture": {"cost": 1, "type": "skill", "desc": "Trigger Wounds\nimmediately.", "dmg": 0, "block": 0, "trigger_wounds": True, "rarity": "epic","class": "Assassin"},

 # LEGENDARY
 "Contagion": {"cost": 3, "type": "skill", "desc": "Double the\nenemy's Wounds.", "dmg": 0, "block": 0, "double_wounds": True, "rarity": "legendary","class": "Assassin"},
 "Fatal Strike": {"cost": 2, "type": "attack", "desc": "Deal 12 dmg.\nApply 5 Wounds.\nDraw 1 card.", "dmg": 12, "block": 0, "wounds": 5, "draw": 1, "rarity": "legendary","class": "Assassin"},


 "Lacerate": {
        "type": "attack", 
        "cost": 1, 
        "dmg": 4, 
        "wounds": 5, 
        "desc": "Deal 4 dmg.\nApply Wounds 5.", 
        "rarity": "common",
        "class": "Assassin"
    },
    "Cruel Strike": {
        "type": "attack", 
        "cost": 1, 
        "dmg": 6, 
        "weak": 1, 
        "desc": "Deal 6 dmg.\nApply 1 Weak.", 
        "rarity": "common",
        "class": "Assassin"
    },
    # WOUND CARDS
    "Serrated Cut": {
        "cost": 1,
        "type": "attack",
        "desc": "Deal 4 dmg.\nApply 2 Wounds.",
        "dmg": 4,
        "block": 0,
        "wounds": 2,
        "rarity": "common",
        "class": "Assassin"
    },

    "Open Wound": {
        "cost": 0,
        "type": "skill",
        "desc": "Apply 2 Wounds.",
        "dmg": 0,
        "block": 0,
        "wounds": 2,
        "rarity": "rare",
        "class": "Assassin"
    },

    "Deep Cut": {
        "cost": 1,
        "type": "attack",
        "desc": "Deal 6 dmg.\nApply 3 Wounds.",
        "dmg": 6,
        "block": 0,
        "wounds": 3,
        "rarity": "rare",
        "class": "Assassin"
    },

    "Bloodbath": {
        "cost": 2,
        "type": "attack",
        "desc": "Deal 8 dmg.\nApply 6 Wounds.",
        "dmg": 8,
        "block": 0,
        "wounds": 6,
        "rarity": "epic",
        "class": "Assassin"
    },

    # ASSASSIN PROGRESSION CARDS
    # LEVEL 1
    "Needle Cut": {
        "cost": 1,
        "type": "attack",
        "desc": "Deal 5 dmg.\nApply 2 Wounds.",
        "dmg": 5,
        "block": 0,
        "wounds": 2,
        "rarity": "common",
        "class": "Assassin",
        "unlock_level": 1
    },

    "Fresh Blood": {
        "cost": 0,
        "type": "skill",
        "desc": "Apply 2 Wounds.\nDraw 1 card.",
        "dmg": 0,
        "block": 0,
        "wounds": 2,
        "draw": 1,
        "rarity": "rare",
        "class": "Assassin",
        "unlock_level": 1
    },


    # LEVEL 2
    "Surgical Cut": {
        "cost": 1,
        "type": "attack",
        "desc": "Deal 7 dmg.\nApply 3 Wounds.",
        "dmg": 7,
        "block": 0,
        "wounds": 3,
        "rarity": "rare",
        "class": "Assassin",
        "unlock_level": 2
    },

    "Hemorrhage": {
        "cost": 2,
        "type": "skill",
        "desc": "Apply 6 Wounds.\nApply 1 Weak.",
        "dmg": 0,
        "block": 0,
        "wounds": 6,
        "weak": 1,
        "rarity": "rare",
        "class": "Assassin",
        "unlock_level": 2
    },


    # LEVEL 3
    "Blood Echo": {
        "cost": 1,
        "type": "skill",
        "desc": "Trigger enemy Wounds.\nDraw 1 card.",
        "dmg": 0,
        "block": 0,
        "trigger_wounds": True,
        "draw": 1,
        "rarity": "epic",
        "class": "Assassin",
        "unlock_level": 3
    },


    # LEVEL 4
    "Open Artery": {
        "cost": 2,
        "type": "attack",
        "desc": "Deal 12 dmg.\nApply 8 Wounds.",
        "dmg": 12,
        "block": 0,
        "wounds": 8,
        "rarity": "epic",
        "class": "Assassin",
        "unlock_level": 4
    },

    "Chain Rupture": {
        "cost": 2,
        "type": "skill",
        "desc": "Trigger enemy Wounds.\nThen double remaining Wounds.",
        "dmg": 0,
        "block": 0,
        "trigger_wounds": True,
        "double_wounds": True,
        "rarity": "legendary",
        "class": "Assassin",
        "unlock_level": 4
    },

    "Execution Cut": {
        "cost": 3,
        "type": "attack",
        "desc": "Deal 18 dmg.\nApply 10 Wounds.\nDraw 1 card.",
        "dmg": 18,
        "block": 0,
        "wounds": 10,
        "draw": 1,
        "rarity": "legendary",
        "class": "Assassin",
        "unlock_level": 4
    }
}

CARD_UPGRADES = {
    "Strike": {
        "dmg": 9,
        "desc": "Deal 9 dmg."
    },

    "Defend": {
        "block": 8,
        "desc": "Gain 8 block."
    },

    "Pommel": {
        "dmg": 12,
        "desc": "Deal 12 dmg."
    },

    "Shrug": {
        "block": 11,
        "desc": "Gain 11 block."
    },

    "Iron Wave": {
        "dmg": 7,
        "block": 7,
        "desc": "Deal 7 dmg.\nGain 7 block."
    },

    "Clash": {
        "dmg": 18,
        "desc": "Deal 18 dmg."
    },

    "Bash": {
        "dmg": 10,
        "vuln": 3,
        "desc": "Deal 10 dmg.\nApply 3 Vulnerable."
    },

    "Thunder": {
        "dmg": 6,
        "vuln": 2,
        "desc": "Deal 6 dmg.\nApply 2 Vulnerable."
    },

    "Flex": {
        "tmp_str": 5,
        "desc": "Gain 5\nTemp Str."
    },

    "Ghost Armor": {
        "block": 14,
        "desc": "Gain 14 block."
    },

    "Clothesline": {
        "dmg": 15,
        "weak": 3,
        "desc": "Deal 15 dmg.\nApply 3 Weak."
    },

    "Uppercut": {
        "dmg": 8,
        "weak": 2,
        "vuln": 2,
        "desc": "Deal 8 dmg.\n2 Weak.\n2 Vulnerable."
    },

    "Carnage": {
        "dmg": 26,
        "desc": "Deal 26 dmg."
    },

    "Inflame": {
        "str": 3,
        "desc": "Gain 3 Str\npermanent."
    },

    "Demon Form": {
        "cost": 2,
        "desc": "Gain 4 Str\npermanent."
    },

    "Bludgeon": {
        "dmg": 42,
        "desc": "Deal 42 dmg."
    },

    "Barricade": {
        "block": 40,
        "desc": "Gain 40 block."
    },

    "Blitz Strike": {
        "dmg": 7,
        "blitz": 7,
        "desc": "Deal 7 dmg.\nApply 7 Blitz."
    },

    "Patient Spark": {
        "blitz": 8,
        "desc": "Apply 8 Blitz."
    },

    "Blitz Shield": {
        "block": 8,
        "blitz": 6,
        "desc": "Gain 8 block.\nApply 6 Blitz."
    },

    "Quick Blitz": {
        "blitz": 7,
        "desc": "Apply 7 Blitz."
    },

    "Blitz Wall": {
        "block": 10,
        "blitz": 18,
        "desc": "Gain 10 block.\nApply 18 Blitz."
    },

    "Blitzkrieg": {
        "dmg": 9,
        "blitz": 16,
        "desc": "Deal 9 dmg.\nApply 16 Blitz."
    },

    "Detonate": {
        "cost": 0
    },

    "Catalyst": {
        "cost": 0
    },

    "Chain Blitz": {
        "dmg": 5,
        "blitz": 5,
        "desc": "Deal 5 dmg.\n5 Blitz.\nDraw 1 card."
    },

    "Cleave": {
        "dmg": 11,
        "desc": "Deal 11 dmg to ALL enemies."
    },

    "Shockwave": {
        "weak": 4,
        "vuln": 4,
        "desc": "Apply 4 Weak and\n4 Vulnerable to ALL enemies."
    },

    "Whirlwind": {
        "dmg": 7,
        "desc": "Deal 7 dmg 3 times\nTo ALL enemies."
    },
    # ASSASSIN UPGRADES
    "Scratch": {
        "dmg": 5,
        "wounds": 2,
        "desc": "Deal 5 dmg.\nApply 2 Wounds."
    },

    "Spiked Shield": {
        "block": 8,
        "wounds": 2,
        "desc": "Gain 8 block.\nApply 2 Wounds."
    },

    "Blood Price": {
        "wounds": 2,
        "desc": "Apply 2 Wounds."
    },

    "Dodge": {
        "block": 9,
        "weak": 2,
        "desc": "Gain 9 block.\nApply 2 Weak."
    },

    "Swift Blade": {
        "dmg": 5,
        "desc": "Deal 5 dmg.\nDraw 1 card."
    },

    "Barbed Armor": {
        "cost": 1,
        "block": 15,
        "wounds_retaliation": 2,
        "desc": (
            "Gain 15 block.\n"
            "When attacked this turn,\n"
            "apply 2 Wounds."
        )
    },

    "Toxic Flask": {
        "wounds": 6,
        "desc": "Apply 6 Wounds."
    },

    "Hamstring": {
        "dmg": 10,
        "weak": 3,
        "desc": "Deal 10 dmg.\nApply 3 Weak."
    },

    "Acrobatics": {
        "block": 7,
        "draw": 2,
        "desc": "Gain 7 block.\nDraw 2 cards."
    },

    "Blood Scent": {
        "cost": 0,
        "desc": (
            "Draw up to 3 cards\n"
            "based on enemy Wounds."
        )
    },

    "Butcher": {
        "dmg": 7,
        "wounds": 6,
        "desc": "Deal 7 dmg.\nApply 6 Wounds."
    },

    "Crippling Strike": {
        "dmg": 11,
        "wounds": 3,
        "weak": 3,
        "desc": (
            "Deal 11 dmg.\n"
            "Apply 3 Wounds\n"
            "and 3 Weak."
        )
    },

    "Rupture": {
        "cost": 0,
        "desc": "Trigger Wounds\nimmediately."
    },

    "Contagion": {
        "cost": 2,
        "desc": "Double the\nenemy's Wounds."
    },

    "Fatal Strike": {
        "dmg": 16,
        "wounds": 7,
        "desc": (
            "Deal 16 dmg.\n"
            "Apply 7 Wounds.\n"
            "Draw 1 card."
        )
    },

    "Lacerate": {
        "dmg": 6,
        "wounds": 7,
        "desc": "Deal 6 dmg.\nApply Wounds 7."
    },

    "Cruel Strike": {
        "dmg": 9,
        "weak": 2,
        "desc": "Deal 9 dmg.\nApply 2 Weak."
    },
    # NEW WOUND CARD UPGRADES
    "Serrated Cut": {
        "dmg": 6,
        "wounds": 3,
        "desc": "Deal 6 dmg.\nApply 3 Wounds."
    },

    "Open Wound": {
        "wounds": 3,
        "desc": "Apply 3 Wounds."
    },

    "Deep Cut": {
        "dmg": 8,
        "wounds": 4,
        "desc": "Deal 8 dmg.\nApply 4 Wounds."
    },

    "Bloodbath": {
        "dmg": 11,
        "wounds": 8,
        "desc": "Deal 11 dmg.\nApply 8 Wounds."
    },
    # BRUISER PROGRESSION UPGRADES
    "Static Jab": {
        "dmg": 8,
        "blitz": 6,
        "desc": "Deal 8 dmg.\nApply 6 Blitz."
    },

    "Charge Up": {
        "blitz": 7,
        "desc": "Apply 7 Blitz.\nDraw 1 card."
    },

    "Voltage Guard": {
        "block": 12,
        "blitz": 7,
        "desc": "Gain 12 block.\nApply 7 Blitz."
    },

    "Heavy Current": {
        "dmg": 15,
        "blitz": 11,
        "desc": "Deal 15 dmg.\nApply 11 Blitz."
    },

    "Feedback Loop": {
        "cost": 0,
        "desc": "Double enemy Blitz.\nDraw 1 card."
    },

    "Thunder Verdict": {
        "dmg": 18,
        "blitz": 15,
        "desc": "Deal 18 dmg.\nApply 15 Blitz."
    },

    "Overload": {
        "blitz": 13,
        "desc": "Apply 13 Blitz.\nTrigger Blitz immediately."
    },

    "Final Discharge": {
        "cost": 2,
        "dmg": 22,
        "blitz": 18,
        "desc": "Deal 22 dmg.\nApply 18 Blitz.\nDraw 1 card."
    },
    # ASSASSIN PROGRESSION UPGRADES
    "Needle Cut": {
        "dmg": 7,
        "wounds": 3,
        "desc": "Deal 7 dmg.\nApply 3 Wounds."
    },

    "Fresh Blood": {
        "wounds": 3,
        "desc": "Apply 3 Wounds.\nDraw 1 card."
    },

    "Surgical Cut": {
        "dmg": 9,
        "wounds": 4,
        "desc": "Deal 9 dmg.\nApply 4 Wounds."
    },

    "Hemorrhage": {
        "wounds": 8,
        "weak": 2,
        "desc": "Apply 8 Wounds.\nApply 2 Weak."
    },

    "Blood Echo": {
        "cost": 0,
        "desc": "Trigger enemy Wounds.\nDraw 1 card."
    },

    "Open Artery": {
        "dmg": 15,
        "wounds": 10,
        "desc": "Deal 15 dmg.\nApply 10 Wounds."
    },

    "Chain Rupture": {
        "cost": 1,
        "desc": "Trigger enemy Wounds.\nThen double remaining Wounds."
    },

    "Execution Cut": {
        "cost": 2,
        "dmg": 20,
        "wounds": 12,
        "desc": "Deal 20 dmg.\nApply 12 Wounds.\nDraw 1 card."
    },

}

RELICS = {
    "Prophet's Eye": {"desc": "See the enemy's intent 1 turn in advance.", "price": 200},
    "Iron Core":     {"desc": "Start each combat with 4 Block.", "price": 150},
    "Demon Horn":    {"desc": "Start each combat with +1 Strength.", "price": 180},
    "Mana Crystal":  {"desc": "Start each combat with +1 Max Mana.", "price": 250},
    "Prosecutor's Badge": {"desc": "Start each combat with 4 Block and +1 Strength.","class": "Assassin"},
    "Bloody Tooth":  {"desc": "Heal 2 HP at the end of combat.", "price": 160},
    "Ancient Coin":  {"desc": "Gain 50 Gold upon pickup.", "price": 140},
    "Heavy Anvil":   {"desc": "Upgrading cards heals you for 10 HP.", "price": 150},
    "Toxic Gland":   {"desc": "Apply 1 Weak to all enemies at turn 1.", "price": 165},
    "Vampire Cloak": {"desc": "Heal 1 HP whenever you play an Attack card.", "price": 220},
    "Golden Idol": {"desc": "+50% gold from battles."},
    "Vampire Fangs": {"desc": "Whenever you play an attack card, heal 2 HP."},
    "Molten Hammer": {"desc": "+1 Max Mana in a battle,but you can no longer Upgrade in a Campfire"},
    "Mind Glass": {"desc": "You draw an extra card at the start of each turn"},
    "Greed Goblet": {"desc": "Cards in the store are 40% cheaprer"},
    "Arcade Token": {"desc": "In minigames, you need to collect one less piece"},
    "Mirror Shield": {"desc": "Whenever you are blocking, deal 4 damage to the enemy back"},
    "Hourglass of Fate": {"desc": "Every 3 turns in a battle, gain 2 mana and draw 2 extra cards"},
    "Mutated Blood": {"desc": "Gain +2 Strenght at the start of combat, but lose 3 HP."},
    "Second Chance": {
        "desc": "Once per run, when you die, revive at 50% Max HP.",
        "price": 999
    },

    "Perfect Verdict": {
        "desc": "Exact lethal damage heals 15 HP.",
        "price": 999
    },
    # BRUISER PROGRESSION RELICS
    "Overcharged Coil": {
        "desc": "Whenever you apply Blitz, apply 2 additional Blitz.",
        "class": "Bruiser",
        "unlock_level": 1
    },

    "Capacitor Core": {
        "desc": "The first Blitz card played each turn costs 1 less Mana.",
        "class": "Bruiser",
        "unlock_level": 2
    },

    "Static Shield": {
        "desc": "Whenever Blitz detonates, gain 4 Block.",
        "class": "Bruiser",
        "unlock_level": 3
    },

    "Storm Engine": {
        "desc": "After applying 10 or more Blitz in one turn, draw 1 card.",
        "class": "Bruiser",
        "unlock_level": 3
    },


    # LEVEL 5
    "Chain Reactor": {
        "desc": "When Blitz detonates, apply half of its value to another enemy.",
        "class": "Bruiser",
        "unlock_level": 5
    },

    "Thunder Heart": {
        "desc": "The first Blitz detonation each combat deals double damage.",
        "class": "Bruiser",
        "unlock_level": 5
    },

    "Infinite Voltage": {
        "desc": "At the start of each turn, apply 5 Blitz to every enemy.",
        "class": "Bruiser",
        "unlock_level": 5
    },
    # ASSASSIN PROGRESSION RELICS
    "Serrated Ring": {
        "desc": "Whenever you apply Wounds, apply 1 additional Wound.",
        "class": "Assassin",
        "unlock_level": 1
    },

    "Blood Needle": {
        "desc": "The first Wound card played each turn costs 1 less Mana.",
        "class": "Assassin",
        "unlock_level": 2
    },

    "Open Vein": {
        "desc": "Whenever you trigger Wounds, gain 4 Block.",
        "class": "Assassin",
        "unlock_level": 3
    },

    "Bloodletter": {
        "desc": "After playing 3 Wound cards in one turn, draw 1 card.",
        "class": "Assassin",
        "unlock_level": 3
    },


    # LEVEL 5 
    "Crimson Edge": {
        "desc": "Whenever you apply Wounds, apply 2 additional Wounds.",
        "class": "Assassin",
        "unlock_level": 5
    },

    "Executioner's Mark": {
        "desc": "The first Wound trigger each combat deals double damage.",
        "class": "Assassin",
        "unlock_level": 5
    },

    "Blood Moon": {
        "desc": "At the start of each turn, apply 2 Wounds to every enemy.",
        "class": "Assassin",
        "unlock_level": 5
    }

}

EASY_ENEMIES = [
    [{
        "name": "Larry Butz",
        "hp": 28,
        "pattern": ["Wild Swing", "Brace", "Wild Swing", "Get Fired Up"],
        "moves": {
            "Wild Swing": ("atk", 5, 0),
            "Brace": ("blk", 0, 5),
            "Get Fired Up": ("buff", 0, 1),
        }
    }],

    [{
        "name": "Yanni Yogi",
        "hp": 30,
        "pattern": ["Rambling Testimony", "Security Bash", "Catch Breath"],
        "moves": {
            "Rambling Testimony": ("weak_player", 1, 0),
            "Security Bash": ("atk", 5, 0),
            "Catch Breath": ("blk", 0, 5),
        }
    }],

    [{
        "name": "Cody Hackins",
        "hp": 26,
        "pattern": ["Snapshot", "Hide", "Snapshot"],
        "moves": {
            "Snapshot": ("atk", 5, 0),
            "Hide": ("blk", 0, 5),
        }
    }],

    [{
        "name": "Penny Nichols",
        "hp": 25,
        "pattern": ["Nervous Hit", "Hide Away", "Nervous Hit"],
        "moves": {
            "Nervous Hit": ("atk", 4, 0),
            "Hide Away": ("blk", 0, 6),
        }
    }],
]


ENEMIES = [
    # SINGLE ENCOUNTERS

    [{
        "name": "Ini Miney",
        "hp": 45,
        "pattern": ["Steel Samurai Strike", "Guard Pose", "Heavy Swing"],
        "moves": {
            "Steel Samurai Strike": ("atk", 7, 0),
            "Guard Pose": ("blk", 0, 8),
            "Heavy Swing": ("atk", 11, 0),
        }
    }],

    [{
        "name": "Maggey Byrde",
        "hp": 42,
        "pattern": ["Sweet Talk", "Cheap Shot", "Play Innocent", "Cheap Shot"],
        "moves": {
            "Sweet Talk": ("vuln_player", 1, 0),
            "Cheap Shot": ("atk", 8, 0),
            "Play Innocent": ("blk", 0, 7),
        }
    }],

    [{
        "name": "Lotta Hart",
        "hp": 46,
        "pattern": ["Photo Barrage", "Duck Behind Camera", "Snapshot"],
        "moves": {
            "Photo Barrage": ("atk_multi", 3, 2),
            "Duck Behind Camera": ("blk", 0, 7),
            "Snapshot": ("atk", 8, 0),
        }
    }],

    [{
        "name": "Moe",
        "hp": 50,
        "pattern": ["Bad Joke", "Malpractice", "Hide Behind Props"],
        "moves": {
            "Bad Joke": ("weak_player", 1, 0),
            "Malpractice": ("atk", 9, 0),
            "Hide Behind Props": ("blk", 0, 8),
        }
    }],

    [{
        "name": "Adrian Andrews",
        "hp": 52,
        "pattern": ["Composed Defense", "Sharp Reply", "Regain Composure"],
        "moves": {
            "Composed Defense": ("blk", 0, 10),
            "Sharp Reply": ("atk", 9, 0),
            "Regain Composure": ("heal", 6, 0),
        }
    }],


    # SCRIPTED DOUBLE ENCOUNTERS


    [
        {
            "name": "Moe",
            "hp": 40,
            "pattern": ["Bad Joke", "Malpractice", "Hide Behind Props"],
            "moves": {
                "Bad Joke": ("weak_player", 1, 0),
                "Malpractice": ("atk", 7, 0),
                "Hide Behind Props": ("blk", 0, 7),
            }
        },
        {
            "name": "Ben Woodman",
            "hp": 38,
            "pattern": ["Nervous Attack", "Hide", "Nervous Attack"],
            "moves": {
                "Nervous Attack": ("atk", 7, 0),
                "Hide": ("blk", 0, 7),
            }
        }
    ],


    #  SCRIPTED TRIPLE ENCOUNTER 


    [
        {
            "name": "Lotta Hart",
            "hp": 32,
            "pattern": ["Snapshot", "Duck Behind Camera"],
            "moves": {
                "Snapshot": ("atk", 6, 0),
                "Duck Behind Camera": ("blk", 0, 5),
            }
        },
        {
            "name": "Lotta Hart",
            "hp": 32,
            "pattern": ["Snapshot", "Photo Barrage"],
            "moves": {
                "Snapshot": ("atk", 6, 0),
                "Photo Barrage": ("atk_multi", 2, 2),
            }
        },
        {
            "name": "Lotta Hart",
            "hp": 32,
            "pattern": ["Snapshot", "Duck Behind Camera"],
            "moves": {
                "Snapshot": ("atk", 6, 0),
                "Duck Behind Camera": ("blk", 0, 5),
            }
        }
    ],
]
ELITES = [
    [{
        "name": "Frank Sahwit",
        "hp": 78,
        "pattern": ["Toupee Barrage", "Panic Guard", "Clock Strike"],
        "moves": {
            "Toupee Barrage": ("atk_multi", 4, 2),
            "Panic Guard": ("blk", 0, 10),
            "Clock Strike": ("atk", 13, 0),
        }
    }],

    [{
        "name": "Redd White",
        "hp": 90,
        "pattern": ["Blackmail", "Executive Punch", "Corporate Shield", "Executive Punch"],
        "moves": {
            "Blackmail": ("vuln_player", 2, 0),
            "Executive Punch": ("atk", 13, 0),
            "Corporate Shield": ("blk", 0, 12),
        }
    }],

    [{
        "name": "Dee Vasquez",
        "hp": 96,
        "pattern": ["Studio Pressure", "Silent Threat", "Pull Strings", "Silent Threat"],
        "moves": {
            "Studio Pressure": ("weak_player", 2, 0),
            "Silent Threat": ("atk", 14, 0),
            "Pull Strings": ("blk", 0, 14),
        }
    }],

    [{
        "name": "Matt Engarde",
        "hp": 105,
        "pattern": ["Public Persona", "Hidden Strike", "Recover Image", "Hidden Strike"],
        "moves": {
            "Public Persona": ("blk", 0, 15),
            "Hidden Strike": ("atk", 15, 0),
            "Recover Image": ("heal", 10, 0),
        }
    }],

    [{
        "name": "Luke Atmey",
        "hp": 100,
        "pattern": ["Magnificent Pose", "Elegant Strike", "Grand Defense", "Elegant Strike"],
        "moves": {
            "Magnificent Pose": ("buff", 0, 2),
            "Elegant Strike": ("atk", 12, 0),
            "Grand Defense": ("blk", 0, 16),
        }
    }],

    [{
        "name": "Furio Tigre",
        "hp": 115,
        "pattern": ["Roar", "Tiger Punch", "Tiger Punch", "Crushing Blow"],
        "moves": {
            "Roar": ("buff", 0, 2),
            "Tiger Punch": ("atk", 13, 0),
            "Crushing Blow": ("atk", 18, 0),
        }
    }],
]
BOSSES = [
    {
        "name": "Edgeworth",
        "hp": 320,
        "max_hp": 320,

        "pattern": [
            "Opening Statement",
            "Objection Barrage",
            "Cross Examination",
            "Perfect Defense",
            "Pressure",
            "Turnabout",
            "Relentless Argument",
            "Final Verdict"
        ],

        "moves": {
            "Opening Statement": (
                "atk",
                22,
                0
            ),

            "Objection Barrage": (
                "atk_multi",
                9,
                3
            ),

            "Cross Examination": (
                "weak_player",
                2,
                0
            ),

            "Perfect Defense": (
                "blk",
                0,
                35
            ),

            "Pressure": (
                "vuln_player",
                2,
                0
            ),

            "Turnabout": (
                "buff",
                0,
                5
            ),

            "Relentless Argument": (
                "atk_multi",
                12,
                3
            ),

            "Final Verdict": (
                "atk",
                38,
                0
            )
        }
    },

    {
        "name": "Franziska (Boxing Champ)",
        "hp": 150,
        "max_hp": 150,
        "type": "boxing_boss",
        "mg": "BoxingBoss"
    }
]


GAME_EVENTS = {
    "Dead Body": {
        "title": "Dead Adventurer",
        "text": "You find the body of a fallen adventurer. His pockets still look suspiciously full.",
        "options": [
            {
                "label": "[Pickpocket] Gain 50 Gold, but lose 8 HP.",
                "action": "gold_and_damage",
                "gold": 50,
                "hp_loss": 8
            },
            {
                "label": "[Leave] Show some respect and walk away.",
                "action": "leave",
                "val": 0
            }
        ]
    },
    "Forbidden Knowledge": {
        "title": "Forbidden Knowledge",
        "text": "A forbidden tome promises absolute mastery, but demands half of your vitality.",
        "options": [
            {
                "label": "[Accept] Halve Max HP. Upgrade ALL cards.",
                "action": "half_max_hp_upgrade_all"
            },
            {
                "label": "[Leave] Close the tome.",
                "action": "leave"
            }
        ]
    },
    "Mysterious Shrine": {
        "title": "Mysterious Shrine",
        "text": "A blood-covered shrine stands before you. A whisper promises power in exchange for a sacrifice.",
        "options": [
            {
                "label": "[Pray] Lose 10 HP and gain a random Relic.",
                "action": "lose_hp_gain_random_relic",
                "hp_loss": 10
            },
            {
                "label": "[Leave] Ignore the shrine.",
                "action": "leave"
            }
        ]
    },

    "Golden Statue": {
        "title": "Golden Statue",
        "text": "An ancient golden statue covered in gemstones radiates wealth... and something far less pleasant.",
        "options": [
            {
                "label": "[Take the Idol] Gain 'Golden Idol' (+50% Gold), but add 1 Strike.",
                "action": "gain_relic_and_strikes",
                "relic": "Golden Idol",
                "strikes": 1
            },
            {
                "label": "[Smash the Statue] Gain 80 Gold, but lose 10 HP.",
                "action": "gold_and_damage",
                "gold": 80,
                "hp_loss": 10
            }
        ]
    },

    "Vampiric Altar": {
        "title": "Vampiric Altar",
        "text": "Fresh blood flows through a black marble altar. A voice in your head offers you eternal strength.",
        "options": [
            {
                "label": "[Drink the Blood] Gain 'Vampire Fangs', but lose 20% Max HP.",
                "action": "gain_vampire_fangs"
            },
            {
                "label": "[Purify the Altar] Fully heal, pay 40 Gold.",
                "action": "full_heal_lose_gold",
                "cost": 40
            },
            {
                "label": "[Leave] Walk away from the altar.",
                "action": "leave"
            }
        ]
    },

    "Molten Forge": {
        "title": "Molten Forge",
        "text": "A blacksmith offers you a molten hammer. Its power is immense, but it destroys your ability to improve weapons normally.",
        "options": [
            {
                "label": "[Take the Hammer] Gain 'Molten Hammer' (+1 Max Mana, no Campfire Upgrades).",
                "action": "gain_relic_simple",
                "relic": "Molten Hammer"
            },
            {
                "label": "[Temper Your Deck] Upgrade 2 random cards, but lose 12 HP.",
                "action": "upgrade_random_cards_lose_hp",
                "count": 2,
                "hp_loss": 12
            }
        ]
    },

    "Mind Wanderer": {
        "title": "Mind Wanderer",
        "text": "A faceless wanderer offers you a crystal capable of expanding your mind.",
        "options": [
            {
                "label": "[Accept the Crystal] Gain 'Mind Glass' (+1 card per turn), but lose 10 Max HP.",
                "action": "gain_mind_glass"
            },
            {
                "label": "[Forget the Past] Remove 1 Strike AND 1 Defend.",
                "action": "remove_two_basic_cards"
            }
        ]
    },

    "Merchant Contract": {
        "title": "Merchant Contract",
        "text": "A suspicious merchant offers you a lifetime VIP membership... for an investment.",
        "options": [
            {
                "label": "[Sign the Contract] Gain 'Greed Goblet' (-40% shop prices), pay 50 Gold.",
                "action": "gain_relic_pay_gold",
                "relic": "Greed Goblet",
                "cost": 50
            },
            {
                "label": "[Rob the Stall] Gain a random Rare card and 40 Gold, but lose 15 HP.",
                "action": "steal_merchant",
                "gold": 40,
                "hp_loss": 15
            }
        ]
    },

    "Arcade Master": {
        "title": "Arcade Master",
        "text": "A strange arcade machine glows in the darkness. A golden token lies beside it.",
        "options": [
            {
                "label": "[Buy the Token] Gain 'Arcade Token', pay 60 Gold.",
                "action": "gain_relic_pay_gold",
                "relic": "Arcade Token",
                "cost": 60
            },
            {
                "label": "[Gamble] 50% chance for +120 Gold / 50% chance to lose 15 HP.",
                "action": "gamble_gold_or_damage",
                "gold": 120,
                "damage": 15
            }
        ]
    },

    "Cursed Mirror": {
        "title": "Cursed Mirror",
        "text": "Your reflection moves on its own. The mirror seems capable of reflecting more than just light.",
        "options": [
            {
                "label": "[Take the Shield] Gain 'Mirror Shield', but add 2 Strikes.",
                "action": "gain_relic_and_strikes",
                "relic": "Mirror Shield",
                "strikes": 2
            },
            {
                "label": "[Look Deeper] Upgrade a random card, but lose 10 HP.",
                "action": "upgrade_random_card_lose_hp",
                "hp_loss": 10
            }
        ]
    },

    "Hourglass Portal": {
        "title": "Hourglass Portal",
        "text": "A floating hourglass freezes the air around it. Time itself seems distorted.",
        "options": [
            {
                "label": "[Take the Hourglass] Gain 'Hourglass of Fate', but lose 15 HP.",
                "action": "gain_relic_lose_hp",
                "relic": "Hourglass of Fate",
                "hp_loss": 15
            },
            {
                "label": "[Shatter It] Pay 30 Gold and leave.",
                "action": "pay_gold_leave",
                "cost": 30
            }
        ]
    },


    "Mutagen Lab": {
        "title": "Mutagen Lab",
        "text": "You discover a vial filled with glowing green liquid. It smells like power and pain.",
        "options": [
            {
                "label": "[Drink It] Gain 'Mutated Blood' (+2 Strength, -3 HP at combat start).",
                "action": "gain_relic_simple",
                "relic": "Mutated Blood"
            },
            {
                "label": "[Purify It] Gain +12 Max HP and heal 12 HP, pay 50 Gold.",
                "action": "gain_max_hp_and_heal",
                "max_hp_gain": 12,
                "hp_gain": 12,
                "cost": 50
            }
        ]
    },
    "Forgotten Evidence": {
    "title": "Forgotten Evidence",
    "text": (
        "Inside an abandoned evidence locker, "
        "you discover an unusual object. "
        "It may prove useful."
    ),

    "options": [
        {
            "label": (
                "[Take it] Gain a random Relic."
            ),
            "action": "gain_random_relic"
        },

        {
            "label": (
                "[Leave] Don't touch the evidence."
            ),
            "action": "leave"
        }
    ]
}
}
RELIC_RANDOM_BLACKLIST = {
    "Prophet's Eye",
    "Second Chance",
    "Perfect Verdict"
}
GLOBAL_CONTROLS = {
    "HaremMaker": {
        "LEFT": pygame.K_LEFT, 
        "RIGHT": pygame.K_RIGHT, 
        "SHOOT": pygame.K_SPACE
    },
    "HaremRunner": {
        "LEFT": pygame.K_LEFT, 
        "RIGHT": pygame.K_RIGHT
    },
    "ManPac": {
        "UP": pygame.K_UP, 
        "DOWN": pygame.K_DOWN, 
        "LEFT": pygame.K_LEFT, 
        "RIGHT": pygame.K_RIGHT
    },
    "BoxingBoss": {
        "PUNCH_L": pygame.K_z, 
        "PUNCH_R": pygame.K_x, 
        "DODGE_L": pygame.K_LEFT, 
        "DODGE_R": pygame.K_RIGHT, 
        "BLOCK": pygame.K_DOWN, 
        "AIM_UP": pygame.K_UP, 
        "SUPER": pygame.K_SPACE
    },
    "UndertaleBoss": {
        "LEFT": pygame.K_LEFT,
        "RIGHT": pygame.K_RIGHT,
        "UP": pygame.K_UP,
        "DOWN": pygame.K_DOWN,
        "ACTION": pygame.K_SPACE
    }
} 
def get_card_data(name, upgraded=False):

    if name not in CARDS:
        return {}

    data = dict(CARDS[name])

    if upgraded:
        data.update(
            CARD_UPGRADES.get(name, {})
        )

    return data

MAP_NODES = ["N","N","C","E","B"]