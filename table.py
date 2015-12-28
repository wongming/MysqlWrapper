#encoding = utf-8
import os,sys,re
import copy
import time
import re
import types
import inspect, types
import logging, logging.config
reload(sys)
sys.setdefaultencoding('utf8')
cur_dir = os.path.split(os.path.realpath(__file__))[0]
import mysql_wrapper

def gen_field_str(fielddict):
    return fielddict['name'] + ' ' + fielddict['type']  + ' ' + fielddict['attr']

class RT(object):
    SUCC = 1
    EMPTY = 2
    DUP = 3
    IERR = 4
    SVN_ERR = 5
    NO_FILE = 6
    STOP = 7

class BaseTable(object):
    logging.config.fileConfig(os.path.join(cur_dir, 'log.conf'))
    logger = logging.getLogger("db")
    def execute(self, line):
        return self.db_wrapper.execute(line)
    def normalize_str(self, in_str):
        out_str = in_str.replace('\\','\\\\')
        out_str = re.sub(r'"','\\"', out_str)
        return out_str
    def clean(self,cond_str):
        if not self.db_wrapper.clear_rows_by_condition(self.TABLE_NAME, cond_str):
            self.logger.error('delete data from table %s, cond_str = %s' % (self.TABLE_NAME, cond_str))
            return(RT.IERR,'')
        return (RT.SUCC,'')
    def _process_bslash(self, in_dict):
        for k in in_dict.keys():
            v=in_dict[k]
            if type(v) == types.StringType or type(v) == types.UnicodeType:
                v = re.sub(r'\\',r'\\\\', v)
                v = re.sub(r'"',r'\\"', v)
                v = re.sub(r"'",r"\\'", v)
            in_dict[k] = v

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

    def __init__(self):
        self.db_wrapper = mysql_wrapper.MysqlWrapper()
        pass
    def select_all(self):
        ret = self.db_wrapper.get_all_rows(self.TABLE_NAME)
        if len(ret) == 0:
            self.logger.warning('get all accounts from T_ACCOUNT failed and T_ACCOUNT is empty')
            return (RT.EMPTY, '')
        return (RT.SUCC, ret)

    def select(self, id):
        ret = self.db_wrapper.get_row(self.TABLE_NAME, id)
        if len(ret) == 0:
            self.logger.error('select account from T_ACCOUNT failed and ID = [%s]' % id)
            return (RT.IERR, '')
        return (RT.SUCC, ret)

    def insert(self, item_dict):
        self._process_bslash(item_dict)
        cond_dict={}
        cond_dict['username'] = item_dict['username']
        if not self.db_wrapper.isunique_by_condition_dict(self.TABLE_NAME, cond_dict):
            self.logger.error('duplicate data in T_ACCOUNT %s' % item_dict['username'])
            return (RT.DUP, 'duplicate item')
        ret = self.db_wrapper.insert_row(self.TABLE_NAME, item_dict)
        if not ret:
            return (RT.IERR, 'somthing error failed when insert item')
        return (RT.SUCC, ret)

    def update(self, id, valueMap):
        self._process_bslash(valueMap)
        ret = self.db_wrapper.update_values(self.TABLE_NAME, id, valueMap)
        if ret:
            return (RT.IERR, 'update success')
        else:
            self.logger.error('update data to account failed, id=[%s], data=[%s]' %(str(suite_id), str(valueMap)))
            return (RT.SUCC, 'update failed')

