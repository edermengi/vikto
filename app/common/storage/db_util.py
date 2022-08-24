from dataclasses import is_dataclass, asdict, dataclass, fields
from decimal import Decimal
from typing import Any


@dataclass
class Add:
    value: Any


@dataclass
class Del:
    value: Any = None


def _to_dynamodb_type(value):
    if isinstance(value, list):
        return [_to_dynamodb_type(v) for v in value]
    if isinstance(value, Add) or isinstance(value, Del):
        return value.value
    elif is_dataclass(value):
        return asdict(value)
    elif isinstance(value, float):
        return Decimal(value)
    elif isinstance(value, Add):
        return value.value
    else:
        return value


def update_expression(cls, **kwargs):
    if not is_dataclass(cls):
        raise ValueError('First argument must be dataclass')
    entity_fields = {field.name: field for field in fields(cls)}
    set_statements = []
    add_statements = []
    del_statements = []
    attr_names = {}
    attr_values = {}
    for prop, value in kwargs.items():
        if prop not in entity_fields.keys():
            raise ValueError(f'Field [{prop}] is not in {cls}')

        if isinstance(value, Add):
            add_statements.append(f'#{prop} :{prop}')
        elif isinstance(value, Del):
            del_statements.append(f'#{prop} :{prop}')
        else:
            set_statements.append(f'#{prop} = :{prop}')

        attr_names[f'#{prop}'] = prop
        attr_values[f':{prop}'] = _to_dynamodb_type(value)
    update_expressions = []
    if len(set_statements) > 0:
        update_expressions.append("SET " + ", ".join(set_statements))
    if len(add_statements) > 0:
        update_expressions.append("ADD " + ", ".join(add_statements))
    if len(del_statements) > 0:
        update_expressions.append("DELETE " + ", ".join(del_statements))

    return {
        'UpdateExpression': " ".join(update_expressions),
        'ExpressionAttributeValues': attr_values,
        'ExpressionAttributeNames': attr_names

    }
