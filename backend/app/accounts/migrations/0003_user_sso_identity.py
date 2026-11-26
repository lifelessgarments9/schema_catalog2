from django.db import migrations, models


def backfill_sso_identity(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    database = schema_editor.connection.alias

    users = User.objects.using(database).filter(username__startswith="sso_")
    for user in users.iterator():
        identity = user.username[4:]
        if identity:
            User.objects.using(database).filter(pk=user.pk).update(
                sso_identity=identity
            )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_ai_requests_user_ai_restore_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="sso_identity",
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
        migrations.RunPython(backfill_sso_identity, migrations.RunPython.noop),
    ]
