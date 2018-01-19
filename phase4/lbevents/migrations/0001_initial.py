# Generated by Django 2.0 on 2018-01-18 16:06

from django.db import migrations, models
import django.db.models.deletion
import lbevents.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lon', models.DecimalField(decimal_places=6, max_digits=9, validators=[lbevents.models.validate_lon])),
                ('lat', models.DecimalField(decimal_places=6, max_digits=9, validators=[lbevents.models.validate_lat])),
                ('locname', models.CharField(max_length=256)),
                ('title', models.CharField(max_length=256)),
                ('desc', models.CharField(max_length=256)),
                ('catlist', models.CharField(max_length=256)),
                ('stime', models.DateTimeField()),
                ('to', models.DateTimeField()),
                ('timetoann', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='EventMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='Map',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lbevents.EventMap'),
        ),
    ]