import pygame
from collections import deque

WIDTH = 700
pygame.init()

WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Dijktdtra's Visualizer")

RED = (255,0,0)
GREEN = (0,255,0)
ORANGE = (255,165,0)
GREY = (128,128,128)
AQUA = (64,224,208)
WHITE = (255,255,255)
BLACK = (0,0,0)


class Node:
    def __init__(self, row, col, gap, total_rows):
        self.row, self.col = row, col
        self.x, self.y = row*gap, col*gap
        self.adjacent = []
        self.color = BLACK
        self.prev = None
        self.visited = False
        self.width = gap
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col
    
    def is_barrier(self):
        return self.color == WHITE
    
    def reset(self):
        self.color = BLACK
    
    def make_open(self):
        self.color = RED
    
    def make_barrier(self):
        self.color = WHITE
    
    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = GREEN
    
    def make_path(self):
        self.color = AQUA
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_adjacent(self, grid):
        self.adjacent = []
        #Check node below
        if (self.row < self.total_rows - 1) and not grid[self.row + 1][self.col].is_barrier():
            self.adjacent.append(grid[self.row + 1][self.col])
        #Check node above
        if (self.row > 0) and not grid[self.row - 1][self.col].is_barrier():
            self.adjacent.append(grid[self.row - 1][self.col])
        #Check node left
        if (self.col < self.total_rows - 1) and not grid[self.row][self.col + 1].is_barrier():
            self.adjacent.append(grid[self.row][self.col + 1])
        #Check node right
        if (self.col > 0) and not grid[self.row][self.col - 1].is_barrier():
            self.adjacent.append(grid[self.row][self.col - 1])


def algorithm(draw, start, end):
    queue = deque()
    queue.append(start)
    flag = False
    noflag = True
    while len(queue) > 0:
        current = queue.popleft()
        if current == end:
            break
        if flag == False:
            for i in current.adjacent:
                if not i.visited and not i.is_barrier():
                    i.visited = True
                    i.make_open()
                    i.prev = current
                    queue.append(i)
        start.make_start()
        end.make_end()
        draw()
    temp = end.prev
    while temp.prev and temp != start:
        temp.make_path()
        temp = temp.prev 
        draw()

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))

def draw(win, grid, rows, width):
    win.fill(BLACK)

    for row in grid:
        for node in row:
            node.draw(win)
    
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y,x = pos

    row = y // gap
    col = x // gap
    
    return row, col

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None
    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            #Left Mouse Button
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                
                if not start and node != end:
                    start = node
                    start.make_start()
                
                elif not end and node != start:
                    end = node
                    end.make_end()

                elif node != start and node != end:
                    node.make_barrier()
            #Right Mouse Button
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()

                if node== start: start = None
                if node == end: end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and (start and end):
                    for row in grid:
                        for node in row:
                            node.update_adjacent(grid)
                    #Passing in information to algorithm
                    algorithm(lambda: draw(win, grid, ROWS, width), start, end)
                #To clear the grid without closing the application each time
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WIN, WIDTH)