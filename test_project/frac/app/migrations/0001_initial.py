# Generated by Django 2.2.16 on 2020-09-05 20:39

from django.db import migrations, models
import djfractions.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('defaults', djfractions.models.fields.DecimalFractionField(coerce_thirds=True, decimal_places=5, limit_denominator=None, max_digits=10)),
                ('denominator_limited_to_ten', djfractions.models.fields.DecimalFractionField(coerce_thirds=True, decimal_places=10, default=None, limit_denominator=10, max_digits=15, null=True)),
                ('coerce_thirds_true', djfractions.models.fields.DecimalFractionField(coerce_thirds=True, decimal_places=10, default=None, limit_denominator=None, max_digits=15, null=True)),
                ('decimal_places_limited', djfractions.models.fields.DecimalFractionField(coerce_thirds=False, decimal_places=10, default=None, limit_denominator=None, max_digits=15, null=True)),
            ],
        ),
    ]