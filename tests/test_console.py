from shutil import rmtree
from unittest import TestCase

from mcdp import Namespace
from mcdp.variable.console import console


nsp = Namespace("test")

class TestConsole(TestCase):
    def tearDown(self) -> None:
        rmtree(nsp.n_name, ignore_errors=True)
    
    @staticmethod
    def read_file():
        with open(f"{nsp.n_name}/functions/__init__.mcfunction", encoding="utf-8") as f:
            return f.read()

    def test_print(self) -> None:
        with nsp:
            console.print("hhh", "hhh")
        text = TestConsole.read_file()
        self.assertEqual(
            text.split(' ', maxsplit=2)[2].replace(' ', ''),
            '[{"text":"hhh"},{"text":""},{"text":"hhh"}]\n'
        )