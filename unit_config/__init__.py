UNIT_TYPES = {
    "settler": {
        "move_points": 2,
        "hp": 100,
        "attack": 0,  # Settlers cannot attack
        "color": (200, 200, 50),
        "radius": 12,
    },
    "warrior": {
        "move_points": 4,
        "hp": 100,
        "attack": 25,
        "color": (200, 50, 50),
        "radius": 12,
    },
    "archer": {
        "move_points": 2,
        "hp": 80,
        "attack": 15,  # Example: not melee, but included for future use
        "color": (50, 50, 200),
        "radius": 12,
    },
    # Add more unit types here as needed
}
