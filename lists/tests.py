import re

from django.test import TestCase

from lists.models import Item, List


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
        self.assertIn('<form method="POST" action="/lists/new/">', content)
        self.assertIn('<input name="item_text"', content)

    def test_can_save_a_POST_request(self):
        self.client.post("/lists/new/", data={"item_text": "A new list item"})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")

    def test_redirects_after_POST(self):
        response = self.client.post(
            "/lists/new/", data={"item_text": "A new list item"}
        )
        new_list = List.objects.get()
        self.assertRedirects(response, f"/lists/{new_list.id}/")

    def test_only_saves_items_when_necessary(self):
        self.client.get("/")
        self.assertEqual(Item.objects.count(), 0)


class NewListTest(TestCase):
    def test_can_save_a_POST_request(self):
        self.client.post("/lists/new/", data={"item_text": "A new list item"})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.get()
        self.assertEqual(new_item.text, "A new list item")

    def test_redirects_after_POST(self):
        response = self.client.post(
            "/lists/new/", data={"item_text": "A new list item"}
        )
        new_list = List.objects.get()
        self.assertRedirects(response, f"/lists/{new_list.id}/")


class ListViewTest(TestCase):
    def test_uses_list_template(self):
        my_list = List.objects.create()
        response = self.client.get(f"/lists/{my_list.id}/")
        self.assertTemplateUsed(response, "list.html")

    def test_renders_input_form(self):
        my_list = List.objects.create()
        response = self.client.get(f"/lists/{my_list.id}/")
        content = normalize_whitespace(response.content.decode())
        self.assertIn(
            f'<form method="POST" action="/lists/{my_list.id}/add_item/">', content
        )
        self.assertIn('<input name="item_text"', content)

    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text="itemey 1", list=correct_list)
        Item.objects.create(text="itemey 2", list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text="other list item", list=other_list)

        response = self.client.get(f"/lists/{correct_list.id}/")
        self.assertContains(response, "itemey 1")
        self.assertContains(response, "itemey 2")
        self.assertNotContains(response, "other list item")


class ListAndItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self) -> None:
        my_list = List()
        my_list.save()

        first_item = Item()
        first_item.text = "The first (ever) list item"
        first_item.list = my_list
        first_item.save()

        second_item = Item()
        second_item.text = "Item the second"
        second_item.list = my_list
        second_item.save()

        saved_list = List.objects.get()
        self.assertEqual(saved_list, my_list)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        self.assertEqual(first_saved_item.text, "The first (ever) list item")
        self.assertEqual(first_item.list, my_list)

        second_saved_item = saved_items[1]
        self.assertEqual(second_saved_item.text, "Item the second")
        self.assertEqual(second_item.list, my_list)


class NewItemTest(TestCase):
    def test_can_save_a_POST_request_to_an_existing_list(self):
        _ = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f"/lists/{correct_list.id}/add_item/",
            data={"item_text": "A new item for an existing list"},
        )
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.get()
        self.assertEqual(new_item.text, "A new item for an existing list")
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_to_list_view(self):
        _ = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.post(
            f"/lists/{correct_list.id}/add_item/",
            data={"item_text": "A new item for an existing list"},
        )
        self.assertRedirects(response, f"/lists/{correct_list.id}/")
