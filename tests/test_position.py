from unittest import TestCase

from mcdp.exception import McdpValueError
from mcdp.variable.position import Position, position, ComponentType


class TestPosition(TestCase):
    def test_init(self) -> None:
        pos = Position("1 2.2 3")

        self.assertAlmostEqual(float(pos.x), 1)
        self.assertAlmostEqual(float(pos.y), 2.2)
        self.assertAlmostEqual(float(pos.z), 3)
        self.assertEqual(str(pos), "1 2.2 3")

        self.assertEqual(pos.type, ComponentType.absolute)
        self.assertEqual(pos.x.type, ComponentType.absolute)
        
        pos1 = Position(x=1, y=2, z=30000000)
        self.assertEqual(pos1.type, ComponentType.absolute)

        pos2 = Position(x=1, y=2022.222, z=0.5, type=ComponentType.local)
        self.assertEqual(str(pos2.x), "^1")
        self.assertRegex(str(pos2.y), r"\^2022.222\d*")
        self.assertEqual(str(pos2.z), "^0.5")

        with self.assertRaises(McdpValueError):
            Position(x=1, y=2, z=30000005)
        with self.assertRaises(McdpValueError):
            Position("^1 1 1")
    
    def test_calc(self) -> None:
        pos = Position("~ ~ ~")
        pos1 = Position("~ ~1 ~")
        pos2 = Position("16 ~2 5")

        self.assertEqual(pos + pos1, pos1)
        with self.assertRaises(TypeError):
            pos += pos2
        
        self.assertAlmostEqual(float(pos1.y - pos2.y), -1)

        x, y, z = Position("1 2 4")
        self.assertNotEqual(x, pos1.y)
        self.assertAlmostEqual(float(x), float(pos1.y))

        self.assertEqual(x + 3, z)
        self.assertEqual(x + x, y)
        self.assertEqual(y - 1, x)
        self.assertEqual(z - y, y)
        self.assertEqual(x * 2, y)
        self.assertEqual(z / 2, y)
        self.assertIs(+x, x)
        self.assertEqual(float(-y), -2)
        self.assertEqual(abs(z), z)

        pos = Position("1 2 4")
        pos1 = Position("2 3 5")
        self.assertEqual(pos + pos1, Position("3 5 9"))
        self.assertEqual(pos + 1, pos1)
        self.assertEqual(pos1 - pos, Position("1 1 1"))
        self.assertEqual(pos1 - 1, pos)
        self.assertEqual((pos * pos1).x, y)
        self.assertEqual(pos * 2, Position("2 4 8"))
        self.assertEqual(pos * (2, 1.5, 4), Position("2 3 16"))
        self.assertEqual((pos / pos1).z, y * 0.4)
        self.assertEqual(pos1 / 2, Position("1 1.5 2.5"))
        self.assertEqual(pos1 / (2, 3, 5), Position("1 1 1"))

    def test_func(self) -> None:
        pos = position(1, 2, 3)
        self.assertEqual(pos, Position("1 2 3"))