class DriverTable(BaseTable):
    TABLE_NAME = 'T_DRIVER'
    ID= {'name':'id', 'type':'INT(4)', 'attr':'NOT NULL AUTO_INCREMENT'}
    NAME = {'name':'name', 'type':'CHAR(40)', 'attr':'NOT NULL'}
    DESCRIPTION = {'name':'description', 'type':'TEXT', 'attr':'NOT NULL'}
    PARAM = {'name':'param', 'type':'TEXT', 'attr':'NOT NULL'}
    SETUP = {'name':'setuppy', 'type':'TEXT', 'attr':'NOT NULL'}
    TEARDOWN = {'name':'teardownpy', 'type':'TEXT', 'attr':'NOT NULL'}
    EXEX = {'name':'exepy', 'type':'TEXT', 'attr':'NOT NULL'}

    CRtab_SQL = 'CREATE TABLE ' + TABLE_NAME + '('\
            + gen_field_str(ID) + ','\
            + gen_field_str(NAME) + ','\
            + gen_field_str(DESCRIPTION) + ','\
            + gen_field_str(PARAM) + ','\
            + gen_field_str(SETUP) + ','\
            + gen_field_str(TEARDOWN) + ','\
            + gen_field_str(EXEX) + ','\
            + 'PRIMARY KEY(id)'\
            + ') ENGINE=InnoDB DEFAULT CHARSET=utf8'

    DROPtab_SQL = 'DROP table ' + TABLE_NAME

    def __init__(self):
        self.db_wrapper = mysql_wrapper.MysqlWrapper()
        pass

    def select(self, id):
        ret = self.db_wrapper.get_row(self.TABLE_NAME, id)
        if len(ret) == 0:
            self.logger.error('select driver from T_Driver failed and ID = [%s]' % id)
            return (RT.IERR, '')
        return (RT.SUCC, ret)

    def insert(self, item_dict):
        self._process_bslash(item_dict)
        cond_dict={}
        cond_dict['name'] = item_dict['name']
        if not self.db_wrapper.isunique_by_condition_dict(self.TABLE_NAME, cond_dict):
            self.logger.error('duplicate data in T_Driver %s' % item_dict['name'])
            return (RT.DUP, 'duplicate item')
        ret = self.db_wrapper.insert_row(self.TABLE_NAME, item_dict)
        if not ret:
            return (RT.IERR, 'somthing error failed when insert item')
        return (RT.SUCC, ret)

class CaseTable(BaseTable):
    TABLE_NAME = 'T_CASE'
    ID= {'name':'id', 'type':'INT(4)', 'attr':'NOT NULL AUTO_INCREMENT'}
    NAME = {'name':'name', 'type':'CHAR(40)', 'attr':'NOT NULL'}
    DESCRIPTION = {'name':'description', 'type':'TEXT', 'attr':'NOT NULL'}
    PARAM = {'name':'param', 'type':'TEXT', 'attr':'NOT NULL'}
    DRIVER = {'name':'driver', 'type':'CHAR(40)', 'attr':'NOT NULL'}

    CRtab_SQL = 'CREATE TABLE ' + TABLE_NAME + '('\
            + gen_field_str(ID) + ','\
            + gen_field_str(NAME) + ','\
            + gen_field_str(DESCRIPTION) + ','\
            + gen_field_str(PARAM) + ','\
            + gen_field_str(DRIVER) + ','\
            + 'PRIMARY KEY(id)'\
            + ') ENGINE=InnoDB DEFAULT CHARSET=utf8'

    DROPtab_SQL = 'DROP table ' + TABLE_NAME

    def __init__(self):
        self.db_wrapper = mysql_wrapper.MysqlWrapper()
        pass

    def select(self, id):
        ret = self.db_wrapper.get_row(self.TABLE_NAME, id)
        if len(ret) == 0:
            self.logger.error('select case from T_CASE failed and ID = [%s]' % id)
            return (RT.IERR, '')
        return (RT.SUCC, ret)

    def insert(self, item_dict):
        self._process_bslash(item_dict)
        cond_dict={}
        cond_dict['name'] = item_dict['name']
        if not self.db_wrapper.isunique_by_condition_dict(self.TABLE_NAME, cond_dict):
            self.logger.error('duplicate data in T_CASE %s' % item_dict['name'])
            return (RT.DUP, 'duplicate item')
        ret = self.db_wrapper.insert_row(self.TABLE_NAME, item_dict)
        if not ret:
            return (RT.IERR, 'somthing error failed when insert item')
        return (RT.SUCC, ret)

