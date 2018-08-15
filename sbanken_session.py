from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import urllib.parse


def create_authenticated_http_session(client_id, client_secret) -> requests.Session:
    oauth2_client = BackendApplicationClient(client_id=client_id)
    session = OAuth2Session(client=oauth2_client)
    session.fetch_token(
        token_url='https://api.sbanken.no/identityserver/connect/token',
        client_id=client_id,
        client_secret=urllib.parse.quote(client_secret)
    )
    return session
