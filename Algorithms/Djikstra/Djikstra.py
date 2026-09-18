import asyncio
import heapq
from itertools import count

import pygame

CELL    = 16
ROWS    = 30
GRID_PX = CELL * ROWS
HUD_PX  = 112
WIDTH   = GRID_PX
HEIGHT  = GRID_PX + HUD_PX

INF = float("inf")

TERRAIN = {
    "open":  (1,   (25, 25, 28)),
    "grass": (2,   (38, 104, 58)),
    "mud":   (5,   (112, 78, 40)),
    "water": (10,  (28, 62, 140)),
    "wall":  (INF, (232, 232, 232)),
}

BRUSH_KEYS = {
    pygame.K_1: "open",
    pygame.K_2: "grass",
    pygame.K_3: "mud",
    pygame.K_4: "water",
    pygame.K_5: "wall",
}

GREY     = (70, 70, 74)
FRONTIER = (196, 62, 62)
CLOSED   = (96, 66, 148)
PATH     = (64, 224, 208)
START_C  = (255, 165, 0)
END_C    = (0, 230, 90)
CURRENT  = (255, 235, 90)
HUD_BG   = (16, 16, 18)
TEXT     = (222, 222, 226)
DIM      = (120, 120, 126)
BTN_BG   = (44, 44, 50)
BTN_HOV  = (70, 70, 80)
BTN_DIS  = (26, 26, 30)
BTN_EDGE = (96, 96, 104)

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dijkstra Visualiser")
CLOCK = pygame.time.Clock()

FONT  = pygame.font.Font(None, 19)
SMALL = pygame.font.Font(None, 17) 

BRUSH_Y, BRUSH_H = GRID_PX + 6,  24
ACT_Y,   ACT_H   = GRID_PX + 36, 28
SWATCH = 11

BRUSH_ORDER = ["open", "grass", "mud", "water", "wall", "start", "end"]

BRUSH_LABELS = {}
for _name, (_cost, _col) in TERRAIN.items():
    BRUSH_LABELS[_name] = _name if _cost == INF else f"{_name} {_cost}"
BRUSH_LABELS["start"] = "start"
BRUSH_LABELS["end"]   = "end"

BRUSH_SWATCH = {name: col for name, (_c, col) in TERRAIN.items()}
BRUSH_SWATCH["start"] = START_C
BRUSH_SWATCH["end"]   = END_C


def _layout_brushes(y, h):
    for pad, gap in ((9, 5), (7, 4), (5, 3), (3, 2)):
        widths = []
        for name in BRUSH_ORDER:
            text_w = SMALL.size(BRUSH_LABELS[name])[0]
            w = pad + SWATCH + 5 + text_w + pad
            widths.append(w)
        total = sum(widths) + gap * (len(widths) - 1)
        if total <= WIDTH - 8:
            rects = {}
            x = (WIDTH - total) // 2
            for name, w in zip(BRUSH_ORDER, widths):
                rects[name] = pygame.Rect(x, y, w, h)
                x += w + gap
            return rects
    rects = {}
    x = 4
    for name, w in zip(BRUSH_ORDER, widths):
        rects[name] = pygame.Rect(x, y, w, h)
        x += w + 2
    return rects


def _layout_actions(y, h, gap=6):
    """Center the 4 action buttons as a group"""
    keys = ["step", "step10", "run", "clear"]
    widths = [92, 96, 108, 92]
    total = sum(widths) + gap * (len(widths) - 1)
    x = (WIDTH - total) // 2
    rects = {}
    for k, w in zip(keys, widths):
        rects[k] = pygame.Rect(x, y, w, h)
        x += w + gap
    return rects


BRUSH_BUTTONS = _layout_brushes(BRUSH_Y, BRUSH_H)
ACTION_BUTTONS = _layout_actions(ACT_Y, ACT_H)


class Node:
    __slots__ = ("row", "col", "x", "y", "terrain", "cost",
                 "adjacent", "state", "dist", "prev", "finalised")

    def __init__(self, row, col):
        self.row, self.col = row, col
        self.x, self.y = row * CELL, col * CELL
        self.adjacent = []
        self.set_terrain("open")
        self.reset_search()

    def set_terrain(self, name):
        self.terrain = name
        self.cost = TERRAIN[name][0]

    @property
    def is_wall(self):
        return self.terrain == "wall"

    def reset_search(self):
        self.state = None
        self.dist = INF
        self.prev = None
        self.finalised = False

    def update_adjacent(self, grid):
        self.adjacent = []
        r, c = self.row, self.col
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < ROWS and not grid[nr][nc].is_wall:
                self.adjacent.append(grid[nr][nc])

    def draw(self, win, start, end, current):
        pygame.draw.rect(win, TERRAIN[self.terrain][1],
                         (self.x, self.y, CELL, CELL))
        overlay = None
        if self is start:
            overlay = START_C
        elif self is end:
            overlay = END_C
        elif self.state == "path":
            overlay = PATH
        elif self.state == "frontier":
            overlay = FRONTIER
        elif self.state == "closed":
            overlay = CLOSED

        if overlay:
            pad = 3
            pygame.draw.rect(win, overlay,
                             (self.x + pad, self.y + pad,
                              CELL - 2 * pad, CELL - 2 * pad))
        if self is current:
            pygame.draw.rect(win, CURRENT, (self.x, self.y, CELL, CELL), 2)


