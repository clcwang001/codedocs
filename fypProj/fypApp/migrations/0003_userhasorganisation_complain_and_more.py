# Generated by Django 5.0 on 2024-01-02 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fypApp', '0002_remove_users_organisationpaymentqr_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userhasorganisation',
            name='complain',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userhasorganisation',
            name='donations',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
