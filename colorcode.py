class Color:
    """
    ANSI color codes for text output in the terminal.
    """
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'


def print_colored(*args, color=Color.YELLOW):
    """
    Print colored text in the terminal.

    Parameters:
        *args: Variable number of arguments to be printed.
        color (str): ANSI color code. Default is Color.YELLOW.

    Example usage:
        print_colored("Hello,", "World!", color=Color.GREEN)
        print_colored("This is another message.")
    """
    formatted_text = f"{color}{' '.join(map(str, args))}{Color.RESET}"
    print(formatted_text)
