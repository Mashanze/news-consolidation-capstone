import logging

from .forms import ArticleForm, NewsletterForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article, CustomUser, Newsletter, Publisher
from .serializers import (
    ArticleSerializer,
    NewsletterSerializer,
    PublisherSerializer,
)


logger = logging.getLogger(__name__)


# =============================================================================
# WEBSITE VIEWS
# =============================================================================


def home(request):
    """
    Public homepage.

    Only approved articles are displayed.
    """

    articles = (
        Article.objects
        .filter(approved=True)
        .select_related("author", "publisher")
        .order_by("-created_at")
    )

    newsletters = (
        Newsletter.objects
        .select_related("author")
        .prefetch_related("articles")
        .order_by("-created_at")[:5]
    )

    context = {
        "articles": articles,
        "newsletters": newsletters,
    }

    return render(
        request,
        "news_app/home.html",
        context,
    )


def article_list(request):
    """
    Display all approved articles.
    """

    articles = (
        Article.objects
        .filter(approved=True)
        .select_related("author", "publisher")
        .order_by("-created_at")
    )

    return render(
        request,
        "news_app/article_list.html",
        {
            "articles": articles,
        },
    )


def article_detail(request, pk):
    """
    Display one approved article.
    """

    article = get_object_or_404(
        Article.objects.select_related(
            "author",
            "publisher",
        ),
        pk=pk,
        approved=True,
    )

    return render(
        request,
        "news_app/article_detail.html",
        {
            "article": article,
        },
    )


def newsletter_list(request):
    """
    Display available newsletters.
    """

    newsletters = (
        Newsletter.objects
        .select_related("author")
        .prefetch_related("articles")
        .order_by("-created_at")
    )

    return render(
        request,
        "news_app/newsletter_list.html",
        {
            "newsletters": newsletters,
        },
    )


# =============================================================================
# READER DASHBOARD
# =============================================================================


@login_required
def reader_dashboard(request):
    """
    Display approved articles from publishers and
    journalists followed by the current reader.
    """

    if not request.user.is_reader:
        return HttpResponseForbidden(
            "Only readers can access this page."
        )

    subscribed_publishers = (
        request.user.subscriptions_publishers.all()
    )

    subscribed_journalists = (
        request.user.subscriptions_journalists.all()
    )

    articles = (
        Article.objects
        .filter(approved=True)
        .filter(
            Q(
                publisher__in=subscribed_publishers
            )
            | Q(
                author__in=subscribed_journalists
            )
        )
        .select_related(
            "author",
            "publisher",
        )
        .distinct()
        .order_by("-created_at")
    )

    context = {
        "articles": articles,
        "subscribed_publishers": subscribed_publishers,
        "subscribed_journalists": subscribed_journalists,
    }

    return render(
        request,
        "news_app/reader_dashboard.html",
        context,
    )

# =============================================================================
# READER SUBSCRIPTION WEBSITE VIEWS
# =============================================================================


@login_required
def reader_subscriptions(request):
    """
    Allow readers to view available publishers and journalists
    and manage their subscriptions.
    """

    if not request.user.is_reader:
        return HttpResponseForbidden(
            "Only readers can manage subscriptions."
        )

    publishers = Publisher.objects.all().order_by("name")

    journalists = CustomUser.objects.filter(
        role=CustomUser.ROLE_JOURNALIST
    ).order_by("username")

    subscribed_publisher_ids = set(
        request.user.subscriptions_publishers.values_list(
            "id",
            flat=True,
        )
    )

    subscribed_journalist_ids = set(
        request.user.subscriptions_journalists.values_list(
            "id",
            flat=True,
        )
    )

    return render(
        request,
        "news_app/reader_subscriptions.html",
        {
            "publishers": publishers,
            "journalists": journalists,
            "subscribed_publisher_ids": subscribed_publisher_ids,
            "subscribed_journalist_ids": subscribed_journalist_ids,
        },
    )


@login_required
def reader_toggle_publisher_subscription(request, pk):
    """
    Subscribe or unsubscribe the logged-in reader
    from a publisher.
    """

    if not request.user.is_reader:
        return HttpResponseForbidden(
            "Only readers can manage subscriptions."
        )

    if request.method != "POST":
        return HttpResponseForbidden(
            "Subscription changes require a POST request."
        )

    publisher = get_object_or_404(
        Publisher,
        pk=pk,
    )

    if request.user.subscriptions_publishers.filter(
        pk=publisher.pk
    ).exists():

        request.user.subscriptions_publishers.remove(
            publisher
        )

    else:

        request.user.subscriptions_publishers.add(
            publisher
        )

    return redirect("reader-subscriptions")


