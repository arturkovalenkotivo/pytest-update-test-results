from pathlib import Path
from xml.etree import ElementTree as ET

from _pytest.reports import TestReport
from pytest_regressions.file_regression import FileRegressionFixture
from pytest_update_test_results.update_test_results import modify_xml


def test_one_failure(datadir: Path) -> None:
    retest_results = {
        "test_xml_three_failed_zero_passed": TestReport(
            nodeid="test/test_pytest_merge_xml.py::test_xml_three_failed_zero_passed",
            outcome="passed",
            location=("test/test_pytest_merge_xml.py", 88, "test_xml_three_failed_zero_passed"),
            keywords="",
            longrepr=None,
            when="call",
        )
    }

    modified_file = datadir / "one_failure.retest.xml"
    modify_xml(Path(datadir / "one_failure.xml"), retest_results, modified_file)

    et = ET.parse(modified_file)
    root_el = et.getroot()
    testsuite_el = root_el.find("testsuite")
    assert testsuite_el.attrib["failures"] == "0"
    assert len(list(testsuite_el.iter("failure"))) == 0


def test_two_failures(datadir: Path) -> None:
    retest_results_passed = {
        "test_xml_one_failed_two_passed": TestReport(
            nodeid="test/test_pytest_merge_xml.py::test_xml_one_failed_two_passed",
            outcome="passed",
            location=("test/test_pytest_merge_xml.py", 9, "test_xml_one_failed_two_passed"),
            keywords={},
            longrepr=None,
            when="call",
        ),
        "test_xml_two_failed_one_passed": TestReport(
            nodeid="test/test_pytest_merge_xml.py::test_xml_two_failed_one_passed",
            outcome="passed",
            location=("test/test_pytest_merge_xml.py", 49, "test_xml_two_failed_one_passed"),
            keywords="",
            longrepr=None,
            when="call",
        ),
        "test_xml_three_failed_zero_passed": TestReport(
            nodeid="test/test_pytest_merge_xml.py::test_xml_three_failed_zero_passed",
            outcome="failed",
            location=("test/test_pytest_merge_xml.py", 88, "test_xml_three_failed_zero_passed"),
            keywords="",
            longrepr=None,
            when="call",
        ),
    }
    modified_file = datadir / "failure_tmp.xml"
    modify_xml(Path(datadir / "two_failures.xml"), retest_results_passed, modified_file)

    root_el = ET.parse(modified_file).getroot()
    testsuite_el = root_el.find("testsuite")
    assert testsuite_el.attrib["failures"] == "1"

    testcases = testsuite_el.findall("testcase")
    assert testcases[1].find("failure") is None
    assert testcases[2].find("failure") is not None


def test_one_failure_one_error(datadir: Path) -> None:
    """Tests modify_xml() with that change a XML with one failure and one error"""
    retest_results_passed = {
        "test_xml_one_failed_two_passed": TestReport(
            nodeid="test/test_pytest_merge_xml.py::test_xml_one_failed_two_passed",
            outcome="passed",
            location=("test/test_pytest_merge_xml.py", 9, "test_xml_one_failed_two_passed"),
            keywords={},
            longrepr=None,
            when="call",
        ),
        "test_xml_three_failed_zero_passed": TestReport(
            nodeid="test/test_pytest_merge_xml.py::test_xml_three_failed_zero_passed",
            outcome="passed",
            location=("test/test_pytest_merge_xml.py", 88, "test_xml_three_failed_zero_passed"),
            keywords="",
            longrepr=None,
            when="call",
        ),
    }
    modified_file = datadir / "failure.retest.xml"
    modify_xml(
        Path(datadir / "one_failure_one_error.xml"),
        retest_results_passed,
        modified_file,
    )

    root_el = ET.parse(modified_file).getroot()
    testsuite_el = root_el.find("testsuite")
    assert testsuite_el.attrib["failures"] == "0"
    assert testsuite_el.attrib["errors"] == "0"
    assert len(list(testsuite_el.iter("failure"))) == 0
    assert len(list(testsuite_el.iter("error"))) == 0


def test_succeed_to_failure_on_retest_not_supported(datadir: Path) -> None:
    """
    For now, pytest-update-test-results is supposed to always run with `--last-failed` flag.

    It convert failed outcomes into passed, but DOES NOT convert passed test cases into
    failed ones (that could happen if `--update-xml` runs without `--last-failed`).
    """
    retest_results_mix = {
        "test_xml_one_failed_two_passed": TestReport(
            nodeid="test/test_pytest_merge_xml.py::test_xml_one_failed_two_passed",
            outcome="failed",
            location=("test/test_pytest_merge_xml.py", 9, "test_xml_one_failed_two_passed"),
            keywords={},
            longrepr=None,
            when="call",
        ),
        "test_xml_two_failed_one_passed": TestReport(
            nodeid="test/test_pytest_merge_xml.py::test_xml_two_failed_one_passed",
            outcome="failed",
            location=("test/test_pytest_merge_xml.py", 49, "test_xml_two_failed_one_passed"),
            keywords="",
            longrepr=None,
            when="call",
        ),
        "test_xml_three_failed_zero_passed": TestReport(
            nodeid="test/test_pytest_merge_xml.py::test_xml_three_failed_zero_passed",
            outcome="failed",
            location=("test/test_pytest_merge_xml.py", 88, "test_xml_three_failed_zero_passed"),
            keywords="",
            longrepr=None,
            when="call",
        ),
    }
    modified_file = datadir / "all_failed.retest.xml"
    modify_xml(Path(datadir / "no_failures.xml"), retest_results_mix, modified_file)

    root_el = ET.parse(modified_file).getroot()
    testsuite_el = root_el.find("testsuite")

    assert testsuite_el.attrib["failures"] == "0"
