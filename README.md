# log_listener
TCP log listener server minimally adapted from [Vinay Sajip's](https://github.com/vsajip) Python
[logging cookbook](https://docs.python.org/3/howto/logging-cookbook.html#sending-and-receiving-logging-events-across-a-network).

This is a standalone process, as [described by Vinay](https://docs.python.org/3/howto/logging-cookbook.html#deploying-web-applications-using-gunicorn-and-uwsgi): 
> "When deploying Web applications using Gunicorn or uWSGI (or similar), multiple worker processes are created to handle
> client requests. In such environments, avoid creating file-based handlers directly in your web application.
> Instead, use a SocketHandler to log from the web application to a listener in a separate process. This can be set up
> using a process management tool such as Supervisor - see Running a logging socket listener in production for more
> details."

There are several SO posts (see for example [here](https://stackoverflow.com/questions/70141427/django-loggers-are-overwriting-the-previous-log-file-along-with-the-new-one)
and [here](https://stackoverflow.com/questions/70944237/how-to-log-to-file-using-django-and-gunicorn-using-timedrotatingfilehandler-mis) incidentally answered by Vinay) around this issue, but remarkably,
Django [does not mention this issue in its documentation](https://docs.djangoproject.com/en/4.1/howto/logging/).
 
`log_listener.py` is a straight copy of Vinay's code for a server listening for log records on a TCP socket.

Log files will be kept in the sub-folder `logs/`.

## Deployment
***ATTENTION: the transmission is not encrypted and this is therefore not suitable for use over a public network***
A log server requires a process to run it, taking four arguments:

> python3 log_listener.py --help
>  
> -p PORT, --port PORT  Which TCP socket port (default: 9020)
>  
> -fn FILENAME, --filename FILENAME
                        Path to log file (default: log_file)
>  
> -l LEVEL, --level LEVEL
                        Logging level (default: DEBUG)
>  
> -f FORMAT, --format FORMAT
                        Logging string format (default: %(asctime)s [%(name)-15s] [%(levelname)-8s] %(message)s)
`


This long-running process is best served by having it overseen by `supervisor` and `log_listener.conf` is a
configuration file for `supervisor` to handle three instances; one for default logging, one for Django and one for
audit logging.

Finally, as log file management has now been decoupled from Django, `log_listener_logrotate.conf` is a configuration
file for `logrotate` to rotate the log files daily. This is an intermittent operation, best set up as a cronjob. For
example:

`
5 12 * * * /usr/sbin/logrotate /etc/logrotate.d/log_listener -state /home/cloo/log_listener/tmp/logrotate-state 
`

Specifying a custom state file for the logrotation resolves an otherwise possible permission issue with the default
location `/var/lib/logrotate/status.tmp`