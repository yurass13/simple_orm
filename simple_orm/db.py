from operator import attrgetter
from typing import Any, Callable, Iterable, List, Literal, Optional, Tuple, Type, Union

from simple_orm.models import M, Model
from simple_orm.utils import camel_to_snake, apply_eq_method


JOIN_TYPES = ['left', 'right', 'inner', 'outer', 'cross']

QueryValues = Tuple[Any]

JoinType = Literal['left', 'right', 'inner', 'outer', 'cross']


class JoinTypeError(Exception):
    pass


# TODO add logic between where conditions. IMPORTANT
def _where_decorator(query_builder_method:Callable) -> Callable:
    method_params = query_builder_method.__code__.co_varnames

    # TODO need check better ways init wrapper signature using reflection
    def wrapper(*args, **kwargs):
        template = "{query} WHERE {conditions}"

        params_dict = {}
        conditions = []

        for key, value in kwargs.items():
            if key in method_params:
                params_dict[key]= value
            else:
                prepared_key = apply_eq_method(key)
                conditions.append(f"{prepared_key}?" 
                                  if '<' in prepared_key or '>' in prepared_key 
                                  else f"{prepared_key}=?")

        if len(conditions) == 0:
            return query_builder_method(*args, **params_dict)

        conditions_str = ', '.join(conditions)
        query = query_builder_method(*args, **params_dict)
        return template.format(query=query, conditions=conditions_str)

    return wrapper


# TODO tests for all types of join.         IMPORTANT
# TODO chain joins.                         IMPORTANT
# TODO add logic between join conditions.   FUTURE IDEA
def _join_type_handler(join_type:Union[JoinType, List[JoinType]]) -> str:
    if isinstance(join_type, str):
        if join_type not in JOIN_TYPES:
            raise JoinTypeError(join_type)
        else:
            result:str = join_type

    elif isinstance(join_type, (list, tuple)):
        if 'cross' in join_type:
            # NOTE Cross join overlapping all other types
            result = 'cross'
        else:
            inner = 'inner' in  join_type
            outer = 'outer' in join_type
            left = 'left' in  join_type
            right = 'right' in join_type

            if (left and right) or (inner and outer):
                raise JoinTypeError("JoinType conflict!")
            elif not any([left, right, inner, outer]):
                # default
                result = 'inner'
            else:
                result = ' left' if left else ''
                result += ' right' if right else ''
                result += ' inner' if inner else ''
                result += ' outer' if outer else ''

    return result.upper()


def _end_of_script_decorator(query_builder_method:Callable) -> Callable:
    def wrapper(*args, **kwargs):
        return f"{query_builder_method(*args, **kwargs)};"

    return wrapper

