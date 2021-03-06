from django.urls import reverse
from rest_framework import status
from parameterized import parameterized
from rest_framework.test import APITestCase

from muzicbox.apps.accounts.tests.factories import UserFactory
from muzicbox.apps.audios.tests.factories import AudioFactory
from .factories import ArtistFactory


class ArtistListViewSetTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('artists:list')
        cls.user = UserFactory()
        cls.PRESENTATION_ARTISTS_COUNT = 3
        cls.PERSONAL_ARTISTS_COUNT = 1
        cls.artist_public1 = ArtistFactory()   # PRESENTATION_ARTISTS_1
        cls.artist_public2 = ArtistFactory()   # PRESENTATION_ARTISTS_2
        cls.artist_public3 = ArtistFactory()   # PRESENTATION_ARTISTS_3
        cls.artist_private = ArtistFactory()   # PERSONAL_ARTISTS_COUNT_1
        AudioFactory(is_presentation=True, artist=cls.artist_public1)
        AudioFactory(is_presentation=True, artist=cls.artist_public2)
        AudioFactory(is_presentation=True, artist=cls.artist_public3)
        AudioFactory(is_presentation=False, owner=cls.user, artist=cls.artist_private)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        AudioFactory.tear_down_files()

    @parameterized.expand([
        (True, ),
        (False, ),
    ])
    def test_list_artists(self, is_anonymous):
        """
            Checking if we can list artists for logged in and logged out users
        """
        if is_anonymous:
            artists_count = self.PRESENTATION_ARTISTS_COUNT
        else:
            artists_count = self.PERSONAL_ARTISTS_COUNT
            self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.json()['count'], artists_count)

    def test_filtering_via_slug(self):
        """
            Testing that filtering via slug works
        """
        artist_slug = self.artist_public1.slug
        self.url += '?search={}'.format(artist_slug)
        response = self.client.get(self.url)
        for artist in response.json()['results']:
            self.assertEqual(artist['slug'], artist_slug)


class ArtistDetailViewSetTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.artist_public = ArtistFactory()
        cls.artist_private = ArtistFactory()
        cls.not_presentation_but_owner_audio = AudioFactory(
            is_presentation=False, owner=cls.user,
            artist=cls.artist_private,
        )
        cls.not_presentation_not_owner_audio = AudioFactory(is_presentation=False)
        cls.presentation_audio = AudioFactory(is_presentation=True, artist=cls.artist_public)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        AudioFactory.tear_down_files()

    @parameterized.expand([
        (True, ),
        (False, ),
    ])
    def test_detail_artist_success(self, is_anonymous):
        """
            Checking that we can get detailed info about artist for logged in (user is owner in related audios)
            and logged out users (artist's audios are in presentation mode)
        """
        if is_anonymous:
            artist_slug = self.presentation_audio.artist.slug
        else:
            self.client.force_authenticate(self.user)
            artist_slug = self.not_presentation_but_owner_audio.artist.slug
        url = reverse('artists:detail', kwargs={'slug': str(artist_slug)})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.json()['slug'], artist_slug)

    @parameterized.expand([
        (True, ),
        (False, ),
    ])
    def test_detail_artist_failure(self, is_anonymous):
        """
            Checking that we can't get detailed info about artist for logged in (user isn't owner in related audios)
            and logged out users (artist's audios aren't in presentation mode)
        """
        if not is_anonymous:
            self.client.force_authenticate(self.user)
        artist_slug = self.not_presentation_not_owner_audio.artist.slug
        url = reverse('artists:detail', kwargs={'slug': str(artist_slug)})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
