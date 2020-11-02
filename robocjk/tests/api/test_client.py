# -*- coding: utf-8 -*-

from django.test import (
    Client, override_settings, RequestFactory, SimpleTestCase, TestCase,
)


class ClientTestCase(TestCase):

#     def setUp(self):
#         self.anonymous_user = AnonymousUser()
#
#         self.authenticated_user = User.objects.create_user(
#             'authenticated-user',
#             'authenticated@django-maintenance-mode.test',
#             'test')
#         self.authenticated_user.save()
#
#         self.staff_user = User.objects.create_user(
#             'staff-user',
#             'staff@django-maintenance-mode.test',
#             'test')
#         self.staff_user.is_staff = True
#         self.staff_user.save()
#
#         self.superuser = User.objects.create_user(
#             'superuser',
#             'superuser@django-maintenance-mode.test',
#             'test')
#         self.superuser.is_superuser = True
#         self.superuser.save()
#
#         self.client = Client()
#         self.request_factory = RequestFactory()
#
#     def tearDown(self):
#         pass
#
#     def __get_anonymous_user_request(self, url):
#         request = self.request_factory.get(url)
#         request.user = self.anonymous_user
#         return request
#
#     def __get_authenticated_user_request(self, url):
#         request = self.request_factory.get(url)
#         request.user = self.authenticated_user
#         return request
#
#     def __get_staff_user_request(self, url):
#         request = self.request_factory.get(url)
#         request.user = self.staff_user
#         return request
#
#     def __get_superuser_request(self, url):
#         request = self.request_factory.get(url)
#         request.user = self.superuser
#         return request
#
#     def __login_staff_user(self):
#         self.client.login(username='staff-user', password='test')
#
#     def __login_superuser(self):
#         self.client.login(username='superuser', password='test')
#
#     def __logout(self):
#         self.client.logout()
#
    def test(self):
        # TODO
        pass

