import csv
import socket
import threading
import time
#s = socket(AF_INET, SOCK_STREAM) #utworzenie gniazda
#s.bind(('', 8888))
#s.listen(5)
import sys
import pandas as pd
import sys

import pickle

import config
import sliding_window

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
#while i<2:
#	client,addr = s.accept() # odebranie polaczenia
#	print client.recv(100)
#	client.send(time.ctime(time.time()) + '\n')
#	# wyslanie danych do klienta


class Server(object):
    def __init__(self):
        self.host = ''
        self.port = 8888
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
        except socket.error, (value, message):
            if self.server:
                self.server.close()
            print "Could not open socket: " + message
            sys.exit(1)

    def run(self):
        self.open_socket()
        running = 1
        while running:
            (client, address) = self.server.accept()
            clientMode = client.recv(self.size)
            print clientMode
            if "SVM" in clientMode and "Enabled" in clientMode:
                ct = Client((client, address))
                ct.start()
                self.threads.append(ct)
        self.server.close()
        for c in self.threads:
            c.join()


class Client(threading.Thread):
    def __init__(self, (client, address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 4096

    def run(self):
        running = 1
        while running:
            mode = self.client.recv(self.size)
            if mode == "":
                self.client.close()
                break
            print "MODE: ", mode
            dataReceived = ""
            expectedData = int(mode.split(':')[1])
            print "Received message:" + str(expectedData)
            self.client.send(str(expectedData))
            while len(dataReceived) < expectedData and running:
                #print "Petla WHILE"
                data = self.client.recv(self.size)
                #print len(data)
                dataReceived += data
                if len(data) == 0:
                    print "Zerwano polaczenie z serverem?"
                    running = 0
            #print dataReceived
            print "Wykryto zdarzenie: %s" % predict_event(dataReceived)
            self.client.send("Wykryto zdarzenie: %s" % predict_event(dataReceived))
            #if len(dataReceived)
            # == expectedData:
            #    self.client.send("przeslano plik pomyslnie")
            #import re
            #dataReceived = re.sub(',','.',dataReceived)
            #dataReceived = re.sub(':', ',', dataReceived)
            #dataReceived = re.sub('\n', ';\n', dataReceived)
            #with open('some.csv', 'w') as f:
            #    f.writelines(dataReceived)
        print "Client closed a connection."
        self.client.close()

class ProcessData(threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)

        #print self.data

    def run(self):
        features = sliding_window.features_from_window(self.data[self.data.columns[0:4]],
                                                            self.data[['time','latitude','longitude','speed']],
                                                            config.FEATURES)
        clf = pickle.load(open("svm_classfier.mdl", 'rb'))
        scaler = pickle.load(open("scaler.mdl", 'rb'))
        print clf.predict(scaler.transform(features.reshape(1, -1)
                                           ))

def predict_event(raw_data):
    data = pd.read_csv(StringIO(raw_data), sep=';', header=None,
                            names=['time', 'x', 'y', 'z', 'latitude', 'longitude', 'speed'])
    features = sliding_window.features_from_window(data[data.columns[0:4]],
                                                   data[['time', 'latitude', 'longitude', 'speed']],
                                                   config.FEATURES)
    clf = pickle.load(open("svm_classfier.mdl", 'rb'))
    scaler = pickle.load(open("scaler.mdl", 'rb'))
    return clf.predict(scaler.transform(features.reshape(1, -1)))[0]
if __name__ == "__main__":
    s = Server()
    s.run()

