# Generated by Django 2.0 on 2018-01-21 08:40

from django.db import migrations, models
import django.db.models.deletion
import lbevents.models


class Migration(migrations.Migration):

    dependencies = [
        ('lbevents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Observer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lon_topleft', models.DecimalField(decimal_places=6, max_digits=9, validators=[lbevents.models.validate_lon])),
                ('lat_topleft', models.DecimalField(decimal_places=6, max_digits=9, validators=[lbevents.models.validate_lat])),
                ('lon_botright', models.DecimalField(decimal_places=6, max_digits=9, validators=[lbevents.models.validate_lon])),
                ('lat_botright', models.DecimalField(decimal_places=6, max_digits=9, validators=[lbevents.models.validate_lat])),
                ('category', models.CharField(max_length=256)),
                ('Map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lbevents.EventMap')),
            ],
        ),
    ]
