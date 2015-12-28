# -*- coding:utf-8 -*-
import sys,os
import types
import inspect
reload(sys)
sys.setdefaultencoding('utf-8')

class DatabaseConfig(object):
    CHARSET = 'utf8'
    UNICODE = True
    WARNINGS = True
    HOST = 'localhost'
    USER = 'root'
    PORT = 3306
    PASSWORD = ''
    DATABASE = 'atrs_test'

    def __init__(self):
        import table
        self.tables_objlist = []
        self.tables_namelist = []
        table_moudle = sys.modules['table']
        for name, table_class in inspect.getmembers(table_moudle):
            if (not type(table_class) == types.TypeType):
                continue
            if issubclass(table_class, table.BaseTable) and (not name == 'BaseTable'):
                #print 'tablename = %s\n' % table_class.TABLE_NAME
                self.tables_objlist.append(table_class)
                self.tables_namelist.append(table_class.TABLE_NAME)
