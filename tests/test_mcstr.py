from unittest import TestCase
from mcdp.variable import MCString, mcstring


class TestMCStr(TestCase):
    def test_init(self) -> None:
        m = mcstring("Hello")
        self.assertEqual(str(m).replace(' ', ''), "{\"text\":\"Hello\"}")
        self.assertEqual(repr(m).replace(' ', ''), "MCString({\"text\":\"Hello\"})")

        with self.assertRaises(TypeError):
            mcstring()
    
    def test_operation(self) -> None:
        m = mcstring("Hello")
        self.assertEqual(m.text, "Hello")

        with self.assertRaises(TypeError):
            m += " world" # type: ignore
        
        self.assertEqual(
            (m + mcstring(" world")).copy().to_dict(),
            {
                "text": "Hello",
                "extra": [
                    {"text": " world"}
                ]
            }
        )