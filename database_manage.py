import os, sys
import inspect
import time
import types
import logging, logging.config
import traceback
import database_config
import ConfigParser
import simplejson as json
import mysql_wrapper
cur_file_dir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(cur_file_dir+'/../conf/')
sys.path.append(cur_file_dir+'/../control/')
sys.path.append(cur_file_dir+'/../data_template/')

class DBmanage(object):
    def __init__(self):
        self.db_wrapper = mysql_wrapper.MysqlWrapper()
        self.conf = database_config.DatabaseConfig()
        self.com_conf = ConfigParser.ConfigParser()
        self.com_conf.optionxform = str
        self.com_conf.read(cur_file_dir+'/../conf/com_conf.cfg')
        pass
    def create_all_table(self):
        for table_obj in self.conf.tables_objlist:
            #print table_obj.CRtab_SQL
            self.db_wrapper.execute(table_obj.CRtab_SQL)
    def drop_all_table(self):
        for table_obj in self.conf.tables_objlist:
            self.db_wrapper.execute(table_obj.DROPtab_SQL)

    def drop_table(self, table_name):
        for table_obj in self.conf.tables_objlist:
            if table_name == table_obj.TABLE_NAME:
                self.db_wrapper.execute(table_obj.DROPtab_SQL)

    def import_proto_default(self):
        metalist = self.com_conf.items('dataDefaultValue')
        for (name, data_file) in metalist:
            data_module = __import__(data_file.split('.')[0])
            default_data = data_module.get_default()
            #proto_type = proto_module.get_type()
            data_type = name
            data_str = json.dumps(default_data,encoding='utf-8', ensure_ascii=True)
            row_data = self.db_wrapper.query('select * from ComponentData where instance_name="##default##" and data_type=\"%s\"' % data_type)
            if len(row_data) == 0:
                in_sql = 'insert into ComponentData (suite_id, instance_name, data_type, data_content, data_path) values (0, "##default##" ,"' +data_type+'", \''+data_str+'\', "default_path")'
                self.db_wrapper.execute(in_sql)
                print 'add new proto %s' % data_type
    def del_proto_default(self, proto_name):
        cmd = 'delete  from ComponentData where instance_name="##default##" and data_type="%s";' % proto_name
        if self.db_wrapper.execute(cmd):
            print 'delete default proto %s from ComponentData successfully' % proto_name
        else:
            print 'delete default proto %s from ComponentData error!!!!' % proto_name

    def import_compare_type(self):
        import comparefunction
        compare_module = sys.modules['comparefunction']
        for name, compare_class in inspect.getmembers(compare_module):
            if (not type(compare_class) == types.TypeType):
                continue
            if issubclass(compare_class, comparefunction.BaseCompare) and (not name == 'BaseCompare'):
                obj = compare_class()
                q_sql = 'select * from ComponentCompareResult where instance_name="##default##" and compare_type=\"%s\"' % obj.compare_type
                row_data = self.db_wrapper.query(q_sql)
                if len(row_data) == 0:
                    in_sql = 'insert into ComponentCompareResult (suite_id, instance_name, compare_type, compare_para, result_type) values (0, "##default##",\"%s\",\"%s\",\"%s\")' %(obj.compare_type, obj.compare_para, obj.result_type)
                    self.db_wrapper.execute(in_sql)

def back_up_database(db_name):
    svn_suffix = '--username chi.zhang --password Xinwei0205 --non-interactive -m "add new db backup "'
    back_dir = cur_file_dir + '/../db_backup/%s/' % db_name
    if not os.path.exists(back_dir):
        os.makedirs(back_dir)
    time_stamp = str(int(time.time()))
    cmd = '/usr/bin/mysqldump -uroot --opt --extended-insert=false --triggers -R --hex-blob -x %s > %s' % (db_name, '%s/db_%s.sql' %(back_dir, time_stamp ))
    os.system(cmd)

    cmd = 'svn add %s' % back_dir+'db_%s.sql' % time_stamp
    os.system(cmd)
    cmd = 'svn ci %s %s' % (back_dir+'db_%s.sql' % time_stamp, svn_suffix)
    os.system(cmd)

'''
restore database
drop database test_DailyrunPlatform;
create database test_DailyrunPlatform;
mysql -uroot test_DailyrunPlatform < /home/admin/dailyrun_platform/db_backup/DailyrunPlatform/db_1414251002.sql
'''


if __name__ == '__main__':
    db_manage = DBmanage()
    if sys.argv[1] == 'proto':
        db_manage.import_proto_default()
    elif sys.argv[1] == 'backup':
        back_up_database('DailyrunPlatform')
    elif sys.argv[1] == 'delproto':
        proto_name = sys.argv[2]
        db_manage.del_proto_default(proto_name)
    # elif sys.argv[1] == 'compare':
    #    db_manage.import_compare_type()
    else:
        print 'para error!!!\n'
