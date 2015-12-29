#encoding=utf-8
import os, sys
reload(sys)
sys.setdefaultencoding('utf8')
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, cur_dir)
#import string_util
import mysql.connector
from mysql.connector.conversion import *
try:
    import database_config
except ImportError:
    print "database_config.py error or no database_config.py found in path."
    sys.exit(1)
import logging, logging.config
import traceback

class MysqlWrapper:
    mysql = None
    conf = None
    cursor = None
    logging.config.fileConfig(os.path.join(cur_dir, 'log.conf'))
    default_logger = logging.getLogger('MysqlWrapper')
    def __init__(self, logger=default_logger, conf = database_config.DatabaseConfig()):
        self.conf = conf
        self.logger = logger
        self._init_db()
        self.conv = MySQLConverter()

    def __del__(self):
        self.close()

    def _init_db(self):
        try:
            self.mysql = mysql.connector.Connect(user=self.conf.USER, password=self.conf.PASSWORD, charset='utf8', host=self.conf.HOST, port=self.conf.PORT, autocommit=True, connection_timeout = 60, connect_timeout = 60)
            self.cursor = self.mysql.cursor()
        except:
            self.logger.error('Connect mysql failed.')
            print traceback.print_exc()
            self.close()
            sys.exit(-1)

        self._do_use(self.conf.DATABASE)
        self.logger.debug('Mysql init success.')

    def _do_use(self, dbName):
        if self._do_use_impl(dbName):
            self.logger.info(dbName)
            return
        self.logger.error('DATABASE: [%s] not exist.' % dbName)
        self.close()
        sys.exit(-1)

    def _do_use_impl(self, dbName):
        try:
            self.mysql.cmd_init_db(dbName)
        except:
            self.logger.error('Init db: [%s] failed.' % dbName)
            return False
        return True

    def close(self):
        if self.mysql.is_connected():
            self.cursor.close()
            self.mysql.close()
            self.logger.debug('Close Database: [%s] success.' % self.conf.DATABASE)

    def execute(self, line):
        #print line
        try:
            self.logger.debug("execute cmd: " + line)
            self.cursor.execute(line)
        except Exception, e:
            error_line = line
            if len(line) > 200:
                error_line = line[:500] + " ..."
            self.logger.error('Execute line: [%s] failed.' % error_line)
            import traceback
            errorstring = traceback.format_exc()
            self.logger.error(errorstring)
            return False
        return True

    def query(self, line):
        #print line
        'return None if query failed, return list is query success'
        try:
            if not self.execute(line):
                self.logger.error('query line: [%s] failed.' % line)
                return None
            return self.cursor.fetchall()
        except:
            self.logger.error('Run line failed. line: [%s]' % line)
            return None

    def _get_all_fields(self, tableName):
        line = 'show fields from %s ;' % (tableName)
        columns = self.query(line)
        if columns == None:
            self.logger.error('Get fields from table: [%s] failed.' % tableName)
            return list()
        fields = list()
        for column in columns:
            if len(column) > 0:
                fields.append(column[0]);
        return fields

    def _convert_cond_dict(self, cond_dict):
        keylist = cond_dict.keys()
        key_length = len(keylist)
        if key_length ==0:
            return ' '
        cond_string = ' where '
        for index in range(key_length):
            key = keylist[index]
            value = str(cond_dict[key])
            if index != key_length - 1:
                cond_string += ' %(colname)s = "%(colvalue)s" and ' % {'colname': key, 'colvalue': value}
            else:
                cond_string += ' %(colname)s = "%(colvalue)s" ' % {'colname': key, 'colvalue': value}
        return cond_string

    def _convert_order_dict(self, order_dict):
        keylist = order_dict.keys()
        key_length = len(keylist)
        if key_length ==0:
            return ' '
        order_str =' order by '
        for index in range(key_length):
            key = keylist[index]
            value = str(order_dict[key])
            if index != key_length - 1:
                order_str += ' %(colname)s %(direction)s, ' % {'colname': key, 'direction': value}
            else:
                order_str += ' %(colname)s %(direction)s ' % {'colname': key, 'direction': value}
        return order_str

    def _convert_text(text):
        try:
            text = eval(text)
        except:
            pass
        return text

    def insert_row(self, tableName, value_map):
        field_names_str = ''
        field_values_str = ''
        keys = value_map.keys()
        key_length = len(keys)
        for index in range(key_length):
            field_name = keys[index]
            field_value = value_map[field_name]
            if field_value == None:
                continue
            field_names_str += field_name
            if type(field_value) == int:
                field_value = str(field_value)
            field_values_str += '"' + field_value + '"'
            if (index != key_length - 1):
                field_names_str += ','
                field_values_str += ','
        insert_str = 'insert into ' + tableName + '(' + field_names_str + ') values (' + field_values_str + ');'
        if self.execute(insert_str):
            return True
        else :
            self.logger.error('Insert row into table: %s failed.' % tableName)
            return False

    def clear_rows(self, tableName, key, value):
        line = 'DELETE FROM %(tableName)s where %(key)s = "%(value)s" ;' % {'tableName': tableName, 'key': key, 'value': value}
        if not self.execute(line):
            self.logger.error('Clear rows from table: [%s] by key: [%s], value: [%s] failed. Exit!' % (tableName, key, str(value)))
            self.close()
            sys.exit(-1)

    def clear_row_by_id(self, tableName, id):
        ids = '(%s)' % id
        self.clear_rows_by_ids(tableName, ids)

    def	clear_rows_by_ids(self, tableName, ids):
        line = 'DELETE FROM %(tableName)s where id in (%(ids)s) ;' % {'tableName': tableName, 'ids': ids}
        if not self.execute(line):
            self.logger.error('Clear rows from table: [%s] by ids, ids: [%s] failed. Exit!' % (tableName, ids))
            self.close()
            sys.exit(-1)

    def clear_rows_by_dict(self, tableName, cond_dict):
        keylist = cond_dict.keys()
        cond_string = self._convert_cond_dict(cond_dict)
        line = 'DELETE FROM %(tableName)s %(condition)s;' % {'tableName': tableName, 'condition': cond_string}
        if not self.execute(line):
            self.logger.error('Clear rows from table: [%s] by condition: [%s] failed. Exit!' % (tableName, cond_dict))
            return False
        return True

	"""修改"""
    def update_value(self, tableName, cond_name, cond_value, value_map):
        return self.update_value_by_dict(tableName, {cond_name:cond_value}, value_map)

    def update_value_by_id(self, tableName, id, value_map):
        return self.update_value(tableName, 'id', id, value_map)

    def update_value_by_dict(self, tableName, cond_dict, value_map):
        sql_str = 'update ' + tableName + ' set '
        keylist = value_map.keys()
        for index in range(len(keylist)):
            key = keylist[index]
            if value_map[key] == None:
                value = "null"
                sql_str += ' %(colname)s = %(colvalue)s' % {'colname': key, 'colvalue': value}
            else:
                value = str(value_map[key])
                sql_str += ' %(colname)s = "%(colvalue)s"' % {'colname': key, 'colvalue': value}
            if index != len(keylist) - 1:
                sql_str += ','
        keylist = cond_dict.keys()
        where_str = self._convert_cond_dict(cond_dict)
        sql_str += where_str
        return self.execute(sql_str)

    def get_row(self, tableName, id_name, id_value, select_fields = '*'):
        line = 'select %(field)s from %(tableName)s where %(id_name)s = %(id_value)s;' % {'field': select_fields, 'tableName':tableName, 'id_name':id_name, 'id_value':id_value}
        rows = self.query(line)

        if select_fields == '*':
            fields = self._get_all_fields(tableName)
        else:
            splited_fields = select_fields.split(',')
            fields = [onefield.strip() for onefield in splited_fields if onefield.strip() != '']

        row_map = dict()
        if rows == None or len(rows) == 0:
            self.logger.error('Get row from table: [%s] by [%s]: [%s] failed.' %(tableName, id_name, id_value))
            return row_map
        row = rows[0]
        if len(row) != len(fields):
            self.logger.error('Row fields count dismatched. Expect: [%d], actual: [%d]' %(len(fields), len(row)))
            return row_map
        for i in range(0, len(row)):
            row_map[fields[i]] = row[i]
        return row_map

    def get_row_by_id(self, tableName, id, select_fields = '*'):
        return self.get_row(tableName, 'id', id, select_fields)

    def get_rows(self, tableName, start, limit, select_fields = '*', order_dict={}):
        return self.get_rows_by_dict(tableName, start, limit, {}, select_fields =select_fields, order_dict=order_dict)

    def get_rows_by_dict(self, tableName, start, limit, cond_dict, select_fields = '*', order_dict={}):
        order_str = self._convert_order_dict(order_dict)
        cond_str = self._convert_cond_dict(cond_dict)
        line = 'select %(fields)s from %(tableName)s %(condition)s %(order)s limit %(start)s,%(limit)s;' \
                % {'fields': select_fields, 'tableName': tableName, 'condition': cond_str, 'order': order_str,'start':start,'limit':limit}
        row_data = self.query(line)
        if row_data == None or len(row_data) == 0:
            #self.logger.warning('Get rows from table: [%s] failed.' % tableName)
            return list()
        rows = list()
        if select_fields == '*':
            fields = self._get_all_fields(tableName)
        else:
            splited_fields = select_fields.split(',')
            fields = [fd.strip() for fd in splited_fields if fd.strip() != '']

        for row in row_data:
            row_map = dict()
            if len(row) != len(fields):
                continue
            for i in range(len(row)):
                row_map[fields[i]] = row[i]
            rows.append(row_map)
        return rows

    def count(self, tableName, cond_dict=None):
        cond_str = ''
        if cond_dict:
            cond_str += self._convert_cond_dict(cond_dict)
        line = 'select count(*) from %(tableName)s %(condition)s' \
                % {'tableName': tableName, 'condition': cond_str}
        rows = self.query(line)
        if rows is None:
            return -1
        return rows[0][0]

    def isunique_by_value(self, tableName, cond_key, cond_value):
        return self.isunique_by_dict(tableName, {cond_key: cond_value})

    def isunique_by_dict(self, tableName, cond_dict):
        rows = self.get_rows_by_dict(tableName, 0, 1, cond_dict)
        if len(rows) == 0:
            return True
        else:
            return False

