# Generated by Django 4.2.1 on 2023-06-28 12:40

from __future__ import annotations

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("django_back_end", "0003_ensure_index_always_increases"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="key",
            field=models.CharField(db_index=True, max_length=100),
        ),
    ]