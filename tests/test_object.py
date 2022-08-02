from mcdp.objects import McdpObject, BaseNamespace
from unittest import TestCase


class TestObject(TestCase):
    def test_init(self) -> None:
        obj = McdpObject()
        nsp = BaseNamespace("test")
    
    def test_property(self) -> None:
        nsp = BaseNamespace("test")
        self.assertEqual(nsp.n_name, "test")

        with self.assertRaises(AttributeError):
            nsp.n_testflag
        
        @BaseNamespace.property
        def testflag(nsp: BaseNamespace) -> str:
            return f"{nsp.n_name}_flag"

        self.assertEqual(nsp.n_testflag, "test_flag")