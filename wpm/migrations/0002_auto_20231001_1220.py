# Generated by Django 3.1.14 on 2023-10-01 10:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wpm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DNSServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(verbose_name='ip address')),
            ],
            options={
                'verbose_name': 'dns server',
                'verbose_name_plural': 'dns servers',
            },
        ),
        migrations.AddField(
            model_name='wireguardendpoint',
            name='wpm_api_port',
            field=models.PositiveIntegerField(default=8080, validators=[django.core.validators.MaxValueValidator(65535)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wireguardendpoint',
            name='wpm_api_token',
            field=models.CharField(default='invalid', max_length=64, verbose_name='api token'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wireguardendpoint',
            name='endpoint_port',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(65535)]),
        ),
        migrations.AddField(
            model_name='wireguardendpoint',
            name='dns_server',
            field=models.ManyToManyField(to='wpm.DNSServer'),
        ),
    ]
