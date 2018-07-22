from socket import *
import csv
import time
data = ""
with open(r'sensor data\normalized_labeled_test_data\
                hamowanie_2018-05-30-16-32-47_2018-05-30_16_33_21', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter = ',')
    for row in reader:
        data+=','.join(row)
        data+='\n'

s = socket(AF_INET, SOCK_STREAM) #utworzenie gniazda
s.connect(('localhost', 8888)) # nawiazanie polaczenia
s.send("Send File")
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
s.close()
