import unittest
import src

class TestProjectInitialization(unittest.TestCase):
    def test_version_exists(self):
        self.assertIsNotNone(src.__version__)

if __name__ == "__main__":
    unittest.main()
