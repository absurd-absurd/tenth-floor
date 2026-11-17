"""The Library: circulation desk, the stacks, the reading room.

West elevator -> Circulation Desk -> The Stacks -> Reading Room -> East elevator.
The floor's digit is in the Special Collections cabinet, up on the high ledge in the Reading Room.
"""
import math

import pygame

from engine import config as C
from engine.bots import PatrolBot, Zapper
from engine.kit import Bookshelf, CeilingLight, Crusher, Desk, Drone, FloorLaser, Plant, Poster, Sign, Window
from engine.room import Furniture, Lift, Platform, Room

NAME = "The Library"
AUTHOR = "Fayth Elisa Navarro"

WOOD = (92, 62, 42)
WOOD_DARK = (62, 42, 30)
WALL_LIB = (58, 46, 40)
GREEN_LAMP = (60, 150, 90)


def tone(f, col):
    """Greyer once searched, like the kit parts."""
    return tuple(int(c * 0.7) for c in col) if f.searched else col


def library_wall(surf, seed):
    """Dark panelled walls, a wainscot rail, and shelves of book spines in the dark behind."""
    surf.fill(WALL_LIB)
    for x in range(0, C.W, 160):                                   # wall panels
        pygame.draw.rect(surf, (66, 52, 45), (x + 10, 130, 140, 250), border_radius=3)
        pygame.draw.rect(surf, (48, 38, 33), (x + 10, 130, 140, 250), 2, border_radius=3)
    pygame.draw.rect(surf, WOOD_DARK, (0, 400, C.W, 100))            # wainscot
    pygame.draw.line(surf, (120, 84, 56), (0, 400), (C.W, 400), 4)
    cols = [(110, 50, 50), (50, 80, 110), (130, 110, 60), (60, 95, 70), (95, 65, 105)]
    k = seed
    for y in (150, 205, 260, 315):                                  # faint book spines on the panels
        x = 20
        while x < C.W - 20:
            w = 5 + (k * 7) % 6
            if (x // 160) % 2 == seed % 2:
                c = cols[k % len(cols)]
                pygame.draw.rect(surf, tuple(int(v * 0.55) for v in c), (x, y, w, 40))
            x += w + 1
            k += 3


# --- furniture with a library look (the searchable area is self.rect) ---

class CirculationDesk(Furniture):
    def __init__(self, x, y, holds_piece=False):
        super().__init__(x, y, 170, 66, "circulation desk", holds_piece)

    def draw(self, surf):
        r = self.rect
        pygame.draw.rect(surf, tone(self, WOOD), r, border_radius=3)
        pygame.draw.rect(surf, tone(self, (120, 84, 56)), (r.left - 6, r.top, r.width + 12, 10), border_radius=2)
        for x in range(r.left + 16, r.right - 10, 38):
            pygame.draw.rect(surf, tone(self, WOOD_DARK), (x, r.top + 18, 26, r.height - 26), 2)
        pygame.draw.rect(surf, (30, 32, 38), (r.left + 20, r.top - 34, 44, 30), border_radius=3)   # old monitor
        pygame.draw.rect(surf, (70, 140, 120), (r.left + 25, r.top - 30, 34, 20))
        pygame.draw.rect(surf, (200, 190, 160), (r.right - 60, r.top - 8, 34, 8))                 # date stamp pad
        pygame.draw.rect(surf, C.INK, r, 2, border_radius=3)


class ReturnBin(Furniture):
    def __init__(self, x, y, holds_piece=False):
        super().__init__(x, y, 60, 74, "book return", holds_piece)
        self._label = pygame.font.Font(None, 16).render("RETURNS", True, (210, 210, 220))

    def draw(self, surf):
        r = self.rect
        pygame.draw.rect(surf, tone(self, (60, 70, 96)), r, border_radius=6)
        pygame.draw.rect(surf, (20, 22, 28), (r.left + 10, r.top + 14, r.width - 20, 8), border_radius=2)
        pygame.draw.rect(surf, C.INK, r, 2, border_radius=6)
        surf.blit(self._label, (r.centerx - self._label.get_width() // 2, r.top + 34))


class CardCatalog(Furniture):
    def __init__(self, x, y, holds_piece=False):
        super().__init__(x, y, 84, 92, "card catalog", holds_piece)

    def draw(self, surf):
        r = self.rect
        pygame.draw.rect(surf, tone(self, (128, 88, 54)), r, border_radius=2)
        for i in range(4):
            for j in range(5):
                d = pygame.Rect(r.left + 6 + i * 19, r.top + 6 + j * 17, 16, 13)
                pygame.draw.rect(surf, tone(self, (150, 108, 70)), d)
                pygame.draw.rect(surf, (230, 222, 196), (d.centerx - 4, d.top + 3, 8, 4))  # label card
                pygame.draw.circle(surf, (200, 170, 90), (d.centerx, d.bottom - 3), 1)
        pygame.draw.rect(surf, C.INK, r, 2, border_radius=2)


class BookCart(Furniture):
    def __init__(self, x, y, holds_piece=False):
        super().__init__(x, y, 80, 60, "book cart", holds_piece)

    def draw(self, surf):
        r = self.rect
        frame = tone(self, (150, 150, 158))
        for y in (r.top + 20, r.bottom - 14):
            pygame.draw.rect(surf, frame, (r.left, y, r.width, 5))
        cols = [(170, 60, 60), (60, 110, 170), (200, 170, 70), (80, 140, 90)]
        for k, x in enumerate(range(r.left + 4, r.right - 8, 9)):
            h = 14 + (k * 5) % 7
            pygame.draw.rect(surf, tone(self, cols[k % 4]), (x, r.top + 20 - h, 7, h))
        for x in (r.left + 2, r.right - 6):
            pygame.draw.line(surf, frame, (x + 2, r.top + 6), (x + 2, r.bottom - 6), 3)
            pygame.draw.circle(surf, (30, 30, 34), (x + 2, r.bottom - 4), 5)
        pygame.draw.line(surf, frame, (r.right - 4, r.top + 6), (r.right + 10, r.top - 4), 3)    # handle


class ReadingTable(Furniture):
    """A long table with two green banker's lamps."""

    def __init__(self, x, y, holds_piece=False):
        super().__init__(x, y, 170, 44, "reading table", holds_piece)

    def draw(self, surf):
        r = self.rect
        top = tone(self, (120, 82, 52))
        pygame.draw.rect(surf, top, (r.left, r.top, r.width, 10), border_radius=2)
        pygame.draw.rect(surf, C.INK, (r.left, r.top, r.width, 10), 1, border_radius=2)
        for x in (r.left + 8, r.right - 16):
            pygame.draw.rect(surf, tone(self, (140, 98, 62)), (x, r.top + 10, 8, r.height - 10))
            pygame.draw.rect(surf, C.INK, (x, r.top + 10, 8, r.height - 10), 1)
        for lx in (r.left + 40, r.right - 50):
            pygame.draw.line(surf, (200, 170, 90), (lx + 5, r.top), (lx + 5, r.top - 16), 2)
            pygame.draw.ellipse(surf, tone(self, GREEN_LAMP), (lx - 8, r.top - 26, 26, 12))
            pygame.draw.circle(surf, (255, 236, 170), (lx + 5, r.top - 16), 3)            # bulb under the shade
        pygame.draw.rect(surf, (225, 220, 200), (r.centerx - 14, r.top - 4, 28, 4))             # open book


class ArchiveCabinet(Furniture):
    """Special Collections: a locked steel flat-file cabinet with a little brass plate."""

    def __init__(self, x, y, holds_piece=False):
        super().__init__(x, y, 70, 96, "special collections", holds_piece)

    def draw(self, surf):
        r = self.rect
        pygame.draw.rect(surf, tone(self, (84, 96, 92)), r, border_radius=3)
        for j in range(5):
            d = pygame.Rect(r.left + 6, r.top + 8 + j * 17, r.width - 12, 13)
            pygame.draw.rect(surf, tone(self, (104, 118, 112)), d, border_radius=2)
            pygame.draw.line(surf, (40, 44, 44), (d.centerx - 10, d.centery), (d.centerx + 10, d.centery), 2)
        pygame.draw.rect(surf, (200, 168, 80), (r.centerx - 14, r.top - 12, 28, 8))             # brass plate
        pygame.draw.rect(surf, C.INK, r, 2, border_radius=3)


# --- the rooms ---

class CirculationDesk_(Room):
    title = "Circulation Desk"

    def build(self):
        self.decor += [Sign(330, 46, "LIBRARY", (230, 205, 150)), Window(620, 120, seed=3),
                       CeilingLight(300), CeilingLight(700), Poster(150, 150, "QUIET", (90, 120, 80))]
        self.furniture += [CirculationDesk(330, C.FLOOR_Y), ReturnBin(560, C.FLOOR_Y),
                           CardCatalog(660, C.FLOOR_Y), Plant(800, C.FLOOR_Y)]
        # the anti-theft gate by the door zaps on and off; the night guard rolls along the desk
        self.hazards.append(Zapper(230, y_top=380, y_bottom=C.FLOOR_Y, on_time=1.2, off_time=1.6))
        self.hazards.append(PatrolBot(500, C.FLOOR_Y, left=300, right=860, speed=70))
        self.gate = pygame.Rect(214, 380, 32, 120)

    def draw_background(self, surf):
        library_wall(surf, 0)

    def draw_foreground(self, surf):
        for x in (self.gate.left, self.gate.right - 6):          # the two pillars of the security gate
            pygame.draw.rect(surf, (170, 172, 180), (x, self.gate.top, 6, self.gate.height), border_radius=2)


class TheStacks(Room):
    """Ride the rolling ladder up to the top shelves."""

    title = "The Stacks"

    def build(self):
        self.decor += [Sign(360, 46, "STACKS  A - M", (230, 205, 150)), CeilingLight(220), CeilingLight(640)]
        self.platforms.append(Platform(110, 400, 230))
        self.platforms.append(Platform(450, 290, 260))
        self.lifts.append(Lift(370, y_top=290, y_bottom=C.FLOOR_Y, width=60))   # the rolling library ladder
        self.furniture += [Bookshelf(130, 400), Bookshelf(240, 400),
                           Bookshelf(480, 290), Bookshelf(610, 290), BookCart(740, C.FLOOR_Y)]
        self.hazards.append(PatrolBot(560, 290, left=460, right=700, speed=50, sees=False))
        self.hazards.append(Drone(800, y_top=300, y_bottom=C.FLOOR_Y, speed=80))

    def draw_background(self, surf):
        library_wall(surf, 1)
        for x in range(30, C.W, 110):                              # tall shelves receding in the dark
            pygame.draw.rect(surf, (44, 34, 30), (x, 90, 70, 310))

    def draw_foreground(self, surf):
        lift = self.lifts[0]
        rx = lift.rect.centerx
        for dx in (-22, 22):                                       # the ladder's rails ride with it
            pygame.draw.line(surf, (150, 110, 70), (rx + dx, lift.rect.top), (rx + dx, lift.rect.top - 70), 3)
        for k in range(1, 5):
            y = lift.rect.top - k * 16
            pygame.draw.line(surf, (150, 110, 70), (rx - 22, y), (rx + 22, y), 2)


class ReadingRoom(Room):
    """The digit is in Special Collections, up on the high ledge past the book drop."""

    title = "Reading Room"

    def build(self):
        self.decor += [Sign(330, 46, "READING ROOM", (230, 205, 150)), Window(80, 110, seed=7),
                       Window(470, 110, seed=8), CeilingLight(260), CeilingLight(600)]
        self.platforms.append(Platform(560, 410, 200))
        self.platforms.append(Platform(720, 320, 150))
        self.furniture += [ReadingTable(110, C.FLOOR_Y), ReadingTable(340, C.FLOOR_Y), Plant(680, 410),
                           ArchiveCabinet(785, 320, holds_piece=True)]
        self.hazards.append(FloorLaser(300, 540, on_time=1.3, off_time=1.5))     # motion sensor across the aisle
        self.hazards.append(Crusher(610, y_top=240, y_bottom=410, w=50, h=40))    # the overnight book drop
        self.sign = pygame.font.Font(None, 22).render("SPECIAL COLLECTIONS", True, (220, 196, 120))
        self.dust = pygame.Surface((C.W, 140), pygame.SRCALPHA)

    def draw_background(self, surf):
        library_wall(surf, 2)
        surf.blit(self.sign, (730, 200))
        t = self.time
        a = 30 + int(15 * (1 + math.sin(t * 2)))                  # a little dust in the lamp light
        dust = self.dust
        dust.fill((0, 0, 0, 0))
        for k in range(18):
            x = (k * 53 + int(t * 12 * (1 + k % 3))) % C.W
            pygame.draw.circle(dust, (255, 240, 200, a), (x, (k * 37) % 140), 1)
        surf.blit(dust, (0, 330))


ROOMS = [CirculationDesk_, TheStacks, ReadingRoom]
