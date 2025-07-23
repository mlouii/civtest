"""
test_unit.py

This file tests the Unit class logic, including:
- Unit creation and attribute validation
- Movement, selection, and move/reset logic
- Serialization and error handling
- __repr__ output
"""
import unittest
from unit import Warrior, Settler
from unit_config import UNIT_TYPES

class DummyMap:
    def is_tile_passable(self, x, y):
        return True

class BlockMap:
    def is_tile_passable(self, x, y):
        return False

class TestUnit(unittest.TestCase):
    def setUp(self):
        self.unit = Settler(unique_id=1, owner="player1", x=2, y=3)

    def test_unit_creation(self):
        self.assertEqual(self.unit.unique_id, 1)
        self.assertEqual(self.unit.owner, "player1")
        self.assertEqual(self.unit.unit_type, "settler")
        self.assertEqual(self.unit.x, 2)
        self.assertEqual(self.unit.y, 3)
        self.assertEqual(self.unit.moves, UNIT_TYPES["settler"]["move_points"])
        self.assertEqual(self.unit.hp, UNIT_TYPES["settler"]["hp"])
        self.assertFalse(self.unit.selected)

    def test_unit_repr(self):
        rep = repr(self.unit)
        self.assertIn("Unit", rep)
        self.assertIn("settler", rep)
        self.assertIn("player1", rep)

    def test_unit_move_and_reset(self):
        moved = self.unit.move(2, 4, DummyMap())
        self.assertTrue(moved)
        self.assertEqual(self.unit.x, 2)
        self.assertEqual(self.unit.y, 4)
        self.assertEqual(self.unit.moves, UNIT_TYPES["settler"]["move_points"] - 1)
        self.unit.reset_moves()
        self.assertEqual(self.unit.moves, UNIT_TYPES["settler"]["move_points"])

    def test_unit_cannot_move_without_moves(self):
        self.unit.moves = 0
        moved = self.unit.move(2, 4, DummyMap())
        self.assertFalse(moved)

    def test_unit_can_move_validation(self):
        self.unit.moves = UNIT_TYPES["settler"]["move_points"]
        # Valid adjacent
        self.assertTrue(self.unit.can_move(2, 4, DummyMap()))
        # Not adjacent
        self.assertFalse(self.unit.can_move(4, 4, DummyMap()))
        # Not passable
        self.assertFalse(self.unit.can_move(2, 4, BlockMap()))

    def test_unit_to_dict(self):
        d = self.unit.to_dict()
        self.assertEqual(d["unique_id"], 1)
        self.assertEqual(d["owner"], "player1")
        self.assertEqual(d["unit_type"], "settler")
        self.assertEqual(d["x"], 2)
        self.assertEqual(d["y"], 3)
        self.assertEqual(d["moves"], UNIT_TYPES["settler"]["move_points"])
        self.assertEqual(d["hp"], UNIT_TYPES["settler"]["hp"])
        self.assertFalse(d["selected"])

    def test_unit_selection(self):
        self.unit.selected = True
        self.assertTrue(self.unit.selected)

    def test_unknown_unit_type_raises(self):
        from unit import Unit
        with self.assertRaises(ValueError):
            Unit.from_dict({
                "unique_id": 2,
                "owner": "player2",
                "unit_type": "unknown",
                "x": 0,
                "y": 0,
                "moves": 2,
                "selected": False
            })

if __name__ == "__main__":
    unittest.main()
