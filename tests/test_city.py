"""
test_city.py

This file tests the City class logic, including:
- City creation and attribute validation
- Serialization and deserialization (to_dict, from_dict)
- __repr__ output
"""
import unittest
from city import City

class TestCity(unittest.TestCase):
    def test_city_creation_defaults(self):
        city = City(owner_id="P1", x=2, y=3)
        self.assertEqual(city.owner_id, "P1")
        self.assertEqual(city.x, 2)
        self.assertEqual(city.y, 3)
        self.assertEqual(city.population, 1)
        self.assertTrue(city.name.startswith("City "))
        self.assertIsInstance(city.city_id, str)

    def test_city_creation_custom(self):
        city = City(owner_id="P2", x=5, y=7, name="Testville", city_id="abc123", population=5)
        self.assertEqual(city.owner_id, "P2")
        self.assertEqual(city.x, 5)
        self.assertEqual(city.y, 7)
        self.assertEqual(city.population, 5)
        self.assertEqual(city.name, "Testville")
        self.assertEqual(city.city_id, "abc123")

    def test_to_dict(self):
        city = City(owner_id="P3", x=8, y=9, name="Alpha", city_id="xyz789", population=4)
        d = city.to_dict()
        self.assertEqual(d["owner_id"], "P3")
        self.assertEqual(d["x"], 8)
        self.assertEqual(d["y"], 9)
        self.assertEqual(d["population"], 4)
        self.assertEqual(d["name"], "Alpha")
        self.assertEqual(d["city_id"], "xyz789")

    def test_from_dict(self):
        data = {
            "city_id": "def456",
            "owner_id": "P4",
            "name": "Beta",
            "population": 7,
            "x": 10,
            "y": 11
        }
        city = City.from_dict(data)
        self.assertEqual(city.city_id, "def456")
        self.assertEqual(city.owner_id, "P4")
        self.assertEqual(city.name, "Beta")
        self.assertEqual(city.population, 7)
        self.assertEqual(city.x, 10)
        self.assertEqual(city.y, 11)

    def test_repr(self):
        city = City(owner_id="P5", x=1, y=2, name="Gamma", population=3)
        rep = repr(city)
        self.assertIn("City", rep)
        self.assertIn("Gamma", rep)
        self.assertIn("P5", rep)
        self.assertIn("(1,2)", rep)
        self.assertIn("pop=3", rep)

if __name__ == "__main__":
    unittest.main()
