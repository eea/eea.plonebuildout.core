#!/bin/bash

# Init file for pound service
#
# chkconfig: 2345 70 25
# description: pound service
#
# processname: pound

# source function library

RETVAL=0
SUCMD='su -s /bin/bash ${parts.configuration['effective-user']} -c'
PREFIX='${parts.buildout.directory}'

start_all() {

# Is SU needed for poundctl?
    $$SUCMD "$$PREFIX/bin/poundctl start"
}

stop_all() {
    $$SUCMD "$$PREFIX/bin/poundctl stop"
}

status_all() {
    echo -n "pound: "
    $$PREFIX/bin/poundctl status
}

case "$1" in
  start)
        start_all
        ;;
  stop)
        stop_all
        ;;
  status)
        status_all
        ;;
  restart)
        stop_all
        start_all
        ;;
  *)
        echo "Usage: $0 {start|stop|status|restart}"
        RETVAL=1
esac
exit $$RETVAL
