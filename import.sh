#!/bin/bash
for filename in csv/*.csv; do
    echo $filename
    psql -c "\COPY dmr FROM '$filename' WITH CSV HEADER"
done