class PlanTable(BaseTable):
    TABLE_NAME = 'T_PLAN'
    ID= {'name':'id', 'type':'INT(4)', 'attr':'NOT NULL AUTO_INCREMENT'}
    NAME = {'name':'name', 'type':'CHAR(40)', 'attr':'NOT NULL'}
    DESCRIPTION = {'name':'description', 'type':'TEXT', 'attr':'NOT NULL'}
    CASE_LIST = {'name':'case_list', 'type':'TEXT', 'attr':'NOT NULL'}
    LASE_STATUS = {'name':'last_status', 'type':'CHAR(40)', 'attr':'NOT NULL'}
    CRONTAB = {'name':'crontab', 'type':'CHAR(100)', 'attr':'NOT NULL'}
    PEOPLE = {'name':'poeple', 'type':'TEXT', 'attr':'NOT NULL'}


    CRtab_SQL = 'CREATE TABLE ' + TABLE_NAME + '('\
            + gen_field_str(ID) + ','\
            + gen_field_str(NAME) + ','\
            + gen_field_str(DESCRIPTION) + ','\
            + gen_field_str(CASE_LIST) + ','\
            + gen_field_str(LASE_STATUS) + ','\
            + gen_field_str(CRONTAB) + ','\
            + gen_field_str(PEOPLE) + ','\
            + 'PRIMARY KEY(id)'\
            + ') ENGINE=InnoDB DEFAULT CHARSET=utf8'

    DROPtab_SQL = 'DROP table ' + TABLE_NAME

    def __init__(self):
        self.db_wrapper = mysql_wrapper.MysqlWrapper()
        pass

    def select(self, id):
        ret = self.db_wrapper.get_row(self.TABLE_NAME, id)
        if len(ret) == 0:
            self.logger.error('select plan from T_PLAN failed and ID = [%s]' % id)
            return (RT.IERR, '')
        return (RT.SUCC, ret)

    def insert(self, item_dict):
        self._process_bslash(item_dict)
        cond_dict={}
        cond_dict['name'] = item_dict['name']
        if not self.db_wrapper.isunique_by_condition_dict(self.TABLE_NAME, cond_dict):
            self.logger.error('duplicate data in T_CASE %s' % item_dict['name'])
            return (RT.DUP, 'duplicate item')
        ret = self.db_wrapper.insert_row(self.TABLE_NAME, item_dict)
        if not ret:
            return (RT.IERR, 'somthing error failed when insert item')
        return (RT.SUCC, ret)

if __name__ == '__main__':
    #ACCOUNT TEST
    '''
    import time
    now = time.time()
    t = AccountTable()
    item_dict = {'username':'wangming2', 'password':'123456','name':'wangming','is_super':1,'create_date':'2015-10-29 00:00:00'}
    print t.insert(item_dict)
    print t.select(1)
    print t.update(1,{'password':'changed'})
    print t.select_all()
    '''
    #DRIVER TEST

    t = DriverTable()
    param ={'a':2,'b':7,'duedata':14}
    setup ='''print 'setup!'
'''
    teardown ='''print 'teardown!'
'''
    exex='assert (self.a*self.b == self.duedata)'
    description ='mutiply driver'
    item_dict = {'name':'mutiply','param':str(param),'setup':setup,'teardown':teardown,'exex':exex,'description':description}
    print item_dict
    print t.insert(item_dict)

    #CASE TEST
    t = CaseTable()
    item_dict = {'name':'mutiply_2_7','param':str(param),'driver':'mutiply','description':'mutiply case'}
    print item_dict
    print t.insert(item_dict)

    #PLAN TEST
    t = PlanTable()
    item_dict =  {'name':'mutiply','case_list':'mutiply;mutiply_2_7'}
    print item_dict
    print t.insert(item_dict)
