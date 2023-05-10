# What is this?

A tiny, `subprocess`-based tool for reading a 
[MS Access](https://products.office.com/en-us/access) 
database (`.rdb`) as a [Pandas](http://pandas.pydata.org/) 
[DataFrame](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html). 

## Installation

To read the database, this package (thinly!) wraps 
[MDBTools](https://github.com/mdbtools/mdbtools). Since I assume you're already 
using Pandas, it should be your only installation requirement. 

If you are on `OSX`, install it via [Homebrew](http://brew.sh/):

```sh
$ brew install mdbtools
```

If you are on `Debian`, install it via apt:
```sh
$ sudo apt install mdbtools
```

Then, do,
```sh
$ pip install pandas_access
```

## Usage

```python
import pandas_access as pd_access

# Listing the tables.
for tbl in pd_access.list_tables("my.mdb"):
    print(tbl)
    
# Read a small table.
df = pd_access.read_table("my.mdb", "MyTable")

# Read a huge table.
accumulator = []
for chunk in pd_access.read_table("my.mdb", "MyTable", chunksize=10000):
    accumulator.append(f(chunk))
```

If you need more power than this, see: 
[pyodbc](https://github.com/mkleehammer/pyodbc).

## Testing

I needed this code in a quick pinch -- I had no access to MS Access, and I had
a single `.mdb` file. If someone with Access would like to create a tiny 
database for unit-testing purposes, I'd be much obliged. 

