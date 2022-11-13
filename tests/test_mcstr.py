from unittest import TestCase
from mcdp import Mcdatapack
from mcdp.variable.mcstring import MCSS, Color, NBTValueString, PlainString, RenderStyle, Score, mcstring, TranslatedString


class MCSTringLikeCls:
    def __mcstr__(self) -> PlainString:
        return mcstring("Hello", clickEvent={"action": "run_command", "value": "say Hello"})


class TestMCStr(TestCase):
    Mcdatapack("test", "1.17", "null")

    def test_init(self) -> None:
        with self.assertRaises(Exception):
            mcstring() # type: ignore
        with self.assertRaises(Exception):
            mcstring(style=None) # type: ignore

        m = mcstring("Hello")
        self.assertEqual(str(m).replace(' ', ''), "{\"text\":\"Hello\"}")
        self.assertEqual(repr(m).replace(' ', ''), "PlainString({\"text\":\"Hello\"})")
        self.assertIs(m, mcstring(m))
        m1 = mcstring(MCSTringLikeCls())
        self.assertEqual(m.text, m1.text)
    
    def test_plainstr(self) -> None:
        m = mcstring("Hello")
        self.assertEqual(m.text, "Hello")
        self.assertEqual(m, PlainString("Hello"))

        with self.assertRaises(TypeError):
            m + " world" # type: ignore
        
        m1 = mcstring(" world")
        self.assertEqual(
            (m + m1).copy().to_dict(),
            {
                "extra": [
                    m,
                    m1
                ]
            }
        )
        sep = mcstring(", ")
        self.assertEqual(
            sep.join([m, m1]).to_dict(),
            {
                "extra": [m, sep, m1]
            }
        )

        m2 = mcstring("Hello, %s")
        m3 = m2 % "Hello"
        self.assertIsInstance(m3, TranslatedString)
        self.assertEqual(m3.with_, (m,))
        self.assertEqual(m3, m2 % m)
    
    def test_transtr(self) -> None:
        m = mcstring(translate="%s %s", with_=["hhh", "hhh"])
        self.assertEqual(m.with_, (PlainString("hhh"),) * 2)
        self.assertEqual(m.copy(), m)
        m1 = TranslatedString("%s %s", "hhh", "hhh")
        m2 = TranslatedString("%s %s", with_=["hhh", "hhh"])
        self.assertEqual(m, m1)
        self.assertEqual(m, m2)
    
    def test_scorestr(self) -> None:
        m = mcstring(score={"name": "dp_cache000", "objective": "@a"})
        self.assertIsInstance(m.score, Score)
        self.assertEqual(m.copy(), m)
    
    def test_entitystr(self) -> None:
        m = mcstring(selector="@a")
        self.assertEqual(m.separator, None)
        self.assertEqual(m.copy(), m)
        m1 = mcstring(selector="@a", separator="..")
        self.assertEqual(m1.separator, PlainString(".."))
    
    def test_nbtstr(self) -> None:
        with self.assertRaises(Exception):
            NBTValueString("x")
        m = mcstring(nbt="rotate[0]", entity="@p")
        self.assertEqual(m.block, None)
        self.assertEqual(m.copy(), m)
    
    def test_mcss(self) -> None:
        mcss = MCSS()
        m = mcstring("Hello")
        self.assertEqual(mcss("Hello"), m)
    
        mcss = MCSS(RenderStyle.bold | RenderStyle.underlined, color=Color.aqua)
        self.assertEqual(
            mcss.to_dict(),
            {"bold": True, "underlined": True, "color": "aqua"}
        )
        m1 = mcss("Hello")
        self.assertNotEqual(m1, m)
        self.assertIs(m1.style, mcss)