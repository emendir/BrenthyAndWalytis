# conftest.py
import sys
from _pytest.terminal import TerminalReporter
from termcolor import colored

class MinimalReporter(TerminalReporter):
    def __init__(self, config):
        super().__init__(config)
        self._tw.hasmarkup = True  # enables colored output safely

    def _write_output(self, *args, **kwargs):
        pass  # override all default output methods

    def _write_summary(self):
        pass

    def pytest_sessionstart(self, session):
        # print("pytest_sessionstart")
        pass  # suppress "collected x items"

    def pytest_runtest_logstart(self, nodeid, location):
        # print("pytest_runtest_logstart")
        pass  # suppress test start lines

    def pytest_runtest_logreport(self, report):
        if report.when != "call":
            return

        test_name = report.nodeid.split("::")[-1]
        if report.passed:
            symbol = colored("✓", "green")
        elif report.failed:
            symbol = colored("✗", "red")
        elif report.skipped:
            symbol = colored("-", "yellow")
        print(f"{symbol} {test_name}")

    def summary_stats(self):
        pass  # suppress result counts

    def pytest_terminal_summary(self, terminalreporter, exitstatus, config):
        pass  # suppress final summary output


def pytest_configure(config):
    # if tests are not being run by pytest
    if "pytest" not in sys.argv[0]:
        pluginmanager = config.pluginmanager
        pluginmanager.register(MinimalReporter(config), "minimal-reporter")
