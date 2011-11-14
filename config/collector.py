from shared.Utils import port_randomizer
##
## Settings file.
##

parallel_threads_num = 1000
tracker_thread_timeout = 5
trackers_refresh_interval = 300
scheduler_maximum_sleep = 15

backdoor_host = '127.0.0.1'
backdoor_port = 8091 + port_randomizer()

