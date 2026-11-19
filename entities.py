import pygame
from config import CW, CH, BLUE_D, WHITE, BORDER, F_MED

def lerp(a, b, t):
    return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

def rrect(surf, col, rect, r=8, bw=0, bc=None):
    pygame.draw.rect(surf, col, rect, border_radius=r)
    if bw and bc:
        pygame.draw.rect(surf, bc, rect, bw, border_radius=r)

def txc(surf, s, font, col, cx, cy):
    r = font.render(s, True, col)
    surf.blit(r, (cx - r.get_width()//2, cy - r.get_height()//2))

class Card:
    def __init__(self, name):
        self.name     = name
        self.upgraded = False
        self.x = 0; self.y = 0

    def do_upgrade(self):
        self.upgraded = True

    def collides(self, pos, ox=None, oy=None):
        x = ox if ox is not None else self.x
        y = oy if oy is not None else self.y
        return x <= pos[0] <= x+CW and y <= pos[1] <= y+CH

class Btn:
    click_callback = None
    def __init__(self, label, x, y, w, h, col=BLUE_D):
        self.label = label
        self.rect  = pygame.Rect(x, y, w, h)
        self.col   = col

    def draw(self, surf, mouse):
        hov = self.rect.collidepoint(mouse)
        rrect(surf, lerp(self.col, WHITE, 0.12) if hov else self.col, self.rect, 8, 2, BORDER)
        txc(surf, self.label, F_MED, WHITE, self.rect.centerx, self.rect.centery)

    def hit(
        self,
        pos
    ):

        clicked = (
            self.rect.collidepoint(
                pos
            )
        )

        if (
            clicked
            and Btn.click_callback
            is not None
        ):

            Btn.click_callback()

        return clicked