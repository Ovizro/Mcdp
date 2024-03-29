from shutil import rmtree
from mcdp import Namespace
from mcdp.context import Context, get_context, Handler, McdpContextError, annotate, insert
from unittest import TestCase


nsp = Namespace("Temp")


class TestContext(TestCase):
    def tearDown(self) -> None:
        rmtree("Temp", ignore_errors=True)

    def test_init(self) -> None:
        with nsp:
            c = get_context()
            self.assertRegex(str(c), r"<context __init__ in namespace Temp at 0x[0-9A-Z]+>")
    
    def test_insert(self) -> None:
        with nsp:
            ctx = get_context()

            with Context("__main__", ctx) as c:
                insert("say Hello world")
        
        with open("Temp/functions/__main__.mcfunction") as fr:
            self.assertEqual(
                fr.read(),
                "say Hello world\n"
            )
    
    def test_annotate(self) -> None:
        with nsp:
            ctx = get_context()

            with Context("__main__", ctx) as c:
                with annotate:
                    insert("hhh")
                annotate("First line\nSecond line")
        
        with open("Temp/functions/__main__.mcfunction") as fr:
            self.assertEqual(
                fr.read(),
                "# hhh\n# First line\n# Second line\n"
            )
    
    def test_handler(self) -> None:
        with nsp:
            ctx = get_context()

            with Context("__main__", ctx) as c:
                h = Handler()
                with annotate:
                    with self.assertRaises(TypeError):
                        c.add_handler(None) # type: ignore
                    c.add_handler(h)
                    self.assertEqual(len(c.get_handler()), 2)
                    c.pop_handler(h)
                    self.assertEqual(len(c.get_handler()), 1)
                    
                self.assertListEqual(c.get_handler(), [])
                with self.assertRaises(McdpContextError):
                    c.pop_handler()