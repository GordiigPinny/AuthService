from TestUtils.models import BaseTestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterTestCase(BaseTestCase):
    """
    Тесты для регистрации
    """
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + 'register/'
        self.data_201 = {
            'username': self.user.username + '11',
            'password': '123456789',
        }
        self.data_400_1 = {
            'username': self.user_username,
            'password': 'RaNd0m',
        }
        self.data_400_2 = {
            'password': 'RaNd0M',
        }

    def testRegisterOk(self):
        response = self.post_response_and_check_status(url=self.path, data=self.data_201)
        self.fields_test(response, needed_fields=['access', 'refresh'], allow_extra_fields=False)

    def testRegisterFail_ExistingUsername(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_1, expected_status_code=400)

    def testRegisterFail_WrongJson(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_2, expected_status_code=400)


class UsersListTestCase(BaseTestCase):
    """
    Тест для спиского представления юзеров
    """
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + 'users/'

    def get_token(self):
        return str(RefreshToken.for_user(self.user).access_token)

    def testGet200_OK(self):
        token = self.get_token()
        response = self.get_response_and_check_status(url=self.path, token=token)
        self.fields_test(response, needed_fields=['id', 'username', 'email', 'is_superuser', 'is_moderator'],
                         allow_extra_fields=False)
        self.list_test(response, User)
        self.assertEqual(len(response), 1, msg='More than one user in response')
        self.assertEqual(response[0]['username'], self.user_username, msg='Unknown user in response')


class UserDetailTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + f'users/{self.user.id}/'
        self.path_404 = self.url_prefix + 'users/101010101/'

    def get_token(self):
        return str(RefreshToken.for_user(self.user).access_token)

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path, token=self.get_token())
        self.fields_test(response, needed_fields=['id', 'username', 'email', 'is_superuser', 'is_moderator'],
                         allow_extra_fields=False)

    def testGet404_WrongId(self):
        _ = self.get_response_and_check_status(url=self.path_404, expected_status_code=404, token=self.get_token())

    def testDelete204_Superuser(self):
        self.user.is_superuser = True
        self.user.save()
        _ = self.delete_response_and_check_status(url=self.path, token=self.get_token())

    def testDelete204_UserHimself(self):
        _ = self.delete_response_and_check_status(url=self.path, token=self.get_token())

    def testDelete404_WrongId(self):
        _ = self.delete_response_and_check_status(url=self.path_404, expected_status_code=403, token=self.get_token())


class ChangePasswordTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + f'change_password/'
        self.data_202 = {
            'old_password': self.user_password,
            'password': '123456789',
            'password_confirm': '123456789',
        }
        self.data_400_1 = {
            'old_password': self.user_password,
        }
        self.data_400_2 = {
            'old_password': self.user_password + '1',
            'password': '123456789',
            'password_confirm': '123456789',
        }
        self.data_400_3 = {
            'old_password': self.user_password,
            'password': '123456789',
            'password_confirm': '123456',
        }
        self.data_400_4 = {
            'old_password': self.user_password,
            'password': '12345',
            'password_confirm': '12345',
        }

    def get_token(self):
        return str(RefreshToken.for_user(self.user).access_token)

    def testPatch202_OK(self):
        _ = self.patch_response_and_check_status(url=self.path, data=self.data_202, token=self.get_token())

    def testPatch400_WrongJson(self):
        _ = self.patch_response_and_check_status(url=self.path, data=self.data_400_1, expected_status_code=400,
                                                 token=self.get_token())

    def testPatch400_WrongOldPassword(self):
        _ = self.patch_response_and_check_status(url=self.path, data=self.data_400_2, expected_status_code=400,
                                                 token=self.get_token())

    def testPatch400_WrongConfirm(self):
        _ = self.patch_response_and_check_status(url=self.path, data=self.data_400_3, expected_status_code=400,
                                                 token=self.get_token())

    def testPatch400_ShortPassword(self):
        _ = self.patch_response_and_check_status(url=self.path, data=self.data_400_4, expected_status_code=400,
                                                 token=self.get_token())