def test():
    db = MysqlWrapper()
    '''
    db.insert_row('t_account', {"username": "1", "password": "z"})
    db.insert_row('t_account', {"username": "2", "password": "bx"})
    db.insert_row('t_account', {"username": "3", "password": "c"})
    db.insert_row('t_account', {"username": "4", "password": "d"})
    db.insert_row('t_account', {"username": "5", "password": "xxs"})
    db.insert_row('t_account', {"username": "6", "password": "x"})
    db.insert_row('t_account', {"username": "7", "password": "g"})
    db.insert_row('t_account', {"username": "8", "password": "n"})
    db.insert_row('t_account', {"username": "9", "password": "y"})
    db.insert_row('t_account', {"username": "10", "password": "o"})

    db.insert_row('t_account', {"username": "insertname", "password": "1111"})
    db.insert_row('t_account', {"username": "insertname", "password": "1111"})
    db.insert_row('t_account', {"username": "insertname", "password": "1111"})
    db.insert_row('t_account', {"username": "insertname", "password": "1111"})
    db.clear_rows('t_account', 'username','insertname1')
    db.clear_row_by_id('t_account', 8)
    db.clear_rows_by_ids('t_account', '7,8,9')
    db.clear_rows_by_dict('t_account',{'username':'insertname'})

    db.update_value('t_account', 'username','wm',{'name':'update_value'})
    db.update_value_by_id('t_account', 1,{'name':'update_value_by_id'})
    db.update_value_by_dict('t_account', {'username': 'wm','password': 'changed'},{'name': 'update_value_by_dict', 'is_super': 1})
    '''
    #print db.get_rows_by_dict('t_account', 0, 1, {'username':'wm','password':'changed'}, 'username,password',{'username':'desc','password':'asc'})
    #print db.get_rows_by_dict('t_account', 0, 5, {}, 'id',{'id':'desc','username':'asc','password':'asc'})
    print db.isunique_by_dict('t_account',{'username':1})
    print db.isunique_by_dict('t_account',{'username':111})
    print db.isunique_by_value('t_account','username',1)
    print db.isunique_by_value('t_account','username',111)
if __name__ == '__main__':
    test()
