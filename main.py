# stats
language = 3
money = 3
mental_health = 3
trust = 3
cultural_identity = 3
confidence = 3
legal_status = "pending"
battery = 50

# game loop
while True:
    # check if game over
    if language >= 5 and trust >= 4 and cultural_identity >= 3:
        # 🌟 The Bridge Builder: You adapt and help others too.
        pass
    elif money >= 6 and confidence >= 5 and cultural_identity <= 2:
        # 💼 The Hustler: You succeed materially but lose cultural connection.
        pass
    elif cultural_identity >= 5 and language >= 4 and trust >= 3:
        # 💖 Rooted and Reunited: You reunite with your family, keeping roots intact.
        pass
    elif mental_health <= 2 or confidence <= 1:
        # 😔 Burnout: You work hard but lose yourself emotionally.
        pass
    elif money <= 1 or legal_status == "denied" or trust <= 1:
        # ✈️ Sent Home: You fail to adapt and are forced to leave.
        pass

    # do scenes
