import json
import os
import sys
import pygame


def _settings_path():

    if getattr(
        sys,
        "frozen",
        False
    ):
        base_dir = os.path.dirname(
            sys.executable
        )

    else:
        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

    return os.path.join(
        base_dir,
        "audio_settings.json"
    )


def _clamp_volume(value):

    return max(
        0.0,
        min(
            1.0,
            float(value)
        )
    )


def load_audio_settings():

    default = {
        "music_volume": 0.30,
        "sfx_volume": 1.00
    }

    path = _settings_path()

    if not os.path.exists(path):
        return default

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return {
            "music_volume": _clamp_volume(
                data.get(
                    "music_volume",
                    0.30
                )
            ),

            "sfx_volume": _clamp_volume(
                data.get(
                    "sfx_volume",
                    1.00
                )
            )
        }

    except Exception:
        return default


def save_audio_settings(
    music_volume,
    sfx_volume
):

    data = {
        "music_volume": _clamp_volume(
            music_volume
        ),

        "sfx_volume": _clamp_volume(
            sfx_volume
        )
    }

    try:

        with open(
            _settings_path(),
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=2
            )

    except Exception as exc:

        print(
            "Could not save audio settings:",
            exc
        )


def apply_audio_settings(
    music_volume,
    sfx_volume
):

    music_volume = _clamp_volume(
        music_volume
    )

    sfx_volume = _clamp_volume(
        sfx_volume
    )

    if not pygame.mixer.get_init():
        return

    pygame.mixer.music.set_volume(
        music_volume
    )

    for channel_index in range(
        pygame.mixer.get_num_channels()
    ):

        pygame.mixer.Channel(
            channel_index
        ).set_volume(
            sfx_volume
        )


def slider_value_from_x(
    mouse_x,
    rect
):

    if rect.width <= 0:
        return 0.0

    value = (
        mouse_x - rect.left
    ) / rect.width

    return _clamp_volume(
        value
    )