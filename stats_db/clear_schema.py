#!/usr/bin/env python
import sqlite3
import logging


if __name__ == "__main__":
    logging.basicConfig(filename="./stats_db/init_schema.log", level=logging.DEBUG)
    try:
        logging.info("---SCRIPT START---")
        con = sqlite3.connect("./stats_db/statisticsDB.db")

        c = con.cursor()
        logging.debug("dropping table  THOSTSTATISTICS")
        c.execute("DROP TABLE THOSTSTATISTICS")
        logging.debug("dropping table  TUDPSTATISTICS")
        c.execute("DROP TABLE TUDPSTATISTICS")
    except sqlite3.Error as e:
        logging.error(
            "Unexcepted error during script execution" + str(e))

    finally:
        logging.info("Schema correctly cleared")
        logging.info("---SCRIPT END---")
        c.close()
        con.close()
