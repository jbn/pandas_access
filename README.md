### Fork of https://github.com/jbn/pandas_access

As of 2023-07-26, this fork incorporates every meaningful upgrade by many contributors. This fork is actively maintained, while upstream is not.

This fork can be added to a `requirements.txt` file like this:
```
git+https://github.com/DeflateAwning/pandas_access.git@master#egg=pandas_access
```

Please Star this repo. Please open Issues on this repo with bug reports, feature requests, and similar.

Other forks are visible using [useful-forks.io](https://useful-forks.github.io/?repo=jbn/pandas_access). Especially interesting forks include:
* [behrenhoff/pandas_access](https://github.com/behrenhoff/pandas_access): Interesting refactor with classes. Failed to address meaningful bugs, unfortunately.

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

If you are on `Windows`, it's a little tougher. Install `mdbtools` for [Windows](https://github.com/lsgunth/mdbtools-win). Manually add to PATH.
1. Download the mdb-tools files from Windows link above. Visit the Releases section, then downloadi the part that says "Source Code (zip)".
2. Extract that to somewhere like `C:/bin/mdbtools-win/mdbtools-win-1.0.0`.
3. Follow these instructions to [add that folder to your environment path](https://linuxhint.com/add-directory-to-path-environment-variables-windows/) (Method 1, but use the path to the mdbtools executable files).
4. Restart your computer or just close and re-open the program you're running it from. You can test that it works by opening a terminal and running `mdb-tables --help` and see that it doesn't fail.

Finally, on all OS's:
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

