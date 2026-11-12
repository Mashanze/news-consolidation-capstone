from unittest.mock import patch

from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Article,
    CustomUser,
    Newsletter,
    Publisher,
)


class NewsAppAPITests(APITestCase):
    """
    Automated API tests for the News Application.
    """

    def setUp(self):
        # ---------------------------------------------------------------------
        # Users
        # ---------------------------------------------------------------------

        self.reader = CustomUser.objects.create_user(
            username="reader1",
            password="password123",
            email="reader@test.com",
            role=CustomUser.ROLE_READER,
        )

        self.journalist = CustomUser.objects.create_user(
            username="journalist1",
            password="password123",
            email="journalist@test.com",
            role=CustomUser.ROLE_JOURNALIST,
        )

        self.editor = CustomUser.objects.create_user(
            username="editor1",
            password="password123",
            email="editor@test.com",
            role=CustomUser.ROLE_EDITOR,
        )

        # ---------------------------------------------------------------------
        # Publisher
        # ---------------------------------------------------------------------

        self.publisher = Publisher.objects.create(
            name="Tech Times",
            description="Technology news",
        )

        self.publisher.journalists.add(
            self.journalist
        )

        self.publisher.editors.add(
            self.editor
        )

        # ---------------------------------------------------------------------
        # Articles
        # ---------------------------------------------------------------------

        self.approved_article = Article.objects.create(
            title="Approved Tech Article",
            content="Approved article content.",
            author=self.journalist,
            approved=True,
            publisher=self.publisher,
        )

        self.unapproved_article = Article.objects.create(
            title="Pending Article",
            content="Pending article content.",
            author=self.journalist,
            approved=False,
            publisher=self.publisher,
        )

        # ---------------------------------------------------------------------
        # Newsletter
        # ---------------------------------------------------------------------

        self.newsletter = Newsletter.objects.create(
            title="Weekly Technology",
            description="Weekly technology stories.",
            author=self.journalist,
        )

        self.newsletter.articles.add(
            self.approved_article
        )


    # =========================================================================
    # Article GET tests
    # =========================================================================

    def test_public_can_view_approved_articles(self):
        """
        Approved articles should be returned by the public
        article endpoint.
        """

        url = reverse("article-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        titles = [
            article["title"]
            for article in response.data
        ]

        self.assertIn(
            "Approved Tech Article",
            titles,
        )

        self.assertNotIn(
            "Pending Article",
            titles,
        )


    def test_editor_can_view_pending_articles(self):
        """
        Editors should be able to review unapproved articles.
        """

        self.client.force_authenticate(
            user=self.editor
        )

        url = reverse("article-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        titles = [
            article["title"]
            for article in response.data
        ]

        self.assertIn(
            "Pending Article",
            titles,
        )


    # =========================================================================
    # Journalist tests
    # =========================================================================

    def test_journalist_can_create_article(self):
        """
        Journalists should be able to create articles.
        """

        self.client.force_authenticate(
            user=self.journalist
        )

        url = reverse("article-list")

        data = {
            "title": "New Breaking News",
            "content": "Breaking news content.",
            "publisher": self.publisher.pk,
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        article = Article.objects.get(
            title="New Breaking News"
        )

        self.assertEqual(
            article.author,
            self.journalist,
        )

        self.assertFalse(
            article.approved
        )


    def test_reader_cannot_create_article(self):
        """
        Readers must not be able to create articles.
        """

        self.client.force_authenticate(
            user=self.reader
        )

        url = reverse("article-list")

        data = {
            "title": "Unauthorized Article",
            "content": "This should not be created.",
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            Article.objects.filter(
                title="Unauthorized Article"
            ).exists()
        )


    # =========================================================================
    # Subscription tests
    # =========================================================================

    def test_reader_can_get_subscribed_articles(self):
        """
        Readers should receive approved articles from
        publishers they subscribe to.
        """

        self.reader.subscriptions_publishers.add(
            self.publisher
        )

        self.client.force_authenticate(
            user=self.reader
        )

        url = reverse(
            "article-subscribed"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        titles = [
            article["title"]
            for article in response.data
        ]

        self.assertIn(
            "Approved Tech Article",
            titles,
        )

        self.assertNotIn(
            "Pending Article",
            titles,
        )


    def test_reader_can_subscribe_to_journalist(self):
        """
        Readers should receive approved articles from
        journalists they subscribe to.
        """

        self.reader.subscriptions_journalists.add(
            self.journalist
        )

        self.client.force_authenticate(
            user=self.reader
        )

        url = reverse(
            "article-subscribed"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        titles = [
            article["title"]
            for article in response.data
        ]

        self.assertIn(
            "Approved Tech Article",
            titles,
        )


    def test_journalist_cannot_use_reader_subscription_endpoint(
        self,
    ):
        """
        The subscription feed is intended for Readers.
        """

        self.client.force_authenticate(
            user=self.journalist
        )

        url = reverse(
            "article-subscribed"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


    # =========================================================================
    # Editor tests
    # =========================================================================

    @patch(
        "news_app.signals.requests.post"
    )
    def test_editor_can_approve_article(
        self,
        mock_post,
    ):
        """
        Editors should be able to approve pending articles.
        """

        mock_post.return_value.status_code = 201

        self.client.force_authenticate(
            user=self.editor
        )

        url = reverse(
            "article-approve",
            args=[self.unapproved_article.pk],
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.unapproved_article.refresh_from_db()

        self.assertTrue(
            self.unapproved_article.approved
        )


    def test_reader_cannot_approve_article(self):
        """
        Readers must not be able to approve articles.
        """

        self.client.force_authenticate(
            user=self.reader
        )

        url = reverse(
            "article-approve",
            args=[self.unapproved_article.pk],
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


    def test_editor_can_delete_article(self):
        """
        Editors should be able to delete articles.
        """

        self.client.force_authenticate(
            user=self.editor
        )

        url = reverse(
            "article-detail",
            args=[self.approved_article.pk],
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Article.objects.filter(
                pk=self.approved_article.pk
            ).exists()
        )


    # =========================================================================
    # Newsletter tests
    # =========================================================================

    def test_reader_can_view_newsletters(self):
        """
        Readers can view newsletters.
        """

        self.client.force_authenticate(
            user=self.reader
        )

        url = reverse(
            "newsletter-list"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )


    def test_journalist_can_create_newsletter(self):
        """
        Journalists can create newsletters.
        """

        self.client.force_authenticate(
            user=self.journalist
        )

        url = reverse(
            "newsletter-list"
        )

        data = {
            "title": "Daily Technology",
            "description": "Daily technology news.",
            "articles": [
                self.approved_article.pk
            ],
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Newsletter.objects.filter(
                title="Daily Technology"
            ).exists()
        )


    def test_reader_cannot_create_newsletter(self):
        """
        Readers must not create newsletters.
        """

        self.client.force_authenticate(
            user=self.reader
        )

        url = reverse(
            "newsletter-list"
        )

        data = {
            "title": "Reader Newsletter",
            "description": "Should not work.",
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


    # =========================================================================
    # Signal tests
    # =========================================================================

    @patch(
        "news_app.signals.requests.post"
    )
    def test_approval_signal_emails_subscriber(
        self,
        mock_post,
    ):
        """
        Approving an article should email subscribers
        and POST to the internal approval API.
        """

        mock_post.return_value.status_code = 201

        self.reader.subscriptions_publishers.add(
            self.publisher
        )

        article = Article.objects.create(
            title="Signal Test Article",
            content="Signal test content.",
            author=self.journalist,
            publisher=self.publisher,
            approved=False,
        )

        article.approved = True
        article.save(
            update_fields=["approved"]
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        self.assertIn(
            self.reader.email,
            mail.outbox[0].to,
        )

        mock_post.assert_called_once()


    @patch(
        "news_app.signals.requests.post"
    )
    def test_signal_does_not_repeat_on_later_save(
        self,
        mock_post,
    ):
        """
        Editing an already-approved article must not
        notify subscribers again.
        """

        mock_post.return_value.status_code = 201

        self.reader.subscriptions_publishers.add(
            self.publisher
        )

        article = Article.objects.create(
            title="One Notification",
            content="Original content.",
            author=self.journalist,
            publisher=self.publisher,
            approved=False,
        )

        article.approved = True
        article.save(
            update_fields=["approved"]
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        article.content = "Updated content."

        article.save(
            update_fields=["content"]
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        mock_post.assert_called_once()