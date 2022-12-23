import pathlib
import sys

from rover import ROVER_COMMAND_FILES


def main():
    # Get the command from the file given and move it
    # to the file the rover is watching (default is Rover1)
    rover_name = "Rover1"
    if len(sys.argv) < 2:
        raise Exception("Missing file path to parse.")
    elif len(sys.argv) == 3:
        rover_name = sys.argv[2]
        if rover_name not in ROVER_COMMAND_FILES:
            raise Exception(f"Unknown rover name given: {rover_name}")
    elif len(sys.argv) != 2:
        raise Exception(f"Expected 2, or 3 arguments but found {len(sys.argv)}")

    fcontent = None
    filepath = pathlib.Path(sys.argv[1])
    with filepath.open() as f:
        fcontent = f.read()

    with ROVER_COMMAND_FILES[rover_name].open("w") as f:
        f.write(fcontent)

    print("Command sent successfully! See the rover for more details")


if __name__ == "__main__":
    main()
