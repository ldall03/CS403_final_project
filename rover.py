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
        # Assume same directory
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
        self.x_pos = pos[0]
        self.y_pos = pos[1]

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
        return self.get_x_pos()

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
        pass

    # When on a g, s, c, or i tile, change tile to ' ' and give some
    # amount of the respective material to  the rover
    def drill(self):
        pass

    # Destroy all x tiles in a radius, give a chance to transform
    # to a d tile
    def shockwave(self):
        pass

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
        pass

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
    def change_map(self):
        pass

    # Change the position to move a given amount of tiles in
    # a given direction. If we cannot because of an x tile then
    # move as far as possible
    def move(self, direction, steps):
        pass

    # Change the current orientation based on the given direction
    def turn(self):
        pass


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


if __name__ == "__main__":
    main()
