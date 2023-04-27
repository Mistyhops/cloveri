from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('path', models.TextField()),
                ('project_id', models.UUIDField()),
                ('item_type', models.TextField()),
                ('item', models.TextField()),
                ('inner_order', models.TextField()),
                ('attributes', models.JSONField(blank=True, null=True)),
                ('hidden', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tree_structure_node',
                'unique_together': {('path', 'id'), ('id', 'project_id', 'item_type', 'item')},
            },
        ),
    ]
