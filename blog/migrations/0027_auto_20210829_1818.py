# Generated by Django 3.0.6 on 2021-08-29 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0026_auto_20210829_1818'),
    ]

    operations = [
        migrations.RenameField(
            model_name='photo',
            old_name='img_file_link',
            new_name='file_link',
        ),
    ]