# Generated by Django 2.2.11 on 2020-03-21 22:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('plaidapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='balances', to='plaidapp.Account'),
        ),
    ]
