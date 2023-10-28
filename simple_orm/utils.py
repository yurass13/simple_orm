import re

from typing import Tuple

from dataclasses import Field


def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def snake_to_camel(name):
    return ''.join(word.title() for word in name.split('_'))


def prepare_table_fields_strategy(fields:Tuple[Tuple[Field]]) -> str:
        # Simplified for current task. 
        prepared = []
        for field in fields:
            if field.name == 'id' and field.type == 'int':
                prepared.append(f"{field.name} INTEGER PRIMARY KEY")
            elif field.type == 'int':
                prepared.append(f"{field.name} INTEGER")
            elif field.type == 'str':
                prepared.append(f"{field.name} TEXT NOT NULL")
            # elif field.type == 'float'
            # ...
            else:
                raise TypeError(f"Unknown type in field {field.name}, that has type {field.type}")

        return ',\n'.join(prepared)
