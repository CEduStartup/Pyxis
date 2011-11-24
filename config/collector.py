from shared.Utils import port_randomizer
from config.context import create_context
##
## Settings file.
##

parallel_threads_num = 1000
tracker_thread_timeout = 5
trackers_refresh_interval = 300
scheduler_maximum_sleep = 15

backdoor_host = '127.0.0.1'
backdoor_port = 8091 + port_randomizer()

component_name = 'COLLECTOR'

create_context(component_name)

