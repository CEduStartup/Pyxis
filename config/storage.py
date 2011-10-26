##
## Settings file.
##
import os

storage_type = 'mongodb'
host = '172.22.60.75'
port = 27017
db_name = 'time-based-data-%s' % (os.environ['LOGNAME'],)
