from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class UsuarioTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_registro(self):
        response = self.client.post(reverse('registro'), {
            'username': 'nuevo',
            'email': 'nuevo@test.com',
            'password1': 'Testpass123',
            'password2': 'Testpass123',
        })
        self.assertEqual(response.status_code, 302)  # Redirige después de crear

    def test_login_logout(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('historial'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.get(reverse('historial'))
        self.assertEqual(response.status_code, 302)  # Redirige porque no está logueado

    def test_favorita_duplicada(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('favoritas'), {'ciudad': 'Madrid'})
        self.assertEqual(response.status_code, 302)
        response2 = self.client.post(reverse('favoritas'), {'ciudad': 'Madrid'})
        self.assertEqual(response2.status_code, 302)


from django.test import TestCase

# Create your tests here.
