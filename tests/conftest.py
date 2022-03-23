import pytest
from flask import Flask
from jwt import PyJWKSet

from flask_cognito_lib import CognitoAuth
from flask_cognito_lib.config import Config


@pytest.fixture(autouse=True)
def app():
    """Create application for the tests."""

    _app = Flask(__name__)
    CognitoAuth(_app)

    ctx = _app.test_request_context()
    ctx.push()

    _app.config["TESTING"] = True
    _app.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = False

    # minimum require configuration for CognitoAuth extension
    _app.config["AWS_COGNITO_USER_POOL_ID"] = "eu-west-1_c7O90SNDF"
    _app.config["AWS_COGNITO_USER_POOL_CLIENT_ID"] = "4lln66726pp3f4gi1krj0sta9h"
    _app.config["AWS_COGNITO_USER_POOL_CLIENT_SECRET"] = "secure-client-secret"
    _app.config["AWS_COGNITO_REDIRECT_URL"] = "http://localhost:5000/postlogin"
    _app.config["AWS_COGNITO_LOGOUT_URL"] = "http://localhost:5000/postlogout"
    _app.config[
        "AWS_COGNITO_DOMAIN"
    ] = "https://webapp-test.auth.eu-west-1.amazoncognito.com"
    _app.config["AWS_REGION"] = "eu-west-1"

    _app.testing = True

    yield _app
    ctx.pop()


@pytest.fixture
def client():
    cl = app.test_client()
    yield cl


@pytest.fixture
def jwks():
    return {
        "keys": [
            {
                "alg": "RS256",
                "e": "AQAB",
                "kid": "spvUVat6clXStpoIh6nCUttT6y6AmPoPAty+UMNvQ2Y=",
                "kty": "RSA",
                "n": "0u3EqunReyXWvYL-TIL41mpybOLQZMkzayIMXrGdw6AjDD0bI_vWo-s4j4Xpw9fqV4XMyfo-q7EB_XfMlTSIDqbYt0PIqw3ULUS2utC5QZrpUsEmcws1RGW1Ed-sZjmhozrFcugywVC7NMFb3zQGmOnLcElsfzAIZOfGQ4KPsLTxpUG8OoxU3wzoqSj00YydMAw-6-KEhv7RQbE5ik82gdSu5vzrB1n8iE4xJtwt7BNA1G3jR6cIATSDubb_mqrN7ZGr_d8_AF4LjscNVT28ois7XQpzY21jsPYftRmrUHitoULzoc_DngPNlG1HFPfU_-RIAq0v_LMgd3qMIEWHaw",
                "use": "sig",
            },
            {
                "alg": "RS256",
                "e": "AQAB",
                "kid": "2gH42FHBLdfSv1YQwmql6bi45sX3dovsvvuCXQQ6Uaw=",
                "kty": "RSA",
                "n": "xaEhQcrn4hEXvAy5iCSTy0Tt_6MlvEk00k8eiJkRN8t-2YRZrU1-DK9FNY2tm9YxwFV1ynPSkkHkUPY3CWQt_zInhc8bx8ZjtzwqdApbkU_2A00LcUd_8VzmfGOToQ80EvTZ5QZvxQQxqcoOopX0WnysqFQT413isUaC4WTQcxb0nC78UZFW0t__xFuwtti-cwvWSUWdv_tLFBqBvhlvohENoCAQrXGsK64QCAj4dsagk2dsmrgdiOyihwnW4zx3Dcu4hDQMEcbMm4b76UN4_084k4rEpwcoDjq9wBx9QVUt9Xt81C2OWBkBz4UDX0QtAvTvl_RzErVDEwFtCEVfDQ",
                "use": "sig",
            },
        ]
    }


@pytest.fixture
def cfg():
    return Config()


@pytest.fixture(autouse=True)
def jwk_patch(mocker, jwks):
    mocker.patch(
        "jwt.jwks_client.PyJWKClient.get_jwk_set",
        return_value=PyJWKSet.from_dict(jwks),
    )


