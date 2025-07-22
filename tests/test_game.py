"""
test_game.py

Centralized test runner and command center for Civ MVP Game.
This file orchestrates all module and integration tests for the project.
Run this file to execute all tests in the suite.
"""

import unittest
import importlib

TEST_MODULES = [
    "tests.test_city",
    "tests.test_unit",
    "tests.test_map",
    "tests.test_pathfinding",
    "tests.test_main",
    "tests.test_starting_tiles"
]


def run_module_tests(suite, module_name):
    result = unittest.TestResult()
    suite.run(result)
    if result.wasSuccessful():
        print(f"{module_name} module: PASS")
    else:
        print(f"{module_name} module: FAIL")
        for failure in result.failures + result.errors:
            print("   ", failure[1].strip().replace('\n', '\n    '))


def run_tests():
    print("\n=== Civ MVP Game - Module Tests ===\n")
    for mod_name in TEST_MODULES:
        try:
            mod = importlib.import_module(mod_name)
            # Find all TestCase classes in the module
            for attr in dir(mod):
                obj = getattr(mod, attr)
                if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
                    run_module_tests(unittest.defaultTestLoader.loadTestsFromTestCase(obj), mod_name)
        except Exception as e:
            print(f"Could not import or run {mod_name}: {e}")
    print("\n============================\n")


if __name__ == "__main__":
    run_tests()
