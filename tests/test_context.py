from shutil import rmtree
from mcdp import BaseNamespace
from mcdp.context import Context, Handler, McdpContextError, comment, init_context, insert
from unittest import TestCase


def clear_file():
    rmtree("Temp", ignore_errors=True)


class TestContext(TestCase):
    def test_init(self) -> None:
        nsp = BaseNamespace("Temp")
        init_context(nsp)
    
    def test_insert(self) -> None:
        self.addCleanup(clear_file)
        nsp = BaseNamespace("Temp")
        ctx = init_context(nsp)

        with Context("__main__", ctx) as c:
            insert("say Hello world")
            with comment:
                h = Handler()
                with self.assertRaises(ValueError):
                    c.add_handler(None)
                c.add_handler(h)
                self.assertEqual(len(c.get_handler()), 2)
                insert("hhh")
                c.pop_handler()
                self.assertEqual(len(c.get_handler()), 1)
                
            self.assertEqual(c.get_handler(), [])
            with self.assertRaises(McdpContextError):
                c.pop_handler()
        
        with open("Temp/functions/__main__.mcfunction") as fr:
            self.assertEqual(
                fr.read(),
                "say Hello world\n# hhh\n"
            )