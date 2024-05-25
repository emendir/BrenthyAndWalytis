_how Brenthy manages logging_

# Brenthy Logging

The logfiles in which Brenthy writes the output of its runtime activities consists of the newest log file called _Brenthy.log_ and a folder called _.log_archive_ which contains older logfiles.
When installed, the location of _Brenthy.log_ and _.log_archive_ is the root of the installation directory.
When not installed, their location is `{USER_APPDATA_DIR}/Brenthy/`

At the time of writing, Brenthy is configured to keep  _Brenthy.log_ at less than 1MiB in size and keeps up to 50 old log files (each around 1MiB in size) before deleting them.
These settings will be customisable in the future, and are hackable anyway!