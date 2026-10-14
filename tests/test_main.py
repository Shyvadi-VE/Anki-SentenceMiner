import unittest
import src

class TestProjectStructure(unittest.TestCase):
    def test_imports(self):
        self.assertIsNotNone(src)

if __name__ == "__main__":
    unittest.main()
