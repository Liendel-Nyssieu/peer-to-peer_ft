from flask import Flask, request
from threading import Thread, Lock
from time import sleep
from os import listdir
import hashlib
import send
import main


app = Flask(__name__)


port_num = ""
uploaded = []
dht = []
pub = 0
prv = 0
p = 0

f_lock = Lock()
dht_lock = Lock()
upl_lock = Lock()


# used_ports: function to return the used ports by other pears
def used_ports():
    global port_num
    used = []
    f_lock.acquire()                                    # mutex lock to make sure the data will not be changed during the following process
    with open("./ports.txt", "r") as ports:             # reading the complete list of ports available to the application
        for i in ports.readlines():
            if i[0:4] != port_num:
                try:
                    res = send.send(i[0:4], "alive")  # sending a ping-like message to all the other ports to see which ones are used
                    res = str(res)[2:-1]
                    print(f"{i[0:4]}, res: {res}\n")
                    used.append(i[0:4])                 # adding all the ports from which an reply was received to the list of used ports
                except:
                    print(f"Node {i[0:4]} unreachable\n")
    ports.close()
    f_lock.release()
    return used


# update_dht: function to send update information for the DHTs of the other nodes
def update_dht():
    global dht
    global port_num
    if len(uploaded) != 0:
        for i in uploaded:  # ^ going through all the uploaded files from this node and informing all the other nodes
            for j in dht:   # v
                try:
                    resp = send.send(j[0], "update", content = {'port': port_num, 'name': i[0], 'hash': i[1], 'keep': True})    # using function send to send messages to the specified node. In content, there is the local port number, the name and hash value of the file and a boolean with value True when file must be added to dht (opposite if file must be removed)
                    resp = str(resp)[2:-1]
                    print(f"resp: {resp}")
                except:
                    print(f"Node {j[0]} unreachable")


# keep_a: function managing the keep_alive messages to know which nodes are still up and running
def keep_a():
    global dht
    while True:
        used = used_ports()                             # getting the ports numbers of all the responsive nodes
        dht_lock.acquire()
        for i in used:
            found = False
            for j in range(0, len(dht)):
                if i == dht[j][0]:                                  # ^
                    found = True                                    # | if the node that answered is in the dht, the search is stopped
                    if not dht[j][1]:                               # |
                        dht[j][1] = True                            # |
                    else:                                           # |
                        print(f"Node {i} already in the DHT\n")     # |
                    break                                           # v
            if found is False:                          # ^ if the node was not found in the dht, it is added to it
                dht.append([i, True])                   # v
                print(f"Node {i} added to the DHT\n")
        for i in range(0, len(dht)):               # if a node is in the dht and does not answer messages, it is marked as unreachable (boolean of the list to false)
            if dht[i][0] not in used:
                dht[i][1] = False
        upl_lock.acquire()
        update_dht()                            # adding all the files uploaded by the local node to the dht of the other nodes
        upl_lock.release()
        print(f"DHT: {dht}\n")
        dht_lock.release()
        sleep(10)                                   # delay before next keep alive


# t_keep_a: function using a thread to call the keep_a function
def t_keep_a():
    t = Thread(target = keep_a, daemon = True)      # creating a thread to manage the keep alive messages (the daemon parameter makes the thread to stop upon termination of the main thread
    t.start()


# init: function to initialize the node
def init():
    global port_num
    used = used_ports()                                 # ^
    f_lock.acquire()                                    # |
    with open("./ports.txt", "r") as ports:             # |
        for i in ports.readlines():                     # | going through all the used ports to find one still available. If one available port is found, it is defined as the local port number and search is stopped
            if i[0:4] not in used:                      # |
                print(f"Port {i[0:4]} available!\n")    # |
                port_num = i[0:4]                       # |
                break                                   # v
        if port_num == "":                      # ^
            print("No port available\n")        # | if no available port was found, program terminates
            exit(-1)                            # v
    ports.close()
    f_lock.release()
    t_keep_a()


# alive: function responding to the requests.get messages to /alive with "up and running",
#        serves to answer keep alive messages
@app.route("/alive")
def alive():
    return "up and running"


