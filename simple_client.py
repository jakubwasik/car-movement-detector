from socket import *
import csv
import time
data = ""
with open('csv-test.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter = ',')
    for row in reader:
        data+=','.join(row)
        data+='\n'

s = socket(AF_INET, SOCK_STREAM) #utworzenie gniazda
s.connect(('localhost', 8888)) # nawiazanie polaczenia
s.send("Wysylam CSV: {}".format(len(data.encode("utf8"))))
response = s.recv(1024)

print response
data_send = 0
time_started = time.time()
print time_started
if response == str(len(data.encode("utf8"))):
    while data_send < len(data.encode("utf8")):
        print "petla WHILE"
        currSend = s.send(data[data_send:])
        if currSend == 0:
            print "server odrzucil polaczenie"
        data_send += currSend
print "juz po wszystkim"
serverResponse = s.recv(1024) #odbior danych (max 1024 bajtow)
print serverResponse
serverResponse = s.recv(1024)
s.close()
print time.time() - time_started
print time.time()