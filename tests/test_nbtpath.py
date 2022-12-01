from unittest import TestCase
from mcdp.variable.nbtpath import NBTPath


class TestNBTPath(TestCase):
    def test_init(self) -> None:
        test_list = [
            "{}",
            "{foo:4.0f}",
            "foo{}.bar",
            "foo.bar[0]",
            "foo.bar[0].\"A [crazy name].\".baz",
            "foo.bar[]",
            "foo.bar[{baz:5b}]"
        ]
        nbtp_list = map(NBTPath, test_list)
        self.assertListEqual(list(map(str, nbtp_list)), test_list)

    def test_len(self) -> None:
        self.assertEqual(len(NBTPath("{foo:4.0f}")), 1)
        self.assertEqual(len(NBTPath("foo.bar[0].\"A [crazy name].\".baz")), 4)
    
    def test_getitem(self) -> None:
        nbtp = NBTPath("foo.bar[0].\"A [crazy name].\".baz")
        self.assertIs(nbtp[-1], nbtp)
        self.assertEqual(str(nbtp[0]), "foo")
        self.assertEqual(str(nbtp[1]), "foo.bar[0]")
        self.assertTupleEqual(nbtp[2].named_tags, ("foo", "bar[0]", "\"A [crazy name].\""))