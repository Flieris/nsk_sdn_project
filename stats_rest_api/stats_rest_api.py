#!/usr/bin/env python
import sqlite3
import json
import os
from flask import Flask
from flask import json
from flask import request

parent_path = os.path.abspath('.')
app = Flask(__name__)
DATABASE = parent_path+"/stats_db/statisticsDB.db"


@app.route('/statistics/<dpid>',methods=['GET','DELETE'])
def statistics(dpid):
    #show info based on router id
    if request.method == 'GET':
        return get_stats_by_dpid(dpid)
    if request.method == 'DELETE':
        return remove_stats_by_dpid(dpid)

def get_stats_by_dpid(dpid):
    conn = get_db(DATABASE)
    if conn is None:
        return app.response_class(
            response=json.dumps({"message":"Error while connecting to database"}, ensure_ascii=False),
            status=500,
            mimetype='application/json'
        )
    validate = "select count(*) from thoststatistics where id = '{}'".format(dpid)
    cur = conn.cursor()
    cur.execute(validate)
    row = cur.fetchone()
    if row[0] == 0:
        return app.response_class(
            response=json.dumps({"message":"Not found"}, ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )

    response = ''
    stats_data = "select * from tudpstatistics where host_id = {}".format(
        dpid)
    host_data = "select * from thoststatistics where id = {}".format(dpid)

    cur.execute(host_data)
    row = cur.fetchone()
    response_dict = []
    print row
    host_data = {
        'host_id': row[0],
        'id_addr': row[1],
        'eth_addr': row[2],
        'total_data': row[3]
    }

    cur.execute(stats_data)
    rows = cur.fetchall()
    stats_data = []
    for row in rows:
        print row
        single = {
            "packet_id": row[0],
            "event_time": row[2],
            "source_eth_addr": row[3],
            "source_ip": row[4],
            "source_port": row[5],
            "destination_eth_addr": row[6],
            "destination_ip": row[7],
            "destination_port": row[8],
            "payload": row[9]
        }
        stats_data.append(single)
    host_data["statistics"] = stats_data
    response_dict.append(host_data)
    json_data = json.dumps(response_dict, ensure_ascii=False)
    response = app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json'
    )
    return response

def remove_stats_by_dpid(dpid):
    conn = get_db(DATABASE)
    if conn is None:
        return app.response_class(
            response=json.dumps({"message":"Error while connecting to database"}, ensure_ascii=False),
            status=500,
            mimetype='application/json'
        )
    validate = "select count(*) from thoststatistics where id = '{}'".format(dpid)
    cur = conn.cursor()
    cur.execute(validate)
    row = cur.fetchone()
    if row[0] == 0:
        return app.response_class(
            response=json.dumps({"message":"Not found"}, ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )
    remove_query1 = "delete from thoststatistics where id = {}".format(dpid)
    remove_query2 = "delete from tudpstatistics where host_id = {}".format(dpid)
    cur.execute(remove_query1)
    cur.execute(remove_query2)
    conn.commit()
    return app.response_class(
        response=json.dumps({"message":"Statistics cleared"},ensure_ascii=False),
        status=200,
        mimetype="application/json"
    )

def get_db(file):
    try:
        conn = sqlite3.connect(file)
        return conn
    except sqlite3.Error as e:
        print e
    return None

