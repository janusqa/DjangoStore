# Generated by Django 5.0.6 on 2024-06-28 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_alter_customer_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['user__last_name', 'user__first_name'], 'permissions': [('view_history', 'Can view history')]},
        ),
    ]