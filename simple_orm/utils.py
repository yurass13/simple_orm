import re


def camel_to_snake(name:str) -> str:
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def snake_to_camel(name:str) -> str:
    return ''.join(word.title() for word in name.split('_'))


def find_eq_method(string:str) -> str:
    # TODO contains? x in key
    return _snake_to_python_path(
        string.replace('__lt', '<').\
               replace('__gt', '>').\
               replace('__le', '<=').\
               replace('__ge', '>=').\
               replace('__in', ' in ')
    )


def _snake_to_python_path(string:str) -> str:
    return string.replace('__', '.')

