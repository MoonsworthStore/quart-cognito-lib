class QuartCognitoError(Exception):
    pass


class TokenVerifyError(QuartCognitoError):
    pass


class CognitoError(QuartCognitoError):
    pass
