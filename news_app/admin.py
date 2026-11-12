from django.contrib import admin

from .models import Article, CustomUser, Newsletter, Publisher


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Manage users and approve requested account roles."""

    list_display = (
        "username",
        "email",
        "role",
        "requested_role",
        "role_request_status",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "requested_role",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
    )

    def get_readonly_fields(self, request, obj=None):
        """Prevent non-superusers from changing account roles."""
        fields = list(super().get_readonly_fields(request, obj))

        if not request.user.is_superuser:
            fields.extend([
                "role",
                "requested_role",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ])

        return tuple(dict.fromkeys(fields))

    actions = (
        "approve_requested_roles",
        "reject_requested_roles",
    )

    @admin.display(description="Role request")
    def role_request_status(self, obj):
        if obj.requested_role == obj.role:
            return "No pending request"
        if obj.requested_role == CustomUser.ROLE_READER:
            return "No pending request"
        return "Pending approval"

    @admin.action(description="Approve selected role requests")
    def approve_requested_roles(self, request, queryset):
        if not request.user.is_superuser:
            self.message_user(
                request,
                "Only superusers can approve roles.",
                level="error",
            )
            return

        count = 0
        for user in queryset:
            if (
                user.requested_role in (
                    CustomUser.ROLE_JOURNALIST,
                    CustomUser.ROLE_EDITOR,
                )
                and user.role != user.requested_role
            ):
                user.role = user.requested_role
                user.save(update_fields=["role"])
                count += 1

        self.message_user(
            request,
            f"{count} role request(s) approved.",
        )

    @admin.action(description="Reject selected role requests")
    def reject_requested_roles(self, request, queryset):
        if not request.user.is_superuser:
            self.message_user(
                request,
                "Only superusers can reject roles.",
                level="error",
            )
            return

        count = 0
        for user in queryset:
            if (
                user.requested_role != CustomUser.ROLE_READER
                and user.requested_role != user.role
            ):
                user.requested_role = CustomUser.ROLE_READER
                user.save(update_fields=["requested_role"])
                count += 1

        self.message_user(
            request,
            f"{count} role request(s) rejected.",
        )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "publisher",
        "approved",
        "created_at",
    )

    list_filter = (
        "approved",
        "publisher",
        "created_at",
    )

    search_fields = (
        "title",
        "content",
        "author__username",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "author__username",
    )

    filter_horizontal = (
        "articles",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    filter_horizontal = (
        "editors",
        "journalists",
    )

    readonly_fields = (
        "created_at",
    )