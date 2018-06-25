import os, sys, psycopg2, time

DB_NAME = os.getenv('TAIGA_DB_NAME')
DB_HOST = os.getenv('TAIGA_DB_HOST')
DB_USER = os.getenv('TAIGA_DB_USER')
DB_PASS = os.getenv('TAIGA_DB_PASSWORD')

conn_string = (
    "dbname='" + DB_NAME +
    "' user='" + DB_USER +
    "' host='" + DB_HOST +
    "' password='" + DB_PASS + "'")
print("Connecting to database:\n" + conn_string)
conn = psycopg2.connect(conn_string)
cur = conn.cursor()

tryLimit = 60
tryCount = 0
sleepSeconds = 1

# Keep trying to connect until the retry limit is reached or connection success
while True:
    cur.execute("select * from information_schema.tables where table_name=%s", ('django_migrations',))
    exists = bool(cur.rowcount)

    if exists is False:

        if tryCount++ < tryLimit:
            print("Database is not yet ready. Connection attempt " + tryCount + " of " tryLimit + ". Sleeping for " + sleepSeconds + " seconds and trying again.\n")
            time.sleep(sleepSeconds)
        else:
            print("\n\nDatabase wait timeout reached after " + tryLimit + " attempts. Exiting.")
            sys.exit(2)

    else:
        print("Database is ready. Continuing with setup.\n\n")
        sys.exit(0)

