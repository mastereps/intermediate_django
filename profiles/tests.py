import shutil
import tempfile

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from followers.models import Follower
from feed.models import Post


TEST_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!"
    b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00"
    b"\x00\x02\x02D\x01\x00;"
)


class ProfileDetailViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_media_root = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_media_root, ignore_errors=True)
        super().tearDownClass()

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

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_profile_detail_uses_fallback_avatar_when_image_missing(self):
        response = self.client.get(
            reverse("profiles:detail", kwargs={"username": self.author.username})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ">a<", html=False)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_profile_settings_allows_avatar_upload(self):
        self.client.force_login(self.viewer)
        upload = SimpleUploadedFile("avatar.gif", TEST_GIF, content_type="image/gif")

        response = self.client.post(
            reverse("profiles:settings"),
            {"image": upload},
            follow=True,
        )

        self.viewer.profile.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.viewer.profile.image.name.startswith("profiles/"))
        self.assertContains(response, "Profile updated.")