@login_required
def reader_toggle_journalist_subscription(request, pk):
    """
    Subscribe or unsubscribe the logged-in reader
    from a journalist.
    """

    if not request.user.is_reader:
        return HttpResponseForbidden(
            "Only readers can manage subscriptions."
        )

    if request.method != "POST":
        return HttpResponseForbidden(
            "Subscription changes require a POST request."
        )

    journalist = get_object_or_404(
        CustomUser,
        pk=pk,
        role=CustomUser.ROLE_JOURNALIST,
    )

    if request.user.subscriptions_journalists.filter(
        pk=journalist.pk
    ).exists():

        request.user.subscriptions_journalists.remove(
            journalist
        )

    else:

        request.user.subscriptions_journalists.add(
            journalist
        )

    return redirect("reader-subscriptions")


# =============================================================================
# JOURNALIST DASHBOARD
# =============================================================================


@login_required
def journalist_dashboard(request):
    """
    Display articles and newsletters created by
    the logged-in journalist.
    """

    if not request.user.is_journalist:
        return HttpResponseForbidden(
            "Only journalists can access this page."
        )

    articles = (
        Article.objects
        .filter(author=request.user)
        .select_related("publisher")
        .order_by("-created_at")
    )

    newsletters = (
        Newsletter.objects
        .filter(author=request.user)
        .prefetch_related("articles")
        .order_by("-created_at")
    )

    return render(
        request,
        "news_app/journalist_dashboard.html",
        {
            "articles": articles,
            "newsletters": newsletters,
        },
    )

# =============================================================================
# JOURNALIST ARTICLE WEBSITE VIEWS
# =============================================================================


@login_required
def journalist_create_article(request):
    """
    Allow a journalist to submit a new article.

    New articles always begin as unapproved and must
    be reviewed by an editor before publication.
    """

    if not request.user.is_journalist:
        return HttpResponseForbidden(
            "Only journalists can create articles."
        )

    if request.method == "POST":
        form = ArticleForm(
            request.POST,
            journalist=request.user,
        )

        if form.is_valid():
            article = form.save(commit=False)

            article.author = request.user
            article.approved = False

            article.save()

            return redirect("journalist-dashboard")

    else:
        form = ArticleForm(
            journalist=request.user,
        )

    return render(
        request,
        "news_app/journalist_article_form.html",
        {
            "form": form,
            "page_title": "Create Article",
            "button_text": "Submit for Review",
        },
    )


@login_required
def journalist_edit_article(request, pk):
    """
    Allow a journalist to edit only an article
    that they personally authored.

    Editing sends the article back for editorial review.
    """

    if not request.user.is_journalist:
        return HttpResponseForbidden(
            "Only journalists can edit articles."
        )

    article = get_object_or_404(
        Article,
        pk=pk,
        author=request.user,
    )

    if request.method == "POST":
        form = ArticleForm(
            request.POST,
            instance=article,
            journalist=request.user,
        )

        if form.is_valid():
            article = form.save(commit=False)

            article.author = request.user

            # Any edited article must be reviewed again.
            article.approved = False

            article.save()

            return redirect("journalist-dashboard")

    else:
        form = ArticleForm(
            instance=article,
            journalist=request.user,
        )

    return render(
        request,
        "news_app/journalist_article_form.html",
        {
            "form": form,
            "article": article,
            "page_title": "Edit Article",
            "button_text": "Save & Resubmit",
        },
    )


@login_required
def journalist_delete_article(request, pk):
    """
    Allow journalists to delete only articles
    that they personally authored.
    """

    if not request.user.is_journalist:
        return HttpResponseForbidden(
            "Only journalists can delete articles."
        )

    article = get_object_or_404(
        Article,
        pk=pk,
        author=request.user,
    )

    if request.method == "POST":
        article.delete()

        return redirect("journalist-dashboard")

    return render(
        request,
        "news_app/journalist_article_confirm_delete.html",
        {
            "article": article,
        },
    )

# =============================================================================
# JOURNALIST NEWSLETTER WEBSITE VIEWS
# =============================================================================


