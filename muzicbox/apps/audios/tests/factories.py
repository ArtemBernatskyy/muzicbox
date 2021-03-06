import os
import random
import factory

from muzicbox.apps.audios.models import Audio, Album, Tag
from muzicbox.apps.accounts.tests.factories import UserFactory
from muzicbox.apps.artists.tests.factories import ArtistFactory


class AlbumFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('company')
    mbid = factory.Faker('uuid4')
    artist = factory.SubFactory(ArtistFactory)

    class Meta:
        model = Album


class TagFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: '#tag{0}'.format(n))
    short_description = factory.Faker('sentence')

    class Meta:
        model = Tag


class AudioFactory(factory.django.DjangoModelFactory):
    owner = factory.SubFactory(UserFactory)
    name = factory.Faker('bs')
    mbid = factory.Faker('uuid4')
    bitrate = factory.Faker('random_int', min=128000, max=320000)
    length = factory.Faker('random_int', min=100, max=400)
    audio_file = factory.django.FileField(from_path='muzicbox/apps/audios/tests/fixtures/with_id3.mp3')
    playcount = factory.Faker('random_int', min=100, max=100000)
    album = factory.SubFactory(AlbumFactory)
    artist = factory.SubFactory(ArtistFactory)
    is_presentation = factory.Faker('boolean')
    year = factory.Faker('date_time')
    lyrics = factory.Faker('paragraph')

    files = set()

    @classmethod
    def tear_down_files(cls):
        for file in cls.files.copy():
            os.remove(file.path)
            cls.files.remove(file)

    class Meta:
        model = Audio
        exclude = ('files',)

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        # keeping track of created files in order to purge in tearDownClass
        AudioFactory.files.add(self.audio_file)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if extracted:
            for tag in extracted:
                self.tags.add(tag)
        elif create:
            factory_tags = TagFactory.create_batch(random.randint(1, 3))
            for tag in factory_tags:
                self.tags.add(tag)
