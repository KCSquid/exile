import os
import re
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


# player as class to make easy to change
class Player:
    def __init__(self):
        self.name = ""
        self.country = ""
        self.language_code = ""
        self.stats = {}
        self.text_speed = 15

        self.resetStats()

    def getStat(self, name):
        return self.stats[name]

    def setStat(self, name, value):
        self.stats[name] = value

    def editStat(self, name, amount):
        self.stats[name] += amount

    def resetStats(self):
        self.stats = {
            "language": 3,
            "money": 3,
            "mental_health": 3,
            "trust": 3,
            "cultural_identity": 3,
            "confidence": 3,
            "legal_status": "pending",
            "battery": 50,
            "days": 0,
            "cultural_knowledge": 0,
        }


# constants
OPTIONS_COUNTRIES = [
    {"name": "Berlin, Germany", "code": "de"},
    {"name": "Paris, France", "code": "fr"},
    {"name": "Madrid, Spain", "code": "es"},
    {"name": "Kyiv, Ukraine", "code": "ua"},
    {"name": "Kingston, Jamaica", "code": "jm"},
    {"name": "Toronto, Canada", "code": "ca"},
]
OPTIONS_COLORS = [
    Colors.YELLOW,
    Colors.CYAN,
    Colors.BLUE,
    Colors.PURPLE,
    Colors.GREEN,
    Colors.RED,
]
OPTIONS_TEXT_SPEED = [
    {"name": "FAST", "value": 5},
    {"name": "MEDIUM", "value": 15},
    {"name": "SLOW", "value": 30},
    {"name": "INSTANT", "value": 0},
]

# global game settings
active_id = "arrival"
stat_changes = {}
game_over = False
played_before = False
player = Player()

# read json into python object
with open("scenes.json") as f:
    scenes = json.load(f)["scenes"]


# search for id through scenes and return it
def get_scene(name: str):
    for s in scenes:
        if s["id"] == name:
            return s


# "_" -> " ", first letter capital + rest of letters, join by a space
def clean_string(string: str):
    return " ".join([w[0].upper() + w[1:] for w in string.split("_")])


def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


# ms adjusted to my reading time-ish
def typewrite(string: str):
    for c in string:
        # flush to force showing it
        print(c, end="", flush=True)
        time.sleep(player.text_speed / 1000)
    print()


# edit std func print to show ANSI reset by default
def print(*args, color: str = None, **kwargs):
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
def getch(prompt: str = ""):
    if prompt:
        print(prompt, end="", flush=True)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        # disable echo so it doesn't show \n or stuff
        new_settings = termios.tcgetattr(fd)
        new_settings[3] = new_settings[3] & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


# sub lang keys
def lang_sub(match):
    key = match.group(1)
    return language.get(key, f"<{key}>")


def get_choice(choices, key: str, prompt: str = "\n> OPTIONS"):
    print("\n> OPTIONS")
    for i in range(len(choices)):
        choice_text = choices[i][key]
        print(f"[{i + 1}]", color=OPTIONS_COLORS[i], end=" ")
        print(choice_text)

    print("\n> ", end="")
    while True:
        try:
            # adjust for 0 index
            char_input = getch()
            if char_input == "q":
                print("'q' Detected, quitting... Thank you for playing!")
                exit(0)
            choice = int(char_input) - 1
            if choice >= 0 and choice <= len(choices) - 1:
                break
        except:
            continue

    return choice


