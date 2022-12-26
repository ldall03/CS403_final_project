import multiprocessing
import pathlib
import time
import traceback
import parser
import random
import copy
import operator

# The maximum amount of time that the rover can run in seconds
MAX_RUNTIME = 36000

# Rovers that exist
ROVER_1 = "Rover1"
ROVER_2 = "Rover2"
ROVERS = [
    ROVER_1,
    ROVER_2,
]

# Command file is stored within the rover directory. Here we're building one file
# for each of the rovers defined above
ROVER_COMMAND_FILES = {
    rover_name: pathlib.Path(pathlib.Path(
        __file__).parent.resolve(), f"{rover_name}.txt")
    for rover_name in ROVERS
}
for _, file in ROVER_COMMAND_FILES.items():
    with file.open("w") as f:
        pass

# Constant used to store the rover command for parsing
ROVER_COMMAND = {
    rover_name: None
    for rover_name in ROVERS
}


def get_command(rover_name):
    """Checks, and gets a command from a rovers command file.

    It returns True when something was found, and False
    when nothing was found. It also truncates the contents
    of the file if it found something so that it doesn't
    run the same command again (unless it was re-run from
    the controller/main program).
    """
    fcontent = None
    with ROVER_COMMAND_FILES[rover_name].open() as f:
        fcontent = f.read()
    if fcontent is not None and fcontent:
        ROVER_COMMAND[rover_name] = fcontent
        with ROVER_COMMAND_FILES[rover_name].open("w+") as f:
            pass
        return True
    return False


