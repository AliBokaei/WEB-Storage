# Generated by Django 5.0.4 on 2024-06-30 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0002_alter_uploadedfile_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfile',
            name='size',
            field=models.IntegerField(),
        ),
    ]
