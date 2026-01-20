import re

from django.http import HttpRequest
from django.test import TestCase

from lists.views import home_page


def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# Create your tests here.
class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_renders_homepage_content(self):
        response = self.client.get("/")
        self.assertContains(response, "To-Do")

    def test_renders_input_form(self):
        response = self.client.get("/")
        content = normalize_whitespace(response.content.decode())
        self.assertIn('<form method="POST">', content)
        self.assertIn('<input name="item_text"', content)

    def test_can_save_a_POST_request(self):
        response = self.client.post("/", data={"item_text": "A new list item"})
        self.assertContains(response, "A new list item")
        self.assertTemplateUsed(response, "home.html")
