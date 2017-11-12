#! /usr/bin/env python3

import random
import time
from threading import Thread

class LogGenerator(Thread):
    """ it creates random lines and write them into the log file """
    
    def __init__(self,logPath,rate):
        
        Thread.__init__(self)
    
        # path of the logfile 
        self.logPath=logPath

        # rate of generation of lines
        self.rate=rate

        # controls the generation of lines and the Thread
        self.running=True

        self.host=[1,2,3,4,5,6,7,8,9,0]
        self.rfc1413=["-"]
        self.username=["Mehdi","user1","user2","user3","user4"]
        self.chemins=["/pages","/pages","/contact","/search","/admin","/donate","/forum","/images"]
        self.methods=["GET","GET","POST","PUT","PATCH","DELETE"]
        self.status=["200","200","200","200","100","402","403","404","404","414","500","300"]
        self.template='%(host)s %(rfc1413)s %(usrid)s [%(date)s] "%(request)s" %(status)s %(size)s'
        
        
    def create_line(self):
        """ it creates a random line """
        
        # create random IPs
        host= "192.168.%d.%d" % (random.choice(self.host),random.choice(self.host))
        
        # create random request-for-comments 1413
        rfc1413= random.choice(self.rfc1413)
        
        # create random user id and username
        usrid= random.choice(self.username)
        
        # create a date 
        date= time.strftime("%d/%m/%Y:%H:%M:%S +0000", time.localtime())
        
        # create a random request
        s= [random.choice(self.methods), random.choice(self.chemins), "HTTP/1.0"]
        request=" ".join(s)
        
        # create a random HTTP status code returned to the client
        status= random.choice(self.status)
        
        # return a random size (bytes) of the object returned to the client
        size= random.randrange(100,10000)

        line={  "host":host,
                "rfc1413":rfc1413,
                "usrid":usrid,
                "date":date,
                "request":request,
                "status":status,
                "size":size}
        return line

    def write_log(self, file):
        """ it writes a line into the logfile"""
        
        file.write(self.template % self.create_line())
        file.write("\n")
        
        # so that the file is not empty
        file.flush()

    def run(self):
        """ it runs the simulation """
        
        with open(self.logPath,"w") as f:
            while self.running:
                self.write_log(f)
            
                # we randomise the creation of hits a bit around self.rate
                time.sleep(random.gauss(1,0.05)*60/self.rate)

    def stop(self):
        """ it stops the Threading """
        
        self.running=False


  
        






