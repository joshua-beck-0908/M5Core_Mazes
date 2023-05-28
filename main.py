import vectorio
import displayio
import digitalio
import mazes
import board
import time
import random
import alarm

class Player():
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    vectors = [[(0, 10), (5, 0), (10, 10)], [(0, 0), (10, 5), (0, 10)], [(0, 0), (5, 10), (10, 0)], [(10, 0), (0, 5), (10, 10)]]
    direction = SOUTH
    
    def __init__(self, maze):
        self.direction = Player.SOUTH
        self.playerColour = displayio.Palette(2)
        self.playerColour[0] = 0xFFFF55
        self.sprite = vectorio.Polygon(pixel_shader=self.playerColour, points=self.vectors[self.direction], x=0, y=0)
        self.maze = maze
        self.maze.addPlayer(self)
        
    def rotateLeft(self):
        self.direction = (self.direction - 1) % 4
        self.sprite.points = self.vectors[self.direction]    
        
    def rotateRight(self):
        self.direction = (self.direction + 1) % 4
        self.sprite.points = self.vectors[self.direction]
        
    def move(self):
        newX = self.sprite.x
        newY = self.sprite.y
        if self.direction == Player.NORTH:
            newY -= 10
        elif self.direction == Player.EAST:
            newX += 10
        elif self.direction == Player.SOUTH:
            newY += 10
        elif self.direction == Player.WEST:
            newX -= 10
        if not self.maze.objectAt(newX, newY):
            self.sprite.x = newX
            self.sprite.y = newY

def lightSleep(buttons):
    print('Deep sleep')
    buttons.io[buttons.pins.index(board.BTN_B)].deinit()
    pinWake = alarm.pin.PinAlarm(pin=board.BTN_B, value=False, pull=False)
    board.DISPLAY.brightness = 0.0
    alarm.light_sleep_until_alarms(pinWake)
    buttons.io[buttons.pins.index(board.BTN_B)] = digitalio.DigitalInOut(board.BTN_B)
    buttons.io[buttons.pins.index(board.BTN_B)].direction = digitalio.Direction.INPUT
    board.DISPLAY.brightness = 0.5
    while buttons.io[buttons.pins.index(board.BTN_B)].value == False:
        time.sleep(0.1)
        
    
class InputButtons:
    LEFT = 0
    CENTRE = 1
    RIGHT = 2
    WAIT = 3

    timeoutSeconds = 20
    
    def __init__(self):
        self.keys = []
        self.pins = [board.BTN_A, board.BTN_B, board.BTN_C]
        self.io = [digitalio.DigitalInOut(pin) for pin in self.pins]
        for pin in self.io:
            pin.direction = digitalio.Direction.INPUT
        self.state = [True for i in range(3)]
        
    def getKey(self):
        if len(self.keys) > 0:
            return self.keys.pop(0)
        return None
    
    def waitKey(self):
        waitTime = 0
        key = self.getKey()

        while key == None:
            time.sleep(0.1)
            waitTime += 0.1
            self.update()
            key = self.getKey()
            if waitTime > InputButtons.timeoutSeconds:
                return InputButtons.WAIT
        return key
    
    def update(self):
        for i, pin in enumerate(self.io):
            if pin.value != self.state[i]:
                self.state[i] = pin.value
                if not pin.value:
                    self.keys.append(i)

class Maze:
    def __init__(self, number):
        self.number = number
        self.maze = mazes.mazeData[number]
        self.width = 20
        self.height = 20
        self.wallWidth = 10
        self.wallHeight = 10
        self.shader = displayio.Palette(2)
        self.shader[0] = random.randint(0, 0xFFFFFF)
        self.shader[1] = 0x654321
        self.player = None
        self.walls = displayio.Group()
        self.objects = displayio.Group()
        self.objects.append(self.walls)
        self.emptyGroup = displayio.Group()
        self._create_walls()
        
    def _create_walls(self):
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == 0:
                    self.walls.append(vectorio.Rectangle(pixel_shader=self.shader, width=self.wallWidth, height=self.wallHeight, x=x*self.wallWidth, y=y*self.wallHeight))
    def show(self):
        board.DISPLAY.root_group = self.objects
        
    def hide(self):
        board.DISPLAY.root_group = self.emptyGroup
        
    def addPlayer(self, player):
        self.player = player
        self.objects.append(player.sprite)
        
    def objectAt(self, x, y):
        for obj in self.walls:
            if obj.x == x and obj.y == y:
                return True
        return False
        
def main():
    board.DISPLAY.brightness = 0.5
    maze = Maze(random.randint(0, len(mazes.mazeData)-1))
    maze.show()
    buttons = InputButtons()
    player = Player(maze)
    while True:
        key = buttons.waitKey()
        if key == buttons.CENTRE:
            player.move()
        elif key == buttons.LEFT:
            player.rotateLeft()
        elif key == buttons.RIGHT:
            player.rotateRight()
        elif key == buttons.WAIT:
            lightSleep(buttons)


    
if __name__ == "__main__":
    main()