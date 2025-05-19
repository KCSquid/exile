import json

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


active_id = "arrival"

# day = 1

stat_changes = {}

# game loop
while True:
    # check if game over by stats
    if (
        stats["language"] >= 5
        and stats["trust"] >= 4
        and stats["cultural_identity"] >= 3
    ):
        active_id = "ending_bridge_builder"
        continue
    elif (
        stats["money"] >= 6
        and stats["confidence"] >= 5
        and stats["cultural_identity"] <= 2
    ):
        active_id = "ending_hustler"
        continue
    elif (
        stats["cultural_identity"] >= 5
        and stats["language"] >= 4
        and stats["trust"] >= 3
    ):
        active_id = "ending_rooted"
        continue
    elif stats["mental_health"] <= 2 or stats["confidence"] <= 1:
        active_id = "ending_burnout"
        continue
    elif (
        stats["money"] <= 1 or stats["legal_status"] == "denied" or stats["trust"] <= 1
    ):
        active_id = "ending_sent_home"
        continue

    # do scenes
    active_scene = get_scene(active_id)

    clear_name = clean_string(active_scene["id"])
    text = active_scene["text"]

    print("EXILE DIARIES: LOST IN TRANSLATION")
    # print(f"Day {day} - ...")
    print(f"{clear_name} - [Unknown Country]")

    print(f"\n[{text}]")

    if len(stat_changes.keys()) > 0:
        print()
    for change in stat_changes:
        stat_value = stat_changes[change]
        stat_name = clean_string(change)

        # is a string - legal status
        if isinstance(stats[change], str):
            if stats[change] != stat_value:
                print(f"[{stat_name}: {stats[change]} → {stat_value}]")
                stats[change] = stat_value
        # a number like regular
        else:
            print(f"[{'+' if stat_value > 0 else ''}{stat_value} {stat_name}]")
            stats[change] += stat_value

    if "ending" in active_scene.keys():
        break

    # inventory?

    choices = active_scene["choices"]

    print("\n> OPTIONS")
    for i in range(len(choices)):
        choice_text = choices[i]["text"]
        print(f"[{i + 1}] {choice_text}")

    # adjust for 0 index
    choice = int(input("\n> ")) - 1

    active_id = choices[choice]["next_scene"]
    stat_changes = choices[choice]["stat_changes"]
