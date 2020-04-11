from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.settings import api_settings


class AppRefreshToken(RefreshToken):
    """
    Рефреш-токен для приложения
    """
    token_type = 'app_refresh'
    lifetime = api_settings.REFRESH_TOKEN_LIFETIME

    @property
    def access_token(self):
        access = AppAccessToken()

        # Use instantiation time of refresh token as relative timestamp for
        # access token "exp" claim.  This ensures that both a refresh and
        # access token expire relative to the same time if they are created as
        # a pair.
        access.set_exp(from_time=self.current_time)

        no_copy = self.no_copy_claims
        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value

        return access


class AppAccessToken(AccessToken):
    """
    Токен для приложения
    """
    token_type = 'app_access'
    lifetime = api_settings.ACCESS_TOKEN_LIFETIME
