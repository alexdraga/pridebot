import string
import time
import random
from httplib import BadStatusLine

from selenium import webdriver
from selenium.common.exceptions import InvalidElementStateException, \
    NoSuchElementException, WebDriverException

from config.default_settings import SETTINGS
from config.localization import LOGS, LANGUAGE


class Quest(object):
    def __init__(self):
        self.driver = None
        self.is_url_opened = False
        self.is_login_performed = False
        if SETTINGS['login_url'][0]:
            print LOGS['opening_firefox'][LANGUAGE]
            self.open_firefox()
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
                self.wait_for_field([SETTINGS['login_locator'][0]])
                by_value_login = self.parse_locator_line(SETTINGS['login_locator'][0])
                login_field = self.find_element_by(by_value_login['by'], by_value_login['value'])
                login_field.send_keys(login)

                # Waiting for password field to appear and sending password to it
                self.wait_for_field([SETTINGS['password_locator'][0]])
                by_value_password = self.parse_locator_line(SETTINGS['password_locator'][0])
                password_field = self.find_element_by(by_value_password['by'], by_value_password['value'])
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
                    'tag': self.driver.find_element_by_tag_name,
            }
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
        try:
            if SETTINGS['code_alt_locator'][0]:
                found_code_locator = self.wait_for_field([SETTINGS['code_locator'][0],
                                                          SETTINGS['code_alt_locator'][0]])
            else:
                found_code_locator = SETTINGS['code_locator'][0]
                self.wait_for_field([SETTINGS['code_locator'][0]])
            time_to_sleep = float(SETTINGS['time_interval'][0]) + random.uniform(0,
                                                                                 float(SETTINGS['random_part'][0]))
            if time_to_sleep:
                print LOGS['waiting_before_next_code'][LANGUAGE] % str(time_to_sleep)
                time.sleep(time_to_sleep)
            by_value = self.parse_locator_line(found_code_locator)
            code_field = self.find_element_by(by_value['by'], by_value['value'])
            if code_field != 'STOP':
                code_field.clear()
                code_field.send_keys(code)
                try:
                    code_field.submit()
                except NoSuchElementException:
                    # For agiotage game
                    button = self.find_element_by('id', 'submit')
                    button.click()
                # If no errors appeared - returning True, else - we are going to terminate the program
                return True
            else:
                return False
        except (InvalidElementStateException, BadStatusLine):
            pass

    def wait_for_field(self, fields):
        """
        Performs checking is field present by interval of time
        """

        def is_code_field_present(field):
            by_value = self.parse_locator_line(field)
            element = self.find_element_by(by_value['by'], by_value['value'])
            if element and element != 'STOP':
                return True
            elif element == 'STOP':
                return 'STOP'
            else:
                return False

        if len(fields) > 1:
            while not (is_code_field_present(fields[0]) or is_code_field_present(fields[1])):
                if is_code_field_present(fields[0]) == 'STOP' or is_code_field_present(fields[1]) == 'STOP':
                    break
                print LOGS['can_not_find_code_field'][LANGUAGE]
                time.sleep(5)
            if is_code_field_present(fields[0]):
                return fields[0]
            else:
                return fields[1]
        else:
            while not is_code_field_present(fields[0]):
                if is_code_field_present(fields[0]) == 'STOP':
                    break
                print LOGS['can_not_find_code_field'][LANGUAGE]
                time.sleep(5)

    @staticmethod
    def parse_locator_line(line):
        by = line[0:string.find(line, '=')]
        value = line[string.find(line, '=') + 1:len(line)]
        return {'by': by, 'value': value}
