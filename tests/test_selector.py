from unittest import TestCase
from mcdp.variable.selector import Selector


class TestSelector(TestCase):
    def test_init(self) -> None:
        slt = Selector("@p")
        self.assertEqual(str(slt), "@p")
    
    def test_args(self) -> None:
        slt = Selector("@p", [("tag", "a"), ("tag", "b")])
        self.assertSetEqual(slt.args["tag"], {"a", "b"})
        self.assertRegex(str(slt), r"@p\[tag=[ab],tag=[ba]\]")