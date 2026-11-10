import os
import tempfile
import unittest

from src.config import build_config, load_config
from src.errors import ConfigError

VALID = {
    "package": "requests",
    "version": "2.32.3",
    "repository": "https://pypi.org/pypi",
    "test_mode": "false",
    "max_depth": "2",
    "exclude": "test",
}


def with_values(**changes):
    data = dict(VALID, **changes)
    return {key: value for key, value in data.items() if value is not None}


def ini_file(text):
    handle, path = tempfile.mkstemp(suffix=".ini")
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        stream.write(text)
    return path


class ConfigTest(unittest.TestCase):
    def test_valid(self):
        config = build_config(VALID)
        self.assertEqual(config.package, "requests")
        self.assertEqual(config.version, "2.32.3")
        self.assertFalse(config.test_mode)
        self.assertEqual(config.max_depth, 2)
        self.assertEqual(config.exclude, "test")

    def test_load_file(self):
        path = ini_file("[settings]\npackage = a\nrepository = x\n"
                        "max_depth = 1\n")
        config = load_config(path)
        self.assertEqual(config.version, "latest")
        self.assertEqual(config.exclude, "")

    def test_missing_file(self):
        with self.assertRaises(ConfigError):
            load_config("no_such_file.ini")

    def test_no_section(self):
        with self.assertRaises(ConfigError):
            load_config(ini_file("package = a\n"))

    def test_bad_format(self):
        with self.assertRaises(ConfigError):
            load_config(ini_file("[settings]\npackage a\n"))

    def test_unknown_key(self):
        with self.assertRaises(ConfigError):
            build_config(with_values(color="red"))

    def test_missing_package(self):
        with self.assertRaises(ConfigError):
            build_config(with_values(package=None))

    def test_package_with_space(self):
        with self.assertRaises(ConfigError):
            build_config(with_values(package="a b"))

    def test_missing_repository(self):
        with self.assertRaises(ConfigError):
            build_config(with_values(repository=None))

    def test_bad_version(self):
        with self.assertRaises(ConfigError):
            build_config(with_values(version="two"))

    def test_prerelease_version(self):
        self.assertEqual(build_config(with_values(version="1.0rc1")).version,
                         "1.0rc1")

    def test_bad_mode(self):
        with self.assertRaises(ConfigError):
            build_config(with_values(test_mode="maybe"))

    def test_bad_depth(self):
        with self.assertRaises(ConfigError):
            build_config(with_values(max_depth="two"))

    def test_zero_depth(self):
        with self.assertRaises(ConfigError):
            build_config(with_values(max_depth="0"))


if __name__ == "__main__":
    unittest.main()
