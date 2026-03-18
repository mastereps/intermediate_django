from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from followers.models import Follower
from feed.models import Post


class ProfileDetailViewTests(TestCase):
    def setUp(self):
        self.viewer = User.objects.create_user(
            username="viewer",
            email="viewer@example.com",
            password="secret123",
        )
        self.author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="secret123",
        )
        Post.objects.create(text="Author post", author=self.author)
        Follower.objects.create(followed_by=self.viewer, following=self.author)

    def test_profile_detail_context_has_follow_counts(self):
        self.client.force_login(self.viewer)

        response = self.client.get(
            reverse("profiles:detail", kwargs={"username": self.author.username})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_posts"], 1)
        self.assertEqual(response.context["total_followers"], 1)
        self.assertTrue(response.context["you_follow"])
