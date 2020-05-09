#!/usr/bin/env/python3
#coding=utf-8
from flask import Flask, request, jsonify
from sun_test import MysqlClient
import json
import sys, traceback

app = Flask(__name__)

@app.route('/api/query',methods=['get'])
def query_data():
    try:
        request_arg = request.args.get('uid')
        sql = "select * from device where uid='%s'"%(request_arg)
        client = MysqlClient()
        client.connect_db()
        results = jsonify(client.query_data(sql))
    except:
        exc_type, exc_value, exc_obj = sys.exc_info()
        traceback.print_tb(exc_obj)
    else:
        return results

@app.route('/api/data',methods=['post'])
def change_data():
    data = request.get_data()
    json_data = json.loads(data.decode('utf-8'))
    return jsonify(json_data)


if __name__ =="__main__":
    app.run(debug=True)