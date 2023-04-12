from unittest import TestCase
from mcdp import Namespace
from mcdp.variable.baseframe import BaseFrame, FrameVariable, NamePool, get_channel


class TestBaseFrame(TestCase):
    def test_bind(self) -> None:
        n = Namespace("temp")
        f = BaseFrame(n)
        self.assertIs(f.__namespace__, n)
        self.assertEqual(get_channel(f, 0).used_size, 0)
        f.var0 = FrameVariable()
        self.assertIs(f.var0.namespace, n)
        self.assertEqual(f.var0.__name__, "dpc_0000")
        self.assertEqual(get_channel(f, 0).used_size, 1)
        f.var0 = FrameVariable()
        f.var1 = FrameVariable()
        self.assertEqual(f.var0.__name__, "dpc_0001")
        self.assertEqual(f.var1.__name__, "dpc_0000")
        f.var1.__name__ = "dpc_eax"
        f.var2 = FrameVariable()
        self.assertEqual(f.var2.__name__, "dpc_0000")
    
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