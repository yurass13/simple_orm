from simple_orm.db import QueryBuilder


CASES = {
    'test_select_all': {
        "method": QueryBuilder.select,
        "params": {"sourse": 'goods'}, 
        "conditions": {},
        "asserts": "SELECT * FROM goods"
    },
    'test_select_where_single_condition': {
        "method": QueryBuilder.select,
        "params": {"sourse": 'goods'},
        "conditions": {'id': 6},
        "asserts": "SELECT * FROM goods WHERE id=?"
    },
    'test_select_concrete_fields': {
        "method": QueryBuilder.select,
        "params": {"sourse": 'goods', "fields":['name', 'barcode']},
        "conditions": {'id': 6},
        "asserts": "SELECT name, barcode FROM goods WHERE id=?"
    },
    'test_inner_join': {
        "method": QueryBuilder.join,
        "params": {"left_table":'goods', "right_table":'country'},
        "conditions": {'country_id':'id'},
        "asserts": "goods INNER JOIN country ON goods.country_id=country.id"
    },
    'test_select_join_tables': {
        "method": QueryBuilder.select,
        "params": {"sourse": 'goods INNER JOIN country ON goods.country_id=country.id'},
        "conditions": {"goods__id__le":15},
        "asserts": f"SELECT * FROM goods INNER JOIN country ON goods.country_id=country.id WHERE goods.id<=?"
    },
    'test_insert': {
        "method": QueryBuilder.insert,
        "params": {"table_name": 'country', "fields": ['id', 'name']}, 
        "conditions": {},
        "asserts": "INSERT INTO country (id, name) VALUES (?, ?);"
    },
    'test_update': {
        "method": QueryBuilder.update,
        "params": {"table_name": 'country', "fields": ['name']}, 
        "conditions": {'id': 999},
        "asserts": "UPDATE country SET name=? WHERE id=?;"
    },
    'test_delete': {
        "method": QueryBuilder.delete,
        "params": {"table_name": 'country'}, 
        "conditions": {'id': 999},
        "asserts": "DELETE FROM country WHERE id=?;"
    },

}


def case_decorator(func):
    case = CASES[func.__name__]
    def wrapper():
        method = case['method']

        sql = method(**case["params"], **case["conditions"])

        assert sql == case['asserts']

    return wrapper


@case_decorator
def test_select_all():
    ...

@case_decorator
def test_select_where_single_condition():
    ...

@case_decorator
def test_select_concrete_fields():
    ...

@case_decorator
def test_inner_join():
    ...

@case_decorator
def test_select_join_tables():
    ...

@case_decorator
def test_insert():
    ...

@case_decorator
def test_update():
    ...

@case_decorator
def test_delete():
    ...
