import builtins
import json
import os
import platform
import random
import re
import sys
import termios
import time
import tty


# ANSI codes
class Colors:
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    GRAY = "\033[90m"
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
    {"name": "Mumbai, India", "code": "in"},
]
OPTIONS_COLORS = [
    Colors.RED,
    Colors.YELLOW,
    Colors.GREEN,
    Colors.CYAN,
    Colors.BLUE,
    Colors.PURPLE,
    Colors.UNDERLINE,
]
OPTIONS_TEXT_SPEED = [
    {"name": "FAST", "value": 5},
    {"name": "MEDIUM", "value": 15},
    {"name": "SLOW", "value": 30},
    {"name": "INSTANT", "value": 0},
]
OPTIONS_GAME_OVER = [
    {"title": "Head to AIRPORT (Restart)", "value": 0},
    {"title": "Head back HOME (Quit)", "value": 1},
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


# clear screen based on os
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
def print(*args, color: str = None, colors: list[str] = None, **kwargs):
    if args:
        msg = " ".join(str(a) for a in args)
        if colors:
            for c in colors:
                msg = f"{c}{msg}"
            msg = f"{msg}{Colors.END}"
        elif color:
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
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char


def get_language_key(match):
    key = match.group(1)
    return language.get(key, f"<{key}>")


def get_translation_key(match):
    key = match.group(1)
    return translations.get(key, f"<{key}>")


# get a choice from a list (easy to reuse)
def get_choice(
    choices, key: str, supports_default: bool = False, prompt: str = "\n> OPTIONS"
):
    print("\n> OPTIONS")
    for i in range(len(choices)):
        choice_text = choices[i][key]
        print(f"[{i + 1}]", color=OPTIONS_COLORS[i], end=" ")
        print(choice_text)

    print("\n> ", end="")
    while True:
        try:
            char_input = getch()
            if char_input == "q":
                print("'q' detected, exiting... Thank you for playing!")
                exit(0)

            # enter key
            if supports_default and char_input == "\r":
                return -1

            # adjust for 0 index
            choice = int(char_input) - 1
            if choice >= 0 and choice <= len(choices) - 1:
                break
        except Exception:
            continue

    return choice


# restart loop
while True:
    clear_screen()
    print("Welcome to:", color=Colors.UNDERLINE)
    print(
        """ ______     __  __     __     __         ______    
/\  ___\   /\_\_\_\   /\ \   /\ \       /\  ___\   
\ \  __\   \/_/\_\/_  \ \ \  \ \ \____  \ \  __\   
 \ \_____\   /\_\/\_\  \ \_\  \ \_____\  \ \_____\ 
  \/_____/   \/_/\/_/   \/_/   \/_____/   \/_____/ 
                                                   """
    )
    print("LOST IN TRANSLATION\n", color=Colors.UNDERLINE)

    if not played_before:
        print(
            f"When you see options like {Colors.RED}[1]{Colors.END}, press the corresponding key on your keyboard to continue."
        )
        print(
            f"You may use {Colors.YELLOW}'q'{Colors.END} at any time during an option to exit the program."
        )
        print(
            f"Press {Colors.GREEN}ENTER{Colors.END} on the following options to choose the default."
        )
        print()

    print("-" * 50)
    print()
    if not played_before:
        # get player info
        while True:
            dirty_name = input("Welcome player! What's your name? ")
            if not dirty_name:
                print("You need a name!")
                continue

            dirty_name = dirty_name[0].upper() + dirty_name[1:]
            player.name = dirty_name
            break

    print(f"Welcome, {player.name}! Which country would you like to live in?")
    country_choice = get_choice(OPTIONS_COUNTRIES, "name", True)

    selected_country = ""
    if country_choice == -1:
        selected_country = random.choice(OPTIONS_COUNTRIES)
        print(f"{selected_country["name"]}, has been selected randomly!\n")
    else:
        selected_country = OPTIONS_COUNTRIES[country_choice]

    player.country = selected_country["name"]
    player.language_code = selected_country["code"]

    if not played_before:
        print("And what about your text speed?")
        text_speed_choice = get_choice(OPTIONS_TEXT_SPEED, "name", True)

        if text_speed_choice == -1:
            player.text_speed = OPTIONS_TEXT_SPEED[1]["value"]
        else:
            player.text_speed = OPTIONS_TEXT_SPEED[text_speed_choice]["value"]

    # after player.country set, load the language file
    language = {}
    translations = {}
    with open(f"./languages/{player.language_code}.json") as f:
        data = json.load(f)
        language = data["phrases"]
        translations = data["translations"]
        cultural_facts = data["cultural_facts"]

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

        text = active_scene["text"]
        text = re.sub(
            r"\$\{name\}", player.name, active_scene["text"]
        )  # first time for just name
        text = re.sub(r"\$\{language\.([a-zA-Z0-9_]+)\}", get_language_key, text)
        text = re.sub(r"\$\{translations\.([a-zA-Z0-9_]+)\}", get_translation_key, text)
        text = re.sub(
            r"\$\{name\}", f"_____ ({player.name})", text
        )  # second time for language/translation

        # update only days prematurely because it matters for info
        if not game_over and "days" in stat_changes:
            player.editStat("days", stat_changes["days"])

        clear_screen()
        print("EXILE:", end="", color=Colors.UNDERLINE)
        print(" LOST IN TRANSLATION", colors=[Colors.UNDERLINE, Colors.GRAY])
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

    choice = get_choice(OPTIONS_GAME_OVER, "title")
    if choice == 1:
        print(f"\nGoodbye!")
        break
