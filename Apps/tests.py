from rest_framework_simplejwt.tokens import RefreshToken
from TestUtils.models import BaseTestCase
from Apps.models import App


class AppsListTestCase(BaseTestCase):
    """
    Тесты для /apps/
    """
    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        self.app = App.objects.create(id='Test', secret='Secret')
        self.path = self.url_prefix + 'apps/'
        self.data_201 = {
            'id': self.app.id + '1',
            'secret': self.app.secret + '1',
        }
        self.data_400_1 = {
            'id': self.app.id + '1',
        }
        self.data_400_2 = {
            'id': self.app.id,
            'secret': 'same id'
        }

    def get_token(self):
        return str(RefreshToken.for_user(self.user).access_token)

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path, token=self.get_token())
        self.list_test(response, App)
        self.fields_test(response, ['id'])

    def testGet403_NotSuperuser(self):
        self.user.is_superuser = False
        self.user.save()
        _ = self.get_response_and_check_status(url=self.path, token=self.get_token(), expected_status_code=403)

    def testPost201_OK(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_201, token=self.get_token())

    def testPost400_WrongJson(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_1, token=self.get_token(),
                                                expected_status_code=400)

    def testPost400_NotUniqueId(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_2, token=self.get_token(),
                                                expected_status_code=400)

    def testPost403_NotSuperuser(self):
        self.user.is_superuser = False
        self.user.save()
        _ = self.post_response_and_check_status(url=self.path, data=self.data_201, token=self.get_token(),
                                                expected_status_code=403)


class AppViewTestCase(BaseTestCase):
    """
    Тесты для /apps/<pk>/
    """
    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        self.app = App.objects.create(id='Test', secret='Secret')
        self.path = self.url_prefix + f'apps/{self.app.id}/'
        self.path_404 = self.url_prefix + f'apps/{self.app.id}111/'

    def get_token(self):
        return str(RefreshToken.for_user(self.user).access_token)

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path, token=self.get_token())
        self.fields_test(response, ['id'])

    def testGet403_NotSuperuser(self):
        self.user.is_superuser = False
        self.user.save()
        _ = self.get_response_and_check_status(url=self.path, token=self.get_token(), expected_status_code=403)

    def testGet404_WrongId(self):
        _ = self.get_response_and_check_status(url=self.path_404, token=self.get_token(), expected_status_code=404)

    def testDelete204_OK(self):
        _ = self.delete_response_and_check_status(url=self.path, token=self.get_token())

    def testDelete403_NotSuperuser(self):
        self.user.is_superuser = False
        self.user.save()
        _ = self.delete_response_and_check_status(url=self.path, token=self.get_token(), expected_status_code=403)

    def testDelete404_WrongId(self):
        _ = self.delete_response_and_check_status(url=self.path_404, token=self.get_token(), expected_status_code=404)


class TokenObtain(BaseTestCase):
    """
    Тесты эндпоинтов, связанных с токеном
    """
    def setUp(self):
        super().setUp()
        self.app = App.objects.create(id='Test', secret='Secret')
        self.obtain_path = self.url_prefix + 'app-token-auth/'
        self.verify_path = self.url_prefix + 'app-token-verify/'
        self.refresh_path = self.url_prefix + 'app-token-refresh/'

    def make_request(self, path, data):
        response = self.client.post(path=path, data=data)
        return response.json()

    def testTokenObtain_OK(self):
        data = {
            'id': self.app.id,
            'secret': self.app.secret,
        }
        response = self.post_response_and_check_status(url=self.obtain_path, data=data, expected_status_code=200)
        self.fields_test(response, ['access', 'refresh'])

    def testTokenObtain_WrongJSON(self):
        data = {
            'id': self.app.id,
        }
        _ = self.post_response_and_check_status(url=self.obtain_path, data=data, expected_status_code=400)

    def testTokenObtain_WrongCredentials(self):
        data = {
            'id': self.app.id,
            'secret': self.app.secret + 'NOOOOOO',
        }
        _ = self.post_response_and_check_status(url=self.obtain_path, data=data, expected_status_code=401)

    def testTokenVerify_OK(self):
        tokens = self.make_request(self.obtain_path, {'id': self.app.id, 'secret': self.app.secret})
        _ = self.post_response_and_check_status(url=self.verify_path, data={'token': tokens['access']},
                                                expected_status_code=200)

    def testTokenVerify_WrongJSON(self):
        _ = self.post_response_and_check_status(url=self.verify_path, data={}, expected_status_code=400)

    def testTokenVerify_WrongToken(self):
        tokens = self.make_request(self.obtain_path, {'id': self.app.id, 'secret': self.app.secret})
        _ = self.post_response_and_check_status(url=self.verify_path, data={'token': tokens['access'][:-2]},
                                                expected_status_code=401)

    def testTokenRefresh_OK(self):
        tokens = self.make_request(self.obtain_path, {'id': self.app.id, 'secret': self.app.secret})
        response = self.post_response_and_check_status(url=self.refresh_path, data={'refresh': tokens['refresh']},
                                                       expected_status_code=200)
        self.fields_test(response, ['access'])
        self.post_response_and_check_status(self.verify_path, data={'token': response['access']},
                                            expected_status_code=200)

    def testTokenRefresh_WrongJSON(self):
        _ = self.post_response_and_check_status(url=self.refresh_path, data={}, expected_status_code=400)

    def testTokenRefresh_WrongToken(self):
        tokens = self.make_request(self.obtain_path, {'id': self.app.id, 'secret': self.app.secret})
        _ = self.post_response_and_check_status(url=self.refresh_path, data={'refresh': tokens['refresh'][:-2]},
                                                expected_status_code=401)
