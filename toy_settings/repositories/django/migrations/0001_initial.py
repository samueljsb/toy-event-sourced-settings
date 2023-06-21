# Generated by Django 4.2.1 on 2023-06-21 22:35

from __future__ import annotations

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies: list[str] = []

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("event_type", models.CharField(max_length=100)),
                ("event_type_version", models.IntegerField()),
                ("key", models.CharField(max_length=100)),
                ("timestamp", models.DateTimeField()),
                ("payload", models.CharField(max_length=500)),
            ],
        ),
    ]
