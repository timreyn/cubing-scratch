#!/bin/bash
# This script fetches the latest WCA export and imports it into a local MYSQL
# database.  To be run periodically, before re-generating rankings.  Should be
# run from the root directory.
set -e

# Load the database config.
DB_USERNAME='root'
DB_PASSWORD=''
DB_DATABASE='wca'
DB_HOSTNAME='localhost'

# Find the name of the latest export.
LATEST_EXPORT=$(curl https://www.worldcubeassociation.org/results/misc/export.html \
| grep SQL:.*WCA_export \
| sed -s 's/.*\(WCA_export[0-9A-Za-z_]*\).sql.zip.*/\1/')

echo 'Fetching export '$LATEST_EXPORT
echo $LATEST_EXPORT > latest_export

# Fetch the database and unzip it.
URL_TO_FETCH="https://www.worldcubeassociation.org/results/misc/$LATEST_EXPORT.sql.zip"
TMP_DIR=".wca_rankings.tmp_export"
mkdir $TMP_DIR || rm -R -f $TMP_DIR/*
ZIP_FILE="$TMP_DIR/$LATEST_EXPORT.sql.zip"

curl $URL_TO_FETCH > $ZIP_FILE
unzip $ZIP_FILE -d $TMP_DIR

MYSQL_COMMAND="mysql -u $DB_USERNAME -p$DB_PASSWORD -h $DB_HOSTNAME $DB_DATABASE"

# Import the WCA export.
$MYSQL_COMMAND < $TMP_DIR/WCA_export.sql
# Run extra commands such as setting primary keys.
$MYSQL_COMMAND < extra_sql_commands.sql

# Cleanup.
rm -R -f $TMP_DIR
