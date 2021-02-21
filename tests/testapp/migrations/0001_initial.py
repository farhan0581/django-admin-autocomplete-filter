"""Create models in database."""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('isbn', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('best_friend', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='testapp.Person')),
                ('twin', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rev_twin', to='testapp.person')),
                ('curated_collections', models.ManyToManyField(blank=True, to='testapp.Collection')),
                ('favorite_book', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='people_with_this_fav_book', to='testapp.Book')),
                ('favorite_food', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='testapp.Food')),
                ('least_favorite_food', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='food_is_least_fav', related_query_name='people_with_this_least_fav_food', to='testapp.Food')),
                ('siblings', models.ManyToManyField(blank=True, related_name='_person_siblings_+', to='testapp.Person')),
            ],
        ),
        migrations.AddField(
            model_name='collection',
            name='curators',
            field=models.ManyToManyField(blank=True, to='testapp.Person'),
        ),
        migrations.AddField(
            model_name='book',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='testapp.Person'),
        ),
        migrations.AddField(
            model_name='book',
            name='coll',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='testapp.Collection'),
        ),
    ]