# TODO CREATE table.                        IMPORTANT
# TODO SELECT DISTINCT.                     FUTURE IDEA
# TODO SELECT TOP N .                       FUTURE IDEA
# TODO ORDER BY.                            FUTURE IDEA
# TODO GROUP BY.                            FUTURE IDEA
# TODO Other patterns.                      FUTURE IDEA
class QueryBuilder:
    @staticmethod
    @_where_decorator
    def select(sourse:str, fields:Union[Iterable[str], str]='*') -> str:
        template = "SELECT {fields} FROM {sourse}"

        if isinstance(fields, str):
            return template.format(fields=fields, sourse=sourse) 
        
        fields_str =', '.join(list(fields))
        return template.format(fields=fields_str, sourse=sourse)


    @staticmethod
    @_end_of_script_decorator
    def insert(table_name:str, fields:Iterable[str]) -> str:
        template = "INSERT INTO {table_name} ({fields}) VALUES ({values})"

        return template.format(table_name=table_name,
                            fields=', '.join(list(map(str, fields))),
                            values=', '.join(['?' for _ in fields]))


    @staticmethod
    @_end_of_script_decorator
    @_where_decorator
    def update(table_name:str, fields:Iterable[str]) -> str:
        template = "UPDATE {table_name} SET {pairs}"

        return template.format(table_name=table_name,
                               pairs=', '.join(list(map(lambda x: f"{x}=?", fields))))


    @staticmethod
    @_end_of_script_decorator
    @_where_decorator
    def delete(table_name:str) -> str:
        # NOTE be careful. Need Decorator QueryConstructorBase.where(**kwargs)
        template = "DELETE FROM {table_name}"

        return template.format(table_name=table_name)


    @staticmethod
    def join(left_table:str,
             right_table:str,
             join_type:Union[JoinType, List[JoinType]]='inner',
             left_alias:Optional[str]=None,
             right_alias:Optional[str]=None,
             **conditions) -> str:
        """
            Return format (join_template, (left_alias, right_alias))
        """
        template = "{left_table} {join_type} JOIN {right_table} ON {conditions}"

        # Apply aliases on tables
        if left_alias is None:
            left_alias = left_table
        else:
            left_table = f"{left_table} AS {left_alias}"

        if right_alias is None:
            right_alias = right_table
        else:
            right_table = f"{right_table} AS {right_alias}"

        # Apply aliases on conditions
        conditions = {f"{left_alias}.{key}":f"{right_alias}.{value}"
                      for key, value in conditions.items()}

        # result
        query = template.format(left_table=left_table,
                                join_type=_join_type_handler(join_type),
                                right_table=right_table,
                                conditions=', '.join(
                                    list(
                                        map(lambda pair:f"{pair[0]}={pair[1]}",
                                            conditions.items()))))

        return query

# TODO need check duplicate queries in insert, update, delete       IMPORTANT
# NOTE insert, update and delete must returns Queue or ect. with unique sorted queries. 
""" NOTE queries DFS walk generator
1. Save lists of queries and find lists with the same items.
2. Union lists with priority of the first list.
3. On duplicated item switch on second or other list and continue.
4. After all left side from lists with same objects are handled return to the first list.
NOTE Be careful with cycles.
"""
# TODO Update table SET choosed_field['s]=?[ WHERE **conditions];   FUTURE IDEA.
# TODO update using Type[M] for all values update                   AFTER CREATE TABLE AND ALTER TABLE
# TODO Delete relations options                                     FUTURE IDEA.
class QueryBuilderModel:
    @staticmethod
    def select(model:Type[M], **conditions) -> str:
        sourse = camel_to_snake(model.__name__)
        fields = model.__match_args__

        # TODO joins on relations.                                  IMPORTANT
        # NOTE unbound super
        return QueryBuilder.select(sourse=sourse,
                                   fields=fields,
                                   **conditions)


    @staticmethod
    def insert(model:M) -> List[str]:
        queries = []
        table_name = camel_to_snake(model.__class__.__name__)
        fields = model.__match_args__

        for field in fields:
            value = attrgetter(field)(model)

            if isinstance(value, Model):
                queries.extend(QueryBuilderModel.insert(value))
                value = value.id

        queries.append(
            QueryBuilder.insert(table_name=table_name,
                                fields=fields))
        return queries


    @staticmethod
    def update(model:M, **conditions) -> List[str]:
        queries = []
        table_name = camel_to_snake(model.__class__.__name__)
        fields = model.__match_args__

        for field in fields:
            value = attrgetter(field)(model)

            if isinstance(value, Model):
                local_conditions = {key.removeprefix(table_name + '.'): conditions[key] 
                                    for key in conditions
                                    if key.startswith(table_name + '.')}
                
                if 'id' not in local_conditions:
                    local_conditions['id'] = value.id
                
                queries.extend(QueryBuilderModel.update(value, **local_conditions))

        queries.append(
            QueryBuilder.update(table_name=table_name,
                                fields=fields,
                                **conditions)
        )
        return queries


    @staticmethod
    def delete(model:Type[M], **conditions) -> List[str]:
        table_name = camel_to_snake(model.__class__.__name__)
        return [QueryBuilder.delete(table_name=table_name, **conditions)]
