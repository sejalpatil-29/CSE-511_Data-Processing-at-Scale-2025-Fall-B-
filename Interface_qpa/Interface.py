#!/usr/bin/python3


import psycopg2
import os
import sys


DATABASE_NAME='dds_assignment'
RATINGS_TABLE_NAME='ratings'
RANGE_TABLE_PREFIX='range_part'
RROBIN_TABLE_PREFIX='rrobin_part'
RANGE_QUERY_OUTPUT_FILE='RangeQueryOut.txt'
PONT_QUERY_OUTPUT_FILE='PointQueryOut.txt'
RANGE_RATINGS_METADATA_TABLE ='rangeratingsmetadata'
RROBIN_RATINGS_METADATA_TABLE='roundrobinratingsmetadata'

def RangeQuery(ratingsTableName, ratingMinValue, ratingMaxValue, openconnection):
    cur = openconnection.cursor()
    results = []
    
    try:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'range_part%' ORDER BY table_name")
        range_partitions = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'rrobin_part%' ORDER BY table_name")
        rrobin_partitions = [row[0] for row in cur.fetchall()]
        
        for partition in range_partitions:
            cur.execute("SELECT userid, movieid, rating FROM {0} WHERE rating >= {1} AND rating <= {2}".format(partition, ratingMinValue, ratingMaxValue))
            for row in cur.fetchall():
                results.append([partition, row[0], row[1], row[2]])
        
        for partition in rrobin_partitions:
            cur.execute("SELECT userid, movieid, rating FROM {0} WHERE rating >= {1} AND rating <= {2}".format(partition, ratingMinValue, ratingMaxValue))
            for row in cur.fetchall():
                results.append([partition, row[0], row[1], row[2]])
        
        writeToFile(RANGE_QUERY_OUTPUT_FILE, results)
        
    finally:
        cur.close()


def PointQuery(ratingsTableName, ratingValue, openconnection):
    cur = openconnection.cursor()
    results = []
    
    try:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'range_part%' ORDER BY table_name")
        range_partitions = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'rrobin_part%' ORDER BY table_name")
        rrobin_partitions = [row[0] for row in cur.fetchall()]
        
        for partition in range_partitions:
            cur.execute("SELECT userid, movieid, rating FROM {0} WHERE rating = {1}".format(partition, ratingValue))
            for row in cur.fetchall():
                results.append([partition, row[0], row[1], row[2]])
        
        for partition in rrobin_partitions:
            cur.execute("SELECT userid, movieid, rating FROM {0} WHERE rating = {1}".format(partition, ratingValue))
            for row in cur.fetchall():
                results.append([partition, row[0], row[1], row[2]])
        
        writeToFile(PONT_QUERY_OUTPUT_FILE, results)
        
    finally:
        cur.close()


def writeToFile(filename, rows):
    f = open(filename, 'w')
    for line in rows:
        f.write(','.join(str(s) for s in line))
        f.write('\n')
    f.close()