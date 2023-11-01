from simple_orm.utils import camel_to_snake, snake_to_camel, apply_eq_method


def test_camel_to_snake():
    cases = {
        'just text':'just text',
        'camelMethod':'camel_method',
        'CamelClass':'camel_class',
    }

    for key, value in cases.items():
        assert value == camel_to_snake(key)


def test_snake_to_camel_error():
    try:
        result = snake_to_camel('text with whitespaces')
    except ValueError as error:
        result = str(error)

    finally:
        assert result == "The string contains a whitespace character!"


def test_snake_to_camel():
    cases = {
        'textwithoutwhitespaces':'Textwithoutwhitespaces',
        'snake_method': 'SnakeMethod',
    }

    for key, value in cases.items():
        assert value == snake_to_camel(key)


def test_apply_eq_method():
    cases = {
        'camelCase': 'camelCase=',
        'snake_case': 'snake_case=',
        'object__attribute': 'object.attribute=',
        'attribute__lt__between': 'attribute.lt.between=',
        'attribute__lt_snake': 'attribute.lt_snake=',
        'attribute__gt__between': 'attribute.gt.between=',
        'attribute__gt_snake': 'attribute.gt_snake=',
        'attribute__le__between': 'attribute.le.between=',
        'attribute__le_snake': 'attribute.le_snake=',
        'attribute__ge__between': 'attribute.ge.between=',
        'attribute__ge_snake': 'attribute.ge_snake=',
        'attribute__in__between': 'attribute.in.between=',
        'attribute__in_snake': 'attribute.in_snake=',
        '__lt': '<',
        '__gt': '>',
        '__le': '<=',
        '__ge': '>=',
        '__in': ' in '
    }
    
    for key, value in cases.items():
        assert value == apply_eq_method(key)