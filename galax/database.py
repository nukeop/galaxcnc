import logging
import os
import sqlite3

logger = logging.getLogger(__name__)

DB_NAME = "galax.db"

class Database(object):
    def __init__(self):
        logger.info("Initializing database connection")

        if not os.path.exists(DB_NAME):
            self.init_db()
        else:
            self.conn = sqlite3.connect(DB_NAME)
            self.cur = self.conn.cursor()


    def init_db(self):
        logger.info("Creating a new database at {}".format(DB_NAME))
        self.conn = sqlite3.connect(DB_NAME)
        self.cur = self.conn.cursor()

        self.cur.execute('CREATE TABLE workers (id integer primary key, name'
                         ' varchar(255), pubkey varchar(4096))')

        self.conn.commit()


    def cleanup(self):
        self.conn.close()
