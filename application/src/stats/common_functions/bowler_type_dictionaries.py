bowler_type = {
    "fast_bowlers": [
        "Right arm Fast",
        "Right arm Fast medium",
        "Right arm Fast Medium",
        "Left arm Fast",
        "Left arm Fast medium"
    ],

    "medium_pace_bowlers": [
        "Right arm Medium",
        "Right arm Medium fast",
        "Left arm Medium",
        "Left arm Medium fast"
    ],

    "right_arm_bowlers": [
        "Right arm Fast",
        "Right arm Fast medium",
        "Right arm Medium",
        "Right arm Offbreak",
        "Right arm Legbreak",
        "Right arm Bowler",
        "Right arm Offbreak, Legbreak Googly",
        "Right arm Medium, Legbreak",
        "Right arm Medium, Right arm Offbreak",
        "Right arm Offbreak, Legbreak",
        "Right arm Offbreak, Slow Left arm Orthodox",
        "Right arm Medium, Right arm Offbreak, Legbreak"
    ],

    "left_arm_bowlers": [
        "Left arm Fast",
        "Left arm Fast medium",
        "Left arm Medium",
        "Left arm Medium fast",
        "Slow Left arm Orthodox",
        "Left arm Wrist spin",
        "Slow Left arm Orthodox, Left arm Wrist spin"
    ],

    "off_spinners": [
        "Right arm Offbreak",
        "Right arm Offbreak, Legbreak Googly",
        "Right arm Offbreak, Legbreak",
        "Right arm Offbreak, Slow Left arm Orthodox",
        "Right arm Medium, Right arm Offbreak",
        "Right arm Medium, Right arm Offbreak, Legbreak"
    ],

    "leg_spinners" : [
        "Legbreak",
        "Legbreak Googly",
        "Right arm Medium, Legbreak"
    ],

    "spinners": [
        "Right arm Offbreak",
        "Right arm Offbreak, Legbreak Googly",
        "Right arm Offbreak, Legbreak",
        "Right arm Offbreak, Slow Left arm Orthodox",
        "Right arm Medium, Right arm Offbreak",
        "Right arm Medium, Right arm Offbreak, Legbreak",
        "Legbreak",
        "Legbreak Googly",
        "Right arm Medium, Legbreak"
    ],

    "slow_left_arm_bowlers": [
        "Slow Left arm Orthodox",
        "Left arm Wrist spin",
        "Slow Left arm Orthodox, Left arm Wrist spin"
    ],

    "right_arm_fast_bowlers": [
        "Right arm Fast",
        "Right arm Fast medium",
        "Right arm Fast Medium"
    ],

    "left_arm_fast_bowlers": [
        "Left arm Fast",
        "Left arm Fast medium"
    ]
}

def resolve_bowler_type(user_input: str) -> str:
    """Map flexible user input to the internal bowler type category."""
    user_input = user_input.lower()

    keyword_to_key = {
        "fast": "fast_bowlers",
        "fast bowler": "fast_bowlers",
        "fast bowlers": "fast_bowlers",
        "pacers": "fast_bowlers",

        "medium pace": "medium_pace_bowlers",
        "medium pacers": "medium_pace_bowlers",
        "medium": "medium_pace_bowlers",

        "right arm": "right_arm_bowlers",
        "right arm bowler": "right_arm_bowlers",

        "left arm": "left_arm_bowlers",
        "left arm bowler": "left_arm_bowlers",

        "spin" : "spinners",
        "spinners" : "spinners",
        "spin bowlers": "spinners",

        "off spin": "off_spinners",
        "off spinner": "off_spinners",
        "off spinners": "off_spinners",

        "leg spin": "leg_spinners",
        "leg spinner": "leg_spinners",
        "leg spinners": "leg_spinners",

        "slow left arm": "slow_left_arm_bowlers",
        "left arm orthodox": "slow_left_arm_bowlers",

        "right arm fast": "right_arm_fast_bowlers",
        "right arm pacer": "right_arm_fast_bowlers",

        "left arm fast": "left_arm_fast_bowlers",
        "left arm pacer": "left_arm_fast_bowlers"
    }

    # Try longest match first to avoid premature short matches
    for keyword in sorted(keyword_to_key.keys(), key=len, reverse=True):
        if keyword in user_input:
            dict_key = keyword_to_key[keyword]
            return bowler_type.get(dict_key, [])

    return []  # fallback if nothing matched