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
            'username': 'Hello',
            'password': 'World'
        }
        self.data_400_1 = {
            'username': self.user_username,
            'password': 'RaNd0m',
        }
        self.data_400_2 = {
            'password': 'RaNd0M',
        }

    def testRegisterOk(self):
        response = self.post_response_and_check_status(url=self.path, data=self.data_201, auth=False)
        self.fields_test(response, needed_fields=['token'], allow_extra_fields=False)

    def testRegisterFail_ExistingUsername(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_1, expected_status_code=400,
                                                auth=False)

    def testRegisterFail_WrongJson(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_2, expected_status_code=400,
                                                auth=False)


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

    def testGetUsers(self):
        token = self.get_token()
        response = self.get_response_and_check_status(url=self.path, auth=False, token=token)
        self.fields_test(response, needed_fields=['id', 'username', 'profile_pic_link', 'is_superuser', 'is_moderator'],
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

    def testGetUserOk(self):
        response = self.get_response_and_check_status(url=self.path, auth=False, token=self.get_token())
        self.fields_test(response, needed_fields=['id', 'username', 'email', 'pin_sprite', 'geopin_sprite',
                                                  'unlocked_pins', 'unlocked_geopins', 'rating', 'profile_pic_link',
                                                  'created_dt', 'is_superuser' , 'is_moderator'],
                         allow_extra_fields=False)
        self.assertEqual(response['id'], self.user.id)

    def testGetUserFail_404(self):
        _ = self.get_response_and_check_status(url=self.path_404, expected_status_code=404, auth=False,
                                               token=self.get_token())

    def testDeleteOk(self):
        _ = self.delete_response_and_check_status(url=self.path, auth=False, token=self.get_token())

    def testDeleteFail_404(self):
        _ = self.delete_response_and_check_status(url=self.path_404, expected_status_code=404, auth=False,
                                                  token=self.get_token())

    def testDeleteFail_WrongUser(self):
        user2 = User.objects.create(username='eeee', password='eeee')
        path_403 = self.url_prefix+f'users/{user2.id}/'
        _ = self.delete_response_and_check_status(url=path_403, expected_status_code=403,
                                                  auth=False, token=self.get_token())

    def testDeleteOk_Moderator(self):
        user2 = User.objects.create(username='eeee', password='eeee')
        g, _ = Group.objects.get_or_create(name='moderators')
        g.user_set.add(self.user)
        g.save()
        path_204 = self.url_prefix + f'users/{user2.id}/'
        _ = self.delete_response_and_check_status(url=path_204, auth=False, token=self.get_token())
