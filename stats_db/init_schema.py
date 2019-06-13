#!/usr/bin/env python
import sqlite3
import logging



def create_db(dbfile):
    try:
        conn = sqlite3.connect(dbfile)
        logging.info("Database created")
        return conn
    except sqlite3.Error as e:
        logging.error(
            "Unexcepted error during database creation" + str(e))

    return None


def create_table(conn, create_sql):
    try:
        c = conn.cursor()
        c.execute(create_sql)
    except sqlite3.Error as e:
        logging.error(
            "Unexcepted error during table creation" + str(e))


if __name__ == "__main__":
    logging.basicConfig(filename="./stats_db/init_schema.log", level=logging.DEBUG)
    logging.info("---SCRIPT START---")
    db = create_db("./stats_db/statisticsDB.db")
    query1 = """CREATE TABLE IF NOT EXISTS tudpstatistics (
        id integer PRIMARY KEY,
        host_id integer not null,
        event_time text not null,
        source_eth_addr text not null,
        source_ip text not null,
        source_port integer not null,
        destination_eth_addr text not null,
        destination_ip text not null,
        destination_port integer not null,
        payload text not null
    )
    """
    logging.debug("Prepared query #1 " + query1)
    query2 = """CREATE TABLE IF NOT EXISTS thoststatistics (
        id integer primary key,
        ip_addr text not null,
        eth_addr text not null,
        total_data integer not null
    )
    """
    logging.debug("[Prepared query #2 " + query2)
    if db is not None:
        create_table(db, query1)
        create_table(db, query2)
    logging.info("Schema correctly created")
    logging.info("---SCRIPT END---")
    db.close()
