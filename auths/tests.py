from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

class SignupViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('signup')  # make sure this matches your urls.py name
        self.data = {
            "first_name":"Nahid Rahman",
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "testpassword123"
        }

    @patch('api.views.sent_email_to.delay')  # Mock Celery task to avoid sending real emails

    def test_user_signup_success(self, mock_send_email):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("success", response.data)
        self.assertTrue(response.data["success"])
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["email"], self.data["email"])

        user = User.objects.get(email=self.data["email"])
        test_user2 = User.objects.get(username=self.data['username'])
        self.assertIsNotNone(user)
        self.assertIsNotNone(test_user2)
        self.assertRegex(user.otp, r"^\d{6}$")

        mock_send_email.assert_called_once()


    def test_signup_invalid_data(self):
        invalid_data = {
            "email": "not-an-email",
            "password": ""
        }
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)



class VerifyEmailSignupTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            otp="123456",
            is_email_varified=False
        )
        self.url = reverse('verify_email_signup', kwargs={"username": self.user.username})

    def test_verify_email_success(self):
        data = {"otp": "123456"}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "verifyed successfully")

        # Refresh user and check updates
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_varified)
        self.assertNotEqual(self.user.otp, "123456")  # OTP should be regenerated

    def test_verify_email_wrong_otp(self):
        data = {"otp": "999999"}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "wrong varification code!")

    def test_verify_email_user_not_found(self):
        url = reverse('verify_email_signup', kwargs={"username": "unknown"})
        data = {"otp": "123456"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "user not found")

    def test_verify_email_invalid_payload(self):
        data = {}  # no otp field
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "validation errors")
        self.assertIn("errors", response.data)




class LoginViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('login')  # Must match your urls.py name

        # Verified user
        self.verified_user = User.objects.create_user(
            username="verified_user",
            email="verified@example.com",
            password="strongpassword123",
            is_email_varified=True
        )

        # Unverified user
        self.unverified_user = User.objects.create_user(
            username="unverified_user",
            email="unverified@example.com",
            password="strongpassword123",
            is_email_varified=False,
            otp="654321"
        )

    def test_login_success_verified_user(self):     
        data = {"username": "verified_user", "password": "strongpassword123"}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["message"], "login successfull!")

    @patch('api.views.sent_email_to.delay')  
    def test_login_unverified_user_sends_otp(self, mock_send_email):
        data = {"username": "unverified_user", "password": "strongpassword123"}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])
        self.assertIn("We sent an otp to your email", response.data["message"])

        # Ensure email was sent
        mock_send_email.assert_called_once()

        # Verify OTP got updated
        self.unverified_user.refresh_from_db()
        self.assertRegex(self.unverified_user.otp, r"^\d{6}$")

    def test_login_invalid_credentials(self):
        data = {"username": "verified_user", "password": "wrongpassword"}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "username or password Invalid!")

    def test_login_invalid_payload(self):
        data = {"username": ""}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "validation errors")
        self.assertIn("errors", response.data)



from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken


class ChangePasswordTest(APITestCase):
    def setUp(self):
        # Create and authenticate a test user
        self.user = User.objects.create_user(
            username="secure_user",
            email="secure@example.com",
            password="OldPassword123!"
        )
        self.url = reverse('change_password')  # Must match urls.py name

        # Generate JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Attach JWT to headers
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_change_password_success(self):
        data = {
            "old_password": "OldPassword123!",
            "new_password": "NewSecurePass@456"
        }
        old_hash = self.user.password

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password changed successfully!")

        self.user.refresh_from_db()
        self.assertNotEqual(self.user.password, old_hash)

        self.assertTrue(self.user.check_password("NewSecurePass@456"))

    def test_wrong_old_password(self):
        data = {
            "old_password": "WrongOldPass",
            "new_password": "AnotherPass789"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "worng old password!")

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OldPassword123!"))

    def test_validation_error(self):
        data = {"old_password": ""}  # missing new_password
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "validation errors")
        self.assertIn("errors", response.data)

    def test_unauthenticated_user_cannot_access(self):
        client = APIClient()  # new unauthenticated client
        data = {
            "old_password": "OldPassword123!",
            "new_password": "HackedPass000"
        }
        response = client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_password_hash_security(self):
        data = {
            "old_password": "OldPassword123!",
            "new_password": "UltraStrong$789"
        }
        self.client.post(self.url, data, format='json')
        self.user.refresh_from_db()

        self.assertFalse(self.user.password == "UltraStrong$789")
        self.assertTrue(self.user.password.startswith("pbkdf2_")) 
        self.assertTrue(check_password("UltraStrong$789", self.user.password))



class ForgetPasswordViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('forget_password')  # must match your urls.py name
        self.user = User.objects.create_user(
            username="reset_user",
            email="reset@example.com",
            password="OldPass123!"
        )

    @patch('api.views.sent_email_to.delay') 
    def test_forget_password_success(self, mock_send_email):

        data = {"username": "reset_user"}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "we sent a otp in your email! verify the otp first")

        self.user.refresh_from_db()
        self.assertRegex(self.user.otp, r"^\d{6}$")

        mock_send_email.assert_called_once_with(
            email=self.user.email,
            text=f"your otp is {self.user.otp}",
            subject='Verification'
        )

        self.assertIn("errors", response.data)
        self.assertEqual(response.data["errors"], {})

    def test_forget_password_user_not_found(self):
        data = {"username": "unknown_user"}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "user not found!")

    def test_forget_password_invalid_payload(self):
        data = {}  
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "validation errors")
        self.assertIn("errors", response.data)

    @patch('api.views.sent_email_to.delay')
    def test_forget_password_otp_security(self, mock_send_email):
        data = {"username": "reset_user"}
        response1 = self.client.post(self.url, data, format='json')
        self.user.refresh_from_db()
        first_otp = self.user.otp
        response2 = self.client.post(self.url, data, format='json')
        self.user.refresh_from_db()
        second_otp = self.user.otp

        self.assertNotEqual(first_otp, second_otp)
        self.assertRegex(second_otp, r"^\d{6}$")
        self.assertEqual(mock_send_email.call_count, 2)



class VerifyUserForgetPasswordTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="recover_user",
            email="recover@example.com",
            password="OldPass123!",
            otp="123456"
        )
        self.url = reverse('verify_user_forget_password', kwargs={'username': self.user.username})

    def test_verify_user_success(self):
        data = {"otp": "123456"}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "verified successfull!")

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertRegex(response.data["access"], r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$")
        self.assertRegex(response.data["refresh"], r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$")

        self.user.refresh_from_db()
        self.assertNotEqual(self.user.otp, "123456")
        self.assertRegex(self.user.otp, r"^\d{6}$")

    def test_verify_user_wrong_otp(self):
        data = {"otp": "999999"}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "wrong varification code!")

        self.user.refresh_from_db()
        self.assertEqual(self.user.otp, "123456")

    def test_verify_user_not_found(self):
        url = reverse('verify_user_forget_password', kwargs={'username': 'ghost_user'})
        data = {"otp": "123456"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "User not found!")

    def test_verify_user_invalid_payload(self):
        data = {}  # No OTP
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "validation errors")
        self.assertIn("errors", response.data)

    def test_jwt_tokens_validity(self):
        data = {"otp": "123456"}
        response = self.client.post(self.url, data, format='json')

        refresh_token = RefreshToken(response.data["refresh"])
        self.assertEqual(refresh_token.payload["user_id"], str(self.user.id))



class ResetPasswordViewTest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="reset_user",
            email="resetuser@example.com",
            password="OldPass123!"
        )

        # URL must match your urls.py path name
        self.url = reverse('reset_password')

        # Generate JWT for authenticated request
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Attach JWT to default client headers
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_reset_password_success(self):
        data = {"new_password": "NewStrongPass@123"}

        old_hash = self.user.password
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "password reset successfully")

        self.user.refresh_from_db()
        self.assertNotEqual(self.user.password, old_hash)
        self.assertTrue(check_password("NewStrongPass@123", self.user.password))

    def test_reset_password_validation_error(self):
        data = {}  # Missing password
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "validation error!")
        self.assertIn("errors", response.data)

    def test_reset_password_unauthenticated(self):
        client = APIClient()  # No auth token
        data = {"new_password": "ShouldFailPass@1"}
        response = client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_password_security_hash(self):
        data = {"new_password": "AnotherSafePass$456"}
        self.client.post(self.url, data, format='json')
        self.user.refresh_from_db()
        self.assertFalse(self.user.password == "AnotherSafePass$456")
        self.assertTrue(self.user.password.startswith("pbkdf2_"))
        self.assertTrue(check_password("AnotherSafePass$456", self.user.password))
