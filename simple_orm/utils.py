import re


def camel_to_snake(name:str) -> str:
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def snake_to_camel(name:str) -> str:
    name = name.strip()
    if ' ' in name or '\t' in name or '\n' in name:
        raise ValueError('The string contains a whitespace character!')

    return ''.join(word.title() for word in name.split('_'))


def apply_eq_method(string:str) -> str:
    """NOTE include python path: '__'->'.'"""
    # TODO add other methods
    eq_methods = {
        '__lt': '<',
        '__gt': '>',
        '__le': '<=',
        '__ge': '>=',
        '__in': ' in ',
    }
    for method in eq_methods:
        if string.endswith(method):
            string = string[:-len(method)] + eq_methods[method]

    return double_underscore_to_dot(string)


def double_underscore_to_dot(string:str) -> str:
    return string.replace('__', '.')

