import string
import time
import random
from httplib import BadStatusLine

from selenium import webdriver
from selenium.common.exceptions import InvalidElementStateException, \
    NoSuchElementException, WebDriverException, NoSuchWindowException
from selenium.webdriver.remote.webelement import WebElement

from config.default_settings import SETTINGS
from config.localization import LOGS, LANGUAGE


class Quest(object):
    # TODO: this class needs full refactor
    def __init__(self):
        self.driver = None
        self.is_url_opened = False
        self.is_login_performed = False
        if SETTINGS['login_url'][0]:
            self.open_firefox()
            print LOGS['opening_login_page'][LANGUAGE]
            if self.open_url(SETTINGS['login_url'][0]):
                # If url was opened - we can try to perform login
                self.is_url_opened = True
                # If login was successful - we can send signals that we are ready to enter codes
                if self.login():
                    self.is_login_performed = True
                    if SETTINGS['game_url'][0]:
                        print LOGS['opening_game_page'][LANGUAGE]
                        self.open_url(SETTINGS['game_url'][0])

    def login(self):
        login = SETTINGS['login'][0].decode('utf-8')
        if login:
            print LOGS['trying_to_login'][LANGUAGE]
            try:
                # Waiting for login field to appear and sending login to it
                login_field = self.wait_for_field([SETTINGS['login_locator'][0]])
                login_field.send_keys(login)

                # Waiting for password field to appear and sending password to it
                password_field = self.wait_for_field([SETTINGS['password_locator'][0]])
                password = SETTINGS['password'][0].decode('utf-8')
                password_field.send_keys(password)
                # Submitting input
                try:
                    password_field.submit()
                except NoSuchElementException:
                    # For agiotage game
                    button = self.find_element_by('id', 'submit')
                    button.click()
                # If no errors appeared - returning True, else - we are going to terminate the program
                return True
            except (BadStatusLine, WebDriverException):
                return False
        else:
            return True

    def find_element_by(self, by, element):
        try:
            func = {'id': self.driver.find_element_by_id,
                    'name': self.driver.find_element_by_name,
                    'css': self.driver.find_element_by_css_selector,
                    'class': self.driver.find_element_by_class_name,
                    'xpath': self.driver.find_element_by_xpath,
                    'tag': self.driver.find_element_by_tag_name}
            return func[by](element)
        except NoSuchElementException:
            return False
        except:
            return 'STOP'

    def open_firefox(self):
        print LOGS['opening_firefox'][LANGUAGE]
        # Creating webdriver for Firefox
        self.driver = webdriver.Firefox()

    def open_url(self, url):
        try:
            # Opening game url
            self.driver.get(url)
            # If no errors appeared - returning True, else - we are going to terminate the program
            return True
        except (BadStatusLine, WebDriverException):
            return False

    def check_code(self, code):
        """
        Performs entering code to the code field
        """

        code_field = self.wait_for_field([SETTINGS['code_locator'][0],
                                          SETTINGS['code_alt_locator'][0]])
        if isinstance(code_field, WebElement):
            time_to_sleep = float(SETTINGS['time_interval'][0]) + \
                            random.uniform(0, float(SETTINGS['random_part'][0]))
            if time_to_sleep:
                print LOGS['waiting_before_next_code'][LANGUAGE] % str(time_to_sleep)
                time.sleep(time_to_sleep)
            code_field.clear()
            code_field.send_keys(code)
            try:
                code_field.submit()
            except NoSuchElementException:
                # TODO: I think, after refactor this won't work anymore
                # For agiotage game
                button = self.find_element_by('id', 'submit')
                button.click()
            except (BadStatusLine, NoSuchWindowException):
                return 'STOP'
            # If no errors appeared - returning True, else - we are going to terminate the program
            return True
        else:
            return 'STOP'

    def wait_for_field(self, fields):
        """
        Performs checking is field present by interval of time
        :param fields: list of locators of object which we are looking for
        :rtype: WebElement
        :return: locator found or status
        """
        field_is_present = False
        while not field_is_present:
            for field in fields:
                by_value = self.parse_locator_line(field)
                found = self.find_element_by(by_value['by'], by_value['value'])
                if found:
                    field_is_present = found
                    break
                else:
                    print LOGS['can_not_find_code_field'][LANGUAGE]
                    time.sleep(5)
        return field_is_present

    @staticmethod
    def parse_locator_line(line):
        return {'by': line.split('=')[0], 'value': line.split('=')[1]}
