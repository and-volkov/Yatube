# Generated by Django 2.2.16 on 2022-04-12 16:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20220219_1558'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Запись', 'verbose_name_plural': 'Записи'},
        ),
    ]