class Rover:
    ores_type = ["G", "S", "C", "I"]
    # 0 = North, 1 = East, 2 = South, 3 = West
    tiles_around = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    def __init__(self, name):
        self.name = name
        self.map = list()

        self.x_pos = None
        self.y_pos = None
        self.orientation = None
        self.gold = 1
        self.silver = 1
        self.copper = 1
        self.iron = 1
        self.power = 100

        self.map_init()
        self.set_coord()

    def map_init(self, path='map1.txt.txt'):
        # Assume map1.txt.txt is in same directory
        with open(path, "r", encoding="utf-8") as file:
            row = list()
            while True:
                char = file.read(1)
                if not char:
                    # if no \n at end of last line
                    if row:
                        self.map.append(row[:])
                    break
                elif char == "\n":
                    self.map.append(row[:])
                    del row[:]
                else:
                    row.append(char)

    def set_coord(self):
        # will be use whenever new map
        pos = random.choice([(r, c)
                             for r, line in enumerate(self.map)
                             for c, tile in enumerate(line) if tile == " "])
        self.y_pos = pos[0]
        self.x_pos = pos[1]

        # 0 = North, 1 = East, 2 = South, 3 = West
        self.orientation = random.choice(range(0, 4))

    def print_map(self):
        print('\n'.join([''.join(['{:4}'.format(item) for item in row])
                         for row in self.map]))

    def print(self, msg):
        print(f"{self.name}: {msg}")

    def parse_and_execute_cmd(self, command):
        self.print(f"Running command: {command}")
        parse_tree = parser.get_parse_tree(command)  # Parse the command
        parse_tree.show()  # Print parse tree
        # Check semantics
        for child in parse_tree.children:
            child.check_semantics()

    def wait_for_command(self):
        start = time.time()
        while (time.time() - start) < MAX_RUNTIME:
            # Sleep 1 second before trying to check for
            # content again
            self.print("Waiting for command...")
            time.sleep(5)
            if get_command(self.name):
                self.print("Found a command...")
                try:
                    self.parse_and_execute_cmd(ROVER_COMMAND[self.name])
                except Exception as e:
                    self.print(
                        f"Failed to run command: {ROVER_COMMAND[self.name]}")
                    self.print(traceback.format_exc())
                finally:
                    self.print("Finished running command.\n\n")

    # ROVER COMMANDS:

    # getters
    def get_orientation(self):
        return self.orientation

    def get_x_pos(self):
        return self.x_pos

    def get_y_pos(self):
        return self.y_pos

    def get_gold(self):
        return self.gold

    def get_silver(self):
        return self.silver

    def get_copper(self):
        return self.copper

    def get_iron(self):
        return self.iron

    def get_power(self):
        return self.power

    def get_tile(self, x=None, y=None) -> str:
        if (x, y) == (None, None):
            x, y = self.x_pos, self.y_pos
        return self.map[y][x]

    # if no x, y, Will be at current tile
    def set_tile(self, tile_type, x=None, y=None):
        if (x, y) == (None, None):
            x, y = self.x_pos, self.y_pos
        self.map[y][x] = tile_type

    def remove_tile(self, x=None, y=None):
        self.set_tile(" ", x, y)

    # Returns the maximum tiles the rover can advance in the given direction
    # Should always return an integer
    def max_move(self, direction) -> int:
        dir = self.tiles_around[direction]
        steps = 0
        while self.get_tile(self.x_pos+dir[0]*(steps+1), self.y_pos+dir[1]*(steps+1)) != "X":
            steps += 1
        return steps

    # Returns True if the rover can move in the given direction
    # Should always return True or False
    def can_move(self, direction):
        dir = self.tiles_around[direction]
        if self.get_tile(self.x_pos+dir[0], self.y_pos+dir[1]) == "X":
            return False
        return True

    # Change the position to move a given amount of tiles in
    # a given direction. If we cannot because of an x tile then
    # move as far as possible
    def move(self, direction, steps):
        dir = self.tiles_around[direction]
        max = self.max_move(direction)

        if max < steps:
            self.x_pos = self.x_pos + dir[0] * max
            self.y_pos = self.y_pos + dir[1] * max
        else:
            self.x_pos = self.x_pos + dir[0] * steps
            self.y_pos = self.y_pos + dir[1] * steps

    # If on a d tile, switch d tile to g, s, c or i randomly
    def scan(self):
        if self.get_tile() != "D":
            print(f"{self.name} must be on a D tile")
            return
        self.set_tile(random.choice(self.ores_type))
        print(f"{self.name} found {self.get_tile()}! ")

    # When on a g, s, c, or i tile, change tile to ' ' and give some
    # amount of the respective material to  the rover
    def drill(self):
        if self.power < 10:
            print(f"{self.name} need more power to drill")
            return
        elif self.get_tile() not in self.ores_type:
            print(f"{self.name} must be on a ore tile")
            return

        if self.get_tile() == "G":
            self.gold += 1
        elif self.get_tile() == "S":
            self.silver += 1
        elif self.get_tile() == "C":
            self.copper += 1
        else:
            self.iron += 1
        self.remove_tile()
        self.power -= 10

    # Destroy all x tiles in a radius, give a chance to transform
    # to a d tile
    def shockwave(self):
        for tile_coord in self.tiles_around:
            if random.uniform(0, 1) < 0.5:
                self.set_tile("D", self.x_pos +
                              tile_coord[0], self.y_pos+tile_coord[1])
            else:
                self.remove_tile(
                    self.x_pos+tile_coord[0], self.y_pos+tile_coord[1])

    # Transform a ' ' tile to a b tile, use materials from inventory
    def build(self):
        if self.power < 10:
            print(f"{self.name} need more power to build")
            return
        elif self.get_copper() < 1 or self.get_gold() < 1 or self.get_iron() < 1 or self.get_silver() < 1:
            print(f"{self.name} need more ores to build")
            return
        elif self.get_tile() != " ":
            print(f"{self.name} must be on an empty tile")
            return
        self.set_tile("B")
        self.copper -= 1
        self.silver -= 1
        self.gold -= 1
        self.iron -= 1
        self.power -= 10

    # Count and print and return the number of d tiles in a radius
    # This can be used as a getter as well as an action in the grammar
    # Should always return an int
    def sonar(self) -> int:
        d_tiles = 0
        for x, row in enumerate(self.map):
            for y, col in enumerate(row):
                if self.get_tile(x, y) == "D":
                    d_tiles += 1
        print(f"{self.name} found {d_tiles} scannable tiles")
        return d_tiles

    # When in front of an r tile, push it one tile up front if not an x
    # Chance to uncover d tile
    def push(self):
        front_tile = tuple(map(operator.add, (self.x_pos, self.y_pos),
                               self.tiles_around[self.orientation]))
        if self.get_tile(front_tile[0], front_tile[1]) != "R":
            print(f"{self.name} must face a R tile to push")
            return
        next_tile = tuple(map(operator.add, front_tile,
                              self.tiles_around[self.orientation]))
        if self.get_tile(next_tile[0], next_tile[1]) == "X":
            print(f"{self.name} unable to push R on an X tile")
            return
        self.set_tile("R", next_tile[0], next_tile[1])
        self.set_tile(random.choice(['X', ' ']), front_tile[0], front_tile[1])

    # When on a digit tile, at that digit * 10 to the rovers power
    def recharge(self):
        if self.get_tile().isdigit():
            self.power += int(self.get_tile()) * 10
            self.remove_tile()
        else:
            print(f"{self.name} must be on a digit tile")

    # This is stupid but it's funny
    def backflip(self):
        self.orientation = (self.orientation + 2) % 4

    # Print what is in our inventory
    def print_inventory(self):
        print("INVENTORY:")
        print(f'    Gold: {self.gold}')
        print(f'    Silver: {self.silver}')
        print(f'    Copper: {self.copper}')
        print(f'    Iron: {self.iron}')
        print()

    # Print the map with the rover in the correct position
    # use ^, >, v, < depending on the orientation
    def _print_map(self):
        # this is bad but good enough
        output_map = copy.deepcopy(self.map)
        x = ""
        if self.orientation == 0:
            x = "^"
        elif self.orientation == 1:
            x = ">"
        elif self.orientation == 2:
            x = "v"
        else:
            x = "<"

        output_map[self.y_pos][self.x_pos] = x
        print('\n'.join([''.join(['{:4}'.format(item) for item in row])
                         for row in output_map]))

    # Print the current position
    def print_pos(self):
        print(f'I am located at: ({self.x_pos}, {self.y_pos})')

    # Print current orientation
    def print_orientation(self):
        if self.orientation == 0:
            print(f'I am facing North.')
        elif self.orientation == 1:
            print(f'I am facing East.')
        elif self.orientation == 2:
            print(f'I am facing South.')
        elif self.orientation == 3:
            print(f'I am facing West.')

    # Change the map given by a path to a file and initialize
    # the rover in a random position
    def change_map(self, path: str):
        self.map.clear()
        self.map_init(path)
        self.set_coord()

    # Change the current orientation based on the given direction
    def turn(self, direction):
        if direction == 0:
            self.orientation -= 1
        elif direction == 1:
            self.orientation += 1
        if self.orientation in [-1, 4]:
            self.orientation = 3


