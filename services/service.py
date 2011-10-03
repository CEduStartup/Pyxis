import bjsonrpc
import pgdb
import config.srv as srv_config


class TrackersService(SharedService):

    def get_trackers(modified_since=None):
        return [1,2,3,4,5]


server = bjsonrpc.createserver(host=srv_config.trackers.bind_host,
                               port=srv_config.trackers.bind_port,
                               handler_factory=TrackersService)
server.serve()

