from pylastfm.api.api import API


class Auth(API):

    def _sign(self, **params):
        api_info = self._client.api_info
        return self._client._signer(api_key=api_info.key, **params)

    def get_token(self):
        """
        Fetch an unathorized request token for an API account.

        http://www.last.fm/api/show/auth.getToken
        """
        resp = self._request('GET', 'auth.getToken', params=self._sign())
        return resp['token']

    def get_session(self, token):
        """
        Fetch a session key for a user. Typically called after the user has
        authorized the token returned from :meth:`Auth.get_token`.

        http://www.last.fm/api/show/auth.getSession
        """
        return self._request(
            'GET', 'auth.getSession',
            params=self._sign(method='auth.getSession', token=token),
            unwrap='session')['key']