@login_required
def journalist_create_newsletter(request):
    """
    Allow journalists to create newsletters.
    """

    if not request.user.is_journalist:
        return HttpResponseForbidden(
            "Only journalists can create newsletters."
        )

    if request.method == "POST":
        form = NewsletterForm(
            request.POST,
            journalist=request.user,
        )

        if form.is_valid():
            newsletter = form.save(commit=False)

            newsletter.author = request.user

            newsletter.save()

            # Save the many-to-many article relationships.
            form.save_m2m()

            return redirect("journalist-dashboard")

    else:
        form = NewsletterForm(
            journalist=request.user,
        )

    return render(
        request,
        "news_app/journalist_newsletter_form.html",
        {
            "form": form,
            "page_title": "Create Newsletter",
            "button_text": "Create Newsletter",
        },
    )


@login_required
def journalist_edit_newsletter(request, pk):
    """
    Allow journalists to edit only newsletters
    that they personally created.
    """

    if not request.user.is_journalist:
        return HttpResponseForbidden(
            "Only journalists can edit newsletters."
        )

    newsletter = get_object_or_404(
        Newsletter,
        pk=pk,
        author=request.user,
    )

    if request.method == "POST":
        form = NewsletterForm(
            request.POST,
            instance=newsletter,
            journalist=request.user,
        )

        if form.is_valid():
            form.save()

            return redirect("journalist-dashboard")

    else:
        form = NewsletterForm(
            instance=newsletter,
            journalist=request.user,
        )

    return render(
        request,
        "news_app/journalist_newsletter_form.html",
        {
            "form": form,
            "newsletter": newsletter,
            "page_title": "Edit Newsletter",
            "button_text": "Save Changes",
        },
    )


@login_required
def journalist_delete_newsletter(request, pk):
    """
    Allow journalists to delete only newsletters
    that they personally created.
    """

    if not request.user.is_journalist:
        return HttpResponseForbidden(
            "Only journalists can delete newsletters."
        )

    newsletter = get_object_or_404(
        Newsletter,
        pk=pk,
        author=request.user,
    )

    if request.method == "POST":
        newsletter.delete()

        return redirect("journalist-dashboard")

    return render(
        request,
        "news_app/journalist_newsletter_confirm_delete.html",
        {
            "newsletter": newsletter,
        },
    )


# =============================================================================
# EDITOR DASHBOARD
# =============================================================================


@login_required
def editor_dashboard(request):
    """
    Display articles awaiting editor approval.
    """

    if not request.user.is_editor:
        return HttpResponseForbidden(
            "Only editors can access this page."
        )

    pending_articles = (
        Article.objects
        .filter(approved=False)
        .select_related(
            "author",
            "publisher",
        )
        .order_by("-created_at")
    )

    approved_articles = (
        Article.objects
        .filter(approved=True)
        .select_related(
            "author",
            "publisher",
        )
        .order_by("-created_at")[:10]
    )

    return render(
        request,
        "news_app/editor_dashboard.html",
        {
            "pending_articles": pending_articles,
            "approved_articles": approved_articles,
        },
    )


@login_required
def editor_review_article(request, pk):
    """
    Allow an editor to review a pending article.
    """

    if not request.user.is_editor:
        return HttpResponseForbidden(
            "Only editors can review articles."
        )

    article = get_object_or_404(
        Article.objects.select_related(
            "author",
            "publisher",
        ),
        pk=pk,
    )

    return render(
        request,
        "news_app/editor_review_article.html",
        {
            "article": article,
        },
    )


@login_required
def editor_approve_article(request, pk):
    """
    Approve an article through the website.

    The save operation triggers the approval signal.
    """

    if not request.user.is_editor:
        return HttpResponseForbidden(
            "Only editors can approve articles."
        )

    if request.method != "POST":
        return HttpResponseForbidden(
            "Article approval requires a POST request."
        )

    article = get_object_or_404(
        Article,
        pk=pk,
    )

    if not article.approved:
        article.approved = True

        article.save(
            update_fields=["approved"]
        )

    return redirect(
        "editor-dashboard"
    )


# =============================================================================
# REST API PERMISSIONS
# =============================================================================


class IsReader(permissions.BasePermission):
    """
    Allow authenticated readers only.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_reader
        )


class IsJournalist(permissions.BasePermission):
    """
    Allow authenticated journalists only.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_journalist
        )


