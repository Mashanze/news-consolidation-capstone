"""Forms for article publishing, newsletters, and user registration.

Provides journalist-specific field filtering and secure account
registration with administrator-controlled editorial roles.
"""

from django import forms

from .models import Article, Newsletter, Publisher


class ArticleForm(forms.ModelForm):
    """
    Form used by journalists to create and edit articles.

    The author and approval status are deliberately excluded.
    The logged-in journalist becomes the author automatically,
    and only an editor can approve an article.
    """

    class Meta:
        model = Article

        fields = [
            "title",
            "content",
            "publisher",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter article title",
                }
            ),

            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Write your article...",
                    "rows": 12,
                }
            ),

            "publisher": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

        labels = {
            "title": "Article Title",
            "content": "Article Content",
            "publisher": "Publisher",
        }

    def __init__(self, *args, journalist=None, **kwargs):
        """Initialize article fields and filter affiliated publishers.

        Args:
            journalist: Optional user whose publisher affiliations
                determine the available publisher choices.
        """
        super().__init__(*args, **kwargs)

        self.fields["publisher"].required = False

        self.fields["publisher"].empty_label = (
            "Independent article — no publisher"
        )

        # If a journalist is supplied, only show publishers
        # with which that journalist is affiliated.
        if journalist is not None:
            self.fields["publisher"].queryset = (
                Publisher.objects.filter(
                    journalists=journalist
                ).order_by("name")
            )


class NewsletterForm(forms.ModelForm):
    """
    Form used by journalists to create and edit newsletters.

    Journalists can select their own approved articles
    to include in the newsletter.
    """

    class Meta:
        model = Newsletter

        fields = [
            "title",
            "description",
            "articles",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter newsletter title",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Write a short newsletter description..."
                    ),
                    "rows": 5,
                }
            ),

            "articles": forms.CheckboxSelectMultiple(),
        }

        labels = {
            "title": "Newsletter Title",
            "description": "Description",
            "articles": "Include Articles",
        }

    def __init__(self, *args, journalist=None, **kwargs):
        """Restrict newsletter article choices to approved author articles.

        Args:
            journalist: Optional journalist whose approved articles
                are available for newsletter selection.
        """
        super().__init__(*args, **kwargs)

        if journalist is not None:
            self.fields["articles"].queryset = (
                Article.objects.filter(
                    author=journalist,
                    approved=True,
                )
                .order_by("-created_at")
            )
        else:
            self.fields["articles"].queryset = (
                Article.objects.none()
            )

from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegistrationForm(UserCreationForm):
    """Register a new user with a requested account role."""

    email = forms.EmailField(required=True)

    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        label="Requested role",
        help_text=(
            "Journalist and Editor access requires administrator approval."
        ),
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "role",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        """Create a reader account while recording the requested role.

        Editorial privileges are never granted during registration.

        Args:
            commit: Whether to save the user to the database.

        Returns:
            CustomUser: The newly created user instance.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        # Never grant editorial privileges through public registration.
        user.requested_role = self.cleaned_data["role"]
        user.role = CustomUser.ROLE_READER

        if commit:
            user.save()

        return user
