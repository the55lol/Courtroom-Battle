import pygame
import json
import os


from config import W, H, GLOBAL_CONTROLS
from audio_settings import (
    save_audio_settings,
    apply_audio_settings,
    slider_value_from_x)

DISPLAY_SETTINGS_FILE = (
    "display_settings.json")

STANDARD_RESOLUTIONS = [
    (1024, 768),
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
]




def get_desktop_resolution():

    try:

        desktops = (
            pygame.display.get_desktop_sizes())

        if desktops:
            return desktops[0]

    except Exception:
        pass

    return (
        W,
        H)


def get_resolution_options():

    desktop_w, desktop_h = (
        get_desktop_resolution())

    available = [
        resolution
        for resolution
        in STANDARD_RESOLUTIONS
        if (
            resolution[0] <= desktop_w
            and resolution[1] <= desktop_h)
    ]

    if not available:
        available = [
            (W, H)
        ]

    return available


def load_display_settings():

    default = {
        "mode": "Windowed",
        "resolution": [
            W,
            H
        ]
    }

    if not os.path.exists(
        DISPLAY_SETTINGS_FILE):
        return default

    try:

        with open(
            DISPLAY_SETTINGS_FILE,
            "r",
            encoding="utf-8") as file:

            data = json.load(
                file)

        mode = data.get("mode", "Windowed")

        if mode not in (
            "Windowed",
            "Borderless",
            "Fullscreen"):
            mode = "Windowed"

        resolution = tuple(
            data.get(
                "resolution",
                [W, H])
        )

        options = (
            get_resolution_options())

        if resolution not in options:
            resolution = options[0]

        return {
            "mode": mode,
            "resolution": list(
                resolution)
        }

    except Exception:

        return default


def save_display_settings(
    settings):

    data = {
        "mode": settings.get("mode", "Windowed"),

        "resolution": list(
            settings.get(
                "resolution",
                (W, H))
        )
    }

    try:

        with open(
            DISPLAY_SETTINGS_FILE,
            "w",
            encoding="utf-8") as file:

            json.dump(
                data,
                file,
                indent=2)

    except Exception:
        pass

