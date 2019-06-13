#!/bin/bash

HOME_DIR=${PWD}
COLLECTOR_DIR="$HOME_DIR/udp_stats_collector"
DATABASE_DIR="$HOME_DIR/stats_db"
REST_DIR="$HOME_DIR/stats_rest_api"
COLLECTOR_PID="$COLLECTOR_DIR/collector.pid"
REST_PID="$REST_DIR/rest_api.pid"
 

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
    echo $! > $COLLECTOR_PID
    cd $HOME_DIR
    export FLASK_APP="$REST_DIR/stats_rest_api.py"
    nohup flask run --host=0.0.0.0 &> "$REST_DIR/stats_rest_api.log" &
    echo $! > $REST_PID
    exit
}

stop_applications() {
    echo "stopping"
    if [ -f "$COLLECTOR_PID" ]
    then
        PID1=`cat $COLLECTOR_PID`
        PID1EXISTS=`ps -ef | awk '{print $2}' | grep $PID1 | wc -l | awk '{print $1}'`
        if [ $PID1EXISTS == "1" ]
        then
            echo "Stopping udp packet statistics collector"
            kill -9 $PID1
            rm -f $COLLECTOR_PID
        else
            echo "$COLLECTOR_PID lock file exists but no process with pid $PID1 found! Removing lock file"
            rm -f $COLLECTOR_PID
        fi
    else
        echo "Udp packet statistics collector is not running!"
    fi
    if [ -f "$REST_PID" ]
    then
        PID2=`cat $REST_PID`
        PID2EXISTS=`ps -ef | awk '{print $2}' | grep $PID2 | wc -l | awk '{print $1}'`
        if [ $PID2EXISTS == "1" ]
        then
            echo "Stopping statistics rest api"
            kill -9 $PID2
            rm -f $REST_PID
        else
            echo "$COLLECTOR_PID lock file exists but no process with pid $PID2 found! Removing lock file"
            rm -f $REST_PID
        fi
    else
        echo "Statistics rest api is not running!"
    fi
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

