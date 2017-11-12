#! /usr/bin/env python3
import time

class Parseline:
    """it extracts the values in a line of w3c HTTTP access log"""
    
    def __init__(self,line):
        """ it inserts the values of the different fields into a hash map """
        # example of log line :   
        # 192.168.4.0 - Mehdi [21/11/2016:23:16:06 +0000]
        # "PATCH /pages HTTP/1.0" 414 5894
        
        parse=line.split(' ')
        self.host=parse[0]
        self.rfc1413=parse[1]
        self.user=parse[2]

        # we put the date in seconds for statistics purposes
        date = time.strptime(parse[3].strip("[]"), "%d/%m/%Y:%H:%M:%S")
        self.time= time.mktime(date)
        
        self.method=parse[5][1:]
        request=parse[6]
        self.section="/"+request.split("/")[1]+"/"
        self.version=parse[7][:-1]
        self.status=int(parse[8][0])
        self.size=int(parse[9])

