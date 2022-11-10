from django.test import TestCase
from django.test import Client, RequestFactory
from django.urls import reverse

from .models import *
from django.contrib.auth import authenticate, login, logout
from .views import *


class NewsBagTestClass(TestCase):

    def test_article_model(self):
        article = Article.objects.create(title="test", content="test", image_path="www.google.com", source_name="test",
                                         source_link="www.google.com")
        self.assertIsNotNone(article)

    def test_library_model(self):
        user = User.objects.create_user(username="test", password="case123A")
        self.assertIsNotNone(user)
        library = Library.objects.create(user=user, name="test")
        self.assertIsNotNone(library)

    def test_libart_model(self):
        user = User.objects.create_user(username="test", password="case123A")
        self.assertIsNotNone(user)
        library = Library.objects.create(user=user, name="test")
        self.assertIsNotNone(library)
        article = Article.objects.create(title="test", content="test", image_path="www.google.com", source_name="test",
                                         source_link="www.google.com")
        self.assertIsNotNone(article)
        libart = LibArt.objects.create(library=library, article=article)
        self.assertIsNotNone(libart)
        self.assertEqual(article.links, 1)
        self.assertEqual(library.articles, 1)

    def test_landing_view(self):
        response = Client().get("/")
        self.assertEqual(response.status_code, 200)

    def test_landing_post_view(self):
        client = Client()
        user = User.objects.create_user(username="test", password="case123A")
        user.save()
        client.force_login(user=user)
        library = Library.objects.create(user=user, name="test")
        library.save()
        args = {'cid': library.id,
                'title': 'test',
                'content': 'test',
                'image_path': 'www.google.com',
                'source_name': 'test',
                'source_link': 'www.google.com'}
        response = client.post(reverse('newsbag_app:landing', kwargs={'category': 'food'}), args)
        self.assertEqual(response.status_code, 200)

    def test_signup_view(self):
        client = Client()
        response = client.post(reverse('newsbag_app:signup', kwargs={'id': 0}),
                               {'username': 'test', 'password1': 'case123A'})
        self.assertEqual(response.status_code, 200)

        data = {'username': 'test',
                'first_name': 'testfirst',
                'last_name': 'testlast',
                'email': 'test@gmail.com',
                'password1': 'case123A',
                'password2': 'case123A'}
        response = client.post(reverse('newsbag_app:signup', kwargs={'id': 0}), data)
        self.assertEqual(response.status_code, 302)

    def test_login_logout_view(self):
        client = Client()
        user = User.objects.create_user(username="test", password="case123A")
        user.save()
        response = client.post(reverse('newsbag_app:login', kwargs={'id': 0}),
                               {'username': 'test', 'password': 'case123A'})
        self.assertEqual(response.status_code, 302)
        response2 = client.post(reverse('newsbag_app:logout', kwargs={'id': 0}))
        self.assertEqual(response2.status_code, 302)
        response = client.post(reverse('newsbag_app:login', kwargs={'id': 0}),
                               {'username': 'test', 'password': 'incorrect'})
        self.assertEqual(response.status_code, 200)

    def test_collection_view1(self):
        client = Client()
        user = User.objects.create_user(username="test", password="case123A")
        user.save()
        client.force_login(user=user)
        library = Library.objects.create(user=user, name="test")
        article1 = Article.objects.create(title="test", content="test", image_path="www.google.com", source_name="test",
                                          source_link="www.google.com")
        libart = LibArt.objects.create(library=library, article=article1)
        response = client.post(reverse('newsbag_app:collection', kwargs={'id': 0}), {'cid': library.id})
        self.assertEqual(response.status_code, 200)

    def test_collection_view2(self):
        client = Client()
        user = User.objects.create_user(username="test", password="case123A")
        user.save()
        client.force_login(user=user)
        library = Library.objects.create(user=user, name="test")
        article1 = Article.objects.create(title="test", content="test", image_path="www.google.com", source_name="test",
                                          source_link="www.google.com")
        library1 = Library.objects.create(user=user, name="test1")
        libart1 = LibArt.objects.create(library=library, article=article1)
        libart2 = LibArt.objects.create(library=library1, article=article1)
        response = client.post(reverse('newsbag_app:collection', kwargs={'id': 0}), {'cid': library.id})
        self.assertEqual(response.status_code, 200)

    def test_addNewLibrary_view(self):
        client = Client()
        user = User.objects.create_user(username="test", password="case123A")
        user.save()
        client.force_login(user=user)
        response = client.post(reverse('newsbag_app:create'), {'name': ''})
        self.assertEqual(response.status_code, 200)

        data = {'name': 'test'}
        response = client.post(reverse('newsbag_app:create'), data)
        self.assertEqual(response.status_code, 302)

    def test_visitLibrary_view(self):
        client = Client()
        user = User.objects.create_user(username="test", password="case123A")
        user.save()
        client.force_login(user=user)
        library = Library.objects.create(user=user, name="test")
        article1 = Article.objects.create(title="test", content="test", image_path="www.google.com", source_name="test",
                                          source_link="www.google.com")
        libart = LibArt.objects.create(library=library, article=article1)
        response1 = client.get(reverse('newsbag_app:library', kwargs={'id': library.id}))
        self.assertEqual(response1.status_code, 200)
        response2 = client.post(reverse('newsbag_app:library', kwargs={'id': library.id}), {'cid': article1.id})
        self.assertEqual(response2.status_code, 200)

    def test_compare_view1(self):
        client = Client()
        user = User.objects.create_user(username="test", password="case123A")
        user.save()
        client.force_login(user=user)
        library = Library.objects.create(user=user, name="test")
        article1 = Article.objects.create(title="test",
                                          content="This is a sentence about Maths. Arrays start at 0",
                                          image_path="www.google.com",
                                          source_name="test",
                                          source_link="www.google.com")
        article2 = Article.objects.create(title="test",
                                          content="Don't stop the bass. Don't stop the music.",
                                          image_path="www.google.com",
                                          source_name="test",
                                          source_link="www.google.com")
        libart1 = LibArt.objects.create(library=library, article=article1)
        libart2 = LibArt.objects.create(library=library, article=article2)
        response2 = client.post(reverse('newsbag_app:compare', kwargs={'lid': library.id, 'aid': article1.id}))
        self.assertEqual(response2.status_code, 200)

    def test_compare_view2(self):
        client = Client()
        user = User.objects.create_user(username="test", password="case123A")
        user.save()
        client.force_login(user=user)
        library = Library.objects.create(user=user, name="test")
        article1 = Article.objects.create(title="test",
                                          content="This is a sentence about Maths. Arrays start at 0",
                                          image_path="www.google.com",
                                          source_name="test",
                                          source_link="www.google.com")
        article2 = Article.objects.create(title="test",
                                          content="Don't stop the bass. Don't stop the music.",
                                          image_path="www.google.com",
                                          source_name="test",
                                          source_link="www.google.com")
        article3 = Article.objects.create(title="test",
                                          content="Math and Science go hand in hand. For example, Physics.",
                                          image_path="www.google.com",
                                          source_name="test",
                                          source_link="www.google.com")
        libart1 = LibArt.objects.create(library=library, article=article1)
        libart2 = LibArt.objects.create(library=library, article=article2)
        libart3 = LibArt.objects.create(library=library, article=article3)
        response2 = client.post(reverse('newsbag_app:compare', kwargs={'lid': library.id, 'aid': article1.id}))
        self.assertEqual(response2.status_code, 200)

