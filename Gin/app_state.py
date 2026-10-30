from __future__ import annotations

import json
import math
import uuid
from pathlib import Path
from typing import Any, Dict

if __package__:
    from .attributes import ATTRIBUTES_LIST, format_attribute_log
    from .dice_engine import roll_dice
else:
    from attributes import ATTRIBUTES_LIST, format_attribute_log
    from dice_engine import roll_dice

DEFAULT_STATE_PATH = Path(__file__).with_name("demo_state.json")


def build_demo_state() -> Dict[str, Any]:
    """Create a realistic sample campaign state for demo work."""
    return {
        "campaign": {
            "id": "campaign-01",
            "name": "The Shattered Vale",
            "description": "A frontier keep haunted by missing caravans and a growing shadow beneath the old stone bridge.",
            "status": "active",
        },
        "rooms": [
            {
                "id": "room-01",
                "name": "Hall of the Watch",
                "description": "The party gathers before the council table while scouts report fresh movement in the valley.",
                "type": "gm",
                "characters": ["char-01", "char-02", "char-03"],
            },
            {
                "id": "room-02",
                "name": "Moonlit Approach",
                "description": "The road narrows between bramble and ruin as the night's fog rolls in.",
                "type": "encounter",
                "characters": ["char-01", "char-02", "char-04"],
            },
        ],
        "characters": [
            {
                "id": "char-01",
                "name": "Ariadne",
                "role": "player",
                "class_name": "Rogue",
                "initiative": 18,
                "health": 18,
                "position": {"x": 4, "y": 2},
                "turn_start_position": {"x": 4, "y": 2},
                "has_moved": False,
                "attributes": {
                    "Strength": 12,
                    "Dexterity": 18,
                    "Constitution": 14,
                    "Intelligence": 10,
                    "Wisdom": 13,
                    "Charisma": 15,
                },
            },
            {
                "id": "char-02",
                "name": "Brannok",
                "role": "player",
                "class_name": "Fighter",
                "initiative": 14,
                "health": 22,
                "position": {"x": 5, "y": 3},
                "turn_start_position": {"x": 5, "y": 3},
                "has_moved": False,
                "attributes": {
                    "Strength": 17,
                    "Dexterity": 12,
                    "Constitution": 16,
                    "Intelligence": 9,
                    "Wisdom": 10,
                    "Charisma": 11,
                },
            },
            {
                "id": "char-03",
                "name": "Mira",
                "role": "npc",
                "class_name": "Cleric",
                "initiative": 12,
                "health": 16,
                "position": {"x": 6, "y": 2},
                "turn_start_position": {"x": 6, "y": 2},
                "has_moved": False,
                "attributes": {
                    "Strength": 10,
                    "Dexterity": 11,
                    "Constitution": 13,
                    "Intelligence": 12,
                    "Wisdom": 17,
                    "Charisma": 14,
                },
            },
            {
                "id": "char-04",
                "name": "Ashen Warden",
                "role": "enemy",
                "class_name": "Guard",
                "initiative": 16,
                "health": 14,
                "position": {"x": 7, "y": 5},
                "turn_start_position": {"x": 7, "y": 5},
                "has_moved": False,
                "attributes": {
                    "Strength": 15,
                    "Dexterity": 13,
                    "Constitution": 12,
                    "Intelligence": 8,
                    "Wisdom": 10,
                    "Charisma": 9,
                },
            },
        ],
        "maps": [
            {
                "id": "map-01",
                "name": "Vale Road",
                "source": "builtin",
                "description": "A narrow road cutting through the bitter valley with ruins on either side.",
            }
        ],
        "logs": [
            {
                "id": "log-01",
                "type": "dice",
                "character_id": "char-01",
                "message": "Ariadne rolls a Stealth check and the party holds their breath.",
            },
            {
                "id": "log-02",
                "type": "movement",
                "character_id": "char-02",
                "message": "Brannok advances to the front of the line and locks his shield.",
            },
        ],
    }


def load_state(path: str | Path = DEFAULT_STATE_PATH) -> Dict[str, Any]:
    """Load the saved application state JSON, falling back to seeded demo data."""
    state_path = Path(path)
    if not state_path.exists():
        state = build_demo_state()
        save_state(state, state_path)
        return state

    with state_path.open("r", encoding="utf-8") as handle:
        loaded_state = json.load(handle)
    if not loaded_state.get("campaign"):
        loaded_state = build_demo_state()
        save_state(loaded_state, state_path)
    else:
        migrated = False
        for character in loaded_state.get("characters", []):
            position = character.get("position", {"x": 0, "y": 0})
            if "turn_start_position" not in character:
                character["turn_start_position"] = dict(position)
                migrated = True
            if "has_moved" not in character:
                character["has_moved"] = False
                migrated = True
        if migrated:
            save_state(loaded_state, state_path)
    return loaded_state


def save_state(state: Dict[str, Any], path: str | Path = DEFAULT_STATE_PATH) -> Dict[str, Any]:
    """Persist a JSON-serializable state payload to disk."""
    state_path = Path(path)
    with state_path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)
    return state


def find_character(state: Dict[str, Any], character_id: str) -> Dict[str, Any] | None:
    for character in state.get("characters", []):
        if character.get("id") == character_id:
            return character
    return None


def add_character(state: Dict[str, Any], character: Dict[str, Any]) -> Dict[str, Any]:
    state.setdefault("characters", [])
    state["characters"].append(character)
    return state


