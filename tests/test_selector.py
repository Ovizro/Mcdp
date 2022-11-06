from unittest import TestCase
from mcdp.variable.mcstring import mcstring
from mcdp.variable.selector import Selector, selector, s_nearest


class SelectorLikeCls:
    def __selector__(self) -> Selector:
        return Selector("@a")

class TestSelector(TestCase):
    def test_init(self) -> None:
        slt = Selector("@p")
        self.assertEqual(slt, s_nearest)
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
        
        with self.assertRaises(TypeError):
            slt.args['tag'] = {"a"} # type: ignore
    
    def test_func(self) -> None:
        slt = selector("@a")
        self.assertIs(slt, selector(slt))
        
        s = SelectorLikeCls()
        self.assertEqual(selector(s), slt)
    
    def test_mcstr(self) -> None:
        slt = s_nearest
        self.assertEqual(mcstring(slt).to_dict(), {"selector": slt.name})