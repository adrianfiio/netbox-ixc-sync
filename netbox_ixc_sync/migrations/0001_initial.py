import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('extras', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IXCConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(default='IXC Principal', max_length=100)),
                ('prefix', models.CharField(max_length=50)),
                ('vrf_name', models.CharField(default='Nicfibra', max_length=100)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Configuração IXC',
                'verbose_name_plural': 'Configurações IXC',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SyncLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('success', models.BooleanField(default=True)),
                ('criados', models.IntegerField(default=0)),
                ('atualizados', models.IntegerField(default=0)),
                ('ignorados', models.IntegerField(default=0)),
                ('total_ixc', models.IntegerField(default=0)),
                ('mensagem', models.TextField(blank=True)),
                ('detalhes', models.TextField(blank=True)),
                ('config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='netbox_ixc_sync.ixcconfig')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Log de Sincronização',
                'verbose_name_plural': 'Logs de Sincronização',
                'ordering': ['-timestamp'],
            },
        ),
    ]
