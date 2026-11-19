import os
import sys


def resource_path(*parts):

    if getattr(sys, "frozen", False):

        base_dir = getattr(
            sys,
            "_MEIPASS",
            os.path.dirname(
                sys.executable)
        )

    else:

        base_dir = os.path.dirname(
            os.path.abspath(
                __file__)
        )

    return os.path.join(base_dir, *parts)


def asset_path(game_folder, *parts):

    return resource_path(
        "assets",
        game_folder,
        *parts)
def load_franziska_sprite(
    pose,
    max_size,
    flip_x=True):

    import pygame

    files = {
        "default": "franziska_default.png",
        "damage": "franziska_damage.png",
        "special": "franziska_special.png",
        "attack": "franziska_attack.png"
    }

    filename = files.get(pose, "franziska_default.png")

    path = asset_path(
        "enemies",
        "Franziska von Karma",
        filename)

    try:

        img = pygame.image.load(
            path)

        visible_bounds = (
            img.get_bounding_rect(
                min_alpha=1)
        )

        if (
            visible_bounds.width > 0
            and visible_bounds.height > 0):

            img = img.subsurface(
                visible_bounds).copy()

        original_w = img.get_width()
        original_h = img.get_height()

        max_w, max_h = max_size

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

        if flip_x:

            img = pygame.transform.flip(
                img,
                True,
                False)

        return img

    except Exception as exc:

        print(
            "Franziska sprite failed:",
            path,
            exc)

        return None