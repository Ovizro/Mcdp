from unittest import TestCase
from mcdp.variable.mcstring import mcstring, TranslatedString


class TestMCStr(TestCase):
    def test_init(self) -> None:
        m = mcstring("Hello")
        self.assertEqual(str(m).replace(' ', ''), "{\"text\":\"Hello\"}")
        self.assertEqual(repr(m).replace(' ', ''), "PlainString({\"text\":\"Hello\"})")
        self.assertIs(m, mcstring(m))
    
    def test_operation(self) -> None:
        m = mcstring("Hello")
        self.assertEqual(m.text, "Hello")

        with self.assertRaises(TypeError):
            m + " world" # type: ignore
        
        m1 = mcstring(" world")
        self.assertEqual(
            (m + m1).copy().to_dict(),
            {
                "text": "Hello",
                "extra": [
                    m1
                ]
            }
        )

        m2 = mcstring("Hello, %s")
        m3 = m2 % "Hello"
        self.assertIsInstance(m3, TranslatedString)
        self.assertEqual(m3.with_, (m,))
        self.assertEqual(m3, m2 % m)