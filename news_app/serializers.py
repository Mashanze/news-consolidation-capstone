from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Article, Newsletter, Publisher


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom user model.
    """

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "role",
        ]

        read_only_fields = [
            "id",
            "role",
        ]


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for publishers.
    """

    class Meta:
        model = Publisher

        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "editors",
            "journalists",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for articles.
    """

    author_detail = UserSerializer(
        source="author",
        read_only=True,
    )

    publisher_detail = PublisherSerializer(
        source="publisher",
        read_only=True,
    )

    class Meta:
        model = Article

        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_detail",
            "publisher",
            "publisher_detail",
            "created_at",
            "approved",
        ]

        read_only_fields = [
            "id",
            "author",
            "author_detail",
            "created_at",
            "approved",
            "publisher_detail",
        ]


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for newsletters.
    """

    author_detail = UserSerializer(
        source="author",
        read_only=True,
    )

    class Meta:
        model = Newsletter

        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "author",
            "author_detail",
            "articles",
        ]

        read_only_fields = [
            "id",
            "author",
            "author_detail",
            "created_at",
        ]