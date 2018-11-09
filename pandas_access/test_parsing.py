from . import MdbColumn, MdbTable
import numpy as np
# import pytest


def test_column_parsing():
    col = MdbColumn.try_parse_schema_line(" [myName]  Integer NOT NULL,")
    assert col is not None
    assert col.get_dtype() == np.int_
    assert col.get_dtype(promote='int_to_float') == np.float_
    assert col.get_dtype(promote='nullable_int_to_float') == np.int_
    assert col.is_not_null() is True
    assert col.maybe_null() is False

    col = MdbColumn.try_parse_schema_line(" [myName]  Integer,")
    assert col is not None
    assert col.get_dtype() == np.int_
    assert col.get_dtype(promote='int_to_float') == np.float_
    assert col.get_dtype(promote='nullable_int_to_float') == np.float_
    assert col.is_not_null() is False
    assert col.maybe_null() is True

    col = MdbColumn.try_parse_schema_line(" [myName]  DateTime")
    assert col is not None
    assert col.get_dtype() == np.str_
    assert col.get_dtype(promote='int_to_float') == np.str_
    assert col.get_dtype(promote='nullable_int_to_float') == np.str_
    assert col.is_not_null() is False
    assert col.maybe_null() is True


def test_table_parsing():
    t = MdbTable("GreatTable")
    t.parse_columns(
        "CREATE TABLE [ThisNameIsIgnored]\n"
        " (\n"
        "\t[SomeDate]\t\t\tDateTime, \n"
        "\t[SomeTime]\t\t\tDateTime NOT NULL, \n"
        "\t[UserName]\t\t\tText (100), \n"
        "\t[IsTested]\t\t\tBoolean NOT NULL, \n"
        "\t[Value]\t\t\tDouble, \n"
        "\t[Number]\t\t\tLong Integer \n"
        ");")
    assert t.get_name() == 'GreatTable'
    cols = t.get_columns()
    assert len(cols) == 6
    assert cols[0].get_name() == 'SomeDate'
    assert cols[0].get_dtype() == np.str_
    assert cols[0].maybe_null() is True
    assert cols[1].maybe_null() is False
    assert cols[4].get_name() == 'Value'
    assert cols[4].get_dtype() == np.float_
    assert cols[5].get_name() == 'Number'
    assert cols[5].get_dtype() == np.int64
