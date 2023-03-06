from pathlib import Path
from typing import Dict

from _pytest.reports import TestReport
from pytest_update_test_results.update_test_results import modify_xml


class UpdateTestResultsPlugin:
    """Class that collects test items and updates an existing XML file with the new test results"""

    def __init__(self, original_xmlfile: Path):
        self.reports: Dict[TestReport] = {}
        self.original_xmlfile = original_xmlfile

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            self.reports[report.nodeid] = report

    def pytest_sessionfinish(self, session, exitstatus):
        modify_xml(Path(self.original_xmlfile), self.reports, Path(self.original_xmlfile))


def pytest_addoption(parser):
    parser.addoption(
        "--update-xml",
        action="store",
        help="Overwrites a junit-xml report by changing failed/error outcomes "
        "to 'passed' in case they succeed.",
    )


def pytest_configure(config):
    original_xmlfile = config.getoption("--update-xml")
    if original_xmlfile:
        report = UpdateTestResultsPlugin(Path(original_xmlfile))
        config.pluginmanager.register(report)
