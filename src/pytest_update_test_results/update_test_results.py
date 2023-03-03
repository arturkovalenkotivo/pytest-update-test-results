import shutil
import xml.etree.ElementTree as Et
from pathlib import Path
from typing import Dict

from _pytest.reports import TestReport


def modify_xml(original_xml: Path, retest_results: Dict[str, TestReport], new_xml: Path) -> None:
    """
    Modifies an XML file containing test results by removing failed test cases that were subsequently
    passed in a retest.

    :param original_xml: Path to the original XML file containing test results.
    :param retest_results: A dictionary mapping test cases to their retest results.
    :param new_xml: The path to the new modified XML file that will be created.
    :return: None. The modified XML file is written to the specified `new_xml` path.
    """

    tree = Et.parse(original_xml)
    root = tree.getroot()
    testsuite = root.find("testsuite")
    original_failure_count = retest_failure_count = int(testsuite.attrib["failures"])
    original_error_count = retest_error_count = int(testsuite.attrib["errors"])

    succeed_in_retest = {
        result.location[2] for result in retest_results.values() if result.outcome == "passed"
    }

    for testcase in testsuite:
        testcase_name = testcase.attrib["name"]
        if testcase_name in succeed_in_retest:
            failure = testcase.find("failure")
            if failure is not None:
                retest_failure_count -= 1
                testcase.remove(failure)
                continue
            error = testcase.find("error")
            if error is not None:
                retest_error_count -= 1
                testcase.remove(error)

    # Only writes a new XML if some test outcome has changed
    if retest_failure_count < original_failure_count or retest_error_count < original_error_count:
        testsuite.attrib["failures"] = str(retest_failure_count)
        testsuite.attrib["errors"] = str(retest_error_count)
        tree.write(new_xml, encoding="utf-8", xml_declaration=True)
    elif original_xml != new_xml:
        shutil.copy(original_xml, new_xml)
