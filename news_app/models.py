from django.contrib.auth.models import AbstractUser
from django.db import models


class Publisher(models.Model):
    """
    Represents a curated news publication.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # Publishers can have multiple editors.
    editors = models.ManyToManyField(
        "CustomUser",
        blank=True,
        related_name="managed_publishers",
        limit_choices_to={"role": "editor"},
    )

    # Publishers can have multiple journalists.
    journalists = models.ManyToManyField(
        "CustomUser",
        blank=True,
        related_name="publisher_affiliations",
        limit_choices_to={"role": "journalist"},
    )

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """
    Custom user model with the three required roles:

    - Reader
    - Journalist
    - Editor
    """

    ROLE_READER = "reader"
    ROLE_JOURNALIST = "journalist"
    ROLE_EDITOR = "editor"

    ROLE_CHOICES = [
        (ROLE_READER, "Reader"),
        (ROLE_JOURNALIST, "Journalist"),
        (ROLE_EDITOR, "Editor"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_READER,
    )

    requested_role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_READER,
        help_text="Role requested during registration.",
    )

    # Reader subscriptions to publishers.
    subscriptions_publishers = models.ManyToManyField(
        Publisher,
        blank=True,
        related_name="subscribers",
    )

    # Reader subscriptions to individual journalists.
    subscriptions_journalists = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="journalist_subscribers",
        limit_choices_to={"role": "journalist"},
    )

    def __str__(self):
        return self.username

    @property
    def is_reader(self):
        return self.role == self.ROLE_READER

    @property
    def is_journalist(self):
        return self.role == self.ROLE_JOURNALIST

    @property
    def is_editor(self):
        return self.role == self.ROLE_EDITOR


class Article(models.Model):
    """
    Represents a news article.

    Articles are written by journalists and can optionally
    belong to a publisher.
    """

    title = models.CharField(
        max_length=255,
    )

    content = models.TextField()

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="authored_articles",
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    approved = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """
    A curated collection of articles.

    Newsletters can be created by journalists and editors.
    """

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="authored_newsletters",
    )

    articles = models.ManyToManyField(
        Article,
        related_name="newsletters",
        blank=True,
    )

    def __str__(self):
        return self.title