def _main():
    # Initialize the rovers
    rover1 = Rover(ROVER_1)
    rover2 = Rover(ROVER_2)
    my_rovers = [rover1, rover2]

    # Run the rovers in parallel
    procs = []
    for rover in my_rovers:
        p = multiprocessing.Process(target=rover.wait_for_command, args=())
        p.start()
        procs.append(p)

    # Wait for the rovers to stop running (after MAX_RUNTIME)
    for p in procs:
        p.join()


def main():  # temporary main for testing
    rover = Rover(ROVER_1)

    # changing current tile
    rover.get_tile()
    assert rover.get_tile() == " "
    rover.set_tile("X")
    assert rover.get_tile() == "X"
    rover.remove_tile()
    assert rover.get_tile() == " "

    # try to drill on a tile that is not an ore , will not work
    rover.set_tile("D", rover.get_x_pos(), rover.get_y_pos())
    assert rover.get_tile() == "D"
    rover.drill()
    assert rover.get_tile() == "D"
    rover.remove_tile()
    assert rover.get_tile() == " "

    # scan and drill on a D tile
    rover.set_tile("D", rover.get_x_pos(), rover.get_y_pos())
    assert rover.get_tile() == "D"
    rover.scan()
    assert rover.get_tile() in rover.ores_type
    rover.drill()
    assert rover.get_tile() == " "
    assert (rover.get_copper() or rover.get_gold()
            or rover.get_iron() or rover.get_silver()) != 0
    rover.print_inventory()

    # test shockwave
    for tile in rover.tiles_around:
        rover.set_tile("X", rover.get_x_pos() +
                       tile[0], rover.get_y_pos() + tile[1])
        assert rover.get_tile(rover.get_x_pos() +
                              tile[0], rover.get_y_pos() + tile[1]) == "X"
    rover.shockwave()
    for tile in rover.tiles_around:
        assert rover.get_tile(rover.get_x_pos() +
                              tile[0], rover.get_y_pos() + tile[1]) in ["D", " "]

    # test change map
    rover_map = Rover("test_map")
    rover.change_map("map2.txt.txt")
    assert rover.map != rover_map.map
    rover.change_map("map1.txt.txt")
    assert rover.map == rover_map.map

    # test recharge
    current_power = rover.get_power()
    rover.set_tile("1")
    rover.recharge()
    assert rover.get_power() == current_power + 10
    rover.build()

    # test push
    front = tuple(map(operator.add, (rover.x_pos, rover.y_pos),
                      rover.tiles_around[rover.orientation]))
    rover.set_tile("R", front[0], front[1])
    front_n = tuple(map(operator.add, front,
                        rover.tiles_around[rover.orientation]))
    rover.remove_tile(front_n[0], front_n[1])
    rover.push()
    assert rover.get_tile(front[0], front[1]) == " "
    assert rover.get_tile(front_n[0], front_n[1]) == "R"

    # test sonar
    for tile in rover.tiles_around:
        rover.set_tile("D", tile[0], tile[1])
    assert rover.sonar() == 4


if __name__ == "__main__":
    main()