class IsEditor(permissions.BasePermission):
    """
    Allow authenticated editors only.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_editor
        )


class IsEditorOrJournalist(
    permissions.BasePermission
):
    """
    Editors and journalists may modify content.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated
            and (
                request.user.is_editor
                or request.user.is_journalist
            )
        )


# =============================================================================
# PUBLISHER REST API
# =============================================================================


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()

    serializer_class = PublisherSerializer

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [IsEditor()]

        return [permissions.AllowAny()]


# =============================================================================
# ARTICLE REST API
# =============================================================================


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        user = self.request.user

        # Editors can see every article.
        if (
            user.is_authenticated
            and user.is_editor
        ):
            return Article.objects.all()

        # Journalists can see published articles plus
        # their own pending articles.
        if (
            user.is_authenticated
            and user.is_journalist
        ):
            return (
                Article.objects
                .filter(
                    Q(approved=True)
                    | Q(author=user)
                )
                .distinct()
            )

        # Readers/public users only see approved content.
        return Article.objects.filter(
            approved=True
        )

    def get_permissions(self):
        if self.action == "create":
            return [IsJournalist()]

        if self.action == "approve":
            return [IsEditor()]

        if self.action in [
            "update",
            "partial_update",
            "destroy",
        ]:
            return [
                IsEditorOrJournalist()
            ]

        return [
            permissions.AllowAny()
        ]

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            approved=False,
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[
            permissions.IsAuthenticated
        ],
    )
    def subscribed(self, request):
        """
        GET /api/articles/subscribed/
        """

        user = request.user

        if not user.is_reader:
            return Response(
                {
                    "detail": (
                        "Only readers can access "
                        "subscription-based articles."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        subscribed_publishers = (
            user
            .subscriptions_publishers
            .all()
        )

        subscribed_journalists = (
            user
            .subscriptions_journalists
            .all()
        )

        articles = (
            Article.objects
            .filter(approved=True)
            .filter(
                Q(
                    publisher__in=(
                        subscribed_publishers
                    )
                )
                | Q(
                    author__in=(
                        subscribed_journalists
                    )
                )
            )
            .distinct()
        )

        serializer = self.get_serializer(
            articles,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsEditor],
    )
    def approve(self, request, pk=None):
        """
        POST /api/articles/<id>/approve/
        """

        article = self.get_object()

        if article.approved:
            return Response(
                {
                    "detail": (
                        "This article has already "
                        "been approved."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        article.approved = True

        article.save(
            update_fields=["approved"]
        )

        serializer = self.get_serializer(
            article
        )

        return Response(
            {
                "detail": (
                    "Article approved successfully."
                ),
                "article": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =============================================================================
# NEWSLETTER REST API
# =============================================================================


class NewsletterViewSet(
    viewsets.ModelViewSet
):
    queryset = Newsletter.objects.all()

    serializer_class = (
        NewsletterSerializer
    )

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [
                IsEditorOrJournalist()
            ]

        return [
            permissions.AllowAny()
        ]

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )


# =============================================================================
# INTERNAL APPROVED ARTICLE API
# =============================================================================


class ApprovedArticleView(APIView):
    """
    Receives approved article information.

    POST /api/approved/
    """

    permission_classes = [
        permissions.AllowAny
    ]

    def post(self, request):
        article_id = request.data.get(
            "article_id"
        )

        title = request.data.get(
            "title"
        )

        author = request.data.get(
            "author"
        )

        if (
            not article_id
            or not title
            or not author
        ):
            return Response(
                {
                    "detail": (
                        "article_id, title and "
                        "author are required."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        logger.info(
            "Approved article received: "
            "%s - %s by %s",
            article_id,
            title,
            author,
        )

        return Response(
            {
                "message": (
                    "Approved article logged "
                    "successfully."
                ),
                "article_id": article_id,
                "title": title,
                "author": author,
            },
            status=status.HTTP_201_CREATED,
        )

# =============================================================================
# USER REGISTRATION
# =============================================================================

from django.contrib.auth import login
from django.shortcuts import redirect
from .forms import RegistrationForm


def register(request):
    """Register a new account and sign the user in."""

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("reader-dashboard")
    else:
        form = RegistrationForm()

    return render(
        request,
        "news_app/register.html",
        {"form": form},
    )
