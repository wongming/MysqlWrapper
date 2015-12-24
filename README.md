# MysqlWrapper
## 1. 数据库配置
可在database_config.py中配置数据库地址账号密码以及数据库，配置示例如下：

    class DatabaseConfig(object):
        CHARSET = 'utf8'
        UNICODE = True
        WARNINGS = True
        HOST = 'localhost'
        USER = 'db_username'
        PORT = 3306
        PASSWORD = 'db_pwd'
        DATABASE = 'db_name'

## 2. MysqlWrapper接口

	#添加
	insert_row(tableName, value_map);

	#删除
	clear_row(tableName, id_name, id_value);

	clear_rows(tableName, id_name, id_values);

	clear_row_by_id(tableName, id);

	clear_rows_by_ids(tableName, ids);

	clear_rows_by_dict(tableName, cond_dict);

	#修改
	update_value(tableName, id_name, id_value, value_map);

	update_value_by_id(tableName, id, value_map);

	update_value_by_dict(tableName, cond_dict, value_map);

	#查询
  get_row(tableName, id_name, id_value, select_fields = '*');

	get_row_by_id(tableName, id, select_field = '*',order_col = 'id', asc = True);

	get_rows_by_dict(start, limit, tableName, cond_dict, select_field = '*', order_col = 'id', asc = True);

  get_rows_by_condition_string(start, limit, tableName, cond_string, select_field = '*', order_col = 'id', asc = True);


	#unique校验
	isunique_by_value(tableName,cond_key,cond_value);

	isunique_by_condition_dict(tableName,cond_dict);
