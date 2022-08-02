from mcdp import BaseNamespace
from mcdp.context import Context, init_context
from unittest import TestCase


class TestContext(TestCase):
    def test_init(self) -> None:
        nsp = BaseNamespace("Hello")
        init_context(nsp)