from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("django_back_end", "0002_sequence_sequence_unique_index_per_key"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""\
CREATE TRIGGER ensure_event_index_always_increases
BEFORE INSERT ON django_back_end_sequence
BEGIN
    SELECT
    CASE WHEN NEW."index" <= (
        SELECT MAX("index") FROM django_back_end_sequence WHERE "key"=NEW."key"
    ) THEN RAISE (ABORT,'index must be greater than all previous indexes')
    END;
END;
""",
            reverse_sql="DROP TRIGGER ensure_event_index_always_increases;",
        )
    ]
