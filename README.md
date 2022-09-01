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
A log server requires a process to run it:

`python3 log_listener.py -c pstf_app.ini`

would pass the configuration file `pstf_app.ini` to the server.

this long running process is best served by having it overseen by `supervisor` and `log_listener.conf` is a
configuration file for `supervisor` to handle two such processes; one for default logging and one for audit logging.

Finally, as log file management has now been decoupled from Django, `log_listener_logrotate.conf` is a configuration
file for `logrotate` to rotate the log files daily.