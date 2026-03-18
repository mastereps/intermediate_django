from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Post


class CreateNewPostTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="secret123",
        )
        self.client.force_login(self.user)

    def test_non_ajax_post_redirects_after_creating_post(self):
        response = self.client.post(
            reverse("feed:new_post"),
            {"text": "Created from the full page form"},
        )

        self.assertRedirects(response, "/")
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().author, self.user)

    def test_ajax_post_returns_html_partial(self):
        response = self.client.post(
            reverse("feed:new_post"),
            {"text": "Created from the modal"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Created from the modal")
        self.assertEqual(Post.objects.count(), 1)
