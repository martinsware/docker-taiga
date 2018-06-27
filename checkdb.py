import os, sys, psycopg2, time

# Checks the DB connection and blocks until the db comes online and returns a query,
# or until the timeout (~1min). Most of the time, the DB is available in 3-5 seconds,
# so 1 minute is more than enough.

# RETURN CODES:
#
# 0: DB came online and already has been configured
# 1: DB came online and needs initial configuration
# 2: DB did not come online in the specified time window

DB_NAME = os.getenv('TAIGA_DB_NAME')
DB_HOST = os.getenv('TAIGA_DB_HOST')
DB_USER = os.getenv('TAIGA_DB_USER')
DB_PASS = os.getenv('TAIGA_DB_PASSWORD')

conn_string = (
    "dbname='" + DB_NAME +
    "' user='" + DB_USER +
    "' host='" + DB_HOST +
    "' password='" + DB_PASS + "'")

# Background polling settings
tryLimit =  250
sleepSeconds = 0.25

print("Waiting for database to come online. Polling every " + str(sleepSeconds) + " seconds in the background until it's online")

# Keep trying to connect until the retry limit is reached or connection success
tryCount = 0
while True:
    try:
        conn = None
        conn = psycopg2.connect(conn_string)
        dbOnline = (conn.closed == 0)

    except psycopg2.Error as e:
        # uncomment this line for debugging
        # print([e, e.pgcode, e.pgerror])
        dbOnline = False

    if dbOnline is False:

        tryCount += 1

        if tryCount < tryLimit:
            # uncomment this line for debugging
            # print("Database is not yet ready. Connection attempt " + str(tryCount) + " of " + str(tryLimit) + ". Sleeping for " + str(sleepSeconds) + " seconds and trying again.\n")
            time.sleep(sleepSeconds)
        else:
            print("Database wait timeout reached. Exiting.")
            sys.exit(2)

    else:
        print("Database is ready.")
        break;


# Once we know the database is online, check to see if the DB has been set up already
cur = conn.cursor()

cur.execute("select * from information_schema.tables where table_name=%s", ('django_migrations',))
exists = bool(cur.rowcount)

if exists is False:
    print("Database does not appear to be setup.")
    sys.exit(1)
else:
    print("Database appears to be setup.")
    sys.exit(0)
