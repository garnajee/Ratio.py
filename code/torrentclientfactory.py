import random
import string

class Transmission406():
    def __init__(self, info_hash, compact=1, supportcrypto=1):
        self.name = "Transmission/4.0.6"
        parameters = {}
        # urlencoded 20-byte SHA1 hash of the value of the info key from the Metainfo file
        parameters['info_hash'] = info_hash
        # urlencoded 20-byte string used as a unique ID for the client
        parameters["peer_id"] = self.generate_peer_id()
        # The port number that the client is listening on
        parameters["port"] = random.randint(1025, 65535)
        # Number of peers that the client would like to receive from the tracker
        parameters["numwant"] = 80
        # An additional identification that is not shared with any other peers
        parameters["key"] = self.generate_key()
        # Setting this to 1 indicates that the client accepts a compact response
        parameters["compact"] = compact
        # Setting this to 1 indicates that the client accepts crypto
        parameters["supportcrypto"] = supportcrypto
        self.parameters = parameters

    def get_headers(self):
        headers = {}
        headers['User-Agent'] = 'Transmission/4.0.6'
        headers['Accept'] = '*/*'
        headers['Accept-Encoding'] = 'Accept-Encoding: gzip;q=1.0,  deflate, identity'
        return headers

    def get_query(self, uploaded, downloaded, left=0, event=None):
        # copy initial parameters
        params_copy = self.parameters.copy()
        # The total amount uploaded (since the client sent the 'started' event)
        params_copy["uploaded"] = uploaded
        # The total amount downloaded (since the client sent the 'started' event)
        params_copy["downloaded"] = downloaded
        # The number of bytes this client still has to download
        params_copy["left"] = left
        # If specified, must be one of started, completed, stopped
        if event:
            params_copy["event"] = event
        params = '&'.join('{}={}'.format(k, v)
                          for k, v in params_copy.items())
        return params

    def id_generator(self, chars, size):
        id = ''
        for _ in range(size):
            id += random.choice(chars)
        return id

    def generate_peer_id(self):
        chars = string.ascii_lowercase + string.digits
        rand_id = self.id_generator(chars, 12)
        peer_id = "-TR4060-" + rand_id
        return peer_id

    def generate_key(self):
        chars = 'ABCDEF' + string.digits
        key = self.id_generator(chars, 8)
        return key
