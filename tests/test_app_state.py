import json
import tempfile
import unittest
from pathlib import Path

from Gin import app_state


class AppStateTests(unittest.TestCase):
    def setUp(self):
        self.state = app_state.build_demo_state()

    def test_roll_adds_persistable_dice_log(self):
        outcome = app_state.perform_roll(
            self.state,
            character_id="char-01",
            dice_type=20,
            quantity=1,
            modifier=2,
            advantage="Advantage",
            attribute_name="Dexterity",
        )

        self.assertIn(outcome["result"]["final_total"], range(3, 23))
        self.assertEqual(self.state["logs"][-1]["type"], "dice")
        self.assertIn("Ariadne rolled 1 D20 (advantage)", outcome["log_message"])

    def test_roll_rejects_unsupported_input(self):
        with self.assertRaisesRegex(ValueError, "supported die"):
            app_state.perform_roll(self.state, "char-01", dice_type=3)
        with self.assertRaisesRegex(ValueError, "Number of dice"):
            app_state.perform_roll(self.state, "char-01", dice_type=6, quantity=0)

    def test_room_creation_validates_name_and_type(self):
        room = app_state.add_room(self.state, "  The Old Bridge  ", "encounter")
        self.assertEqual(room["name"], "The Old Bridge")
        self.assertEqual(room["type"], "encounter")
        self.assertEqual(room["characters"], ["char-01", "char-02"])
        with self.assertRaisesRegex(ValueError, "already exists"):
            app_state.add_room(self.state, "the old bridge", "gm")
        with self.assertRaisesRegex(ValueError, "Room type"):
            app_state.add_room(self.state, "Another Room", "player")

    def test_movement_enforces_turn_limit_occupancy_and_reset(self):
        moved = app_state.move_character(self.state, "char-01", 8, 2)
        character = app_state.find_character(moved, "char-01")
        self.assertEqual(character["position"], {"x": 8, "y": 2})
        self.assertTrue(character["has_moved"])
        self.assertFalse(app_state.can_move_character(moved, "char-01", {"x": 9, "y": 2}))
        self.assertFalse(app_state.can_move_character(self.state, "char-01", {"x": 6, "y": 2}, 1))
        self.assertFalse(app_state.can_move_character(self.state, "char-01", {"x": 9, "y": 2}, 36))

        with self.assertRaisesRegex(ValueError, "invalid"):
            app_state.move_character(moved, "char-02", 8, 2)

        app_state.reset_turn(moved)
        self.assertTrue(app_state.can_move_character(moved, "char-01", {"x": 9, "y": 2}))

    def test_state_round_trips_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            app_state.save_state(self.state, state_path)
            loaded_state = app_state.load_state(state_path)

        self.assertEqual(json.dumps(loaded_state), json.dumps(self.state))


if __name__ == "__main__":
    unittest.main()
