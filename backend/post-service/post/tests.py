from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from mongoengine import connect, disconnect, Document, StringField
from .models import Post, Like, Comment, Hashtag
from .views import get_document_or_404


class User(Document):
    username = StringField(required=True, max_length=150)
    password = StringField(required=True)


class MockRequestUser:
    def __init__(self, username):
        self.username = username


class PostServiceTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Disconnect any existing connection
        disconnect(alias='default')
        # Connect to the test database
        connect('test_thread_hive_db', host='mongodb://localhost/test_thread_hive_db')

    @classmethod
    def tearDownClass(cls):
        # Disconnect from the test database
        disconnect()
        super().tearDownClass()

    def setUp(self):
        # Set up the API client
        self.client = APIClient()

        # Create and authenticate a test user
        self.test_user = User(username="testuser", password="password123").save()
        self.client.force_authenticate(user=MockRequestUser(username="testuser"))

        # Create test posts
        self.test_post = Post.objects.create(
            username=self.test_user.username,
            content="This is a test post.",
            # hashtags=["#test", "#threadhive"]
        )

        self.another_post = Post.objects.create(
            username="anotheruser",
            content="Another test post.",
            # hashtags=["#example"]
        )

        # Create test hashtags
        self.test_hashtag = Hashtag.objects.create(
            tag="test",
            count=1,
            posts=[self.test_post]
        )

    def tearDown(self):
        # Clean up the database after each test
        Post.drop_collection()
        Like.drop_collection()
        Comment.drop_collection()
        Hashtag.drop_collection()
        User.drop_collection()

    def test_create_post(self):
        """
        Test creating a new post.
        """
        post_data = {
            "content": "A new post from testuser",
            "hashtags": ["#newpost", "#testing"]
        }
        response = self.client.post(
            "/api/posts/",
            data=post_data,
            format="json",
            # HTTP_AUTHORIZATION=f"Bearer testtoken"  # Replace with a valid token if using JWT
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], post_data["content"])

    def test_get_posts(self):
        """
        Test retrieving all posts.
        """
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_single_post(self):
        """
        Test retrieving a single post by its ID.
        """
        response = self.client.get(f"/api/posts/{self.test_post.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], self.test_post.content)

    def test_like_post(self):
        """
        Test liking a post.
        """
        response = self.client.post(
            f"/api/posts/{self.test_post.id}/likes/",
            # HTTP_AUTHORIZATION=f"Bearer testtoken"  # Replace with a valid token if using JWT
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.count(), 1)

    def test_unlike_post(self):
        """
        Test unliking a post.
        """
        # Like the post first
        Like.objects.create(post=self.test_post.id, username=self.test_user["username"])

        response = self.client.delete(
            f"/api/posts/{self.test_post.id}/likes/",
            # HTTP_AUTHORIZATION=f"Bearer testtoken"  # Replace with a valid token if using JWT
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.count(), 0)

    def test_add_comment_to_post(self):
        """
        Test adding a comment to a post.
        """
        comment_data = {"content": "This is a comment."}
        response = self.client.post(
            f"/api/posts/{self.test_post.id}/comments/",
            data=comment_data,
            format="json",
            # HTTP_AUTHORIZATION=f"Bearer testtoken"  # Replace with a valid token if using JWT
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(response.data["content"], comment_data["content"])

    def test_get_comments_for_post(self):
        """
        Test retrieving comments for a specific post.
        """
        Comment.objects.create(post=self.test_post.id, username=self.test_user["username"], content="A test comment.")
        response = self.client.get(f"/api/posts/{self.test_post.id}/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_trending_hashtags(self):
        """
        Test retrieving trending hashtags.
        """
        response = self.client.get("/api/hashtags/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_posts_by_hashtag(self):
        """
        Test retrieving posts associated with a specific hashtag.
        """
        response = self.client.get(f"/api/hashtags/test/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["posts"]), 1)