# my_files: function to display all the files available for upload to the network
@app.route("/myfiles")
def my_files():
    files_list = ""
    for i in listdir("./files"):            # getting the list of all the files in the directory '/files' inside the software folder
        files_list += f"-{i}<br>"
    files_list = files_list.replace("[", "")        # ^
    files_list = files_list.replace("]", "")        # | parsing the string to make it easier to read
    files_list = files_list.replace(", ", "")       # v

    return f"Here are the following files available to upload:<br>{files_list}"


# access_local_file: function to access the specified local file. and to encrypt it before sending it to the network.
#                    It will be then accessed by the distant node to decrypt the file and get its content
@app.route("/myfiles/<fname>")
def access_local_file(fname):
    global uploaded
    upl_lock.acquire()
    print(f"uploaded: {uploaded}")
    for i in uploaded:                                  # ^
        if fname in i:                                  # |
            upl_lock.release()                          # |
            try:                                        # | trying to access the requested local file if it was previously added to the list of uploaded files
                f = open(f"./files/{fname}", "r")       # |
                content = f.read()                      # |
                f.close()                               # |
            except:                                     # |
                return "No such file"                   # v
            dist_port = request.json['port']                            # getting the port number of the node that requested the file to ask its public key in the main encryption file
            encrypted = main.main(dist_port, content, True, prv, p)     # calling the main method from the main encryption file to encrypt (boolean to True) the content of the file.
            print(f"encrypted: {encrypted}")
            return encrypted
    upl_lock.release()
    return "File not available yet"


# upload_file: function to upload a file from the list of available to be uploaded files
@app.route("/myfiles/<fname>/upload")
def upload_file(fname):
    global dht
    try:
        f = open(f"./files/{fname}", "rb")      # trying to access the content of the specified file in the /files folder
        content = f.read()
        f.close()
    except:
        return "No such file"
    hash_tool = hashlib.sha256()                # ^
    file_content = content                      # |
    hash_tool.update(file_content)              # | computing the hash value of the content of the file
    fhash = hash_tool.digest()                  # |
    fhash = int.from_bytes(fhash, 'big')        # v
    dht_lock.acquire()
    for i in dht:                                                                                   # ^
        for j in i:                                                                                 # |
            if type(j) is tuple:                                                                    # | checking if any node has already uploaded a file with the same hash value
                if fhash in j:                                                                      # |
                    dht_lock.release()                                                              # |
                    return f"File already uploaded by another node: {i[0]}, file named: {j[0]}"     # v
    dht_lock.release()
    upl_lock.acquire()
    if len(uploaded) != 0:                                                          # ^
        for i in uploaded:                                                          # |
            if i[1] == fhash:                                                       # | checking if the local node has already uploaded a file with the same hash value
                upl_lock.release()                                                  # |
                return f"File already uploaded by yourself, file named: {i[0]}"     # v
    uploaded.append((fname, fhash))             # if there is no file with the same content, the file is added to the list of uploaded file
    upl_lock.release()
    return "uploaded"


# clear_file_upload: function to remove the specified file from the list of uploaded files and from
#                    the other dht
@app.route("/myfiles/<fname>/clear")
def clear_file_upload(fname):
    upl_lock.acquire()
    if len(uploaded) != 0:              # ^
        for i in uploaded:              # | if the file is found in the list of uploaded files, it is removed from it
            if fname in i:              # |
                uploaded.remove(i)      # v
                dht_lock.acquire()
                for j in dht:                                                                                                           # ^
                    try:                                                                                                                # |
                        resp = send.send(j[0], "update", content = {'port': port_num, 'name': i[0], 'hash': i[1], 'keep': False})       # |
                        resp = str(resp)[2:-1]                                                                                          # | after the file has been found in the list, the program tries to reach all the nodes and requests them to remove (boolean to False) the file from their dht
                        print(f"resp: {resp}")                                                                                          # |
                    except:                                                                                                             # |
                        print(f"Node {j[0]} unreachable")                                                                               # v
                dht_lock.release()
    upl_lock.release()
    return "file cleared"


# get_uploaded: function to display all the uploaded files from the local node
@app.route("/myfiles/uploaded")
def get_uploaded():
    global uploaded
    res = ""
    upl_lock.acquire()
    if len(uploaded) != 0:                                      # going through all the elements of the list of uploaded files to display them in the returned variable
        res = "Here are the following uploaded files:<br>"
        for i in uploaded:
            res += f"-{i[0]}<br>"           # parsing the information upon adding it in the returned variable, to make it easier te read
        upl_lock.release()
        return res
    else:
        upl_lock.release()
        return "No file uploaded"


