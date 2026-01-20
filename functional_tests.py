import time
import unittest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

CHROMEDRIVER = "/usr/bin/chromedriver"


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        print("Setting up webdriver...")
        service = Service(CHROMEDRIVER)
        self.browser = webdriver.Chrome(service=service)
        print("Setup complete")

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_todo_list(self):
        # Edith has heard about a cool new online to-do app
        # She goes to check out its homepage
        self.browser.get("http://localhost:8000")

        # She notices the page title and header mention to-do lists
        self.assertIn("To-Do", self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn("To-Do", header_text)

        # She is invited to enter a to-do item straight away
        time.sleep(1)
        input_box = self.browser.find_element(By.ID, "id_new_item")
        self.assertEqual(input_box.get_attribute("placeholder"), "Enter a to-do item")

        # She types "Buy peacock feathers" into a text box
        # (Edith's hobby is tying fly-fishing lures)
        input_box.send_keys("Buy peacock feathers")

        # When she hits enter, the page updates, and now the page lists
        # "1. Buy peacock feathers" as an item in a to-do list
        input_box.send_keys(Keys.ENTER)
        time.sleep(1)

        table = self.browser.find_element(By.ID, "id_list_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        first_item = "1: Buy peacock feathers"
        self.assertTrue(
            any(row.text == first_item for row in rows),
            f"New to-do item did not appear in table. Contents were: \n{table.text} \n Required: \n{first_item}",
        )

        # There is a text box inviting her to add another item
        # She enters "Use peacock feathers to make fly" (Edith is very methodical)
        input_box = self.browser.find_element(By.ID, "id_new_item")
        input_box.send_keys("Use peacock feathers to make fly")
        input_box.send_keys(Keys.ENTER)
        time.sleep(1)

        # The page updates again, and now shows both items on her list
        table = self.browser.find_element(By.ID, "id_list_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        first_item = "1: Buy peacock feathers"
        self.assertTrue(
            any(row.text == first_item for row in rows),
            f"New to-do item did not appear in table. Contents were: \n{table.text} \n Required: \n{first_item}",
        )
        second_item = "2: Use peacock feathers to make fly"
        self.assertTrue(
            any(row.text == second_item for row in rows),
            f"New to-do item did not appear in table. Contents were: \n{table.text} \n Required: \n{first_item}",
        )

        self.fail("Finish the test")
        # Satisfied, she goes back to sleep


if __name__ == "__main__":
    unittest.main()
