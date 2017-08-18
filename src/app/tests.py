# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from django_downloadview.test import temporary_media_root

import jpype
# Create your tests here.

class IndexViewsTestCase(TestCase):

    def test_index(self):
        resp = self.client.get('/app/',follow=True,secure=True)
        self.assertEqual(resp.status_code,200)      #Status OK
        self.assertEqual(resp.redirect_chain,[])    # No redirection
        self.assertIn("app/index.html",(i.name for i in resp.templates))    #list of templates
        self.assertEqual(resp.resolver_match.func.__name__,"index")     #View function called

class AboutViewsTestCase(TestCase):

    def test_about(self):
        resp = self.client.get('/app/about/',follow=True,secure=True)
        self.assertEqual(resp.status_code,200)      #Status OK
        self.assertEqual(resp.redirect_chain,[])    # No redirection
        self.assertIn("app/about.html",(i.name for i in resp.templates))    #list of templates
        self.assertEqual(resp.resolver_match.func.__name__,"about")     #View function called

class LoginViewsTestCase(TestCase):

    def initialise(self):
        self.credentials = {'username':'testuser','password':'testpass' }
        user = User.objects.create_user(**self.credentials)     # Staff
        user.is_staff = True
        user.is_active = True
        user.save()
        self.credentials2 = {'username':'testuser2','password':'testpass2' }
        user2 = User.objects.create_user(**self.credentials2)   # Non-staff
        user2.is_staff = False
        user2.is_active = True
        user2.save()
        self.credentials3 = {'username':'testuser3','password':'testpass3' }
        user3 = User.objects.create_user(**self.credentials3) # Inactive
        user3.is_staff = True
        user3.is_active = False
        user3.save()

    def test_login(self):
        resp = self.client.get('/app/login/',follow=True,secure=True)
        self.assertEqual(resp.status_code,200)      #Status OK
        self.assertEqual(resp.redirect_chain,[])    # No redirection
        self.assertIn("app/login.html",(i.name for i in resp.templates))    #list of templates
        self.assertEqual(resp.resolver_match.func.__name__,"loginuser")     #View function called

    def test_postlogin(self):
        self.initialise()
        resp = self.client.post('/app/login/',self.credentials,follow=True,secure=True)
        self.assertEqual(resp.status_code,200)
        self.assertNotEqual(resp.redirect_chain,[])
        self.assertIn(settings.LOGIN_REDIRECT_URL, (i[0] for i in resp.redirect_chain))
        self.assertTrue(resp.context['user'].is_active)
        self.assertTrue(resp.context['user'].is_staff)
        self.assertFalse(resp.context['user'].is_superuser)
        self.client.get('/app/logout/')

        resp2 = self.client.post('/app/login/',self.credentials2,follow=True,secure=True)
        self.assertEqual(resp2.status_code,403)
        self.assertEqual(resp2.redirect_chain,[])
        self.assertFalse(resp2.context['user'].is_active)
        self.assertFalse(resp2.context['user'].is_staff)
        self.assertFalse(resp2.context['user'].is_superuser)
        self.assertTrue('invalid' in resp2.context)
        self.assertIn("app/login.html",(i.name for i in resp2.templates))
        self.client.get('/app/logout/')

        resp3 = self.client.post('/app/login/',self.credentials3,follow=True,secure=True)
        self.assertEqual(resp3.status_code,403)
        self.assertEqual(resp3.redirect_chain,[])
        self.assertFalse(resp3.context['user'].is_active)
        self.assertFalse(resp3.context['user'].is_staff)
        self.assertFalse(resp3.context['user'].is_superuser)
        self.assertTrue('invalid' in resp3.context)
        self.assertIn("app/login.html",(i.name for i in resp3.templates))
        self.client.get('/app/logout/')

