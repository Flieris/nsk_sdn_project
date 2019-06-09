import sqlite3



def create_db(dbfile):
    try:
        conn = sqlite3.connect(dbfile)
        return conn
    except sqlite3.Error as e:
        print e

    return None

def create_table(conn,create_sql):
    try:
        c = conn.cursor()
        c.execute(create_sql)
    except sqlite3.Error as e:
        print e


if __name__ == "__main__":
    db = create_db("./statisticsDB.db")
    query1 = """CREATE TABLE IF NOT EXISTS tudpstatistics (
        id integer PRIMARY KEY,
        event_time text not null,
        source_ip text not null,
        source_port integer not null,
        destination_ip text not null,
        destination_port integer not null,
        payload text not null
    )
    """
    query2 = """CREATE TABLE IF NOT EXISTS thoststatistics (
        id text primary key,
        ip_addr text not null,
        eth_addr text not null,
        total_data integer not null
    )
    """
    if db is not None:
        create_table(db,query1)
        create_table(db,query2)
    db.close()