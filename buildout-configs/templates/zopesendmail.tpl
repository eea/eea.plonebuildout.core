#!/bin/bash
#
# Daemon Name: zopesendmail_ctl
#
# chkconfig: - 58 74
# description: zope-sendmail service script

# Source function library.

. /etc/init.d/functions

SOFTWARE_HOME="${buildout:directory}"
USER=${configuration:effective-user}

NAME="zope-sendmail"
SENDMAIL=$SOFTWARE_HOME/bin/$NAME
QUEUE=${configuration:mail-queue}

if [ -z "$PYTHON" ]; then
  PYTHON="/usr/bin/env python2.7"
fi

# Make sure python is 2.7 or later
PYTHON_OK=`$PYTHON -c 'import sys
print (sys.version_info >= (2, 7) and "1" or "0")'`

SCL_PKG='python27'

if [ ! "$PYTHON_OK" = '1' ];then
    TEST_SCL_PY=`/usr/bin/scl --list | grep -q $SCL_PKG`
    if [ ! -f /usr/bin/scl ] || [ ! TEST_SCL_PY ];then
        echo "Python 2.7 or later is required"
        exit 0
    else
        OPTS="/usr/bin/scl enable $SCL_PKG --"
    fi
else
    OPTS=''
fi

prog="$OPTS $SENDMAIL --daemon $QUEUE --hostname ${configuration:smtp-server}"
lockfile=/var/lock/subsys/$NAME

start() {
    #Make some checks for requirements before continuing
    [ -x $SENDMAIL ] || exit 5

    # Start our daemon daemon
    echo -n $"Starting $NAME: "
    daemon --user=$USER --pidfile /var/run/$NAME.pid $prog >/dev/null 2>&1 &
    RETVAL=$?
    echo

    #
    #If all is well touch the lock file
    [ $RETVAL -eq 0 ] && touch $lockfile
    return $RETVAL
}

stop() {
    echo -n $"Shutting down $NAME: "
    killproc $NAME
    RETVAL=$?
    echo

    #If all is well remove the lockfile
    [ $RETVAL -eq 0 ] && rm -f $lockfile
    return $RETVAL
}

# See how we were called.
case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;
  status)
        status $NAME
        ;;
  restart)
        stop
        start
        ;;
   *)
        echo $"Usage: $0 {start|stop|status|restart}"
        exit 2
esac

#  daemon user=zope $SENDMAIL --daemon $QUEUE >/dev/null 2>&1 &

