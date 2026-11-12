from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from news_app.models import Article, Newsletter, Publisher


User = get_user_model()


def get_or_create_group(name):
    """
    Create a Django group if it does not already exist.
    """
    group, _ = Group.objects.get_or_create(name=name)
    return group


def create_user(
    username,
    email,
    password,
    role,
    is_staff=False,
    is_superuser=False,
):
    """
    Create a user or update an existing seeded user.
    """

    user, _ = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "role": role,
            "is_staff": is_staff,
            "is_superuser": is_superuser,
        },
    )

    user.email = email
    user.role = role
    user.is_staff = is_staff
    user.is_superuser = is_superuser

    # Keep development seed credentials predictable.
    user.set_password(password)

    user.save()

    return user


def run_seed():
    print("\nStarting database seed...")
    print("----------------------------------------")

    # =========================================================
    # 1. CREATE ROLE GROUPS
    # =========================================================

    reader_group = get_or_create_group("Reader")
    journalist_group = get_or_create_group("Journalist")
    editor_group = get_or_create_group("Editor")

    print("✓ Reader group ready")
    print("✓ Journalist group ready")
    print("✓ Editor group ready")

    # =========================================================
    # 2. CONFIGURE GROUP PERMISSIONS
    # =========================================================

    reader_permissions = Permission.objects.filter(
        codename__in=[
            "view_article",
            "view_newsletter",
            "view_publisher",
        ]
    )

    reader_group.permissions.set(reader_permissions)

    journalist_permissions = Permission.objects.filter(
        codename__in=[
            "add_article",
            "view_article",
            "change_article",
            "delete_article",
            "add_newsletter",
            "view_newsletter",
            "change_newsletter",
            "delete_newsletter",
            "view_publisher",
        ]
    )

    journalist_group.permissions.set(
        journalist_permissions
    )

    editor_permissions = Permission.objects.filter(
        codename__in=[
            "view_article",
            "change_article",
            "delete_article",
            "view_newsletter",
            "change_newsletter",
            "delete_newsletter",
            "view_publisher",
            "change_publisher",
        ]
    )

    editor_group.permissions.set(editor_permissions)

    print("✓ Reader permissions configured")
    print("✓ Journalist permissions configured")
    print("✓ Editor permissions configured")

    # =========================================================
    # 3. CREATE TEST USERS
    # =========================================================

    reader = create_user(
        username="reader_user",
        email="reader@example.com",
        password="password123",
        role=User.ROLE_READER,
    )

    journalist = create_user(
        username="journalist_user",
        email="journalist@example.com",
        password="password123",
        role=User.ROLE_JOURNALIST,
    )

    editor = create_user(
        username="admin_editor",
        email="editor@example.com",
        password="password123",
        role=User.ROLE_EDITOR,
        is_staff=True,
        is_superuser=True,
    )

    # =========================================================
    # 4. ASSIGN USERS TO GROUPS
    # =========================================================

    reader.groups.set([reader_group])
    journalist.groups.set([journalist_group])
    editor.groups.set([editor_group])

    print("✓ Reader user ready")
    print("✓ Journalist user ready")
    print("✓ Editor user ready")

    # =========================================================
    # 5. CREATE PUBLISHERS
    # =========================================================

    pub1, _ = Publisher.objects.update_or_create(
        name="Tech Chronicle",
        defaults={
            "description": (
                "A publication covering technology, "
                "software development and artificial "
                "intelligence."
            )
        },
    )

    pub2, _ = Publisher.objects.update_or_create(
        name="Global News Wire",
        defaults={
            "description": (
                "A publication covering global news, "
                "technology and current affairs."
            )
        },
    )

    print("✓ Tech Chronicle publisher ready")
    print("✓ Global News Wire publisher ready")

    # =========================================================
    # 6. PUBLISHER STAFF
    # =========================================================

    pub1.journalists.add(journalist)
    pub1.editors.add(editor)

    pub2.journalists.add(journalist)
    pub2.editors.add(editor)

    print("✓ Publisher staff relationships configured")

    # =========================================================
    # 7. READER SUBSCRIPTIONS
    # =========================================================

    reader.subscriptions_publishers.add(pub1)
    reader.subscriptions_journalists.add(journalist)

    print("✓ Reader subscriptions configured")

    # =========================================================
    # 8. CREATE ARTICLES
    # =========================================================

    article1, _ = Article.objects.update_or_create(
        title="The Rise of AI Life Operating Systems",
        defaults={
            "content": (
                "Exploring how AI-driven architectures "
                "are transforming personal productivity "
                "and modern software development workflows."
            ),
            "author": journalist,
            "publisher": pub1,
            "approved": False,
        },
    )

    article2, _ = Article.objects.update_or_create(
        title="Next.js and Django: Building Modern Hybrids",
        defaults={
            "content": (
                "A deep dive into combining powerful "
                "Python backend services with modern "
                "React and Next.js frontends."
            ),
            "author": journalist,
            "publisher": pub2,
            "approved": True,
        },
    )

    print("✓ First article ready")
    print("✓ Second article ready")

    # =========================================================
    # 9. CREATE NEWSLETTER
    # =========================================================

    newsletter, _ = Newsletter.objects.update_or_create(
        title="Weekly Tech Digest",
        defaults={
            "description": (
                "The top technology stories and software "
                "engineering breakthroughs of the week."
            ),
            "author": journalist,
        },
    )

    newsletter.articles.set(
        [
            article1,
            article2,
        ]
    )

    print("✓ Weekly Tech Digest newsletter ready")

    # =========================================================
    # FINISHED
    # =========================================================

    print("----------------------------------------")
    print("Database seeding completed successfully!")
    print("----------------------------------------")

    print("\nTEST ACCOUNTS")
    print("========================================")

    print("\nREADER")
    print("Username: reader_user")
    print("Password: password123")

    print("\nJOURNALIST")
    print("Username: journalist_user")
    print("Password: password123")

    print("\nEDITOR / ADMIN")
    print("Username: admin_editor")
    print("Password: password123")

    print("\n========================================")

    print("\nDATABASE CONTENT")
    print("----------------------------------------")

    print(f"Users: {User.objects.count()}")
    print(f"Publishers: {Publisher.objects.count()}")
    print(f"Articles: {Article.objects.count()}")
    print(f"Newsletters: {Newsletter.objects.count()}")

    print("----------------------------------------\n")


run_seed()