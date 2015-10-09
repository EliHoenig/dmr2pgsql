#il-dmr

This repository contains a couple of scripts for downloading the Illinois EPA Discharge Monitoring Reports (DMR) and importing them into a database.

The main script is `dmr.py` which downloads the csv files from the EPA website. Some useful examples:

To download all dmr csv files (to `il-dmr/csv` directory) use 

```python dmr.py```

To download and import csv files (serially, which is good in case of failure) first run `create.csv` and then

```python dmr.py --psql```

The import is done using `psql -c '\copy` so place the relevant PostgreSQL credentials in [environment variables](http://www.postgresql.org/docs/9.1/static/libpq-envars.html). To download a particular year

```python dmr.py --year 2015```

To download a particular NPDES id (all years, unless `--year` is specified)

```python dmr.py --npdes IL0000035```

By default existing csv files will not be re-downloaded. To re-download (useful for updating a year in progress)

```python dmr.py -o --year 2015```

There are two additional scripts:

`create.sql` for creating the target dmr table

`import.sh` for bulk import of csvs after they have been downloaded.
