export STATION_ID=$1
export PARAMS=$2


TARGET='PM2.5' LAG=1 SCALING='Standard' POLLUTANT_PARAMS_LAG=1 python -m data_load