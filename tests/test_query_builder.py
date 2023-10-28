import sqlite3

from simple_orm.db import QueryBuilder


CASES = {
    'test_select_all': {
        "method": QueryBuilder.select,
        "params": {"sourse": 'goods'}, 
        "commit": False,
        "values": [],
        "conditions": {},
        "asserts": {len: 9130}
    },
    'test_empty_select': {
        "method": QueryBuilder.select,
        "params": {"sourse": 'goods'},
        "commit": False,
        "values": [],
        "conditions": {'id': 2},
        "asserts": {len: 0}
    },
    'test_get_by_id': {
        "method": QueryBuilder.select,
        "params": {"sourse": 'goods'},
        "commit": False,
        "values": [],
        "conditions": {'id': 6},
        "asserts": {len: 1}
    },
    'test_select_concrete_fields': {
        "method": QueryBuilder.select,
        "params": {"sourse": 'goods', "fields":['name', 'barcode']},
        "commit": False,
        "values": [],
        "conditions": {'id': 6},
        "asserts": {len: 1, list: [('Аммиак р-р 10% 40мл инд.уп Кемеровская ФФ', '4605903007932')]}
    },
    'test_select_unknown_column': {
        "method": QueryBuilder.select,
        "params": {"sourse": 'goods', "fields":['name', 'shit']},
        "commit": False,
        "values": [],
        "conditions": {},
        "asserts": {str: "no such column: shit"}
    },
    'test_inner_join_syntax': {
        "method": QueryBuilder.join,
        "params": {"left_table":'goods', "right_table":'country'},
        "commit": False,
        "values": [],
        "conditions": {'country_id':'id'},
        "asserts": {str: "goods INNER JOIN country ON goods.country_id=country.id"}
    },
    'test_select_join_tables': {
        "method": QueryBuilder.select,
        "params": {"sourse": 'goods INNER JOIN country ON goods.country_id=country.id'},
        "commit": False,
        "values": [],
        "conditions": {"goods__id__le":15},
        "asserts": {len: 4}
    },
    'test_error_in_condition': {
        "method": QueryBuilder.select,
        "params": {"sourse": 'goods'},
        "commit": False,
        "values": [],
        "conditions": {'bull': "shit"},
        "asserts": {str: "no such column: bull"}
    },
    'test_insert': {
        "method": QueryBuilder.insert,
        "params": {"table_name": 'country', "fields": ['id', 'name']}, 
        "commit": True,
        "values": [999, "Test"],
        "conditions": {},
        "asserts": {lambda x:len(exec(QueryBuilder.select("country", id=999), False, 999)): 1}
    },
    'test_update': {
        "method": QueryBuilder.update,
        "params": {"table_name": 'country', "fields": ['name']}, 
        "commit": True,
        "values": ['test'],
        "conditions": {'id': 999},
        "asserts": {lambda x:len(exec(QueryBuilder.select("country", id=999), False, 999)): 1,
                    lambda x:exec(QueryBuilder.select("country", id=999), False, 999)[0][1]: 'test'}
    },
    'test_delete': {
        "method": QueryBuilder.delete,
        "params": {"table_name": 'country'}, 
        "commit": True,
        "values": [],
        "conditions": {'id': 999},
        "asserts": {lambda x:len(exec(QueryBuilder.select("country", id=999), False, 999)): 0}
    },

}


def exec(query:str, commit:bool, *parameters):
    result = None
    with sqlite3.Connection('./volumes/default.sqlite3') as conn:
        cur = conn.execute(query, tuple(parameters))
        if not commit:
            result = cur.fetchall()
        else:
            conn.commit()

    return result


def test_select_all():
    case = CASES["test_select_all"]

    sql = case["method"](**case["params"], **case["conditions"])
    result = exec(sql,
                    case["commit"],
                    *case["values"],
                    *case["conditions"].values())
    assert all([func(result) == required 
                for func, required  in case["asserts"].items()])


def test_empty_select():
    case = CASES["test_empty_select"]

    sql = case["method"](**case["params"], **case["conditions"])
    result = exec(sql,
                    case["commit"],
                    *case["values"],
                    *case["conditions"].values())
    assert all([func(result) == required 
                for func, required  in case["asserts"].items()])


def test_get_by_id():
    case = CASES["test_get_by_id"]

    sql = case["method"](**case["params"], **case["conditions"])
    result = exec(sql,
                    case["commit"],
                    *case["values"],
                    *case["conditions"].values())
    assert all([func(result) == required 
                for func, required  in case["asserts"].items()])


def test_select_concrete_fields():
    case = CASES["test_select_concrete_fields"]

    sql = case["method"](**case["params"], **case["conditions"])
    result = exec(sql,
                    case["commit"],
                    *case["values"],
                    *case["conditions"].values())
    assert all([func(result) == required 
                for func, required  in case["asserts"].items()])


def test_select_unknown_column():
    case = CASES["test_select_unknown_column"]

    sql = case["method"](**case["params"], **case["conditions"])
    try:
        result = exec(sql,
                        case["commit"],
                        *case["values"],
                        *case["conditions"].values())
    except sqlite3.OperationalError as error:
        result = str(error)

    assert all([func(result) == required 
                for func, required  in case["asserts"].items()])


def test_inner_join_syntax():
    case = CASES["test_inner_join_syntax"]

    result = case["method"](**case["params"], **case["conditions"])

    assert all([func(result) == required 
                for func, required  in case["asserts"].items()])


def test_select_join_tables():
    case = CASES["test_select_join_tables"]

    sql = case["method"](**case["params"], **case["conditions"])
    result = exec(sql,
                    case["commit"],
                    *case["values"],
                    *case["conditions"].values())
    assert all([func(result) == required 
                for func, required  in case["asserts"].items()])


def test_error_in_condition():
    case = CASES["test_error_in_condition"]

    sql = case["method"](**case["params"], **case["conditions"])
    try:
        result = exec(sql,
                        case["commit"],
                        *case["values"],
                        *case["conditions"].values())
    except sqlite3.OperationalError as error:
        result = str(error)

    assert all([func(result) == required 
                for func, required  in case["asserts"].items()])


def test_insert():
    case = CASES["test_insert"]

    sql = case["method"](**case["params"], **case["conditions"])
    result = exec(sql,
                    case["commit"],
                    *case["values"],
                    *case["conditions"].values())
    assert all([func(result) == required 
                for func, required  in case["asserts"].items()])


def test_update():
    case = CASES["test_update"]

    sql = case["method"](**case["params"], **case["conditions"])
    result = exec(sql,
                    case["commit"],
                    *case["values"],
                    *case["conditions"].values())
    assert all([func(result) == required 
                for func, required  in case["asserts"].items()])


def test_delete():
    case = CASES["test_delete"]

    sql = case["method"](**case["params"], **case["conditions"])
    result = exec(sql,
                    case["commit"],
                    *case["values"],
                    *case["conditions"].values())
    assert all([func(result) == required 
                for func, required  in case["asserts"].items()])
