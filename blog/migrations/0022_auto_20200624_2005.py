# Generated by Django 3.0.6 on 2020-06-24 14:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0021_auto_20200623_2023'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentreply',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user_post_comment_reply', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comments',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user_post_comment', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]