
from WebsiteReporter import WebsiteReporter
import time


if __name__ == '__main__':
    if not WebsiteReporter.readState('tempLog.txt', time.strftime("%m-%d", time.localtime())):
        reporter = WebsiteReporter()
        reporter.login_twsb()
        reporter.reportTemperature()
    