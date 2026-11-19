import pygame

from config import (
    W, H, BG, PANEL, BORDER, GOLD, RED, RED_D, GREEN, GREEN_D,
    BLUE, BLUE_D, PURPLE_D, WHITE, GRAY, GRAY_L, ORANGE,
    F_BIG, F_MED, F_TINY_BOLD)
from entities import rrect, txc


def _txt(surf, text, font, color, x, y):
    surf.blit(font.render(str(text), True, color), (x, y))


def _safe_history(g):
    history = g.get_history() if hasattr(g, "get_history") else []
    return history if isinstance(history, list) else []


def _entry_title(entry):
    if not isinstance(entry, dict):
        return "Unknown"

    enemy = entry.get("enemy", "Enemy")
    if isinstance(enemy, list):
        enemy = ", ".join(str(x) for x in enemy)

    return str(enemy or "Enemy")


def _entry_color(entry):
    if not isinstance(entry, dict):
        return GRAY

    node_type = str(entry.get("node_type", "enemy"))
    result = str(entry.get("result", "")).upper()

    if result == "DEFEAT":
        return RED
    if node_type == "boss":
        return GOLD
    if node_type == "elite":
        return PURPLE_D
    return RED_D


def _draw_hp_bar(surf, cur, mx, x, y, width=210):
    mx = max(1, int(mx or 1))
    cur = max(0, int(cur or 0))
    ratio = max(0.0, min(1.0, cur / mx))

    rrect(surf, (55, 18, 18), (x, y, width, 14), 4)
    rrect(surf, GREEN, (x, y, int(width * ratio), 14), 4)
    rrect(surf, BORDER, (x, y, width, 14), 4, 1)
    txc(surf, f"{cur}/{mx}", F_MED, WHITE, x + width // 2, y + 7)


def _draw_actor_box(surf, rect, title, snap, is_player=False, highlighted=False):
    border = GOLD if highlighted else BORDER
    rrect(surf, PANEL, rect, 10, 2, border)

    txc(surf, title, F_BIG if is_player else F_MED, WHITE, rect.centerx, rect.top + 28)

    hp = snap.get("hp", 0)
    max_hp = snap.get("max_hp", max(1, hp))
    _draw_hp_bar(surf, hp, max_hp, rect.left + 20, rect.top + 58, rect.width - 40)

    y = rect.top + 88

    block = int(snap.get("block", 0) or 0)
    strength = int(snap.get("str", 0) or 0)
    weak = int(snap.get("weak", 0) or 0)
    vuln = int(snap.get("vuln", 0) or 0)

    if block > 0:
        txc(surf, f"Block {block}", F_MED, BLUE, rect.centerx, y)
        y += 19
    if strength > 0:
        txc(surf, f"Strength +{strength}", F_MED, GREEN, rect.centerx, y)
        y += 19
    if weak > 0:
        txc(surf, f"Weak {weak}", F_MED, ORANGE, rect.centerx, y)
        y += 19
    if vuln > 0:
        txc(surf, f"Vulnerable {vuln}", F_MED, ORANGE, rect.centerx, y)

    if is_player:
        txc(
            surf,
            f"Mana {int(snap.get('mana', 0) or 0)}",
            F_MED,
            BLUE,
            rect.centerx,
            rect.bottom - 22,)


def _draw_arrow(surf, start, end, color, width=6):
    pygame.draw.line(surf, color, start, end, width)

    direction = 1 if end[0] >= start[0] else -1
    tip_x, tip_y = end
    pygame.draw.polygon(
        surf,
        color,
        [
            (tip_x, tip_y),
            (tip_x - 15 * direction, tip_y - 9),
            (tip_x - 15 * direction, tip_y + 9),
        ],)


def draw_run_history(surf, g, mouse):


    surf.fill(BG)
    txc(surf, "RUN HISTORY", F_BIG, GOLD, W // 2, 38)

    history = _safe_history(g)
    g.history_run_rects = []
    g.history_node_rects = []
    g.history_build_rect = pygame.Rect(0,0,0,0)

    if not history:
        txc(surf, "No completed runs yet.", F_MED, GRAY_L, W // 2, H // 2)
        g.btn_hist_back.draw(surf, mouse)
        return

    selected = max(0, min(getattr(g, "selected_history_index", 0), len(history) - 1))
    g.selected_history_index = selected

    # Left column runs
    rrect(surf, PANEL, (18, 78, 220, H - 155), 8, 2, BORDER)

    for i, run in enumerate(history[:10]):
        rect = pygame.Rect(28, 90 + i * 46, 200, 38)
        g.history_run_rects.append((i, rect))

        is_selected = i == selected
        result = str(run.get("result", "UNKNOWN")) if isinstance(run, dict) else "UNKNOWN"
        col = GOLD if is_selected else (GREEN_D if result == "VICTORY" else RED_D)

        rrect(surf, col, rect, 6, 1, WHITE if is_selected else BORDER)
        txc(surf, f"Run #{len(history) - i} - {result}", F_MED, WHITE, rect.centerx, rect.centery)

    run = history[selected] if isinstance(history[selected], dict) else {}
    path = run.get("path", [])

    if not isinstance(path, list) or not path:
        txc(surf, "Legacy history entry", F_BIG, GRAY_L, (W + 238) // 2, 190)
        txc(surf, "This run was saved by the old history system.", F_MED, WHITE, (W + 238) // 2, 235)
        txc(surf, "New runs will use the visual timeline + replay system.", F_MED, GOLD, (W + 238) // 2, 260)
        # FINAL BUILD BUTTON
        g.history_build_rect = pygame.Rect(W - 230, H - 70, 200, 42)

        has_build = bool(
            run.get("final_deck", []))

        hover = (
            has_build
            and g.history_build_rect.collidepoint(
                mouse)
        )

        rrect(
            surf,
            BLUE_D
            if hover
            else PANEL,
            g.history_build_rect,
            7,
            2,
            BLUE if has_build else GRAY)

        txc(
            surf,
            "VIEW FINAL BUILD"
            if has_build
            else "BUILD NOT SAVED",
            F_MED,
            WHITE if has_build else GRAY,
            g.history_build_rect.centerx,
            g.history_build_rect.centery)
        g.btn_hist_back.draw(surf, mouse)
        return

    char_name = run.get("character", "Unknown")
    result = run.get("result", "UNKNOWN")
    txc(surf, f"{char_name}  |  {result}", F_MED, WHITE, 625, 92)
    # FINAL BUILD
    final_deck = run.get("final_deck", [])

    relics = run.get("relics", [])


    has_build = bool(
        final_deck)
    if has_build:
        txc(
            surf,
            (
                f"Final Build: "
                f"{len(final_deck)} cards  |  "
                f"{len(relics)} relics"),
            F_MED,
            GOLD,
            625,
            118)

        g.history_build_rect = pygame.Rect(W - 230, H - 70, 200, 42)

        hover = (
            g.history_build_rect.collidepoint(
                mouse)
        )

        rrect(
            surf,
            BLUE_D if hover else PANEL,
            g.history_build_rect,
            7,
            2,
            BLUE)

        txc(
            surf,
            "VIEW FINAL BUILD",
            F_MED,
            WHITE,
            g.history_build_rect.centerx,
            g.history_build_rect.centery)
    start_x = 300
    start_y = 165
    gap_x = 105
    gap_y = 145
    per_row = 7
    radius = 27

    hovered = None

    for i, entry in enumerate(path):
        row = i // per_row
        col = i % per_row
        cx = start_x + col * gap_x
        cy = start_y + row * gap_y

        if col > 0:
            pygame.draw.line(surf, (75, 65, 95), (cx - gap_x + radius, cy), (cx - radius, cy), 3)

        rect = pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)
        g.history_node_rects.append((i, rect))

        circle_col = _entry_color(entry)
        hover = rect.collidepoint(mouse)
        border = WHITE if hover else GOLD if str(entry.get("node_type", "")) == "boss" else BORDER

        pygame.draw.circle(surf, circle_col, (cx, cy), radius)
        pygame.draw.circle(surf, border, (cx, cy), radius, 3 if hover else 2)

        floor_num = entry.get("floor", i + 1)
        txc(surf, str(floor_num), F_MED, WHITE, cx, cy)

        label = "BOSS" if entry.get("node_type") == "boss" else "ELITE" if entry.get("node_type") == "elite" else "FIGHT"
        txc(surf, label, F_TINY_BOLD, GOLD if label == "BOSS" else GRAY_L, cx, cy + 42)

        if hover:
            hovered = (entry, cx, cy)

    if hovered:
        entry, cx, cy = hovered
        box_w = 360
        box_h = 165
        tx = min(W - box_w - 15, max(250, mouse[0] + 18))
        ty = min(H - box_h - 15, max(90, mouse[1] + 18))

        rrect(surf, PANEL, (tx, ty, box_w, box_h), 8, 2, GOLD)

        txc(surf, _entry_title(entry), F_MED, GOLD, tx + box_w // 2, ty + 20)
        _txt(surf, f"Floor: {entry.get('floor', '?')}  |  Act: {entry.get('act', 1)}", F_MED, WHITE, tx + 12, ty + 42)
        _txt(surf, f"Minigame: {entry.get('minigame', 'None')}", F_MED, WHITE, tx + 12, ty + 62)
        _txt(surf, f"Damage dealt: {entry.get('dmg_dealt', 0)}", F_MED, GREEN, tx + 12, ty + 82)
        _txt(surf, f"Damage taken: {entry.get('dmg_taken', 0)}", F_MED, RED, tx + 180, ty + 82)

        mg_name = entry.get("minigame", "None")

        mg_status = entry.get("minigame_status", "UNKNOWN")

        _txt(
            surf,
            f"Minigame: {mg_name} - {mg_status}",
            F_MED,
            GOLD if mg_status == "PLAYED" else GRAY_L,
            tx + 12,
            ty + 62)

        cards = entry.get("reward_options", [])

        cards_text = (
            " | ".join(cards)
            if cards
            else "None")

        if len(cards_text) > 48:
            cards_text = (
                cards_text[:45]
                + "...")

        _txt(
            surf,
            f"Cards: {cards_text}",
            F_MED,
            WHITE,
            tx + 12,
            ty + 104)

        choice = entry.get(
            "reward_choice")

        if not choice:
            choice = "NONE"

        choice_col = (
            GRAY
            if str(choice).upper() == "SKIPPED"
            else GREEN)

        _txt(
            surf,
            f"Chosen: {choice}",
            F_MED,
            choice_col,
            tx + 12,
            ty + 126)

    g.btn_hist_back.draw(surf, mouse)


def draw_combat_replay(surf, g, mouse):
    surf.fill(BG)

    entry = getattr(g, "history_replay_entry", None)
    if not isinstance(entry, dict):
        g.history_replay_entry = None
        return

    replay = entry.get("replay", [])
    if not replay:
        g.history_replay_entry = None
        return

    step_i = max(0, min(getattr(g, "history_replay_step", 0), len(replay) - 1))
    g.history_replay_step = step_i
    step = replay[step_i]

    txc(surf, "COMBAT REPLAY", F_BIG, GOLD, W // 2, 35)
    txc(surf, _entry_title(entry), F_MED, WHITE, W // 2, 72)

    snap = step.get("snapshot", {})
    player = snap.get("player", {})
    enemies = snap.get("enemies", [])

    player_rect = pygame.Rect(55, 150, 250, 250)

    target_name = str(step.get("target", ""))
    actor = str(step.get("actor", ""))

    _draw_actor_box(
        surf,
        player_rect,
        "PLAYER",
        player,
        is_player=True,
        highlighted=(actor == "enemy" and target_name == "Player"),)

    enemy_rects = []
    enemy_count = max(1, len(enemies))
    enemy_w = 220
    enemy_gap = 20
    total_w = enemy_count * enemy_w + (enemy_count - 1) * enemy_gap
    start_enemy_x = max(360, W - total_w - 45)

    for i, enemy in enumerate(enemies):
        rect = pygame.Rect(start_enemy_x + i * (enemy_w + enemy_gap), 150, enemy_w, 250)
        enemy_rects.append((enemy, rect))
        _draw_actor_box(
            surf,
            rect,
            enemy.get("name", f"Enemy {i + 1}"),
            enemy,
            highlighted=(target_name == enemy.get("name", "")),)

    action = str(step.get("action", "Action"))
    value = int(step.get("value", 0) or 0)
    kind = str(step.get("kind", "action"))

    action_box = pygame.Rect(W // 2 - 220, 430, 440, 95)
    rrect(surf, PANEL, action_box, 8, 2, GOLD)
    txc(surf, action, F_BIG, WHITE, action_box.centerx, action_box.top + 28)

    if kind == "damage":
        detail = f"{value} DAMAGE"
        detail_col = RED
    elif kind == "block":
        detail = f"+{value} BLOCK"
        detail_col = BLUE
    elif kind == "buff":
        detail = f"+{value}"
        detail_col = GREEN
    else:
        detail = step.get("detail", "")
        detail_col = GRAY_L

    if detail:
        txc(surf, detail, F_MED, detail_col, action_box.centerx, action_box.top + 67)

    
    if kind == "damage":
        if actor == "player" and enemy_rects:
            target_rect = next((r for e, r in enemy_rects if e.get("name") == target_name), enemy_rects[0][1])
            _draw_arrow(surf, (player_rect.right + 10, 280), (target_rect.left - 10, 280), GOLD)
        elif actor == "enemy":
            source_rect = next((r for e, r in enemy_rects if e.get("name") == step.get("source")), enemy_rects[0][1] if enemy_rects else None)
            if source_rect:
                _draw_arrow(surf, (source_rect.left - 10, 280), (player_rect.right + 10, 280), RED)

    g.history_prev_rect = pygame.Rect(W // 2 - 220, H - 70, 150, 42)
    g.history_next_rect = pygame.Rect(W // 2 + 70, H - 70, 150, 42)
    g.history_replay_back_rect = pygame.Rect(20, H - 70, 140, 42)

    rrect(surf, BLUE_D if g.history_prev_rect.collidepoint(mouse) else PANEL, g.history_prev_rect, 7, 2, BLUE)
    rrect(surf, BLUE_D if g.history_next_rect.collidepoint(mouse) else PANEL, g.history_next_rect, 7, 2, BLUE)
    rrect(surf, RED_D if g.history_replay_back_rect.collidepoint(mouse) else PANEL, g.history_replay_back_rect, 7, 2, RED)

    txc(surf, "< PREVIOUS", F_MED, WHITE, g.history_prev_rect.centerx, g.history_prev_rect.centery)
    txc(surf, "NEXT >", F_MED, WHITE, g.history_next_rect.centerx, g.history_next_rect.centery)
    txc(surf, "BACK", F_MED, WHITE, g.history_replay_back_rect.centerx, g.history_replay_back_rect.centery)
    txc(surf, f"Step {step_i + 1} / {len(replay)}", F_MED, GOLD, W // 2, H - 48)


def handle_run_history_click(g, pos):
    if getattr(g, "history_replay_entry", None) is not None:
        if getattr(g, "history_replay_back_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
            g.history_replay_entry = None
            g.history_replay_step = 0
            return True

        if getattr(g, "history_prev_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
            g.history_replay_step = max(0, getattr(g, "history_replay_step", 0) - 1)
            return True

        if getattr(g, "history_next_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
            replay = g.history_replay_entry.get("replay", [])
            g.history_replay_step = min(max(0, len(replay) - 1), getattr(g, "history_replay_step", 0) + 1)
            return True

        return False

    if hasattr(g, "btn_hist_back") and g.btn_hist_back.hit(pos):
        g.state = "start_menu"
        return True

    if getattr(
        g,
        "history_build_rect",
        pygame.Rect(0, 0, 0, 0)).collidepoint(pos):

        history = _safe_history(g)

        selected = getattr(
            g,
            "selected_history_index",
            0)

        if (
            0 <= selected < len(history)
            and isinstance(history[selected], dict)
            and history[selected].get(
                "final_deck")
        ):

            g.history_build_index = (
                selected)

            g.state = "history_build"

            return True

    for index, rect in getattr(g, "history_run_rects", []):
        if rect.collidepoint(pos):
            g.selected_history_index = index
            return True

    history = _safe_history(g)
    selected = getattr(g, "selected_history_index", 0)

    if 0 <= selected < len(history) and isinstance(history[selected], dict):
        path = history[selected].get("path", [])

        

    return False
