from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_ixc_sync', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ixcconfig',
            name='remove_orphans',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='synclog',
            name='removidos',
            field=models.IntegerField(default=0),
        ),
    ]
