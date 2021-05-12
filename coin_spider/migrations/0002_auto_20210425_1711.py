# Generated by Django 3.1.5 on 2021-04-25 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coin_spider', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cointrick',
            name='best_ask',
            field=models.BigIntegerField(verbose_name='卖一价'),
        ),
        migrations.AlterField(
            model_name='cointrick',
            name='best_ask_size',
            field=models.BigIntegerField(verbose_name='卖一价对应的量'),
        ),
        migrations.AlterField(
            model_name='cointrick',
            name='best_bid',
            field=models.BigIntegerField(max_length=32, verbose_name='买一价'),
        ),
        migrations.AlterField(
            model_name='cointrick',
            name='best_bid_size',
            field=models.BigIntegerField(verbose_name='买一价对应的数量'),
        ),
        migrations.AlterField(
            model_name='cointrick',
            name='last',
            field=models.BigIntegerField(verbose_name='最新成交价'),
        ),
        migrations.AlterField(
            model_name='cointrick',
            name='last_qty',
            field=models.BigIntegerField(verbose_name='最新成交的数量'),
        ),
        migrations.AlterField(
            model_name='cointrick',
            name='open_utc0',
            field=models.BigIntegerField(verbose_name='UTC+0时开盘价'),
        ),
        migrations.AlterField(
            model_name='cointrick',
            name='open_utc8',
            field=models.BigIntegerField(verbose_name='UTC+8时开盘价'),
        ),
        migrations.AlterField(
            model_name='cointrick',
            name='product_id',
            field=models.CharField(db_index=True, max_length=32, verbose_name='币对'),
        ),
        migrations.AlterField(
            model_name='cointrick',
            name='timestamp',
            field=models.DateTimeField(db_index=True, verbose_name='时间'),
        ),
    ]