def make_grid():
    return [[Node(r, c) for c in range(ROWS)] for r in range(ROWS)]

def clear_search_state(grid):
    for row in grid:
        for node in row:
            node.reset_search()

class Search:
    def __init__(self, grid, start, end):
        self.grid, self.start, self.end = grid, start, end
        for row in grid:
            for node in row:
                node.reset_search()
                node.update_adjacent(grid)
        self.tiebreak = count()
        start.dist = 0
        self.pq = [(0, next(self.tiebreak), start)]
        self.phase = "search"
        self.expanded = 0
        self.path_cost = "-"
        self.current = None
        self.path_nodes = []
        self.path_i = 0
        self.step_no = 0
        self.note = "ready - press Step"

    def can_step(self):
        return self.phase != "done"

    def step(self):
        if self.phase == "done":
            return False
        if self.phase == "search":
            self._step_search()
        else:
            self._step_path()
        self.step_no += 1
        return True

    def _step_search(self):
        node = None
        while self.pq:
            _, _, cand = heapq.heappop(self.pq)
            if not cand.finalised:
                node = cand
                break
        if node is None:
            self.phase = "done"
            self.current = None
            self.path_cost = "no path"
            self.note = "queue empty - target unreachable"
            return
        node.finalised = True
        node.state = "closed"
        self.current = node
        self.expanded += 1
        if node is self.end:
            self.path_cost = node.dist
            chain, p = [], node.prev
            while p is not None and p is not self.start:
                chain.append(p)
                p = p.prev
            self.path_nodes = chain
            self.path_i = 0
            self.phase = "path"
            self.note = "target finalised - tracing path"
            return
        relaxed = 0
        for nb in node.adjacent:
            if nb.finalised:
                continue
            alt = node.dist + nb.cost
            if alt < nb.dist:
                nb.dist = alt
                nb.prev = node
                nb.state = "frontier"
                heapq.heappush(self.pq, (alt, next(self.tiebreak), nb))
                relaxed += 1
        self.note = (f"pop ({node.row},{node.col}) d={node.dist}"
                     f"  relaxed {relaxed}")

    def _step_path(self):
        if self.path_i >= len(self.path_nodes):
            self.phase = "done"
            self.current = None
            self.note = f"done - shortest path cost {self.path_cost}"
            return
        n = self.path_nodes[self.path_i]
        n.state = "path"
        self.current = n
        self.path_i += 1
        self.note = "tracing path back through prev pointers"

def draw_grid_lines(win):
    for i in range(ROWS + 1):
        p = i * CELL
        pygame.draw.line(win, GREY, (0, p), (GRID_PX, p))
        pygame.draw.line(win, GREY, (p, 0), (p, GRID_PX))

def draw_brush_button(win, name, rect, selected, mouse):
    bg = BTN_HOV if selected or rect.collidepoint(mouse) else BTN_BG
    pygame.draw.rect(win, bg, rect)
    pygame.draw.rect(win, CURRENT if selected else BTN_EDGE, rect, 2 if selected else 1)
    swatch = pygame.Rect(0, 0, SWATCH, SWATCH)
    swatch.midleft = (rect.x + 7, rect.centery)
    pygame.draw.rect(win, BRUSH_SWATCH[name], swatch)
    pygame.draw.rect(win, BTN_EDGE, swatch, 1)
    surf = SMALL.render(BRUSH_LABELS[name], True, TEXT)
    win.blit(surf, surf.get_rect(midleft=(swatch.right + 5, rect.centery)))

def draw_button(win, rect, label, enabled, mouse):
    if not enabled:
        bg = BTN_DIS
    elif rect.collidepoint(mouse):
        bg = BTN_HOV
    else:
        bg = BTN_BG
    pygame.draw.rect(win, bg, rect)
    pygame.draw.rect(win, BTN_EDGE, rect, 1)
    surf = FONT.render(label, True, TEXT if enabled else DIM)
    win.blit(surf, surf.get_rect(center=rect.center))