def apply_display_settings(
    settings):

    mode = settings.get("mode", "Windowed")

    resolution = tuple(
        settings.get(
            "resolution",
            (W, H))
    )

    desktop_w, desktop_h = (
        get_desktop_resolution())

    if mode == "Fullscreen":

        actual_size = (
            desktop_w,
            desktop_h)

        flags = pygame.NOFRAME

        os.environ[
            "SDL_VIDEO_WINDOW_POS"
        ] = "0,0"

    elif mode == "Borderless":

        actual_size = resolution
        flags = pygame.NOFRAME

        res_w, res_h = actual_size

        x = max(
            0,
            (desktop_w - res_w) // 2)

        y = max(
            0,
            (desktop_h - res_h) // 2)

        os.environ[
            "SDL_VIDEO_WINDOW_POS"
        ] = f"{x},{y}"

    else:

        actual_size = resolution
        flags = 0

        res_w, res_h = actual_size

        x = max(
            0,
            (desktop_w - res_w) // 2)

        y = max(
            0,
            (desktop_h - res_h) // 2)

        os.environ[
            "SDL_VIDEO_WINDOW_POS"
        ] = f"{x},{y}"

    display = pygame.display.set_mode(actual_size, flags)

    pygame.display.set_caption(
        "Courtroom Battle")

    return display


def create_minigame_view(virtual_width, virtual_height):

    display = (
        pygame.display.get_surface())

    if display is None:

        display = (
            apply_display_settings(
                load_display_settings())
        )

    virtual = pygame.Surface(
        (
            virtual_width,
            virtual_height)
    )

    return (
        display,
        virtual)


def present_minigame(display, virtual):
    display_size = (display.get_size())

    scaled = (pygame.transform.smoothscale(virtual,display_size))

    display.blit(scaled,(0, 0))

    pygame.display.flip()


def screen_to_virtual(
    mouse_pos,
    virtual_width,
    virtual_height):

    display = (
        pygame.display.get_surface())

    if display is None:
        return mouse_pos

    display_w, display_h = (
        display.get_size())

    if (
        display_w <= 0
        or display_h <= 0):
        return mouse_pos

    mx, my = mouse_pos

    vx = (
        mx
        * virtual_width
        / display_w)

    vy = (
        my
        * virtual_height
        / display_h)

    return (
        int(vx),
        int(vy))

# MINIGAME SETTINGS / PAUSE
def get_minigame_settings_rect(virtual_width, virtual_height):

    return pygame.Rect(virtual_width - 125, 12, 110, 36)


def draw_minigame_settings_button(virtual, g):
    if getattr(g, "tutorial_active", False):
        return

    vw, vh = virtual.get_size()

    rect = (get_minigame_settings_rect(vw, vh))

    mouse = screen_to_virtual(
        pygame.mouse.get_pos(),
        vw,
        vh)

    hover = rect.collidepoint(
        mouse)

    pygame.draw.rect(
        virtual,
        (65, 70, 95)
        if hover
        else (35, 38, 55),
        rect,
        border_radius=7)

    pygame.draw.rect(
        virtual,
        (180, 180, 200),
        rect,
        2,
        border_radius=7)

    font = pygame.font.SysFont(
        "arial",
        16,
        bold=True)

    text = font.render(
        "SETTINGS",
        True,
        (245, 245, 245))

    virtual.blit(
        text,
        text.get_rect(
            center=rect.center)
    )


def minigame_settings_requested(
    event,
    g,
    virtual_width,
    virtual_height):
    if getattr(g, "tutorial_active", False):
        return False

    # ESC
    if (
        event.type == pygame.KEYDOWN
        and event.key == pygame.K_ESCAPE):
        return True

    # SETTINGS button
    if (
        event.type == pygame.MOUSEBUTTONDOWN
        and event.button == 1):

        pos = screen_to_virtual(
            event.pos,
            virtual_width,
            virtual_height)

        rect = (
            get_minigame_settings_rect(virtual_width, virtual_height))

        return rect.collidepoint(pos)

    return False

class MinigameQuitToMenu(Exception):
    pass


class MinigameQuitGame(Exception):
    pass



def run_minigame_settings(
    display,
    virtual,
    g):

    pause_started = (
        pygame.time.get_ticks())

    pygame.mixer.pause()
    pygame.mixer.music.pause()

    clock = pygame.time.Clock()

    virtual = pygame.Surface(
        (W, H))

    vw, vh = (
        W,
        H)

    page = "settings"

    selected_game = getattr(g, "selected_minigame_ctrls", "HaremMaker")

    awaiting_key = None
    dragging_audio_slider = None

    def settings_click():

        if hasattr(g, "play_sfx"):

            g.play_sfx("universfield-computer-mouse-click-352734", 0.40)
    games = [
        "HaremMaker",
        "HaremRunner",
        "ManPac",
        "BoxingBoss",
        "UndertaleBoss"
    ]

    running = True

    while running:

        mouse = screen_to_virtual(
            pygame.mouse.get_pos(),
            vw,
            vh)

        virtual.fill(
            (18, 14, 28))

        title_font = pygame.font.SysFont(
            "Georgia",
            30,
            bold=True)

        font = pygame.font.SysFont(
            "Georgia",
            18,
            bold=True)

        small_font = pygame.font.SysFont("Georgia", 14)
        # SETTINGS PAGE
        if page == "settings":

            old_prev_settings_state = getattr(g, "prev_settings_state", "start_menu")
            g.prev_settings_state = "play_minigame"

            g.draw_settings_menu(
                virtual,
                g,
                mouse)

            g.prev_settings_state = (
                old_prev_settings_state)
          
            # MINIGAME EVENT HANDLER
            mode_rect = (
                g.display_mode_rect)

            res_rect = (
                g.display_resolution_rect)

            apply_rect = (
                g.display_apply_rect)

            music_slider_rect = (
                g.music_slider_rect)

            sfx_slider_rect = (
                g.sfx_slider_rect)

            controls_rect = (
                g.btn_set_ctrls.rect)

            quit_menu_rect = (
                g.btn_set_quit.rect)

            quit_game_rect = (
                g.btn_set_quit_desktop.rect)

            resume_rect = (
                g.btn_set_back.rect)
            # SETTINGS EVENTS
            for event in pygame.event.get():
                # CLOSE WINDOW
                if event.type == pygame.QUIT:

                    pygame.mixer.stop()
                    pygame.mixer.music.stop()

                    raise MinigameQuitGame()
                # ESC = RESUME
                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE):

                    running = False
                    continue
                # DRAG AUDIO SLIDER
                if (
                    event.type == pygame.MOUSEMOTION
                    and dragging_audio_slider
                    is not None):

                    pos = screen_to_virtual(
                        event.pos,
                        vw,
                        vh)

                    if (
                        dragging_audio_slider
                        == "music"):

                        g.music_volume = (
                            slider_value_from_x(pos[0], music_slider_rect)
                        )

                    elif (
                        dragging_audio_slider
                        == "sfx"):

                        g.sfx_volume = (
                            slider_value_from_x(pos[0], sfx_slider_rect)
                        )

                    apply_audio_settings(g.music_volume, g.sfx_volume)

                    continue
                # RELEASE AUDIO SLIDER
                if (
                    event.type == pygame.MOUSEBUTTONUP
                    and event.button == 1
                    and dragging_audio_slider
                    is not None):

                    save_audio_settings(g.music_volume, g.sfx_volume)

                    dragging_audio_slider = None

                    continue
                # LEFT CLICK
                if (
                    event.type
                    == pygame.MOUSEBUTTONDOWN
                    and event.button == 1):

                    pos = screen_to_virtual(
                        event.pos,
                        vw,
                        vh)
                    # MUSIC
                    if music_slider_rect.inflate(0, 20).collidepoint(pos):
                        settings_click()
                        dragging_audio_slider = (
                            "music")

                        g.music_volume = (
                            slider_value_from_x(pos[0], music_slider_rect)
                        )

                        apply_audio_settings(g.music_volume, g.sfx_volume)
                    # SFX
                    elif sfx_slider_rect.inflate(0, 20).collidepoint(pos):

                        dragging_audio_slider = (
                            "sfx")

                        g.sfx_volume = (
                            slider_value_from_x(pos[0], sfx_slider_rect)
                        )

                        apply_audio_settings(g.music_volume, g.sfx_volume)
                        settings_click()
                    # DISPLAY MODE
                    elif mode_rect.collidepoint(
                        pos):
                        settings_click()

                        modes = [
                            "Windowed",
                            "Borderless",
                            "Fullscreen"
                        ]

                        try:

                            idx = modes.index(
                                g.display_mode)

                        except ValueError:

                            idx = 0

                        g.display_mode = (
                            modes[
                                (idx + 1)
                                % len(modes)
                            ])
                    # RESOLUTION
                    elif (
                        res_rect.collidepoint(pos)
                        and g.display_mode
                        != "Fullscreen"):
                        settings_click()
                        options = getattr(g, "display_resolutions", get_resolution_options())

                        try:

                            idx = options.index(
                                g.display_resolution)

                        except ValueError:

                            idx = 0

                        g.display_resolution = (
                            options[
                                (idx + 1)
                                % len(options)
                            ])
                    # APPLY DISPLAY
                    elif apply_rect.collidepoint(
                        pos):
                        settings_click()
                        settings = {
                            "mode": (
                                g.display_mode),
                            "resolution": list(
                                g.display_resolution)
                        }

                        save_display_settings(
                            settings)

                        g.display_restart_notice = True
                    # CONTROLS
                    elif controls_rect.collidepoint(
                        pos):
                        settings_click()
                        page = "controls_select"
                    # SAVE & QUIT TO MENU
                    elif quit_menu_rect.collidepoint(
                        pos):
                        settings_click()

                        pygame.time.delay(
                            80)
                        pygame.mixer.stop()
                        pygame.mixer.music.stop()

                        raise MinigameQuitToMenu()
                    # SAVE & QUIT GAME
                    elif quit_game_rect.collidepoint(
                        pos):
                        settings_click()

                        pygame.time.delay(
                            80)
                        pygame.mixer.stop()
                        pygame.mixer.music.stop()

                        raise MinigameQuitGame()
                    # RESUME
                    elif resume_rect.collidepoint(
                        pos):
                        settings_click()
                        running = False
        # SELECT MINIGAME CONTROLS
        elif page == "controls_select":

            title = title_font.render(
                "SELECT MINIGAME",
                True,
                (235, 225, 215))

            virtual.blit(
                title,
                title.get_rect(
                    center=(
                        vw // 2,
                        65)
                ))

            game_rects = []

            start_y = 120

            for i, game_name in enumerate(
                games):

                rect = pygame.Rect(vw // 2 - 160, start_y + i * 55, 320, 44)

                hover = rect.collidepoint(
                    mouse)

                pygame.draw.rect(
                    virtual,
                    (45, 60, 105)
                    if hover
                    else (30, 24, 48),
                    rect,
                    border_radius=8)

                pygame.draw.rect(
                    virtual,
                    (80, 110, 190),
                    rect,
                    2,
                    border_radius=8)

                label = font.render(
                    game_name,
                    True,
                    (235, 225, 215))

                virtual.blit(
                    label,
                    label.get_rect(
                        center=rect.center)
                )

                game_rects.append(
                    (
                        game_name,
                        rect)
                )

            back_rect = pygame.Rect(vw // 2 - 110, vh - 70, 220, 44)

            pygame.draw.rect(
                virtual,
                (100, 35, 50)
                if back_rect.collidepoint(mouse)
                else (30, 24, 48),
                back_rect,
                border_radius=8)

            pygame.draw.rect(
                virtual,
                (190, 65, 75),
                back_rect,
                2,
                border_radius=8)

            back_text = font.render(
                "BACK",
                True,
                (235, 225, 215))

            virtual.blit(
                back_text,
                back_text.get_rect(
                    center=back_rect.center)
            )

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    pygame.mixer.stop()
                    pygame.mixer.music.stop()

                    raise MinigameQuitGame()

                if (
                    event.type == pygame.KEYDOWN
                    and event.key
                    == pygame.K_ESCAPE):

                    page = "settings"
                    continue

              
                if (
                    event.type
                    == pygame.MOUSEBUTTONDOWN
                    and event.button == 1):

                    pos = screen_to_virtual(
                        event.pos,
                        vw,
                        vh)

                    if back_rect.collidepoint(
                        pos):
                        settings_click()
                        page = "settings"
                        continue

                    for (
                        game_name,
                        rect) in game_rects:

                        if rect.collidepoint(
                            pos):
                            settings_click()
                            selected_game = (
                                game_name)

                            g.selected_minigame_ctrls = (
                                game_name)

                            awaiting_key = None
                            page = (
                                "controls_menu")

                            break
        # REBIND CONTROLS
        elif page == "controls_menu":

            title = title_font.render(
                (
                    selected_game
                    + " CONTROLS"),
                True,
                (235, 225, 215))

            virtual.blit(
                title,
                title.get_rect(
                    center=(
                        vw // 2,
                        55)
                ))

            actions = GLOBAL_CONTROLS.get(selected_game, {})

            action_rects = []

            start_y = 105

            for i, (
                action,
                key_value) in enumerate(
                actions.items()):

                y = (
                    start_y
                    + i * 48)

                label = font.render(
                    action,
                    True,
                    (235, 225, 215))

                virtual.blit(
                    label,
                    (
                        vw // 2 - 190,
                        y + 9)
                )

                key_rect = pygame.Rect(vw // 2 + 20, y, 170, 38)

                waiting = (
                    awaiting_key
                    == action)

                pygame.draw.rect(
                    virtual,
                    (120, 70, 25)
                    if waiting
                    else (
                        (65, 70, 95)
                        if key_rect.collidepoint(
                            mouse)
                        else (30, 24, 48)),
                    key_rect,
                    border_radius=7)

                pygame.draw.rect(
                    virtual,
                    (210, 170, 60)
                    if waiting
                    else (150, 150, 175),
                    key_rect,
                    2,
                    border_radius=7)

                key_text = font.render(
                    (
                        "PRESS KEY..."
                        if waiting
                        else pygame.key.name(
                            key_value).upper()
                    ),
                    True,
                    (245, 245, 245))

                virtual.blit(
                    key_text,
                    key_text.get_rect(
                        center=key_rect.center)
                )

                action_rects.append(
                    (
                        action,
                        key_rect)
                )

            back_rect = pygame.Rect(vw // 2 - 110, vh - 65, 220, 42)

            pygame.draw.rect(
                virtual,
                (100, 35, 50)
                if back_rect.collidepoint(mouse)
                else (30, 24, 48),
                back_rect,
                border_radius=8)

            pygame.draw.rect(
                virtual,
                (190, 65, 75),
                back_rect,
                2,
                border_radius=8)

            back_text = font.render(
                "BACK",
                True,
                (235, 225, 215))

            virtual.blit(
                back_text,
                back_text.get_rect(
                    center=back_rect.center)
            )

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    pygame.mixer.unpause()
                    pygame.mixer.music.unpause()

                    raise MinigameQuitGame()
                # WAITING FOR NEW KEY
                if (
                    event.type
                    == pygame.KEYDOWN
                    and awaiting_key
                    is not None):

                    if (
                        event.key
                        == pygame.K_ESCAPE):

                        awaiting_key = None

                    else:

                        GLOBAL_CONTROLS[
                            selected_game
                        ][
                            awaiting_key
                        ] = event.key

                        awaiting_key = None

                    continue

                # ESC
                if (
                    event.type
                    == pygame.KEYDOWN
                    and event.key
                    == pygame.K_ESCAPE):

                    page = (
                        "controls_select")

                    continue

                if (
                    event.type
                    == pygame.MOUSEBUTTONDOWN
                    and event.button == 1):

                    pos = screen_to_virtual(
                        event.pos,
                        vw,
                        vh)

                    if back_rect.collidepoint(
                        pos):

                        awaiting_key = None

                        page = (
                            "controls_select")

                        continue

                    for (
                        action,
                        rect) in action_rects:

                        if rect.collidepoint(
                            pos):

                            awaiting_key = (
                                action)

                            break

        present_minigame(display, virtual)

        clock.tick(
            60)

    pygame.mixer.unpause()
    pygame.mixer.music.unpause()

    paused_ms = (
        pygame.time.get_ticks()
        - pause_started)

    return (
        display,
        paused_ms)