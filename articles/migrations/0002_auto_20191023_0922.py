# Generated by Django 2.2.5 on 2019-10-23 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Student',
        ),
        migrations.AddField(
            model_name='article',
            name='like_users',
            field=models.ManyToManyField(blank=True, related_name='like_articles', to='accounts.User'),
        ),
    ]