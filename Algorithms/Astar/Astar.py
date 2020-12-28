#A star algorithm is an informed algorithm, it knows where the end point and starting point both are
#F(n) = G(n) + H(n)
#Where H(n) is a guess of how far the current node is from the end node, WIll be calculated using Manhattan equation not Euclidean
#Where G(n) is the shortest path of start node to current node
import pygame
import math
from queue import PriorityQueue

WIDTH = 700
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Visualizer")
PURPLE = (149, 46, 153)
RED = (255,0,0)
GREEN = (0,255,0)
ORANGE = (255,165,0)
GREY = (128,128,128)
AQUA = (64,224,208)
WHITE = (255,255,255)
BLACK = (0,0,0)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = BLACK
        self.adjacent = []
        self.width = width
        self.total_rows = total_rows
    
    def get_pos(self):
        return self.row, self.col
    
    def is_closed(self):
        return self.color == PURPLE
    
    def isopen(self):
        return self.color == RED
    
    def is_barrier(self):
        return self.color == WHITE
    
    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == GREEN
    
    def reset(self):
        self.color = BLACK

    def make_closed(self):
        self.color = PURPLE
    
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

    def __lt__(self, other):
        return False


#Manhattan distance equation used
def distance(p1, p2):
    x1,y1 = p1
    x2,y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(visited, current, draw):
    while current in visited:
        current = visited[current]
        current.make_path()
        draw()

#Main algorithm
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start)) #Passing in: F(n), counter, node. Counter will be used incases of tie
    visited = {}
    open_set_hash = {start}

    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = distance(start.get_pos(), end.get_pos())
    

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(visited, end, draw)
            end.make_end()
            start.make_start()
            return True
        
        for adjacent in current.adjacent:
            temp_g = g_score[current] + 1
            if g_score[adjacent] > temp_g:
                
                visited[adjacent] = current
                g_score[adjacent] = temp_g
                f_score[adjacent] = temp_g + distance(adjacent.get_pos(), end.get_pos())  
                
                if adjacent not in open_set_hash:
                    count += 1
                    open_set.put((f_score[adjacent], count, adjacent))
                    open_set_hash.add(adjacent)
                    adjacent.make_open()
        draw()

        if current != start:
            current.make_closed()
    
    return False

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

                    algorithm(lambda: draw(win, grid, ROWS, width) , grid, start, end)
                
                #To clear the grid without closing the application each time
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WIN, WIDTH)