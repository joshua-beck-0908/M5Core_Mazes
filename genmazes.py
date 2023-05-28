from calendar import c
import mazegen.maze_generator as mg

mazes = []

for m in range(0, 20):
    maze = []
    mazeImg = mg.generate_maze(15, 11)
    for row in range(1, mazeImg.height):
        maze.append([])
        for col in range(1, mazeImg.width):
            if mazeImg.getpixel((col, row)) == (255, 255, 255):
                maze[row - 1].append(1)
            else:
                maze[row - 1].append(0)
    mazes.append(maze)
with open("mazes.py", "w") as f:
    f.write("mazeData = " + str(mazes))
