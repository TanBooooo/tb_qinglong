
import hashlib
import time


def encrypt(payload):
    timestamp = int(time.time() * 1000)
    data = (str(payload) + ':D7C92C3FDB52D54147B668DC6F8A5@' + str(timestamp)).replace("'", '"').encode()
    sign = hashlib.md5(data).hexdigest()
    payload['timestamp'] = timestamp
    payload['hash'] = sign
    return payload