@pytest.fixture
def access_token():
    return (
        "eyJraWQiOiIyZ0g0MkZIQkxkZlN2MVlRd21xbDZiaTQ1c1gzZG92c3Z2dUNYUVE2VWF3PSIsImFsZyI6IlJTMjU2In0."
        "eyJzdWIiOiI5MDQ4ZDM4Zi04MTc0LTQ5YjktOGQ1OS0zMjM4MTcyODIzZDgiLCJjb2duaXRvOmdyb3VwcyI6WyJhZG1pbiJdLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtd2VzdC0xLmFtYXpvbmF3cy5jb21cL2V1LXdlc3QtMV9jN085MFNOREYiLCJ2ZXJzaW9uIjoyLCJjbGllbnRfaWQiOiI0bGxuNjY3MjZwcDNmNGdpMWtyajBzdGE5aCIsIm9yaWdpbl9qdGkiOiJkNDgxMWJmMS0yNzk4LTRkMzMtYjY1Yy0yZjgyNTQ3MjlkZDIiLCJldmVudF9pZCI6IjE4ODI4ZDE4LWI0NjUtNDcwZS04NGI2LTE3NTIwZGVkMjk5YiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoicGhvbmUgb3BlbmlkIGVtYWlsIiwiYXV0aF90aW1lIjoxNjQ3OTYxNDkzLCJleHAiOjE2NDc5NjUwOTMsImlhdCI6MTY0Nzk2MTQ5MywianRpIjoiMGZlMjlhOWUtNmU5NC00NzliLTk4N2ItZTQ1Njk2ZDU4NDNhIiwidXNlcm5hbWUiOiJtYmxhY2sifQ."
        "U0ucoBT7X40jGuuJpDpxLhlL3084Qc_Sq5MAfIoHvujRMqdea6_2QEMrT-p4XvYVQArYmJKPuP40N8i5YR_fOyoW_truqzFtu-MiCCBGOCVXZ0yZ5K8YX6Arb0TbZiyFsU1fj-qx_DmlQIuPDoiTNVo4_d0Ff1NvsHtYZ-00A-7cAtZIu9FvuEumIqOTawBXv4O5QViRYmnnS6hGl8Fh0-N8Eutb_MnhJk47xulvNcoCUIzw7GX8ayn6WgLDdEHYvJs1zrXiyBDx4T5oV667PdELc-DQOy4j6vBlXxjc-fptVT9k-AD_p_Pe70xvzBhFejKCQz5fI0FF7_MM683fIw"
    )


@pytest.fixture
def id_token():
    return (
        "eyJraWQiOiJzcHZVVmF0NmNsWFN0cG9JaDZuQ1V0dFQ2eTZBbVBvUEF0eStVTU52UTJZPSIsImFsZyI6IlJTMjU2In0."
        "eyJhdF9oYXNoIjoiV3FUZ0JON3VGUG5uSlJneWQ4NldMQSIsInN1YiI6IjkwNDhkMzhmLTgxNzQtNDliOS04ZDU5LTMyMzgxNzI4MjNkOCIsImNvZ25pdG86Z3JvdXBzIjpbImFkbWluIl0sImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfYzdPOTBTTkRGIiwiY29nbml0bzp1c2VybmFtZSI6Im1ibGFjayIsIm5vbmNlIjoiTVNsbjZudlBJSUJWTWhzTlVPdFVDdHNzY2VVS3o0ZGhDUlppNVFaUlU0QT0iLCJvcmlnaW5fanRpIjoiZDQ4MTFiZjEtMjc5OC00ZDMzLWI2NWMtMmY4MjU0NzI5ZGQyIiwiYXVkIjoiNGxsbjY2NzI2cHAzZjRnaTFrcmowc3RhOWgiLCJldmVudF9pZCI6IjE4ODI4ZDE4LWI0NjUtNDcwZS04NGI2LTE3NTIwZGVkMjk5YiIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjQ3OTYxNDkzLCJleHAiOjE2NDc5NjUwOTMsImlhdCI6MTY0Nzk2MTQ5MywianRpIjoiMDU0YjhlNjYtNTg1My00MTI3LTlkNTUtZTNhMjlkYmQ4NGJkIiwiZW1haWwiOiJtYmxhY2tAc3BhcmtnZW8uY29tIn0."
        "vnGkFOxtC7ubRkQHByNst5Uyxj4kGFXRP-kaG09iRCADJQSgxwGjZDbG4xbvW0EISA4mGz1sfnCiinuWLNrbKR4KUC3qTytu4hq91OCjB2-KKxeVHxQR1NsjYZ8u7DBOCVeKSouO4oaHDf966f1gubdYXDp12urtiDJy9MybV9diRxOm2eRLAQPIxSFO5owGNcGh03OWystMEJvUwwDVbdpf562OZ72Eo9UHnv3eR3VvH1Gv49WAzwqweIVRiv4-hJqGjLeKnqo3X1toBvU_2QPN9KmM7oYcIpYqagKQNCIcsLq6ZngOJfbCBPCPQX9XYrCkMAmm0VaBRix2zzHYtg"
    )

