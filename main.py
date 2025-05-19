import os
import json
import platform

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
    "day": 0,
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
            or stats["day"] >= 90
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

    clear_screen()
    print("EXILE DIARIES: LOST IN TRANSLATION")
    print(f"Day {stats["day"] + 1}")
    print(f"{clear_name} - [Unknown Country]")

    print(f"\n[{text}]")

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
            print(f"[{'+' if stat_value > 0 else ''}{stat_value} {stat_name}]")
            stats[change] += stat_value

    if "ending" in active_scene.keys():
        stats["legal_status"] = active_scene["legal_status"]
        break

    # TODO: inventory?

    choices = active_scene["choices"]

    print("\n> OPTIONS")
    for i in range(len(choices)):
        choice_text = choices[i]["text"]
        print(f"[{i + 1}] {choice_text}")

    # adjust for 0 index
    choice = int(input("\n> ")) - 1

    active_id = choices[choice]["next_scene"]
    stat_changes = choices[choice]["stat_changes"]

print("\nThank you for playing!")
print("Final stats:\n")

for stat in stats:
    print(f"{clean_string(stat)}: {stats[stat]}")
