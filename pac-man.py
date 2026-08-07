from mazegenerator import MazeGenerator


def draw_maze(maze_gen: MazeGenerator, show_path: bool = False) -> None:
    grid = maze_gen.maze
    height = len(grid)
    width = len(grid[0])
    entry_x, entry_y = maze_gen.maze_entry
    exit_x, exit_y = maze_gen.maze_exit

    canvas = [["█" for _ in range(width * 2 + 1)]
              for _ in range(height * 2 + 1)]

    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            gx, gy = x * 2 + 1, y * 2 + 1
            canvas[gy][gx] = " "

            if not (cell & 1):
                canvas[gy - 1][gx] = " "
            if not (cell & 2):
                canvas[gy][gx + 1] = " "
            if not (cell & 4):
                canvas[gy + 1][gx] = " "
            if not (cell & 8):
                canvas[gy][gx - 1] = " "

    if show_path and isinstance(maze_gen.shortest_path, str):
        cx, cy = entry_x * 2 + 1, entry_y * 2 + 1
        moves = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}
        for move in maze_gen.shortest_path:
            dx, dy = moves[move]
            canvas[cy + dy][cx + dx] = "·"
            cx += dx * 2
            cy += dy * 2
            canvas[cy][cx] = "·"

    # Marcar Entrada y Salida
    canvas[entry_y * 2 + 1][entry_x * 2 + 1] = "E"
    canvas[exit_y * 2 + 1][exit_x * 2 + 1] = "X"

    # Imprimir en la terminal
    for row in canvas:
        print("".join(row))


maze_gen = MazeGenerator(size=(47, 47), entry_cell=(0, 0),
                         exit_cell=(5, 5), perfect=False, seed=0)

maze_grid = maze_gen.maze
shortest_path = maze_gen.shortest_path

print(f"Maze dimensions: {len(maze_grid[0])}x{len(maze_grid)}")
print(f"Entry: {maze_gen.maze_entry}, Exit: {maze_gen.maze_exit}")
print(f"Shortest path length: {len(shortest_path)}")
draw_maze(maze_gen, show_path=True)