def button_specs(search, start, end):
    has = search is not None
    return {
        "step":   (ACTION_BUTTONS["step"],   "Step >",   has and search.can_step()),
        "step10": (ACTION_BUTTONS["step10"], "Step x10", has and search.can_step()),
        "run":    (ACTION_BUTTONS["run"],
                   "Reset search" if has else "Start",
                   has or bool(start and end)),
        "clear":  (ACTION_BUTTONS["clear"],  "Clear",    True),
    }

def draw_hud(win, brush, search, start, end):
    y0 = GRID_PX
    pygame.draw.rect(win, HUD_BG, (0, y0, WIDTH, HUD_PX))
    pygame.draw.line(win, BTN_EDGE, (0, y0), (WIDTH, y0))
    mouse = pygame.mouse.get_pos()

    for name, rect in BRUSH_BUTTONS.items():
        draw_brush_button(win, name, rect, brush == name, mouse)

    for rect, label, enabled in button_specs(search, start, end).values():
        draw_button(win, rect, label, enabled, mouse)

    if search is None:
        if start is None:
            stat = "pick the start brush, then click a cell"
        elif end is None:
            stat = "pick the end brush, then click a cell"
        else:
            stat = "ready - press Start or SPACE"
        note = "keys: 1-5 terrain   S/E start,end   SPACE step   C clear"
    else:
        stat = (f"step {search.step_no}   phase {search.phase}   "
                f"queue {len(search.pq)}   finalised {search.expanded}   "
                f"cost {search.path_cost}")
        note = search.note

    stat_surf = FONT.render(stat, True, TEXT)
    note_surf = FONT.render(note, True, DIM)
    win.blit(stat_surf, stat_surf.get_rect(centerx=WIDTH//2, y=y0 + 72))
    win.blit(note_surf, note_surf.get_rect(centerx=WIDTH//2, y=y0 + 90))

def draw(win, grid, start, end, brush, search):
    win.fill((0, 0, 0))
    current = search.current if search else None
    for row in grid:
        for node in row:
            node.draw(win, start, end, current)
    draw_grid_lines(win)
    draw_hud(win, brush, search, start, end)
    pygame.display.update()

def cell_at(pos):
    mx, my = pos
    if not (0 <= mx < GRID_PX and 0 <= my < GRID_PX):
        return None
    return mx // CELL, my // CELL

async def main():
    grid = make_grid()
    start = end = None
    search = None
    brush = "start" 
    run = True
    while run:
        CLOCK.tick(60)
        draw(WIN, grid, start, end, brush, search)
        cell = cell_at(pygame.mouse.get_pos())
        if cell:
            left, _middle, right = pygame.mouse.get_pressed()
            if left or right:
                if search is not None:
                    search = None
                    clear_search_state(grid)
                node = grid[cell[0]][cell[1]]
                if right:
                    node.set_terrain("open")
                    if node is start:
                        start = None
                    if node is end:
                        end = None
                elif brush == "start":
                    if node is not end:
                        start = node
                        node.set_terrain("open")
                elif brush == "end":
                    if node is not start:
                        end = node
                        node.set_terrain("open")
                elif node is not start and node is not end:
                    node.set_terrain(brush)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                hit_brush = False
                for name, rect in BRUSH_BUTTONS.items():
                    if rect.collidepoint(event.pos):
                        brush = name
                        hit_brush = True
                        break
                if not hit_brush:
                    for key, (rect, _label, enabled) in button_specs(search, start, end).items():
                        if not (enabled and rect.collidepoint(event.pos)):
                            continue
                        if key == "step":
                            search.step()
                        elif key == "step10":
                            for _ in range(10):
                                if not search.step():
                                    break
                        elif key == "run":
                            if search is None:
                                search = Search(grid, start, end)
                            else:
                                search = None
                                clear_search_state(grid)
                        elif key == "clear":
                            grid = make_grid()
                            start = end = search = None
                            brush = "start"
                        break 
            elif event.type == pygame.KEYDOWN:
                if event.key in BRUSH_KEYS:
                    brush = BRUSH_KEYS[event.key]
                elif event.key == pygame.K_s:
                    brush = "start"
                elif event.key == pygame.K_e:
                    brush = "end"
                elif event.key == pygame.K_c:
                    grid = make_grid()
                    start = end = search = None
                    brush = "start"
                elif event.key in (pygame.K_SPACE, pygame.K_RIGHT):
                    if search is None:
                        if start and end:
                            search = Search(grid, start, end)
                    else:
                        search.step()
        await asyncio.sleep(0)
    pygame.quit()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        asyncio.ensure_future(main())