class RegisterViewsTestCase(TestCase):

    def initialise(self):
        self.username = "testuser4"
        self.password ="testpass4"
        self.data = {"first_name": "test","last_name" : "test" ,
            "email" : "test@spdx.org","username":self.username,
            "password":self.password,"confirm_password":self.password,"organisation":"spdx"}
            
    def test_register(self):
        resp = self.client.get('/app/register/',follow=True,secure=True)
        self.assertEqual(resp.status_code,200)
        self.assertTrue('user_form' in resp.context)
        self.assertTrue('profile_form' in resp.context)
        self.assertEqual(resp.redirect_chain,[])    # No redirection
        self.assertIn("app/register.html",(i.name for i in resp.templates))    #list of templates
        self.assertEqual(resp.resolver_match.func.__name__,"register")     #View function called

    def test_formregister(self):
        self.initialise()
        resp = self.client.post('/app/register/',self.data,follow=True,secure=True)
        self.assertEqual(resp.status_code,200)
        self.assertNotEqual(resp.redirect_chain,[])
        self.assertIn(settings.REGISTER_REDIRECT_UTL, (i[0] for i in resp.redirect_chain))
        loginresp = self.client.post('/app/login/',{'username':self.username,'password':self.password},follow=True,secure=True)
        self.assertEqual(loginresp.status_code,200)
        self.assertTrue(loginresp.context['user'].is_active)
        self.assertTrue(loginresp.context['user'].is_staff)
        self.assertFalse(loginresp.context['user'].is_superuser)
        self.assertIn(settings.LOGIN_REDIRECT_URL, (i[0] for i in loginresp.redirect_chain))
        self.client.get('/app/logout/')

class ValidateViewsTestCase(TestCase):

    def test_validate(self):
        resp = self.client.get('/app/validate/',follow=True,secure=True)
        self.assertNotEqual(resp.redirect_chain,[])
        self.assertIn(settings.LOGIN_URL, (i[0] for i in resp.redirect_chain))
        self.assertEqual(resp.status_code,200)
        self.client.force_login(User.objects.get_or_create(username='validatetestuser')[0])
        resp3 = self.client.get('/app/validate/',follow=True,secure=True)
        self.assertEqual(resp3.status_code,200)
        self.assertEqual(resp3.redirect_chain,[])    # No redirection
        self.assertIn("app/validate.html",(i.name for i in resp3.templates))    #list of templates
        self.assertEqual(resp3.resolver_match.func.__name__,"validate")     #View function called
        self.client.logout()
        
    def test_validate_post_without_login(self):
        self.tv_file = open("examples/SPDXTagExample-v2.0.spdx")
        resp = self.client.post('/app/validate/',{'file' : self.tv_file},follow=True,secure=True)
        self.assertNotEqual(resp.redirect_chain,[])
        self.assertIn(settings.LOGIN_URL, (i[0] for i in resp.redirect_chain))
        self.assertEqual(resp.status_code,200)

    def test_validate_post_without_file(self):
        self.client.force_login(User.objects.get_or_create(username='validatetestuser')[0])
        resp = self.client.post('/app/validate/',{},follow=True,secure=True)
        self.assertEqual(resp.status_code,404)
        self.assertTrue('error' in resp.context)
        self.assertEqual(resp.redirect_chain,[])
        self.client.logout()

    # def test_upload_tv(self):
    #     self.client.force_login(User.objects.get_or_create(username='validatetestuser')[0])
    #     self.tv_file = open("examples/SPDXTagExample-v2.0.spdx")
    #     resp = self.client.post('/app/validate/',{'file' : self.tv_file},follow=True,secure=True)
    #     self.assertEqual(resp.content,"This SPDX Document is valid.")
    #     self.assertEqual(resp.status_code,200)
    #     self.client.logout()

    # def test_upload_rdf(self):
    #     self.client.force_login(User.objects.get_or_create(username='validatetestuser')[0])
    #     self.rdf_file = open("examples/SPDXRdfExample-v2.0.rdf")
    #     resp = self.client.post('/app/validate/',{'file' : self.rdf_file},follow=True,secure=True)
    #     self.assertEqual(resp.content,"This SPDX Document is valid.")
    #     self.assertEqual(resp.status_code,200)
    #     self.client.logout()
    
    # def test_upload_other(self):
    #     self.client.force_login(User.objects.get_or_create(username='validatetestuser')[0])
    #     self.other_file = open("examples/Other.txt")
    #     resp = self.client.post('/app/validate/',{'file' : self.other_file},follow=True,secure=True)
    #     self.assertTrue(resp.status_code,400)
    #     self.assertTrue('error' in resp.context)
    #     self.client.logout()

    # def test_upload_inv_tv(self):
    #     self.client.force_login(User.objects.get_or_create(username='validatetestuser')[0])
    #     self.invalid_tv_file = open("examples/SPDXTagExample-v2.0_invalid.spdx")
    #     resp = self.client.post('/app/validate/',{'file' : self.invalid_tv_file},follow=True)
    #     self.assertTrue(resp.status_code,400)
    #     self.assertTrue('error' in resp.context)
    #     self.client.logout()

    # def test_upload_inv_rdf(self):
    #     self.client.force_login(User.objects.get_or_create(username='validatetestuser')[0])
    #     self.invalid_rdf_file = open("examples/SPDXRdfExample-v2.0_invalid.rdf")
    #     resp = self.client.post('/app/validate/',{'file' : self.invalid_rdf_file},follow=True)
    #     self.assertTrue(resp.status_code,400)
    #     self.assertTrue('error' in resp.context)
    #     self.client.logout()


