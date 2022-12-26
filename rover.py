import multiprocessing
import pathlib
import time
import traceback
import parser
import random

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
    tiles_around = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def __init__(self, name):
        self.name = name
        self.map = list()

        self.x_pos = None
        self.y_pos = None
        self.orientation = None
        self.gold = 0
        self.silver = 0
        self.copper = 0
        self.iron = 0
        self.power = 100

        self.map_init()
        self.set_coord()

    def map_init(self, path='map.txt.txt'):
        # Assume map.txt.txt is in same directory
        with open(path, "r", encoding="utf-8") as file:
            row = list()
            while True:
                char = file.read(1)
                if not char:
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
        self.x_pos = pos[1]
        self.y_pos = pos[0]

        # 0 = North, 1 = East, 2 = South, 3 = West
        self.orientation = random.choice(range(0, 4))

    def print_map(self):
        print('\n'.join([''.join(['{:4}'.format(item) for item in row])
                         for row in self.map]))

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
        if (x, y) == (None, None):  # lol ?
            x, y = self.x_pos, self.y_pos
        return self.map[y][x]

    # if no x, y, Will be at current tile
    def set_tile(self, tile_type, x=None, y=None):
        if (x, y) == (None, None):  # lol ?
            x, y = self.x_pos, self.y_pos
        self.map[y][x] = tile_type

    def remove_tile(self, x=None, y=None):
        self.set_tile(" ", x, y)
    # Returns the maximum tiles the rover can advance in the given direction
    # Should always return an integer

    def max_move(self, direction):
        pass

    # Returns True if the rover can move in the given direction
    # Should always return True or False
    def can_move(self, direction):
        pass

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
        if self.get_tile() not in self.ores_type:
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

    # Destroy all x tiles in a radius, give a chance to transform
    # to a d tile
    def shockwave(self):
        for i in self.tiles_around:
            if random.uniform(0, 1) < 0.5:
                self.set_tile("D", self.x_pos+i[0], self.y_pos+i[1])
            else:
                self.remove_tile(self.x_pos+i[0], self.y_pos+i[1])

    # Transform a ' ' tile to a b tile, use materials from inventory
    def build(self):
        pass

    # Count and print and return the number of d tiles in a radius
    # This can be used as a getter as well as an action in the grammar
    # Should always return an int
    def sonar(self):
        pass

    # When in front of an r tile, push it one tile up front if not an x
    # Chance to uncover d tile
    def push(self):
        pass

    # When on a digit tile, at that digit * 10 to the rovers power
    def recharge(self):
        pass

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
        pass

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
        pass
    # Change the position to move a given amount of tiles in
    # a given direction. If we cannot because of an x tile then
    # move as far as possible

    def move(self, direction, steps):
        pass

    # Change the current orientation based on the given direction
    def turn(self, direction):
        self.orientation = direction


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
    rover.print_map()
    rover.print_orientation()
    rover.print_pos()
    rover.print_inventory()

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


if __name__ == "__main__":
    main()
