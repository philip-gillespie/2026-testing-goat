import time

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

CHROMEDRIVER = "/usr/bin/chromedriver"
MAX_WAIT = 5


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        print("Setting up webdriver...")
        service = Service(CHROMEDRIVER)
        self.browser = webdriver.Chrome(service=service)
        print("Setup complete")

    def tearDown(self):
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text) -> None:
        start_time = time.time()
        while True:
            table = self.browser.find_element(By.ID, "id_list_table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            try:
                self.assertIn(
                    row_text,
                    [row.text for row in rows],
                    f"New to-do item did not appear in table. Contents were: \n{table.text} \n Required: \n{row_text}",
                )
                return None
            except AssertionError as e:
                if time.time() - start_time > MAX_WAIT:
                    raise (e)
                time.sleep(0.1)

    def test_can_start_a_todo_list(self):
        # Edith has heard about a cool new online to-do app
        # She goes to check out its homepage
        self.browser.get(self.live_server_url)

        # She notices the page title and header mention to-do lists
        self.assertIn("To-Do", self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn("To-Do", header_text)

        # She is invited to enter a to-do item straight away
        input_box = self.browser.find_element(By.ID, "id_new_item")
        self.assertEqual(input_box.get_attribute("placeholder"), "Enter a to-do item")

        # She types "Buy peacock feathers" into a text box
        # (Edith's hobby is tying fly-fishing lures)
        input_box.send_keys("Buy peacock feathers")

        # When she hits enter, the page updates, and now the page lists
        # "1. Buy peacock feathers" as an item in a to-do list
        input_box.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Buy peacock feathers")

        # There is a text box inviting her to add another item
        # She enters "Use peacock feathers to make fly" (Edith is very methodical)
        input_box = self.browser.find_element(By.ID, "id_new_item")
        input_box.send_keys("Use peacock feathers to make fly")
        input_box.send_keys(Keys.ENTER)
        time.sleep(1)

        # The page updates again, and now shows both items in her list
        self.wait_for_row_in_list_table("1: Buy peacock feathers")
        self.wait_for_row_in_list_table("2: Use peacock feathers to make fly")

        # Satisfied, she goes back to sleep
        return None

    def test_multiple_users_can_start_lists_at_different_urls(self):
        # Edith starts a new list
        self.browser.get(self.live_server_url)
        input_box = self.browser.find_element(By.ID, "id_new_item")
        input_box.send_keys("Buy peacock feathers")
        input_box.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Buy peacock feathers")

        # She notices that her list has a unique URL
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, "/lists/.+")

        # Now a new user, Francis, comes along to the site.
        ## Delete all cookies to simulate a brand new user session
        self.browser.delete_all_cookies()

        # Francis visits the home page. There is no sign of Edith's list
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("Buy peacock feathers", page_text)

        # Francis starts a new list by entering a new item.
        # He is less interesting than edith.
        input_box = self.browser.find_element(By.ID, "id_new_item")
        input_box.send_keys("Buy milk")
        input_box.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: " + "Buy milk")

        # Francis gets his own unique URL
        francis_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, "/lists/.+")
        self.assertNotEqual(francis_list_url, edith_list_url)

        # Again there is no trace of Edith's list
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("Buy peacock feathers", page_text)
        self.assertIn("Buy milk", page_text)

        # Satisfied they both go back to sleep
        return None
