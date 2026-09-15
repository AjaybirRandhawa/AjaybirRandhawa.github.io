import asyncio
import heapq
from itertools import count

import pygame

CELL    = 20
ROWS    = 30
GRID_PX = CELL * ROWS
# enough for legend + buttons + two text lines
HUD_PX  = 98
WIDTH   = GRID_PX
HEIGHT  = GRID_PX + HUD_PX

INF = float("inf")

# walls are just terrain with infinite cost, saves having a separate flag
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

# separate from TERRAIN because dict order is insertion order and I want the
# legend sorted by cost, not by whatever order I happened to type them in
LEGEND_ORDER = [("1", "open"), ("2", "grass"), ("3", "mud"),
                ("4", "water"), ("5", "wall")]

# ----------------------------------------------------------------- colours
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

FONT = pygame.font.Font(None, 19)

# Button rects, worked out by hand until they stopped overlapping.
# x positions are cumulative: 8, 8+92+6, etc.
BTN_Y, BTN_H = GRID_PX + 26, 28

def _btn(x, w):
    return pygame.Rect(x, BTN_Y, w, BTN_H)

BUTTONS = {
    "step":   _btn(8,    92),
    "step10": _btn(106,  96),
    "run":    _btn(208, 108),
    "clear":  _btn(324,  92),
}


class Node:
    """
    One cell of the grid
    """

    __slots__ = ("row", "col", "x", "y", "terrain", "cost",
                 "adjacent", "state", "dist", "prev", "finalised")

    def __init__(self, row, col):
        self.row, self.col = row, col
        # note: row maps to x, col maps to y. Confusing, but it matches the
        # order cell_at() returns and I'd rather keep them consistent than
        # rename everything now
        self.x, self.y = row * CELL, col * CELL
        self.adjacent = []
        self.set_terrain("open")
        self.reset_search()

    def set_terrain(self, name):
        self.terrain = name
        self.cost = TERRAIN[name][0]

    @property
    def is_wall(self):
        # was comparing colours for this originally, which broke the moment
        # the search painted over a cell. Terrain name is the source of truth
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
        # terrain underneath, search state as a smaller square on top, so you
        # can still see the mud/water the algorithm is trying to avoid
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
    """
    Dijkstra implementation
    """

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
        # heapq has no decrease, so when a node's distance improves we
        # push a second entry instead of editing the old one. The outdated
        # entry is still in the heap, so throw away anything already closed.
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


def draw_legend(win, brush, y):
    x = 8
    for key, name in LEGEND_ORDER:
        cost, colour = TERRAIN[name]
        swatch = pygame.Rect(x, y + 2, 12, 12)
        pygame.draw.rect(win, colour, swatch)
        pygame.draw.rect(win, BTN_EDGE, swatch, 1)

        if brush == name:
            pygame.draw.rect(win, CURRENT, swatch.inflate(4, 4), 1)

        label = f"{key} {name}" if cost == INF else f"{key} {name}:{cost}"
        surf = FONT.render(label, True, TEXT)
        win.blit(surf, (x + 17, y))
        x += 17 + surf.get_width() + 12

    tag = {"start": "START", "end": "END"}.get(brush)
    if tag:
        win.blit(FONT.render(f"brush: {tag}", True, CURRENT), (x, y))


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
        "step":   (BUTTONS["step"],   "Step >",   has and search.can_step()),
        "step10": (BUTTONS["step10"], "Step x10", has and search.can_step()),
        "run":    (BUTTONS["run"],
                   "Reset search" if has else "Start",
                   has or bool(start and end)),
        "clear":  (BUTTONS["clear"],  "Clear",    True),
    }


def draw_hud(win, brush, search, start, end):
    y0 = GRID_PX
    pygame.draw.rect(win, HUD_BG, (0, y0, WIDTH, HUD_PX))
    pygame.draw.line(win, BTN_EDGE, (0, y0), (WIDTH, y0))

    draw_legend(win, brush, y0 + 5)

    mouse = pygame.mouse.get_pos()
    for rect, label, enabled in button_specs(search, start, end).values():
        draw_button(win, rect, label, enabled, mouse)

    if search is None:
        stat = "no search - place START (S) and END (E), then Start"
        note = "S start  E end  LMB paint  RMB erase  SPACE step  C clear"
    else:
        stat = (f"step {search.step_no}   phase {search.phase}   "
                f"queue {len(search.pq)}   finalised {search.expanded}   "
                f"cost {search.path_cost}")
        note = search.note

    win.blit(FONT.render(stat, True, TEXT), (8, y0 + 60))
    win.blit(FONT.render(note, True, DIM), (8, y0 + 78))


def draw(win, grid, start, end, brush, search):
    win.fill((0, 0, 0))

    current = search.current if search else None
    for row in grid:
        for node in row:
            node.draw(win, start, end, current)

    draw_grid_lines(win)
    draw_hud(win, brush, search, start, end)
    pygame.display.update()


# ------------------------------------------------------------------- input
def cell_at(pos):
    mx, my = pos
    if not (0 <= mx < GRID_PX and 0 <= my < GRID_PX):
        return None
    return mx // CELL, my // CELL


async def main():
    grid = make_grid()
    start = end = None
    search = None
    brush = "wall"
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
                elif event.key in (pygame.K_SPACE, pygame.K_RIGHT):
                    if search is None:
                        if start and end:
                            search = Search(grid, start, end)
                    else:
                        search.step()

        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
