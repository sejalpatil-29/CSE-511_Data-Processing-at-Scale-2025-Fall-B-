#!/usr/bin/python3

import psycopg2

def getOpenConnection(user='postgres', password='root', dbname='postgres'):
    return psycopg2.connect("dbname='" + dbname + "' user='" + user + "' host='localhost' password='" + password + "'")


def loadRatings(ratingstablename, ratingsfilepath, openconnection):
    cur = openconnection.cursor()
    
    try:
        cur.execute("DROP TABLE IF EXISTS {0} CASCADE".format(ratingstablename))
        openconnection.commit()
        
        cur.execute("""CREATE TABLE {0} (
            userid INT,
            movieid INT,
            rating FLOAT
        )""".format(ratingstablename))
        openconnection.commit()
        
        with open(ratingsfilepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split('::')
                if len(parts) >= 3:
                    userid = int(parts[0])
                    movieid = int(parts[1])
                    rating = float(parts[2])
                    
                    cur.execute(
                        "INSERT INTO {0} (userid, movieid, rating) VALUES ({1}, {2}, {3})".format(
                            ratingstablename, userid, movieid, rating
                        )
                    )
        
        openconnection.commit()
        
    except Exception as e:
        openconnection.rollback()
        raise
    finally:
        cur.close()


def rangePartition(ratingstablename, numberofpartitions, openconnection):
    cur = openconnection.cursor()
    
    try:
        range_size = 5.0 / numberofpartitions
        
        for i in range(numberofpartitions):
            table_name = "range_part{0}".format(i)
            
            cur.execute("DROP TABLE IF EXISTS {0} CASCADE".format(table_name))
            openconnection.commit()
            
            cur.execute("""CREATE TABLE {0} (
                userid INT,
                movieid INT,
                rating FLOAT
            )""".format(table_name))
            openconnection.commit()
            
            lower_bound = i * range_size
            upper_bound = (i + 1) * range_size
            
            if i == 0:
                cur.execute(
                    "INSERT INTO {0} (userid, movieid, rating) SELECT userid, movieid, rating FROM {1} WHERE rating >= {2} AND rating <= {3}".format(
                        table_name, ratingstablename, lower_bound, upper_bound
                    )
                )
            else:
                cur.execute(
                    "INSERT INTO {0} (userid, movieid, rating) SELECT userid, movieid, rating FROM {1} WHERE rating > {2} AND rating <= {3}".format(
                        table_name, ratingstablename, lower_bound, upper_bound
                    )
                )
            openconnection.commit()
        
    except Exception as e:
        openconnection.rollback()
        raise
    finally:
        cur.close()


def roundRobinPartition(ratingstablename, numberofpartitions, openconnection):
    cur = openconnection.cursor()
    
    try:
        for i in range(numberofpartitions):
            table_name = "rrobin_part{0}".format(i)
            
            cur.execute("DROP TABLE IF EXISTS {0} CASCADE".format(table_name))
            openconnection.commit()
            
            cur.execute("""CREATE TABLE {0} (
                userid INT,
                movieid INT,
                rating FLOAT
            )""".format(table_name))
            openconnection.commit()
        
        cur.execute("SELECT userid, movieid, rating FROM {0}".format(ratingstablename))
        rows = cur.fetchall()
        
        for idx, row in enumerate(rows):
            partition_idx = idx % numberofpartitions
            table_name = "rrobin_part{0}".format(partition_idx)
            
            cur.execute(
                "INSERT INTO {0} (userid, movieid, rating) VALUES ({1}, {2}, {3})".format(
                    table_name, row[0], row[1], row[2]
                )
            )
        
        openconnection.commit()
        
    except Exception as e:
        openconnection.rollback()
        raise
    finally:
        cur.close()


def roundrobininsert(ratingstablename, userid, itemid, rating, openconnection):
    cur = openconnection.cursor()
    
    try:
        cur.execute(
            "INSERT INTO {0} (userid, movieid, rating) VALUES ({1}, {2}, {3})".format(
                ratingstablename, userid, itemid, rating
            )
        )
        openconnection.commit()
        
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'rrobin_part%'
            ORDER BY table_name
        """)
        partition_tables = [row[0] for row in cur.fetchall()]
        
        if partition_tables:
            total_count = 0
            for table in partition_tables:
                cur.execute("SELECT COUNT(*) FROM {0}".format(table))
                total_count += cur.fetchone()[0]
            
            partition_idx = total_count % len(partition_tables)
            table_name = "rrobin_part{0}".format(partition_idx)
            
            cur.execute(
                "INSERT INTO {0} (userid, movieid, rating) VALUES ({1}, {2}, {3})".format(
                    table_name, userid, itemid, rating
                )
            )
            openconnection.commit()
        
    except Exception as e:
        openconnection.rollback()
        raise
    finally:
        cur.close()


def rangeinsert(ratingstablename, userid, itemid, rating, openconnection):
    cur = openconnection.cursor()
    
    try:
        cur.execute(
            "INSERT INTO {0} (userid, movieid, rating) VALUES ({1}, {2}, {3})".format(
                ratingstablename, userid, itemid, rating
            )
        )
        openconnection.commit()
        
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'range_part%'
            ORDER BY table_name
        """)
        partition_tables = [row[0] for row in cur.fetchall()]
        
        if partition_tables:
            numberofpartitions = len(partition_tables)
            range_size = 5.0 / numberofpartitions
            
            partition_idx = 0
            
            if rating >= 0 and rating <= range_size:
                partition_idx = 0
            else:
                for i in range(1, numberofpartitions):
                    lower_bound = i * range_size
                    upper_bound = (i + 1) * range_size
                    if rating > lower_bound and rating <= upper_bound:
                        partition_idx = i
                        break
            
            table_name = "range_part{0}".format(partition_idx)
            
            cur.execute(
                "INSERT INTO {0} (userid, movieid, rating) VALUES ({1}, {2}, {3})".format(
                    table_name, userid, itemid, rating
                )
            )
            openconnection.commit()
        
    except Exception as e:
        openconnection.rollback()
        print(f"Error in rangeinsert: {e}")
        raise
    finally:
        cur.close()


def createDB(dbname='dds_assignment'):
    con = getOpenConnection(dbname='postgres')
    con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    cur.execute('SELECT COUNT(*) FROM pg_catalog.pg_database WHERE datname=\'%s\'' % (dbname,))
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute('CREATE DATABASE %s' % (dbname,))
    else:
        print('A database named {0} already exists'.format(dbname))

    cur.close()
    con.close()


def deletepartitionsandexit(openconnection):
    cur = openconnection.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    l = []
    for row in cur:
        l.append(row[0])
    for tablename in l:
        cur.execute("drop table if exists {0} CASCADE".format(tablename))

    cur.close()


def deleteTables(ratingstablename, openconnection):
    try:
        cursor = openconnection.cursor()
        if ratingstablename.upper() == 'ALL':
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = cursor.fetchall()
            for table_name in tables:
                cursor.execute('DROP TABLE %s CASCADE' % (table_name[0]))
        else:
            cursor.execute('DROP TABLE %s CASCADE' % (ratingstablename))
        openconnection.commit()
    except psycopg2.DatabaseError as e:
        if openconnection:
            openconnection.rollback()
        print('Error %s' % e)
    except IOError as e:
        if openconnection:
            openconnection.rollback()
        print('Error %s' % e)
    finally:
        if cursor:
            cursor.close()