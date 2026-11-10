import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from src.main import FAILURE_CODE, main


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


class MainTest(unittest.TestCase):
    def test_params(self):
        code, out, _ = run("configs/simple.ini", "params")
        self.assertEqual(code, 0)
        self.assertIn("package = A", out)

    def test_deps(self):
        _, out, _ = run("configs/simple.ini", "deps")
        self.assertIn("  B", out)

    def test_order(self):
        _, out, _ = run("configs/cycle.ini", "order")
        self.assertIn("Порядок загрузки: D C B A", out)

    def test_all(self):
        _, out, _ = run("configs/simple.ini")
        self.assertIn("@startuml", out)

    def test_unknown_mode(self):
        code, _, err = run("configs/simple.ini", "draw")
        self.assertEqual(code, FAILURE_CODE)
        self.assertIn("неизвестный режим", err)

    def test_config_error(self):
        code, _, _ = run("configs/errors/zero_depth.ini")
        self.assertEqual(code, FAILURE_CODE)


if __name__ == "__main__":
    unittest.main()
