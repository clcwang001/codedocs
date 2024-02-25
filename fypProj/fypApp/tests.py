import time
from django.test import TestCase, Client
from django.urls import reverse
from .models import OrganisationDetails, Users, Activities, UserHasActivities, UserHasOrganisation

class loginTest(TestCase): #basic login cases 
    def setUp(self):
        self.user = Users.objects.create_user(username='test', password='testpw123', email="test@gmail.com",userType='0')
        self.client = Client() #django client

    def test_homePage(self): #checks homepage loads and renders correctly 
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Loginpage.html')
        self.assertContains(response, "Sign In")
        self.assertContains(response, "SignUp")
        self.assertNotContains(response, "Logout")

    def test_validLogin(self): # Test login view, correct login
        response = self.client.post(reverse('login'), {'username': 'test', 'password': 'testpw123'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Loginpage.html')
        self.assertContains(response, 'test')
        self.assertContains(response, 'Welcome, test!')
        self.assertContains(response, "Logout")

    def test_invalidLogin(self): # Test login view, invalid login
        response = self.client.post(reverse('login'), {'username': 'testx', 'password': 'testpw123'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Loginpage.html')
        self.assertNotContains(response, 'testx')
        self.assertNotContains(response, 'Welcome, testx!')
        self.assertContains(response, "Sign In")
        self.assertContains(response, "SignUp")
        self.assertNotContains(response, "Logout")

class loginTestOG(TestCase): #organisational login cases 
    def setUp(self):
        self.user = Users.objects.create_user(username='test', password='testpw123', email="test@gmail.com",userType='2', isOrganisation='True')
        self.client = Client() #django client

    def test_homePage(self): #checks homepage loads and renders correctly 
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Loginpage.html')


    def test_validLogin(self): # Test login view, correct login
        response = self.client.post(reverse('login'), {'username': 'test', 'password': 'testpw123'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Loginpage.html')
        self.assertContains(response, 'test')
        self.assertContains(response, 'Welcome, test!')
        self.assertContains(response, "User's View")
        self.assertContains(response, "Organisation Details")
        self.assertContains(response, "Events")

class loginTestStandard(TestCase): #standard login cases 
    def setUp(self):
        self.user = Users.objects.create_user(username='test', password='testpw123', email="test@gmail.com",userType='2', isOrganisation='False')
        self.client = Client() #django client

    def test_homePage(self): #checks homepage loads and renders correctly 
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Loginpage.html')


    def test_validLogin(self): # Test login view, correct login
        response = self.client.post(reverse('login'), {'username': 'test', 'password': 'testpw123'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Loginpage.html')
        self.assertContains(response, 'test')
        self.assertContains(response, 'Welcome, test!')
        self.assertNotContains(response, "User's View")
        self.assertNotContains(response, "Organisation Details")
        self.assertContains(response, "Events")
        self.assertContains(response, "Organisations")


class loginTestAdmin(TestCase): #admin login cases 
    def setUp(self):
        self.user = Users.objects.create_user(username='test', password='testpw123', email="test@gmail.com",userType='1')
        self.client = Client() #django client

    def test_homePage(self): #checks homepage loads and renders correctly 
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Loginpage.html')


    def test_validLogin(self): # Test login view, correct login
        response = self.client.post(reverse('login'), {'username': 'test', 'password': 'testpw123'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Loginpage.html')
        self.assertContains(response, 'test')
        self.assertContains(response, 'Welcome, test!')
        self.assertContains(response, 'Review Charites')
        self.assertNotContains(response, "User's View")
        self.assertNotContains(response, "Organisation Details")