def add_room(state: Dict[str, Any], name: str, room_type: str) -> Dict[str, Any]:
    if not isinstance(name, str) or not isinstance(room_type, str):
        raise ValueError("Room name and type must be text.")
    normalized_name = name.strip()
    if not normalized_name or len(normalized_name) > 80:
        raise ValueError("Room name must contain between 1 and 80 characters.")
    if room_type not in ("gm", "encounter"):
        raise ValueError("Room type must be gm or encounter.")
    if any(room.get("name", "").casefold() == normalized_name.casefold() for room in state.get("rooms", [])):
        raise ValueError("A room with that name already exists.")

    room = {
        "id": f"room-{uuid.uuid4().hex[:12]}",
        "name": normalized_name,
        "description": "",
        "type": room_type,
        "characters": [],
    }
    state.setdefault("rooms", []).append(room)
    return room


def set_character_position(state: Dict[str, Any], character_id: str, x: int, y: int) -> Dict[str, Any]:
    character = find_character(state, character_id)
    if character is None:
        raise ValueError(f"Character not found: {character_id}")
    character["position"] = {"x": x, "y": y}
    state.setdefault("logs", []).append(
        {
            "id": f"log-{len(state.get('logs', [])) + 1}",
            "type": "movement",
            "character_id": character_id,
            "message": f"{character['name']} moves to ({x}, {y}).",
        }
    )
    return state


def movement_distance(start: Dict[str, int], end: Dict[str, int]) -> float:
    """Calculate movement distance using the proximity prototype's Euclidean grid rule."""
    return math.hypot(end.get("x", 0) - start.get("x", 0), end.get("y", 0) - start.get("y", 0))


def can_move_character(state: Dict[str, Any], character_id: str, destination: Dict[str, int], max_distance: int = 35) -> bool:
    """Check the turn movement cap, board bounds, and occupied destination."""
    character = find_character(state, character_id)
    if character is None:
        raise ValueError(f"Character not found: {character_id}")
    if character.get("has_moved", False):
        return False
    x = destination.get("x")
    y = destination.get("y")
    if not isinstance(x, int) or not isinstance(y, int) or not (0 <= x < 36 and 0 <= y < 24):
        return False
    start = character.get("turn_start_position", character.get("position", {"x": 0, "y": 0}))
    if movement_distance(start, destination) > max_distance:
        return False
    return not any(
        other.get("id") != character_id
        and other.get("position") == destination
        for other in state.get("characters", [])
    )


def move_character(
    state: Dict[str, Any],
    character_id: str,
    x: int,
    y: int,
    max_distance: int = 35,
) -> Dict[str, Any]:
    destination = {"x": x, "y": y}
    if not can_move_character(state, character_id, destination, max_distance):
        raise ValueError("Move is invalid, occupied, out of bounds, or exceeds the movement limit.")
    character = find_character(state, character_id)
    if character is None:
        raise ValueError(f"Character not found: {character_id}")
    character["position"] = destination
    character["has_moved"] = True
    state.setdefault("logs", []).append(
        {
            "id": f"log-{len(state.get('logs', [])) + 1}",
            "type": "movement",
            "character_id": character_id,
            "message": f"{character['name']} moves to ({x}, {y}).",
        }
    )
    return state


def reset_turn(state: Dict[str, Any]) -> Dict[str, Any]:
    for character in state.get("characters", []):
        character["turn_start_position"] = dict(character.get("position", {"x": 0, "y": 0}))
        character["has_moved"] = False
    return state


def perform_roll(
    state: Dict[str, Any],
    character_id: str,
    dice_type: int,
    quantity: int = 1,
    modifier: int = 0,
    advantage: str = "None",
    attribute_name: str = "None",
) -> Dict[str, Any]:
    character = find_character(state, character_id)
    if character is None:
        raise ValueError(f"Character not found: {character_id}")
    if dice_type not in (2, 4, 6, 8, 10, 12, 20, 100):
        raise ValueError("Choose a supported die (D2, D4, D6, D8, D10, D12, D20, or D100).")
    if not isinstance(quantity, int) or not 1 <= quantity <= 100:
        raise ValueError("Number of dice must be between 1 and 100.")
    if not isinstance(modifier, int) or not -100 <= modifier <= 100:
        raise ValueError("Modifier must be a whole number between -100 and 100.")
    if advantage not in ("None", "Advantage", "Disadvantage"):
        raise ValueError("Advantage must be None, Advantage, or Disadvantage.")
    if attribute_name not in ATTRIBUTES_LIST:
        raise ValueError("Choose a valid character attribute.")

    result = roll_dice(dice_type, quantity, modifier, advantage)
    log_line = (
        f"{character['name']} rolled {quantity} D{dice_type}"
        f"{f' ({advantage.lower()})' if advantage != 'None' else ''}"
        f"{format_attribute_log(attribute_name, modifier)}: {result['final_total']} "
        f"| Rolls: {', '.join(str(roll) for roll in result['rolls'])}"
    )

    state.setdefault("logs", []).append(
        {
            "id": f"log-{len(state.get('logs', [])) + 1}",
            "type": "dice",
            "character_id": character_id,
            "message": log_line,
            "result": result,
        }
    )
    return {
        "character": character,
        "result": result,
        "log_message": log_line,
        "state": state,
    }


def state_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """Return a simple summary suitable for UI or backend tests."""
    return {
        "campaign_name": state.get("campaign", {}).get("name", "Unknown Campaign"),
        "room_count": len(state.get("rooms", [])),
        "character_count": len(state.get("characters", [])),
        "log_count": len(state.get("logs", [])),
        "attribute_names": ATTRIBUTES_LIST,
    }


if __name__ == "__main__":
    initial_state = load_state(DEFAULT_STATE_PATH)
    print(json.dumps(state_summary(initial_state), indent=2))