class CompareViewsTestCase(TestCase):
    def initialise(self):
        self.rdf_file = open("examples/SPDXRdfExample-v2.0.rdf")
        self.rdf_file2 = open("examples/SPDXRdfExample2-v2.0.rdf")
        self.tv_file = open("examples/SPDXTagExample-v2.0.spdx")

    def test_compare(self):
        resp = self.client.get('/app/compare/',follow=True,secure=True)
        self.assertNotEqual(resp.redirect_chain,[])
        self.assertIn(settings.LOGIN_URL, (i[0] for i in resp.redirect_chain))
        self.assertEqual(resp.status_code,200)
        self.client.force_login(User.objects.get_or_create(username='comparetestuser')[0])
        resp3 = self.client.get('/app/compare/',follow=True,secure=True)
        self.assertEqual(resp3.status_code,200)
        self.assertEqual(resp3.redirect_chain,[])    # No redirection
        self.assertIn("app/compare.html",(i.name for i in resp3.templates))    #list of templates
        self.assertEqual(resp3.resolver_match.func.__name__,"compare")     #View function called
        self.client.logout()

    def test_compare_post_without_login(self):
        self.initialise()
        resp = self.client.post('/app/compare/',{'compare':'compare','nofile': "2" ,'rfilename': "comparetest",'file1' : self.rdf_file, 'file2' : self.rdf_file2},follow=True,secure=True)
        self.assertNotEqual(resp.redirect_chain,[])
        self.assertIn(settings.LOGIN_URL, (i[0] for i in resp.redirect_chain))
        self.assertEqual(resp.status_code,200)

    def test_compare_post_without_file(self):
        self.initialise()
        self.client.force_login(User.objects.get_or_create(username='comparetestuser')[0])
        resp = self.client.post('/app/validate/',{'compare':'compare','nofile': "2" ,'rfilename': "comparetest"},follow=True,secure=True)
        self.assertEqual(resp.status_code,404)
        self.assertTrue('error' in resp.context)
        self.assertEqual(resp.redirect_chain,[])
        self.client.logout()

    def test_compare_two_rdf(self):
        self.initialise()
        self.client.force_login(User.objects.get_or_create(username='comparetestuser')[0])
        resp = self.client.post('/app/compare/',{'compare':'compare','nofile': "2" ,'rfilename': "comparetest",'file1' : self.rdf_file, 'file2' : self.rdf_file2},follow=True,secure=True)
        print resp.context["error"]
        self.assertEqual(resp.status_code,200)
        self.client.logout()

    
    
