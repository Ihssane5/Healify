# Generated by Django 5.2 on 2025-05-08 17:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assistant_medical', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='conversation',
            old_name='user',
            new_name='patient',
        ),
    ]
