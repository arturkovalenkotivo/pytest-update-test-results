# pytest-update-test-results

Deal with flaky tests by re-running failed tests and overwrite test results
on a test report from a previous run.

The primary purpose of this plugin is to avoid flaky tests to break a CI
build by executing them again after a failed run. The plugin does not rerun
tests by itself, but allow the user to leverage the pytest `--last-failed`
option to execute failed tests in a separate run and provides `--update-xml`
option so if previously failed tests passes, the XML test report will be
updated (and as result, your CI would flag the test as successfull).

In summary, your CI script would have something like:

```bash
#/bin/bash
pytest tests/my-test-suite --junix-xml pytest.xml

if [ $? -eq 2 ]  # pytest exit code for test failure
then
    # re-run failed test and update previous run report.
    pytest tests/my-test-suite --last-failed --update-xml pytest.xml
fi
```

## Rationale

In our particular case, most of the flakiness comes from using a shared
storage on our virtualized on-premise CI cluster, which made for random
file access times to varies in order of 10x-100x depending on
the cluster loading. This does not influence small unit tests, but greatly
affects execution time of integration and end-to-end tests, resulting
in flaky tests due timeout or race condition.

Our first attempt to solve the problem was to mark individual tests as flaky
(using [flaky]). But that felt like beating a dead horse, since new flaky
tests were constantly popping up.

Then, we tried [pytest-rerunfailures] (which automatically
re-run all test failures), but that didn't work either, due the way
[it deals with session fixtures][1].

So we opted to develop this plugin to re-run only the failed tests from
the previous run in a new pytest execution (using pytest built-in option `--last-failed`) and update the XML report. Besides working just fine with
session fixtures, re-running failed tests in a separate process has other
advantages:

1. By starting a new process for the test run, we make sure no "test
contamination" occurs (memory leaks vanish, objects that live during the
entire test session are reset).
1. Because we heavily parallelize the test suite (using **pytest-xdist**),
some flaky tests can occur due high CPU/IO usage. In the re-run
we can reduce number of parallel processes to make more resources
available for each test.

## At ESSS

To enable this for our internal projects:

1. Add `test_py_retest: True` to your project's `spec` file.
2. Add `pytest-update-test-results` dependency. 

[flaky]: https://github.com/box/flaky
[pytest-rerunfailures]: https://github.com/pytest-dev/pytest-rerunfailures
[1]: https://github.com/pytest-dev/pytest-rerunfailures/issues/51
