# Generated by Django 3.0.7 on 2020-09-20 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CovidData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('var', models.CharField(choices=[('C', 'Cases'), ('A', 'Active'), ('R', 'Recovery'), ('D', 'Deaths'), ('T', 'Tests')], max_length=1)),
                ('ec', models.IntegerField()),
                ('fs', models.IntegerField()),
                ('gp', models.IntegerField()),
                ('kzn', models.IntegerField()),
                ('lp', models.IntegerField()),
                ('mp', models.IntegerField()),
                ('nc', models.IntegerField()),
                ('nw', models.IntegerField()),
                ('wc', models.IntegerField()),
                ('unknown', models.IntegerField()),
                ('total', models.IntegerField()),
                ('source', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ReproductionNum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('date', models.DateField()),
                ('state', models.CharField(max_length=20)),
                ('rt', models.DecimalField(decimal_places=3, max_digits=5)),
                ('high', models.IntegerField()),
                ('low', models.IntegerField()),
                ('infect', models.IntegerField(null=True)),
                ('adj', models.IntegerField(null=True)),
            ],
        ),
    ]
