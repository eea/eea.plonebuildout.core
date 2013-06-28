#! /bin/sh
#
# monit         Monitor Unix systems
#
# Author:   Clinton Work,   <work@scripty.com>
#
# chkconfig:    2345 98 02
# description:  Monit is a utility for managing and monitoring processes,
#               files, directories and filesystems on a Unix system. 
# processname:  monit
# pidfile:      /var/run/monit.pid
# config:       /etc/monitrc

# Source function library.
. /etc/rc.d/init.d/functions

# Source networking configuration.
. /etc/sysconfig/network

MONIT=${buildout:bin-directory}/monit

# Source monit configuration.
if [ -f /etc/sysconfig/monit ] ; then
        . /etc/sysconfig/monit
fi

[ -f $MONIT ] || exit 0

RETVAL=0

# See how we were called.
case "$1" in
  start)
        echo -n "Starting monit: "
        daemon $NICELEVEL $MONIT
        RETVAL=$?
        echo
        [ $RETVAL = 0 ] && touch /var/lock/subsys/monit
        ;;
  stop)
        echo -n "Stopping monit: "
        killproc monit
        RETVAL=$?
        echo
        [ $RETVAL = 0 ] && rm -f /var/lock/subsys/monit
        ;;
  restart)
    $0 stop
    $0 start
    RETVAL=$?
    ;;
  condrestart)
       [ -e /var/lock/subsys/monit ] && $0 restart
       ;;
  status)
        status monit
    RETVAL=$?
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|condrestart|status}"
    exit 1
esac

exit $RETVAL

