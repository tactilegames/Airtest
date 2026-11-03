# -*- coding: utf-8 -*-
import json
import unittest
from unittest import mock

from airtest.report import report
from airtest.report.report import LogToHtml

TITLE = 'Waiting timeout for appearance of "LocationHubView(Clone)>LocationsTab" while 3 < 5 </script>'


class TestAngleBrackets(unittest.TestCase):
    """No device needed: the run is stubbed, only the step text going into the page matters."""

    def _data(self):
        rpt = LogToHtml("/tmp/does_not_matter.air", log_root="/tmp/does_not_matter.air/log")
        with mock.patch.object(LogToHtml, "_load"), \
                mock.patch.object(LogToHtml, "_analyse", return_value=[{"title": TITLE}]), \
                mock.patch.object(LogToHtml, "get_relative_log", return_value=""), \
                mock.patch.object(LogToHtml, "get_console", return_value=""), \
                mock.patch.object(report, "get_script_info", return_value="{}"):
            return rpt.report_data()["data"]

    def test_stock_template_still_gets_braces(self):
        data = self._data()
        self.assertNotIn("<", data)
        self.assertIn("LocationHubView(Clone)}LocationsTab", data)

    def test_escaping_template_gets_the_real_characters(self):
        with mock.patch.object(report, "ESCAPE_ANGLE_BRACKETS", True):
            data = self._data()
        self.assertNotIn("<", data)
        self.assertNotIn(">", data)
        self.assertEqual(json.loads(data)["steps"][0]["title"], TITLE)


if __name__ == "__main__":
    unittest.main()
