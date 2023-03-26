# Generated by Django 4.1.7 on 2023-03-06 21:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("books", "0005_book_can_buy_all_book_subscription_user_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="chapter",
            name="users_with_access",
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
