import re
import subprocess
import pandas as pd
import numpy as np
try:
    from StringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO


TABLE_RE = re.compile("CREATE TABLE \[(\w+)\]\s+\((.*?\));",
                      re.MULTILINE | re.DOTALL)


class MdbTable:
    """ A MdbTable is basically a list of MdbColumns with some added
    functionality.
    :param name: Name of the table
    """
    def __init__(self, name):
        self._name = name
        # array instead of dict to preserve the order
        self._columns = []

    def update_dtypes(self, newDtypes):
        """ sets the dtype manually to the given types
        :param newDtypes: a dictionary {columnName: newDtype}
        """
        for c in self._columns:
            if c.get_name() in newDtypes:
                c.set_dtype(newDtypes[c.get_name()])

    def get_dtypes(self, promote=None):
        """ return a dictionary of {columnName: dataType}
        :param promote: see MdbColumn.get_dtype
        """
        return {c.get_name(): c.get_dtype(promote) for c in self._columns}

    def date_field_indices(self):
        """ returns the column indices of all datetime fields """
        result = []
        for idx, col in enumerate(self._columns):
            if col.is_datetime():
                result.append(idx)
        return result

    def parse_columns(self, defs_str, implicit_string=True):
        """
        Initialize the columns of the table from a schema definition string
        created by mdb-schema. The defs_str needs to look like:
            [FieldA]   Text (100) NOT NULL,
            [FieldB]   DateTime NOT NULL
            ...
        Even though the table name can be included in the defs_str, the table
        name will NOT be altered by this function.
        """
        defs = []
        lines = defs_str.splitlines()
        for line in lines:
            col = MdbColumn.try_parse_schema_line(line)
            if col is None:
                continue
            if col.get_dtype() is None and implicit_string:
                col.set_dtype(np.str_)
            defs.append(col)
        self._columns = defs

    def get_columns(self):
        return self._columns

    def get_name(self):
        return self._name


class MdbColumn:
    __type_conversions = {
        'single': np.float32,
        'double': np.float64,
        'long integer': np.int64,
        'integer': np.int_,
        'text': np.str_,
        'long text': np.str_,
        'boolean': np.bool_,
        'datetime': np.str_,  # additional special handling
    }
    __schema_line_regex = re.compile(
        "^\s*\[(\w+)\]\s*(.*?)(?:\s+(NOT NULL))?,?\s*$", re.IGNORECASE)

    @staticmethod
    def try_parse_schema_line(line):
        """ Create a new MdbColumn object from the given line if possible.
        If the format doesn't fit, return None. """
        m = MdbColumn.__schema_line_regex.match(line)
        if m:
            return MdbColumn(m.group(1), m.group(2), m.group(3) == 'NOT NULL')
        return None

    def __init__(self, name, mdb_type_name, not_null):
        self._name = name
        self._data_type_name = mdb_type_name
        self._dtype = self.__get_numpy_type(mdb_type_name)
        self._not_null = not_null

    def is_datetime(self):
        return self._data_type_name.lower().startswith('datetime')

    def __get_numpy_type(self, mdb_type_name):
        mdb_name_lc = mdb_type_name.lower()
        for mdbstart, nptype in MdbColumn.__type_conversions.items():
            if mdb_name_lc.startswith(mdbstart):
                return nptype
        # print("Unknown type:", mdb_type_name)
        return None

    def get_name(self):
        return self._name

    def get_dtype(self, promote=None):
        """
        Returns the data type of a column, possibly promoted to a different
        type - promotions are useful for NAN values where no NAN is supported
        in pandas.
        :param promote: Valid values: 'int_to_float', 'nullable_int_to_float'
        """
        if self._dtype in [np.int_, np.int64]:
            if (promote == 'nullable_int_to_float' and self.maybe_null()) or \
               (promote == 'int_to_float'):
                return np.float_
        return self._dtype

    def set_dtype(self, newtype):
        self._dtype = newtype

    def is_not_null(self):
        return self._not_null

    def maybe_null(self):
        return not self.is_not_null()


def list_tables(rdb_file, encoding="utf-8"):
    """
    :param rdb_file: The MS Access database file.
    :param encoding: The content encoding of the output. MDBTools
        print the output in UTF-8.
    :return: A list of the tables in a given database.
    """
    # We use -1 (one table name per line) to support stange table names
    tables = subprocess.check_output(['mdb-tables', '-1', rdb_file])
    return tables.decode(encoding).splitlines()


def read_schema(rdb_file, encoding='utf8', implicit_string=True):
    """
    :param rdb_file: The MS Access database file.
    :param encoding: The schema encoding. I'm almost positive that MDBTools
        spits out UTF-8, exclusively.
    :return: a dictionary of tablename -> MdbTable object
    """
    output = subprocess.check_output(['mdb-schema', rdb_file])
    lines = output.decode(encoding).splitlines()
    schema_ddl = "\n".join(l for l in lines if l and not l.startswith('-'))

    schema = {}
    for tablename, defs in TABLE_RE.findall(schema_ddl):
        table = MdbTable(tablename)
        table.parse_columns(defs, implicit_string)
        schema[tablename] = table

    return schema


def read_table(rdb_file, table_name, *args, **kwargs):
    """
    Read a MS Access database as a Pandas DataFrame.

    Unless you set `converters_from_schema=False`, this function assumes you
    want to infer the schema from the Access database's schema. This sets the
    `dtype` argument of `read_csv`, which makes things much faster, in most
    cases. If you set the `dtype` keyword argument also, it overrides
    inferences. The `schema_encoding and implicit_string keyword arguments are
    passed through to `read_schema`.

    In case you have integer columns with NaNs (not supported by pandas), you
    can either manually set the corresponding columns to float by passing the
    `dtype` argument. By passing `promote='int_to_float'`, all ints are
    automatically converted to float64. For NOT NULL int columns, it is safe
    to keep them as int. To promote only int columns that aren't marked NOT
    NULL, pass `promote='nullable_int_to_float'`to `read_table`.

    I recommend setting `chunksize=k`, where k is some reasonable number of
    rows. This is a simple interface, that doesn't do basic things like
    counting the number of rows ahead of time. You may inadvertently start
    reading a 100TB file into memory. (Although, being a MS product, I assume
    the Access format breaks after 2^32 bytes -- har, har.)

    :param rdb_file: The MS Access database file.
    :param table_name: The name of the table to process.
    :param args: positional arguments passed to `pd.read_csv`
    :param kwargs: keyword arguments passed to `pd.read_csv`
    :return: a pandas `DataFrame` (or, `TextFileReader` if you set
        `chunksize=k`)
    """
    if kwargs.pop('converters_from_schema', True):
        specified_dtypes = kwargs.pop('dtype', {})
        schema_encoding = kwargs.pop('schema_encoding', 'utf8')
        promote = kwargs.pop('promote', None)
        schemas = read_schema(rdb_file, schema_encoding,
                              kwargs.pop('implicit_string', True))
        table = schemas[table_name]
        table.update_dtypes(specified_dtypes)
        kwargs['dtype'] = table.get_dtypes(promote)
        kwargs['parse_dates'] = table.date_field_indices()

    cmd = ['mdb-export', '-D', '%Y-%m-%d %H:%M:%S', rdb_file, table_name]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    try:
        return pd.read_csv(proc.stdout, *args, **kwargs)
    except ValueError as ve:
        if 'Integer column has NA values' in str(ve):
            msg = str(ve).splitlines()[-1]
            raise ValueError("\n".join((
                msg,
                "Consider passing promote='nullable_int_to_float' or",
                "passing promote='int_to_float' to read_table")))
        else:
            raise ve
