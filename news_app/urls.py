from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ApprovedArticleView,
    ArticleViewSet,
    NewsletterViewSet,
    PublisherViewSet,
)


# =============================================================================
# REST API ROUTER
# =============================================================================

router = DefaultRouter()

router.register(
    r"articles",
    ArticleViewSet,
    basename="article",
)

router.register(
    r"newsletters",
    NewsletterViewSet,
    basename="newsletter",
)

router.register(
    r"publishers",
    PublisherViewSet,
    basename="publisher",
)


# =============================================================================
# API URLS
# =============================================================================

urlpatterns = [
    path(
        "approved/",
        ApprovedArticleView.as_view(),
        name="approved-article",
    ),

    path(
        "",
        include(router.urls),
    ),
]