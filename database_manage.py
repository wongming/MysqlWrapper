import os, sys
import inspect
import time
import types
import logging, logging.config
import traceback
try:
    import database_config
except ImportError:
    print "database_config.py error or no database_config.py found in path."
    sys.exit(1)

import ConfigParser
import json
import mysql_wrapper
cur_dir = os.path.split(os.path.realpath(__file__))[0]

class DBmanage(object):
    def __init__(self):
        self.db_wrapper = mysql_wrapper.MysqlWrapper()
        self.conf = database_config.DatabaseConfig()

    def create_all_table(self):
        for table_obj in self.conf.tables_objlist:
            self.db_wrapper.execute(table_obj.CRtab_SQL)

    def drop_all_table(self):
        for table_obj in self.conf.tables_objlist:
            self.db_wrapper.execute(table_obj.DROPtab_SQL)

    def creat_table(self, table_Name):
        for table_obj in self.conf.tables_objlist:
            if table_name == table_obj.TABLE_NAME:
                self.db_wrapper.execute(table_obj.CRtab_SQL)

    def drop_table(self, table_name):
        flag = False
        for table_obj in self.conf.tables_objlist:
            if table_name == table_obj.TABLE_NAME:
                self.db_wrapper.execute(table_obj.DROPtab_SQL)
