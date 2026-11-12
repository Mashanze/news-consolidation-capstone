from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from news_app import views


urlpatterns = [

    # WEBSITE AUTHENTICATION
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="news_app/login.html"
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),


    # =============================================================================
    # WEBSITE
    # =============================================================================

    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "articles/",
        views.article_list,
        name="article-list-page",
    ),

    path(
        "articles/<int:pk>/",
        views.article_detail,
        name="article-detail-page",
    ),

    path(
        "newsletters/",
        views.newsletter_list,
        name="newsletter-list-page",
    ),

    # =============================================================================
    # READER
    # =============================================================================

    path(
        "reader/",
        views.reader_dashboard,
        name="reader-dashboard",
    ),

    path(
    "reader/subscriptions/",
    views.reader_subscriptions,
    name="reader-subscriptions",
),

path(
    "reader/subscriptions/publishers/<int:pk>/toggle/",
    views.reader_toggle_publisher_subscription,
    name="reader-toggle-publisher-subscription",
),

path(
    "reader/subscriptions/journalists/<int:pk>/toggle/",
    views.reader_toggle_journalist_subscription,
    name="reader-toggle-journalist-subscription",
),

    # =============================================================================
    # JOURNALIST
    # =============================================================================

    path(
        "journalist/",
        views.journalist_dashboard,
        name="journalist-dashboard",
    ),

    # Journalist Article CRUD

path(
    "journalist/articles/new/",
    views.journalist_create_article,
    name="journalist-create-article",
),

path(
    "journalist/articles/<int:pk>/edit/",
    views.journalist_edit_article,
    name="journalist-edit-article",
),

path(
    "journalist/articles/<int:pk>/delete/",
    views.journalist_delete_article,
    name="journalist-delete-article",
),

# Journalist Newsletter CRUD

path(
    "journalist/newsletters/new/",
    views.journalist_create_newsletter,
    name="journalist-create-newsletter",
),

path(
    "journalist/newsletters/<int:pk>/edit/",
    views.journalist_edit_newsletter,
    name="journalist-edit-newsletter",
),

path(
    "journalist/newsletters/<int:pk>/delete/",
    views.journalist_delete_newsletter,
    name="journalist-delete-newsletter",
),

    # =============================================================================
    # EDITOR
    # =============================================================================

    path(
        "editor/",
        views.editor_dashboard,
        name="editor-dashboard",
    ),

    path(
        "editor/articles/<int:pk>/",
        views.editor_review_article,
        name="editor-review-article",
    ),

    path(
        "editor/articles/<int:pk>/approve/",
        views.editor_approve_article,
        name="editor-approve-article",
    ),

    # =============================================================================
    # DJANGO ADMIN
    # =============================================================================

    path(
        "admin/",
        admin.site.urls,
    ),

    # =============================================================================
    # TOKEN AUTHENTICATION
    # =============================================================================

    path(
        "api/token/",
        obtain_auth_token,
        name="api-token",
    ),

    # =============================================================================
    # REST API
    # =============================================================================

    path(
        "api/",
        include("news_app.urls"),
    ),

    # =============================================================================
    # DRF BROWSABLE API LOGIN / LOGOUT
    # =============================================================================

    path(
        "api-auth/",
        include("rest_framework.urls"),
    ),
]