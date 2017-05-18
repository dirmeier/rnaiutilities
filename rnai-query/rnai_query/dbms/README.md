### Tix database

Add meta files to the target infect x database. **A `postgres` database
called `tix` must be running if no sqlite file is provided.** I.e if you want
 to use `postgres` for inserting the meta files, start the postgres service, and
 create a db called `tix`. If you want to use `sqlite3` just provide a file
 name as argument.


This uses a postgres db:

```python
  python dbms.py --path /i/am/a/path/to/data
```


```python
  python dbms.py --path /i/am/a/path/to/data --db  /i/am/a/file/called/tix.db
```


