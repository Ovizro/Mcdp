from unittest import TestCase
from mcdp.variable.selector import Selector, selector


class SelectorLikeCls:
    def __selector__(self) -> Selector:
        return Selector("@a")

class TestSelector(TestCase):
    def test_init(self) -> None:
        slt = Selector("@p")
        self.assertEqual(str(slt), "@p")
    
    def test_args(self) -> None:
        slt = Selector("@p", [("tag", "a"), ("tag", "b")], scores={"myscore": 1})
        self.assertSetEqual(slt.args["tag"], {"a", "b"})
        self.assertRegex(str(slt), r"@p\[scores={myscore=1},tag=[ab],tag=[ba]\]")

        slt = Selector("@p[tag=a,tag=b]")
        self.assertEqual(slt.args["tag"], {"a", "b"})
        with self.assertRaises(ValueError):
            Selector("@a[tag=a,]")
        with self.assertRaises(ValueError):
            Selector("@a[tag=a,tag=b")
    
    def test_func(self) -> None:
        slt = selector("@a")
        self.assertIs(slt, selector(slt))
        
        s = SelectorLikeCls()
        self.assertEqual(selector(s), slt)