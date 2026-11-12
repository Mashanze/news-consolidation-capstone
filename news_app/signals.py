import logging

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Article


logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Article)
def track_article_approval(sender, instance, **kwargs):
    """
    Determine whether an existing article is changing
    from unapproved to approved.
    """

    instance._just_approved = False

    if not instance.pk:
        return

    try:
        previous_article = Article.objects.get(
            pk=instance.pk
        )
    except Article.DoesNotExist:
        return

    if (
        not previous_article.approved
        and instance.approved
    ):
        instance._just_approved = True


@receiver(post_save, sender=Article)
def handle_article_approval(
    sender,
    instance,
    created,
    **kwargs,
):
    """
    When an article transitions from:

        approved=False
                to
        approved=True

    notify subscribers and POST the approved article
    to the internal REST endpoint.
    """

    if created:
        return

    if not getattr(
        instance,
        "_just_approved",
        False,
    ):
        return

    recipient_emails = set()

    # -------------------------------------------------------------------------
    # Publisher subscribers
    # -------------------------------------------------------------------------

    if instance.publisher:
        publisher_subscribers = (
            instance.publisher.subscribers.all()
        )

        for subscriber in publisher_subscribers:
            if subscriber.email:
                recipient_emails.add(
                    subscriber.email
                )

    # -------------------------------------------------------------------------
    # Journalist subscribers
    # -------------------------------------------------------------------------

    if instance.author:
        journalist_subscribers = (
            instance.author.journalist_subscribers.all()
        )

        for subscriber in journalist_subscribers:
            if subscriber.email:
                recipient_emails.add(
                    subscriber.email
                )

    recipient_emails = list(recipient_emails)

    # -------------------------------------------------------------------------
    # Email subscribers
    # -------------------------------------------------------------------------

    if recipient_emails:
        subject = (
            f"New Approved Article: {instance.title}"
        )

        message = (
            "Hello,\n\n"
            f"A new article titled '{instance.title}' "
            "has been approved and published.\n\n"
            f"Author: {instance.author.username}\n\n"
            "Thank you for subscribing."
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_emails,
                fail_silently=False,
            )

            logger.info(
                "Sent article %s to %s subscriber(s).",
                instance.pk,
                len(recipient_emails),
            )

        except Exception as mail_error:
            logger.exception(
                "Unable to send subscriber email "
                "for article %s: %s",
                instance.pk,
                mail_error,
            )

    # -------------------------------------------------------------------------
    # Internal REST API integration
    # -------------------------------------------------------------------------

    api_url = getattr(
        settings,
        "INTERNAL_APPROVED_API_URL",
        "http://127.0.0.1:8000/api/approved/",
    )

    payload = {
        "article_id": instance.pk,
        "title": instance.title,
        "author": instance.author.username,
    }

    try:
        response = requests.post(
            api_url,
            json=payload,
            timeout=5,
        )

        if response.status_code == 201:
            logger.info(
                "Article %s successfully logged "
                "through the approved API.",
                instance.pk,
            )

        else:
            logger.warning(
                "Approved API returned status %s "
                "for article %s.",
                response.status_code,
                instance.pk,
            )

    except requests.RequestException as error:
        logger.error(
            "Unable to POST article %s to "
            "the approved API: %s",
            instance.pk,
            error,
        )