# Generated by Django 3.0.7 on 2020-10-29 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LatestUpdate',
            fields=[
                ('var', models.CharField(choices=[('C', 'Cases'), ('A', 'Active'), ('R', 'Recovery'), ('D', 'Deaths'), ('T', 'Tests'), ('1', 'Rt1'), ('2', 'Rt2')], max_length=1, primary_key=True, serialize=False)),
                ('date', models.DateField()),
            ],
        ),
        migrations.RenameField(
            model_name='reproductionnum',
            old_name='version',
            new_name='var',
        ),
    ]