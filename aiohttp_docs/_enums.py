from enum import StrEnum


class SwaggerLayout(StrEnum):
    BASE = 'BaseLayout'
    STANDALONE = 'StandaloneLayout'


class ParameterType(StrEnum):
    PATH = 'path'
    QUERY = 'query'
    HEADER = 'header'
    COOKIE = 'cookie'
