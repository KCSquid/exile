import os
import sys
import tty
import json
import time
import termios
import platform
import builtins


# ANSI codes
class Colors:
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# stats as obj to make easy to change
stats = {
    "language": 3,
    "money": 3,
    "mental_health": 3,
    "trust": 3,
    "cultural_identity": 3,
    "confidence": 3,
    "legal_status": "pending",
    "battery": 50,
    "days": 0,
}

# read json into python object
with open("scenes.json") as f:
    scenes = json.load(f)["scenes"]


# search for id through scenes and return it
def get_scene(name):
    for s in scenes:
        if s["id"] == name:
            return s


# "_" -> " ", first letter capital + rest of letters, join by a space
def clean_string(string):
    return " ".join([w[0].upper() + w[1:] for w in string.split("_")])


def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


# ms adjusted to my reading time-ish
def typewrite(string, ms=15):
    for c in string:
        # flush to force showing it
        print(c, end="", flush=True)
        time.sleep(ms / 1000)
    print()


# edit std func print to show ANSI reset by default
def print(*args, color=None, **kwargs):
    if args:
        msg = " ".join(str(a) for a in args)
        if color:
            msg = f"{color}{msg}{Colors.END}"
        # prevent dupes
        elif not msg.endswith(Colors.END):
            msg += Colors.END
        builtins.print(msg, **kwargs)
    else:
        builtins.print(**kwargs)


# get singular char
def getch(prompt):
    print(prompt, end="", flush=True)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    print()
    return ch


active_id = "arrival"

stat_changes = {}
game_over = False

# game loop
while True:
    # check if game over by stats
    if not game_over:
        if (
            stats["language"] >= 7
            and stats["trust"] >= 6
            and stats["cultural_identity"] >= 5
        ):
            active_id = "ending_bridge_builder"
            game_over = True
            continue
        elif (
            stats["money"] >= 8
            and stats["confidence"] >= 7
            and stats["cultural_identity"] <= 2
        ):
            active_id = "ending_hustler"
            game_over = True
            continue
        elif (
            stats["cultural_identity"] >= 7
            and stats["language"] >= 6
            and stats["trust"] >= 5
        ):
            active_id = "ending_rooted"
            game_over = True
            continue
        elif (
            stats["mental_health"] <= 0
            or stats["confidence"] <= 0
            or stats["days"] >= 90
        ):
            active_id = "ending_burnout"
            game_over = True
            continue
        elif (
            stats["money"] <= 0
            or stats["legal_status"] == "denied"
            or stats["trust"] <= 0
        ):
            active_id = "ending_sent_home"
            game_over = True
            continue

    # do scenes
    active_scene = get_scene(active_id)

    clear_name = clean_string(active_scene["id"])
    text = active_scene["text"]

    # update only days prematurely because it matters for info
    if not game_over and "days" in stat_changes:
        stats["days"] += stat_changes["days"]

    clear_screen()
    print("EXILE DIARIES: LOST IN TRANSLATION", color=Colors.UNDERLINE)
    print(f"Day {stats["days"] + 1}")
    print(f"{clear_name} - [Unknown Country]")

    print()
    dialogue = text.split("\n")
    for message in dialogue:
        typewrite(f"[{message}]")

    if len(stat_changes.keys()) > 0:
        print()
    for change in stat_changes:
        stat_value = stat_changes[change]
        stat_name = clean_string(change)

        # is a string - legal status
        # otherwise regular number stat
        if isinstance(stats[change], str):
            if stats[change] != stat_value:
                print(f"[{stat_name}: {stats[change]} → {stat_value}]")
                stats[change] = stat_value
        else:
            positive = stat_value > 0
            corresponding_color = Colors.GREEN if positive else Colors.RED
            print("[", end="")
            print(
                f"{'+' if positive else ''}{stat_value}",
                color=corresponding_color,
                end=" ",
            )
            print(f"{stat_name}]")
            stats[change] += stat_value

    if "ending" in active_scene.keys():
        stats["legal_status"] = active_scene["legal_status"]
        break

    # TODO: inventory?

    choices = active_scene["choices"]

    option_colors = [Colors.YELLOW, Colors.CYAN, Colors.BLUE, Colors.PURPLE]
    print("\n> OPTIONS")
    for i in range(len(choices)):
        choice_text = choices[i]["text"]
        print(f"[{i + 1}]", color=option_colors[i], end=" ")
        print(choice_text)

    # adjust for 0 index
    while True:
        try:
            choice = int(getch("\n> ")) - 1
            if choice >= 0 and choice <= 3:
                break
        except:
            continue

    active_id = choices[choice]["next_scene"]
    stat_changes = choices[choice]["stat_changes"]

print("\nThank you for playing!")
print("\nFinal stats:")

# show stats cleanly
for stat in stats:
    typewrite(f"{clean_string(stat)}: {stats[stat]}")
