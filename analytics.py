import configparser
import psycopg2
import pandas as pd
from sql_queries import analytical_queries

def analyze_tables(cur, conn):
    """
    Function:
        Executes queries listed in chapter analytical_queries in file sql_queries.py
    Args:
        cur,conn: cursor of database connection string, database connection string 
    Returns:
        Drops a CSV file with result data in current folder
    """
    list_results=[]
    for query in analytical_queries:
        cur.execute(query)
        result=cur.fetchall()
        list_results.append(result)
    df=pd.DataFrame(list_results)
    df.to_csv("analytics.csv")

def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()

    list_results=analyze_tables(cur, conn)
    print(list_results)
    conn.close()
    return list_results

if __name__ == "__main__":
    main()