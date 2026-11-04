# -*- coding: utf-8 -*-
import json
import os
import tempfile
import unittest

from airtest.core import assertions
from airtest.core.helper import G
from airtest.utils import logwraper


class TestLogExtra(unittest.TestCase):
    """No device needed: only what lands in log.txt matters."""

    def setUp(self):
        self.logfile = os.path.join(tempfile.mkdtemp(), "log.txt")
        G.LOGGER.set_logfile(self.logfile)
        self.addCleanup(G.LOGGER.set_logfile, None)

    def _logged_call(self):
        G.LOGGER.set_logfile(None)
        with open(self.logfile) as f:
            entries = [json.loads(line) for line in f if line.strip()]
        return [e["data"] for e in entries if e["tag"] == "function"][-1]

    def test_extra_facts_are_saved_with_the_call(self):
        sources = {"actual": {"code": "tickets_after"}, "expected": {"code": "tickets_before + 50"}}

        assertions.assert_equal(200, 200, "Verify that tickets increased", snapshot=False,
                                log_extra={"sources": sources})

        call = self._logged_call()
        self.assertEqual(call["name"], "assert_equal")
        self.assertEqual(call["call_args"]["sources"], sources)
        self.assertEqual(call["call_args"]["first"], 200)

    def test_the_function_never_sees_the_keyword(self):
        def check(first, second, msg=""):
            return first, second, msg
        wrapped = logwraper.Logwrap(check, G.LOGGER)

        self.assertEqual(wrapped(1, 2, log_extra={"sources": {}}), (1, 2, ""))

    def test_a_failing_call_keeps_them_too(self):
        with self.assertRaises(AssertionError):
            assertions.assert_equal(150, 200, "Verify that tickets increased", snapshot=False,
                                    log_extra={"sources": {"actual": {"code": "tickets_after"}}})

        call = self._logged_call()
        self.assertIn("traceback", call)
        self.assertEqual(call["call_args"]["sources"]["actual"]["code"], "tickets_after")

    def test_without_it_the_call_is_logged_as_before(self):
        assertions.assert_equal(1, 1, "same", snapshot=False)

        self.assertNotIn("sources", self._logged_call()["call_args"])


if __name__ == "__main__":
    unittest.main()
