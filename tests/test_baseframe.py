from unittest import TestCase
from mcdp import Namespace
from mcdp.variable.baseframe import BaseFrame, FrameVariable, NamePool


class TestBaseFrame(TestCase):
    def test_init(self) -> None:
        f = BaseFrame(None)
        with self.assertRaises(AttributeError):
            f.__namespace__
        f.var0 = FrameVariable()
        
    def test_bind(self) -> None:
        n = Namespace("temp")
        f = BaseFrame(n)
        self.assertIs(f.__namespace__, n)
        f.var0 = FrameVariable()
        self.assertIs(f.var0.namespace, n)
    
    def test_pool(self) -> None:
        p = NamePool("dp_%04d")
        n1 = p.fetch()
        self.assertEqual(n1, "dp_0000")
        n2 = p.fetch()
        self.assertEqual(n2, "dp_0001")
        self.assertEqual(p.used_size, 2)
        p.release(n1)
        n3 = p.fetch()
        self.assertEqual(n1, n3)
        self.assertEqual(p.used_size, 2)