import requests


# send: function to send messages to other servers
def send(port, msg_type, content=None):
    if content is not None:                                                         # ^
        resp = requests.get(f"http://127.0.0.1:{port}/{msg_type}", json=content)    # | considering two options: if there is some data to transmit to the other node or if the caller just needs to access a webpage
    else:                                                                           # |
        resp = requests.get(f"http://127.0.0.1:{port}/{msg_type}")                  # v
    resp = resp.content                                                             # getting the return of the webpage
    return resp