# class ConvertViewsTestCase(TestCase):
#     def setUp(self):
#         self.rdf_file = open("examples/SPDXRdfExample-v2.0.rdf")
#         self.tv_file = open("examples/SPDXTagExample-v2.0.spdx")
#         self.xls_file = open("examples/SPDXSpreadsheetExample-2.0.xls")

#     def test_convert(self):
#         resp = self.client.get('/app/convert/')
#         self.assertEqual(resp.status_code,302) # Not Logged in

#     def test_convert_tagtordf(self):
#         global_media_root = settings.MEDIA_ROOT
#         with temporary_media_root():
#             self.assertNotEqual(global_media_root,settings.MEDIA_ROOT)
#         self.assertEqual(global_media_root,settings.MEDIA_ROOT)
#         resp = self.client.post('/app/convert/',{'cfilename': "test" ,'cfileformat': ".rdf",'from_format' : "Tag", 'to_format' : "RDF", 'file' : self.tv_file},follow=True)
#         self.assertEqual(resp.status_code,200)  #Not logged in and  Because test download file do not exist

#     # def test_convert_tagtoxlsx(self):
#     #     resp = self.client.post('/app/convert/',{'cfilename': "test" ,'cfileformat': ".xlsx",'from_format' : "Tag", 'to_format' : "Spreadsheet", 'file' : self.tv_file},follow=True)
#     #     self.assertEqual(resp.status_code,404)  #Because test download file do not exist

#     # def test_convert_rdftotag(self):
#     #     resp = self.client.post('/app/convert/',{'cfilename': "test" ,'cfileformat': ".spdx",'from_format' : "RDF", 'to_format' : "Tag", 'file' : self.rdf_file},follow=True)
#     #     self.assertEqual(resp.status_code,404)  #Because test download file do not exist

#     # def test_convert_rdftoxlsx(self):
#     #     resp = self.client.post('/app/convert/',{'cfilename': "test2" ,'cfileformat': ".xlsx",'from_format' : "RDF", 'to_format' : "Spreadsheet", 'file' : self.rdf_file},follow=True)
#     #     self.assertEqual(resp.status_code,404)  #Because test download file do not exist

#     # def test_convert_rdftohtml(self):
#     #     resp = self.client.post('/app/convert/',{'cfilename': "test" ,'cfileformat': ".html",'from_format' : "RDF", 'to_format' : "Html", 'file' : self.rdf_file},follow=True)
#     #     self.assertEqual(resp.status_code,404)  #Because test download file do not exist

#     def test_convert_xlsxtotag(self):
#         resp = self.client.post('/app/convert/',{'cfilename': "test2" ,'cfileformat': ".spdx",'from_format' : "Spreadsheet", 'to_format' : "Tag", 'file' : self.xls_file},follow=True)
#         self.assertEqual(resp.status_code,200)  #Not logged in and Because test download file do not exist

#     def test_convert_xlsxtordf(self):
#         resp = self.client.post('/app/convert/',{'cfilename': "test2" ,'cfileformat': ".rdf",'from_format' : "Spreadsheet", 'to_format' : "RDF", 'file' : self.xls_file},follow=True)
#         self.assertEqual(resp.status_code,200)  #Not logged in and Because test download file do not exist

# class SearchViewsTestCase(TestCase):
#     def test_search(self):
#         resp = self.client.get('/app/search/')
#         self.assertEqual(resp.status_code,404) # Does not exist



# class LogoutViewsTestCase(TestCase):
#     def test_logout(self):
#         resp = self.client.get('/app/logout/')
#         # For Url Redirection to index after logout
#         self.assertEqual(resp.status_code,302)

# class RootViewsTestCase(TestCase):
#     def test_logout(self):
#         resp = self.client.get('/')
#         # For View Redirection to index
#         self.assertEqual(resp.status_code,302)
