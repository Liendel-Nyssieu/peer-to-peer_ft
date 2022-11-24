The files have been written using python 3.8.1 so I recommend using any version of Python 3 to run them. The script to run is the p2p.py file (without any parameter). The main.py file is the main file of the encryption and does NOT need to be runned. 

================================================

The scripts use the following libraries:
	-flask.Flask and flask.request
	-threading.Thread and threading.Lock
	-time.sleep
	-os.listdir
	-hashlib
	-requests
to install flask: python3 -m pip install flask
to install requests: python3 -m pip install requests
	
================================================

The information requested by the subject is either available in the shell as administration information or visible on the webpages if needed to be known by the user.

================================================

for the encryption part, files from the assignment 2 were used. Some modifications were brought to the main.py file to fragment the functions in order to get the needed data. Also, the way the algorithm got the public key of the distant node has been changed to an html request (requests.get) through the use of the send.send() function defined in the send.py file.

================================================

make sure not to change any of the following elements:
	-ports.txt (they contain the available ports for the program, please do not change aither the name or the content of the file)
	-/files/ (the folder containing the files to possibly share, please do not change its name or location, but feel free to add files)
