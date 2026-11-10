import unittest

from src.pypi import (PypiRepository, normalize, parse_requirement,
                      requirements_to_names)


class RequirementTest(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize("Typing_Extensions"), "typing-extensions")

    def test_plain(self):
        self.assertEqual(parse_requirement("idna<4,>=2.5"), "idna")

    def test_with_marker(self):
        text = 'colorama; platform_system == "Windows"'
        self.assertEqual(parse_requirement(text), "colorama")

    def test_extra_is_skipped(self):
        text = 'PySocks!=1.5.7,>=1.5.6; extra == "socks"'
        self.assertIsNone(parse_requirement(text))

    def test_unique_names(self):
        names = requirements_to_names(["a>1", "a<3", "b"])
        self.assertEqual(names, ["a", "b"])

    def test_none(self):
        self.assertEqual(requirements_to_names(None), [])


class FakePypi(PypiRepository):
    def __init__(self):
        super().__init__("https://example.org/pypi/")
        self.urls = []

    def _load(self, package, version):
        self.urls.append((package, version))
        return {"info": {"requires_dist": ["b>=1", "c; extra == 'x'"]}}


class RepositoryTest(unittest.TestCase):
    def test_dependencies(self):
        repository = FakePypi()
        self.assertEqual(repository.dependencies("a", "1.0"), ["b"])

    def test_cache(self):
        repository = FakePypi()
        repository.dependencies("a")
        repository.dependencies("a")
        self.assertEqual(repository.urls, [("a", "latest")])


if __name__ == "__main__":
    unittest.main()
