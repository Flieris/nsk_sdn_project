#!/bin/bash

HOME_DIR=${PWD}
COLLECTOR_DIR="$HOME_DIR/udp_stats_collector"
DATABASE_DIR="$HOME_DIR/stats_db"
REST_DIR="$HOME_DIR/stats_rest_api"


 

start_applications() {
    echo "Starting"

    touch "$COLLECTOR_DIR/udp_statistics.log"
    touch "$REST_DIR/stats_rest_api.log"
    chmod +x "$COLLECTOR_DIR/udp_statistics.py"
    chmod +x "$COLLECTOR_DIR/udp_statistics.log"
    chmod +x "$REST_DIR/stats_rest_api.py"
    chmod +x "$REST_DIR/stats_rest_api.log"
    cd $COLLECTOR_DIR
    nohup ryu-manager "udp_statistics.py" --observe-links &> "udp_statistics.log" &
    cd $HOME_DIR
    export FLASK_APP="$REST_DIR/stats_rest_api.py"
    nohup flask run --host=0.0.0.0 &> "$REST_DIR/stats_rest_api.log" &
    exit
}

stop_applications() {
    echo "stopping"
}

init_schema() {
    echo "Init schema"
    chmod +x "$DATABASE_DIR/init_schema.py"
    "$DATABASE_DIR/init_schema.py"
}

clear_schema() {
    echo "clear schema"
    chmod +x "$DATABASE_DIR/clear_schema.py"
    "$DATABASE_DIR/clear_schema.py"
}

print_usage() {
    echo "usage"
}


if [ $1 == "start" ] 
then
    start_applications
elif [ $1 == "stop" ]
then
    stop_applications
elif [ $1 == "initschema" ]
then
    init_schema
elif [ $1 == "clearschema" ]
then
    clear_schema
else
    print_usage
fi