# restart loop
while True:
    clear_screen()
    if not played_before:
        # get player info
        dirtyName = input("Welcome player! What's your name? ")
        dirtyName = dirtyName[0].upper() + dirtyName[1:]
        player.name = dirtyName

    print(f"Welcome, {player.name}! Which country would you like to live in?")
    country_choice = get_choice(OPTIONS_COUNTRIES, "name")
    player.country = OPTIONS_COUNTRIES[country_choice]["name"]
    player.language_code = OPTIONS_COUNTRIES[country_choice]["code"]

    if not played_before:
        print("And what about your text speed?")
        text_speed_choice = get_choice(OPTIONS_TEXT_SPEED, "name")
        player.text_speed = OPTIONS_TEXT_SPEED[text_speed_choice]["value"]

    # after player.country set, load the language file
    language = {}
    with open(f"./languages/{player.language_code}.json") as f:
        language = json.load(f)

    cultural_facts = language["cultural_facts"]
    MAX_FACTS_LEN = len(cultural_facts)

    # reset everything
    played_before = True
    game_over = False
    active_id = "arrival"
    stat_changes = {}
    player.resetStats()
    # game loop
    while True:
        # check if game over by stats
        if not game_over:
            route = ""

            if (
                player.getStat("language") >= 7
                and player.getStat("trust") >= 6
                and player.getStat("cultural_identity") >= 5
            ):
                route = "ending_bridge_builder"
            elif (
                player.getStat("money") >= 8
                and player.getStat("confidence") >= 7
                and player.getStat("cultural_identity") <= 2
            ):
                route = "ending_hustler"
            elif (
                player.getStat("cultural_identity") >= 7
                and player.getStat("language") >= 6
                and player.getStat("trust") >= 5
            ):
                route = "ending_rooted"
            elif (
                player.getStat("mental_health") <= -2
                or player.getStat("confidence") <= -2
                or player.getStat("days") >= 120
            ):
                route = "ending_burnout"
            elif (
                player.getStat("money") <= -2
                or player.getStat("legal_status") == "denied"
                or player.getStat("trust") <= -2
            ):
                route = "ending_sent_home"

            if route:
                game_over = True
                continue

        fact_threshold = MAX_FACTS_LEN + 1 - len(cultural_facts)
        if (
            player.getStat("cultural_knowledge") == fact_threshold
            and fact_threshold <= 5
        ):
            print(
                f"\n"
            )  # I really don't know why this works but don't touch it I guess
            print(
                f"Before you continue, a {Colors.UNDERLINE}cultural fact{Colors.END}:"
            )
            print(f'"{cultural_facts[-1]}"')
            cultural_facts.pop()
            getch(f"\nPRESS {Colors.GREEN}ANY KEY{Colors.END} TO ADVANCE...")

        # show scenes
        active_scene = get_scene(active_id)

        clear_name = clean_string(active_scene["id"])
        text = re.sub(r"\$\{name\}", player.name, active_scene["text"])

        text = re.sub(r"\$\{language\.([a-zA-Z0-9_]+)\}", lang_sub, text)
        text = re.sub(r"\$\{name\}", f"_____ ({player.name})", text)

        # update only days prematurely because it matters for info
        if not game_over and "days" in stat_changes:
            player.editStat("days", stat_changes["days"])

        clear_screen()
        print("EXILE: LOST IN TRANSLATION", color=Colors.UNDERLINE)
        print(f"Day {player.getStat("days") + 1}")
        print(f"{clear_name} - {player.country}")

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
            if isinstance(player.getStat(change), str):
                if player.getStat(change) != stat_value:
                    print(f"[{stat_name}: {player.getStat(change)} → {stat_value}]")
                    player.setStat(change, stat_value)
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
                player.editStat(change, stat_value)

        if "ending" in active_scene.keys():
            player.setStat("legal_status", active_scene["legal_status"])
            break

        # TODO: inventory?

        scene_choices = active_scene["choices"]
        choice = get_choice(scene_choices, "text")
        active_id = scene_choices[choice]["next_scene"]
        stat_changes = scene_choices[choice]["stat_changes"]

    print("\nThank you for playing!")
    print("\nFinal stats:")

    # show stats cleanly
    for stat in player.stats:
        typewrite(f"{clean_string(stat)}: {player.getStat(stat)}")

    choice = get_choice(
        [
            {"title": "Head to AIRPORT (Restart)", "value": 0},
            {"title": "Head back HOME (Quit)", "value": 1},
        ],
        "title",
    )

    if choice == 1:
        print(f"\nGoodbye!")
        break
