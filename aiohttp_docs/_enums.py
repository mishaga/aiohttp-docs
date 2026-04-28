from enum import StrEnum


class SwaggerLayout(StrEnum):
    BASE = 'BaseLayout'
    STANDALONE = 'StandaloneLayout'


class ParameterType(StrEnum):
    PATH = 'path'
    QUERY = 'query'
    HEADER = 'header'
    COOKIE = 'cookie'


class SecuritySchemeIn(StrEnum):
    QUERY = 'query'
    HEADER = 'header'
    COOKIE = 'cookie'


class SecuritySchemeType(StrEnum):
    API_KEY = 'apiKey'
    HTTP = 'http'
    MUTUAL_TLS = 'mutualTLS'
    OAUTH2 = 'oauth2'
    OPEN_ID_CONNECT = 'openIdConnect'
