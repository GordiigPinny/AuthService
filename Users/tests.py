from TestUtils.models import BaseTestCase
from django.contrib.auth.models import User, Group
from rest_framework_jwt.settings import api_settings


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
        self.fields_test(response, needed_fields=['token', 'user'], allow_extra_fields=False)

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
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(self.user)
        return jwt_encode_handler(payload)

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
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(self.user)
        return jwt_encode_handler(payload)

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path, token=self.get_token())
        self.fields_test(response, needed_fields=['id', 'username', 'email', 'is_superuser', 'is_moderator'],
                         allow_extra_fields=False)

    def testGet404_WrongId(self):
        _ = self.get_response_and_check_status(url=self.path_404, expected_status_code=404, token=self.get_token())

    def testDelete204_OK(self):
        _ = self.delete_response_and_check_status(url=self.path, token=self.get_token())

    def testDelete404_WrongId(self):
        _ = self.delete_response_and_check_status(url=self.path_404, expected_status_code=404, token=self.get_token())

    def testDelete403_WrongUser(self):
        user2 = User.objects.create(username='eeee', password='eeee')
        path_403 = self.url_prefix+f'users/{user2.id}/'
        _ = self.delete_response_and_check_status(url=path_403, expected_status_code=403, token=self.get_token())

    def testDelete204_ModeratorDeleteAnother(self):
        user2 = User.objects.create(username='eeee', password='eeee')
        g, _ = Group.objects.get_or_create(name='moderators')
        g.user_set.add(self.user)
        g.save()
        path_204 = self.url_prefix + f'users/{user2.id}/'
        _ = self.delete_response_and_check_status(url=path_204, token=self.get_token())


class ChangePasswordTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.new_user = User.objects.create(username='Local', password='')
        self.path = self.url_prefix + f'users/{self.user.id}/change_password/'
        self.path_403 = self.url_prefix + f'users/{self.new_user.id}/change_password/'
        self.path_404 = self.url_prefix + f'users/{self.user.id+1000}/change_password/'
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
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(self.user)
        return jwt_encode_handler(payload)

    def testPatch202_OK(self):
        _ = self.patch_response_and_check_status(url=self.path, data=self.data_202, token=self.get_token())

    def testPatch403_WrongId(self):
        self.user.is_superuser = False
        self.user.save()
        _ = self.patch_response_and_check_status(url=self.path_403, data=self.data_202, expected_status_code=403,
                                                 token=self.get_token())

    def testPatch404_WrongId(self):
        _ = self.patch_response_and_check_status(url=self.path_404, data=self.data_202, expected_status_code=404,
                                                 token=self.get_token())

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
