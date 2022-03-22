import firebase_admin
import shutil
from firebase_admin import credentials, firestore
from google.auth.exceptions import GoogleAuthError
import socket
import os

# holds the default error sent if credentials is not found the first time
FIRESTORE_FILE_ERROR = 'Could not locate the configuration file, please ' \
      'upload a file by providing its path location. This configuration file ' \
      'can be obtained through the firebase website ' \
      '(https://firebase.google.com/) after an empty firestore ' \
      'database is created.\n'

# holds the firebase file path
FIREBASE_PATH = "FirestoreConfig.json"

# holds the name of the collection
FIREBASE_COLLECTION = "OmniCord"


# gets the json file with credentials to open database
def get_firestore_file(error_msg=FIRESTORE_FILE_ERROR):
    # global cred to be used in try and except
    cred = None

    # catches errors during authentication
    try:
        # tries to open the config file
        cred = credentials.Certificate(FIREBASE_PATH)
    except OSError:  # runs if file couldn't be opened
        # prints error information
        print(error_msg)

        # obtains file path as input
        filepath = input('Path to Configuration File: ')

        # holds error msg if the file path was invalid
        error_msg = 'Path was Invalid.\nPlease Re-enter New Path:'

        try:
            # copies file using file path and places it into the project
            shutil.copy(filepath, FIREBASE_PATH)
        except IOError:  # runs if the file couldn't copy
            # changes error information
            error_msg = 'File could not be uploaded' \
                        '(path may have been incorrect).\n' \
                        'Please Re-enter New Path:'

        # reruns function until correct configuration is provided
        cred = get_firestore_file(error_msg=error_msg)
    except ValueError:  # runs if the json is missing values
        # holds error msg if the file  was invalid
        error_msg = 'The current configuration file is invalid.\n' \
                    'Please provide a new configuration file.\n'

        # removes bad file
        os.remove(FIREBASE_PATH)

        # reruns function until correct configuration is provided
        cred = get_firestore_file(error_msg=error_msg)

    # returns credentials
    return cred


# gets the client object for firestore using credentials
def get_firestore_client(cred):
    db = None
    try:
        # initializes and obtains the firestore database
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except GoogleAuthError:  # runs if there is an error authenticating
        # closes current app to avoid value error
        firebase_admin.get_app(firebase_admin._DEFAULT_APP_NAME)._cleanup()

        # checks if we are connected to the internet
        if(not __internet()):
            # displays error msgs
            print('Make sure you are connected to the internet!')
            print('Press Enter to Try Again...')

            # waits for user response to try connecting again
            input()

            # recalls function to try connecting to database again
            get_firestore_client(cred)
        else:
            # holds error msg if the file  was invalid
            error_msg = 'The current configuration file is invalid.\n' \
                        'Please provide a new configuration file.\n'

            # removes bad file
            os.remove(FIREBASE_PATH)

            # reruns function until correct configuration is provided
            cred = get_firestore_file(error_msg=error_msg)
            get_firestore_client(cred)

    # returns the database
    return db


# helper function checks connection to internet
# (by default tries connecting to google dns over TCP)
def __internet(test_ip='8.8.8.8', port=53, timeout=3):
    try:
        # sets default timeout for connection
        socket.setdefaulttimeout(timeout)

        # connects to a test ip address using a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((test_ip, port))

        # if no errors were thrown at this point, there is a connection
        return True
    except socket.error:
        # there was an error connecting so no internet is found
        return False


# wrapper function to get firestore database
def get_firestore_db():
    # gets the credentials
    cred = get_firestore_file()

    # returns the database after it is obtained using credentials
    return get_firestore_client(cred)
