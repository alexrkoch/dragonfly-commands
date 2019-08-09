#!/usr/bin/env python
# (c) Copyright 2015 by James Stout
# Licensed under the LGPL, see <http://www.gnu.org/licenses/>

"""Actions for manipulating Chrome via WebDriver."""

import json
from six.moves import urllib_request
from six.moves import urllib_error

from dragonfly import (DynStrActionBase)
import _dragonfly_local as local

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

def create_driver():
    global driver
    driver = None
    try:
        urllib_request.urlopen("http://127.0.0.1:9222/json")
    except urllib_error.URLError:
        print("Unable to start WebDriver, Chrome is not responding.")
        return
    chrome_options = Options()
    chrome_options.experimental_options["debuggerAddress"] = "127.0.0.1:9222"
    driver = webdriver.Chrome(local.CHROME_DRIVER_PATH, chrome_options=chrome_options)


def quit_driver():
    global driver
    if driver:
        driver.quit()
    driver = None


def switch_to_active_tab():
    tabs = json.load(urllib_request.urlopen("http://127.0.0.1:9222/json"))
    # Chrome seems to order the tabs by when they were last updated, so we find
    # the first one that is not an extension.
    for tab in tabs:
        if not tab["url"].startswith("chrome-extension://"):
            active_tab = tab["id"]
            break
    for window in driver.window_handles:
        # ChromeDriver adds to the raw ID, so we just look for substring match.
        if active_tab in window:
            driver.switch_to_window(window);
            print("Switched to: " + driver.title.encode('ascii', 'backslashreplace'))
            return


def test_driver():
    switch_to_active_tab()
    driver.get('http://www.google.com/xhtml');


class ElementAction(DynStrActionBase):

    def __init__(self, by, spec):
        DynStrActionBase.__init__(self, spec)
        self.by = by

    def _parse_spec(self, spec):
        return spec

    def _execute_events(self, events):
        switch_to_active_tab()
        element = driver.find_element(self.by, events)
        self._execute_on_element(element)


class ClickElementAction(ElementAction):

    def _execute_on_element(self, element):
        element.click()


class DoubleClickElementAction(ElementAction):

    def _execute_on_element(self, element):
        ActionChains(driver).double_click(element).perform()


class ClickElementOffsetAction(ElementAction):

    def __init__(self, by, spec, xoffset, yoffset):
        super(ClickElementOffsetAction, self).__init__(by, spec)
        self.xoffset = xoffset
        self.yoffset = yoffset

    def _execute_on_element(self, element):
        ActionChains(driver).move_to_element_with_offset(element, self.xoffset, self.yoffset).click().perform()
