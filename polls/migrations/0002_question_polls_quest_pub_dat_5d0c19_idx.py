# Generated by Django 5.1.2 on 2024-11-03 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['pub_date'], name='polls_quest_pub_dat_5d0c19_idx'),
        ),
    ]
