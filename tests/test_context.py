from shutil import rmtree
from mcdp import BaseNamespace
from mcdp.context import Context, Handler, McdpContextError, comment, init_context, insert
from unittest import TestCase


def clear_file():
    rmtree("Temp")


class TestContext(TestCase):
    def test_init(self) -> None:
        nsp = BaseNamespace("Temp")
        c = init_context(nsp)
        self.assertRegex(str(c), r"<context __init__ in namespace Temp at 0x[0-9A-Z]+>")
    
    def test_insert(self) -> None:
        self.addCleanup(clear_file)
        nsp = BaseNamespace("Temp")
        ctx = init_context(nsp)

        with Context("__main__", ctx) as c:
            insert("say Hello world")
        ctx.deactivate()
        
        with open("Temp/functions/__main__.mcfunction") as fr:
            self.assertEqual(
                fr.read(),
                "say Hello world\n"
            )
    
    def test_comment(self) -> None:
        self.addCleanup(clear_file)
        nsp = BaseNamespace("Temp")
        ctx = init_context(nsp)

        with Context("__main__", ctx) as c:
            with comment:
                insert("hhh")
            comment("First line\nSecond line")
        ctx.deactivate()
        
        with open("Temp/functions/__main__.mcfunction") as fr:
            self.assertEqual(
                fr.read(),
                "# hhh\n# First line\n# Second line\n"
            )
    
    def test_handler(self) -> None:
        self.addCleanup(clear_file)
        nsp = BaseNamespace("Temp")
        ctx = init_context(nsp)

        with Context("__main__", ctx) as c:
            h = Handler()
            with comment:
                
                with self.assertRaises(ValueError):
                    c.add_handler(None)
                c.add_handler(h)
                self.assertEqual(len(c.get_handler()), 2)
                c.pop_handler(h)
                self.assertEqual(len(c.get_handler()), 1)
                
            self.assertEqual(c.get_handler(), [])
            with self.assertRaises(McdpContextError):
                c.pop_handler()
        ctx.deactivate()