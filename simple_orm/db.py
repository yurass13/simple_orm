from operator import attrgetter
from typing import Any, Callable, Iterable, List, Literal, Optional, Tuple, Type, Union

from simple_orm.bases import M, ModelBase
from simple_orm.utils import camel_to_snake


JOIN_TYPES = ['left', 'right', 'inner', 'outer', 'cross']

QueryValues = Tuple[Any]

JoinType = Literal['left', 'right', 'inner', 'outer', 'cross']


class JoinTypeError(Exception):
    pass


def _where_decorator(query_builder_method:Callable) -> Callable:
    method_params = query_builder_method.__code__.co_varnames

    # TODO need check better ways init wrapper signature using reflection
    def wrapper(*args, **kwargs):
        template = "{query} WHERE {conditions};"

        params_dict = {}
        conditions = []

        for key, value in kwargs.items():
            if key in method_params:
                params_dict[key]= value
            else:
                prepared_key = key.replace('__lt', '<').\
                                   replace('__gt', '>').\
                                   replace('__le', '<=').\
                                   replace('__ge', '>=').\
                                   replace('__','.')
                conditions.append(f"{prepared_key}?" 
                                  if '<' in prepared_key or '>' in prepared_key 
                                  else f"{prepared_key}=?")

        if len(conditions) == 0:
            return query_builder_method(*args, **params_dict)

        conditions_str = ', '.join(conditions)
        query = query_builder_method(*args, **params_dict)
        return template.format(query=query, conditions=conditions_str)

    return wrapper


def _join_type_handler(join_type:Union[JoinType, List[JoinType]]) -> str:
    if isinstance(join_type, str):
        if isinstance(join_type, str):
            if join_type in JOIN_TYPES:
                return join_type.upper()

        raise JoinTypeError(join_type)
    else:
        if 'cross' in join_type:
            # NOTE Cross join overlapping all other types
            return 'CROSS'
        else:
            inner = 'inner' in  join_type
            outer = 'outer' in join_type
            left = 'left' in  join_type
            right = 'right' in join_type

            if (left and right) or (inner and outer):
                raise JoinTypeError("JoinType conflict!")
            elif not any([left, right, inner, outer]):
                # default
                return 'INNER'
            else:
                result = ' left' if left else ''
                result += ' right' if right else ''
                result += ' inner' if inner else ''
                result += ' outer' if outer else ''
                return result.upper()


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
    def insert(table_name:str, fields:Iterable[str]) -> str:
        template = "INSERT INTO {table_name} ({fields}) VALUES ({values});"

        return template.format(table_name=table_name,
                            fields=', '.join(list(map(str, fields))),
                            values=', '.join(['?' for _ in fields]))


    @staticmethod
    @_where_decorator
    def update(table_name:str,
               fields:Iterable[str]) -> str:
        template = "UPDATE {table_name} SET {pairs}"

        return template.format(table_name=table_name,
                               pairs=', '.join(list(map(lambda x: f"{x}=?", fields))))


    @staticmethod
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


class ModelQueryBuilder:
    @staticmethod
    def select(model:Type[M], **conditions) -> str:
        sourse = camel_to_snake(model.__name__)
        fields = model.__match_args__

        # NOTE unbound super
        return QueryBuilder.select(sourse=sourse,
                                   fields=fields,
                                   **conditions)


    @staticmethod
    def insert(model:M) -> List[str]:
        queries = []
        table_name = camel_to_snake(model.__class__.__name__)
        fields = model.__match_args__

        values = []
        for field in fields:
            value = attrgetter(field)(model)

            if isinstance(value, ModelBase):
                queries.extend(ModelQueryBuilder.insert(value))
                value = value.id
            values.append(value)

        queries.append(
            QueryBuilder.insert(table_name=table_name,
                                fields=fields))
        return queries


    @staticmethod
    def update(model:M, **conditions) -> List[str]:
        queries = []
        table_name = camel_to_snake(model.__class__.__name__)
        fields = model.__match_args__

        values = []
        for field in fields:
            value = attrgetter(field)(model)

            if isinstance(value, ModelBase):
                local_conditions = {key.removeprefix(table_name + '.'): conditions[key] 
                                    for key in conditions
                                    if key.startswith(table_name + '.')}
                
                if 'id' not in local_conditions:
                    local_conditions['id'] = value.id
                
                queries.extend(ModelQueryBuilder.update(value, **local_conditions))
                value = value.id
            values.append(value)

        queries.append(
            QueryBuilder.update(table_name=table_name,
                                fields=fields,
                                values=values,
                                **conditions)
        )
        return queries


    @staticmethod
    def delete(model:Type[M], **conditions) -> List[str]:
        table_name = camel_to_snake(model.__class__.__name__)

        return QueryBuilder.delete(table_name=table_name, **conditions)
