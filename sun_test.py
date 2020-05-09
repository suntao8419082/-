#!/usr/bin/env python3
# coding=utf-8
import pymysql
from configobj import ConfigObj
import traceback
import sys

config_ini = r"../../config/config.ini"
config = ConfigObj(config_ini, encoding='utf-8')


class MysqlClient():

    def __init__(self):
        self.host = config["mysql_master_info"]["host"]
        self.port = int(config["mysql_master_info"]["port"])
        self.username = config["mysql_master_info"]["user"]
        self.password = config["mysql_master_info"]["password"]
        self.db = config["mysql_master_info"]["db"]
        self.charset = "utf8"

    def connect_db(self):
        self.connection = pymysql.connect(host=self.host, port=self.port, user=self.username,
                                          password=self.password, db=self.db, charset=self.charset)
        self.cursor = self.connection.cursor()

    def query_data(self, sql):
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
        except:
            exc_type, exc_value, exc_obj = sys.exc_info()
            traceback.print_tb(exc_type, exc_value, exc_obj)
            self.connection.rollback()
        else:
            return results

    def change_data(self, sql):
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except:
            exc_type, exc_value, exc_obj = sys.exc_info()
            traceback.print_tb(exc_type, exc_value, exc_obj)
            self.connection.rollback()


if __name__ == "__main__":
    mysql_cli = MysqlClient()
    mysql_cli.connect_db()
    data = mysql_cli.query_data("select * from device;")
    print(type(data))
