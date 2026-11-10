import unittest

from src.plantuml import to_plantuml


class PlantUmlTest(unittest.TestCase):
    def test_frame(self):
        text = to_plantuml({"A": []})
        self.assertTrue(text.startswith("@startuml"))
        self.assertTrue(text.endswith("@enduml\n"))

    def test_component_alias(self):
        text = to_plantuml({"typing-extensions": []})
        self.assertIn(
            'component "typing-extensions" as p_typing_extensions', text)

    def test_edge(self):
        self.assertIn("p_A --> p_B", to_plantuml({"A": ["B"], "B": []}))

    def test_cycle_edge(self):
        graph = {"A": ["B"], "B": ["A"]}
        text = to_plantuml(graph, [["A", "B", "A"]])
        self.assertIn("p_B -[#red]-> p_A", text)


if __name__ == "__main__":
    unittest.main()