# clear_full_upload: function to clear all the uploaded files from the local node off the dht of the other nodes
@app.route("/myfiles/uploaded/clear")
def clear_full_upload():
    global uploaded
    global port_num
    upl_lock.acquire()
    for i in uploaded:          # for each element in the list of uploaded files, it is removed the same way as in the 'clear_file_upload' function
        dht_lock.acquire()
        for j in dht:
            try:
                resp = send.send(j[0], "update", content={'port': port_num, 'name': i[0], 'hash': i[1], 'keep': False})
                resp = str(resp)[2:-1]
                print(f"resp: {resp}")
            except:
                print(f"Node {j[0]} unreachable")
        dht_lock.release()
    uploaded = []
    upl_lock.release()
    return "cleared"


# get_update: function to handle the reception of notifications of files uploaded or removed by other nodes
@app.route("/update")
def get_update():
    global dht
    content = request.json          # getting the data transmitted along with the requests.get message
    print(content)
    dht_lock.acquire()
    for i in range(0, len(dht)):                # ^ going through the whole dht to find the port number of the received message
        if dht[i][0] == content['port']:        # v
            for j in dht[i]:                                # ^
                if type(j) is tuple:                        # |
                    if j[1] == content['hash']:             # | checking if the file is already in the dht or not
                        if content['keep']:                 # |
                            dht_lock.release()              # |
                            return "file already in dht"    # v
                        else:                               # ^
                            dht[i].remove(j)                # | if the notification was about removing the file, it is the removed
                            dht_lock.release()              # |
                            return "removed"                # v
            if content['keep']:                                     # ^ if the file needed to be added and was not already in the dht, it is then added
                dht[i].append((content['name'], content['hash']))   # v
            else:                                           # ^
                dht_lock.release()                          # | if the file needed to be removed and was already not in the dht, nothing happens
                return "file was already not in dht"        # v
    dht_lock.release()
    return "added"


# get_available: function to show to the user all the available files fomr the other nodes
@app.route("/getfile/available")
def get_available():
    global dht
    available = "Here are the available files:<br>"
    dht_lock.acquire()
    if len(dht) != 0:                       # going through the whole dht to get all the files added by the distant nodes
        for i in dht:
            if i[1] is True:        # if the node is actually available, then it is added the returned string
                for j in i:
                    if type(j) == tuple:
                        available += f"-'{j[0]}' port: {int(i[0])}<br>"
        dht_lock.release()
        return available


# get_file: function to get a specific file from another node
@app.route("/getfile/<fport>/<fname>")
def get_file(fport, fname):
    global port_num
    try:
        resp = send.send(fport, f"myfiles/{fname}", content = {'port': port_num})   # trying to access an encrypted file from another node (with the specified port number)
    except:
        return "Node unavailable"
    if str(resp)[2:-1] == "File not available yet" or str(resp)[2:-1] == "No such file":    # ^
        return resp                                                                         # |
    else:                                                                                   # | handling the possible answers and error messages received from the other node
        decrypted = main.main(fport, resp, False, prv, p)                                   # |
        return decrypted                                                                    # v


# getkey: function to display the public key generated for encryption and
#         shared with the distant node
@app.route("/getkey")
def getkey():
    global pub
    return str(pub)


# mainpage: function to show the organisation of the pages to help users
#           to know what they can access
@app.route("/")
def mainpage():
    tree = "<pre>Organisation of the webpages:<br>|_'/': main page<br>|_'/alive': page displaying 'up and running' if the node is active<br>"
    tree += "|_'/myfiles': page summing up the files available to upload<br>   |_'/[file name]/upload': page accessed to upload the corresponding file into the peer to peer network<br>   |_'/[file name]/clear': page accessed to remove a file from the peer to peer network<br>   |_'/uploaded': page showing all the files uploaded by the node<br>      |_'/clear': page accessed to remove all the uploaded files from the network<br>"
    tree += "|_'/getfile/available': page showing the uploaded files on the network with the port of the node that uploaded it<br>|_'/getfile/[distant node port]/[file name]': page accessed to ask for transmission of the corresponding file from the corresponding node<br><pre>"
    return tree


if __name__ == "__main__":
    init()
    pub, prv, p = main.init()
    app.run(debug=False, port=int(port_num))
