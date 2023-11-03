from django.test import TestCase
from model_bakery import baker

from .models import Post


class PostModelTestCase(TestCase):
    def test_list_only_published_posts(self):
        post_published = baker.make(Post, status="published")
        baker.make(Post, status="draft", _quantity=2)
        posts = Post.published.all()
        self.assertEqual(posts.count(), 1)
        self.assertIn(post_published, posts)
