import base64
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class IXCWebserviceClient:
    """
    Cliente Python equivalente ao WebserviceClient.php do IXCSoft.
    Autenticação HTTP Basic com o token no formato 'id:hash'.
    """

    def __init__(self, host, token, verify_ssl=False):
        # host ex: https://SEU_DOMINIO/webservice/v1  (sem barra no final)
        self.host = host.rstrip('/')
        self.token = token
        self.verify_ssl = verify_ssl

        # O IXC usa Basic Auth: base64(token) — o token já é "id:hash"
        auth = base64.b64encode(self.token.encode()).decode()
        self.headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/json',
        }

    def _url(self, endpoint):
        return f'{self.host}/{endpoint}'

    def listar(self, endpoint, params):
        """
        LISTAR no IXC usa verbo POST + header 'ixcsoft: listar'.
        """
        headers = dict(self.headers)
        headers['ixcsoft'] = 'listar'
        resp = requests.post(
            self._url(endpoint),
            json=params,
            headers=headers,
            verify=self.verify_ssl,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()

    def get(self, endpoint, params):
        return self.listar(endpoint, params)
