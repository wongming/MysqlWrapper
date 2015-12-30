#encoding = utf-8
import os,sys
import time
import re
import types
import json
reload(sys)
sys.setdefaultencoding('utf8')
import mysql_wrapper
import logging, logging.config

cur_dir = os.path.split(os.path.realpath(__file__))[0]

class Result(object):
    SUCC = 0
    EMPTY = 1
    DUP = 2
    ERR = 3

RT = Result()

class BaseTable(object):
    logging.config.fileConfig(os.path.join(cur_dir, 'log.conf'))
    logger = logging.getLogger("db")
    def __init__(self):
        self.db = mysql_wrapper.MysqlWrapper()

    def execute(self, line):
        return self.db_wrapper.execute(line)

    def normalize_str(self, in_str):
        out_str = in_str.replace('\\','\\\\')
        out_str = re.sub(r'"','\\"', out_str)
        return out_str

    def clean(self,cond_str):
        if not self.db_wrapper.clear_rows_by_condition(self.TABLE_NAME, cond_str):
            self.logger.error('delete data from table %s, cond_str = %s' % (self.TABLE_NAME, cond_str))
            return(RT.ERR,'')
        return (RT.SUCC,'')

    def _process_bslash(self, in_dict):
        for k in in_dict.keys():
            v=in_dict[k]
            if type(v) == types.StringType or type(v) == types.UnicodeType:
                v = re.sub(r'\\',r'\\\\', v)
                v = re.sub(r'"',r'\\"', v)
                v = re.sub(r"'",r"\\'", v)
            in_dict[k] = v
    def select(self, id):
        ret = self.db.get_row_by_id(self.TABLE_NAME, id)
        if len(ret) == 0:
            self.logger.error('select item from %s failed and ID = [%s]' % (self.TABLE_NAME, id))
            return (RT.ERR, '')
        return (RT.SUCC, ret)

    def selects(self, start, limit, cond_dict={}):
        ret = self.db.get_rows_by_dict(self.TABLE_NAME, start, limit, cond_dict)
        return (RT.SUCC, ret)

    def count(self, cond_dict={}):
        ret = self.db.count(self.TABLE_NAME, cond_dict)
        if ret == -1:
            self.logger.error('count item of %s failed' % self.TABLE_NAME)
            return (RT.ERR, '')
        return (RT.SUCC, ret)

    def insert(self, item_dict):
        #self._process_bslash(item_dict)
        cond_dict={}
        cond_dict['name'] = item_dict['name']
        if not self.db.isunique_by_dict(self.TABLE_NAME, cond_dict):
            self.logger.error('duplicate data in %s [%s]' % (self.TABLE_NAME, item_dict['name']))
            return (RT.DUP, 'duplicate item')
        ret = self.db.insert_row(self.TABLE_NAME, item_dict)
        if not ret:
            return (RT.ERR, 'somthing error failed when insert item to %s' % self.TABLE_NAME)
        return (RT.SUCC, ret)

def gen_field_str(field_dict):
    return field_dict['name'] + ' ' + field_dict['type']  + ' ' + field_dict['attr']

class AccountTable(BaseTable):
    TABLE_NAME = 'T_ACCOUNT'
    ID= {'name':'id', 'type':'INT(4)', 'attr':'NOT NULL AUTO_INCREMENT'}
    USERNAME = {'name':'username', 'type':'CHAR(40)', 'attr':'NOT NULL'}
    PASSWORD = {'name':'password', 'type':'CHAR(40)', 'attr':'NOT NULL'}
    NAME = {'name':'name', 'type':'CHAR(40)', 'attr':'NOT NULL'}
    IS_SUPER = {'name':'is_super', 'type':'BOOL', 'attr':'NOT NULL DEFAULT 0'}
    CREATE_DATE = {'name':'create_date', 'type':'DATETIME', 'attr':'NOT NULL'}

    CRtab_SQL = 'CREATE TABLE ' + TABLE_NAME + '('\
            + gen_field_str(ID) + ','\
            + gen_field_str(USERNAME) + ','\
            + gen_field_str(PASSWORD) + ','\
            + gen_field_str(NAME) + ','\
            + gen_field_str(IS_SUPER) + ','\
            + gen_field_str(CREATE_DATE) + ','\
            + 'PRIMARY KEY(id)'\
            + ') ENGINE=InnoDB DEFAULT CHARSET=utf8'

    DROPtab_SQL = 'DROP table ' + TABLE_NAME

if __name__ == '__main__':
    pass
