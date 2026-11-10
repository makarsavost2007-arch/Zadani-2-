import os
import unittest

from src.errors import RepositoryError
from src.graph import build_graph, load_order
from src.local_repo import LocalRepository, parse_graph


def repo(name):
    return LocalRepository(os.path.join("tests", "data", name + ".txt"))


class LocalRepositoryTest(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_graph("A: B C\nB:"), {"A": ["B", "C"], "B": []})

    def test_lowercase_name(self):
        with self.assertRaises(RepositoryError):
            parse_graph("A: b")

    def test_bad_line(self):
        with self.assertRaises(RepositoryError):
            parse_graph("A B")

    def test_missing_file(self):
        with self.assertRaises(RepositoryError):
            LocalRepository("no_such_file.txt")

    def test_unknown_package(self):
        with self.assertRaises(RepositoryError):
            repo("simple").dependencies("Z")


class BuildGraphTest(unittest.TestCase):
    def test_full_graph(self):
        graph, cycles = build_graph(repo("simple"), "A", 10)
        self.assertEqual(list(graph), ["A", "B", "D", "F", "C", "E"])
        self.assertEqual(graph["C"], ["D", "E"])
        self.assertEqual(cycles, [])

    def test_depth(self):
        graph, _ = build_graph(repo("simple"), "A", 1)
        self.assertEqual(graph, {"A": ["B", "C"], "B": [], "C": []})

    def test_depth_limit(self):
        graph, _ = build_graph(repo("deep"), "A", 2)
        self.assertEqual(graph["XA"], ["E"])
        self.assertNotIn("D", graph)

    def test_shallow_path_wins(self):
        graph, _ = build_graph(repo("shortcut"), "A", 2)
        self.assertEqual(graph["C"], ["D"])

    def test_exclude(self):
        graph, _ = build_graph(repo("deep"), "A", 10, "X")
        self.assertNotIn("XA", graph)
        self.assertNotIn("XB", graph)
        self.assertIn("E", graph)

    def test_cycle(self):
        graph, cycles = build_graph(repo("cycle"), "A", 10)
        self.assertEqual(graph["C"], ["A", "D"])
        self.assertEqual(cycles, [["A", "B", "C", "A"]])

    def test_several_cycles(self):
        _, cycles = build_graph(repo("multi_cycle"), "A", 10)
        self.assertIn(["B", "C", "B"], cycles)
        self.assertIn(["A", "B", "C", "D", "A"], cycles)


class LoadOrderTest(unittest.TestCase):
    def order(self, name):
        graph, _ = build_graph(repo(name), "A", 10)
        return load_order(graph, "A")

    def test_simple(self):
        self.assertEqual(self.order("simple"), ["F", "D", "B", "E", "C", "A"])

    def test_cycle(self):
        self.assertEqual(self.order("cycle"), ["D", "C", "B", "A"])

    def test_dependencies_first(self):
        order = self.order("deep")
        self.assertLess(order.index("E"), order.index("XA"))
        self.assertEqual(order[-1], "A")


if __name__ == "__main__":
    unittest.main()
