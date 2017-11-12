#! /usr/bin/env python3
from Parseline import Parseline
from datetime import datetime
import time
from threading import Thread
# useful for the storage of hits
from collections import Counter, deque

# better display if running the program on Linux
import os
if os.name=="posix":
    import curses

class Monitoring(Thread):
    """ it monitors the loglines """

    def __init__(self,logPath,refresh,alertThreshold,monitoringRate):

        Thread.__init__(self)

        self.logPath = logPath # path of the logfile
        self.refresh= refresh # 10s
        self.alertThreshold= alertThreshold # 100 hits/min
        self.monitoringRate= monitoringRate # 120s

        # we initialise the "last read time" to read all values within monitoring rate
        self.lastReadTime=int(time.time())- self.monitoringRate

        # it is a list-like container with fast appends and pops on either end : O(1)
        self.deque= deque()

        # example : GET, PUT
        self.methods= Counter()

        # status 1:information; 2:success; 3:redirection; 4:client error; 5:server error
        self.status = Counter()

        # hits per section
        self.sections = Counter()

        # differents users (user1, user2...)
        self.users=Counter()
        
        self.hits = 0
        self.size = 0
        self.running = True
        self.alertStatus= False

        # useful for the testing the alerting logic
        self.displaying= True

        # we write the alerts
        self.alerts="\n" 

    def add_new_line(self, line):
        """ add a new line to be monitored """

        self.deque.append(line)
        self.status[line.status]+=1
        self.sections[line.section]+=1
        self.users[line.user]+=1
        self.methods[line.method]+=1
        self.size+= line.size
        self.hits+=1

    def delete_line(self):
        """ delete old lines typically after monitoring rate"""
        
        line= self.deque.popleft()
        self.status[line.status]-=1
        self.sections[line.section]-=1
        self.users[line.user]-=1
        self.methods[line.method]-=1
        self.size-= line.size
        self.hits-=1

    def reader(self):
        """ it reads the logfile+ append lines"""
        
        # we need to check all lines since lastReadTime
        lastReadTime=self.lastReadTime
        self.lastReadTime= int(time.time())
        
        with open(self.logPath,'r') as f:
            lines= f.readlines()
            i=1
            while i<=len(lines) and Parseline(lines[-i]).time > lastReadTime:
                self.add_new_line(Parseline(lines[-i]))
                i+=1

    def delete_old_lines(self):
        """ it drops lines (where line.time is old compared to monitoringRate) """
        
        while len(self.deque)!=0 and self.deque[0].time< self.lastReadTime-self.monitoringRate:
            self.delete_line()

    def statistics(self, element):
        """ uses Counter() elements to calculate statistics """
        
        disp=""
        if self.hits==0:
            for e in element.most_common(3):
                disp+=str(e[0])+" (%d%%)   " % (0)
        else:
            for e in element.most_common(3):
                disp+=str(e[0])+" (%d%%)   " % ((e[1]/self.hits)*100)
        return disp

    def average_traffic(self):
        """ calculate the average traffic in kb/hit during monitoring rate """
        
        res="0"
        if self.hits==0:
            return res
        else:
            res="%d kb/hit" % (self.size/self.hits)
            return res
            
    def start_alert(self):
        """ set alert mode on """
        
        alert = ("[%s] HIGH TRAFFIC generated an alert - hits/min = %d\n"
                 % (datetime.now().strftime("%d/%b/%Y:%H:%M:%S"),
                    (self.hits/self.monitoringRate)*60))
        self.alerts=alert+self.alerts
        with open("alert.log",'a') as a:
            a.write(alert)
        self.alertStatus= True
        
    def stop_alert(self):
        """ turns alert mode off """
        
        recovered= ("[%s] Recovered from high traffic\n"
                     % (datetime.now().strftime("%d/%b/%Y:%H:%M:%S")))
        self.alerts = recovered + self.alerts
        with open("alert.log",'a') as a:
            a.write(recovered)
        self.alertStatus= False

    def display(self):
        """ display the monitor depends on the OS used """
        if self.displaying:
            if os.name=="posix":
                self.display_linux()
            elif os.name=="nt":
                self.display_windows()
            else:
                self.stop("the OS is not Supported")

    def stop_displaying(self):
        """ prevents the program from displaying the monitoring screen while running """

        self.displaying=False
            
    def display_windows(self):
        """ display function for windows """
        
        display="********************************\n     Welcome to HTTP Monitor\
                \n********************************\n\n"
        
        display+="Parameters used:\
                \n Alert Threshold = %d hits/min\
        Refresh= %ds\
        Monitoring Rate= %ds \n\n" % (self.alertThreshold,self.refresh,
                                                self.monitoringRate)
        display+="Summary:\n\n"
        display+="Average hits/min: %d" % int(self.hits/self.monitoringRate*60)

        if self.alertStatus:
            display+=(" > %d " % self.alertThreshold)
            display+= "                  /!\*****ALERT******/!\\" 
        else:
            display+= "               Traffic is OK"

        display+="\n\nSections : "+self.statistics(self.sections)
        display+="\nUsers : "+self.statistics(self.users)
        display+="\nStatus : "+self.statistics(self.status)
        display+="\nMethods : "+self.statistics(self.methods)
        display+="\nAverage data : " + self.average_traffic()
        
        display+= "\n\nAlerts in alert.log:\n"
        display+= self.alerts

        # clear the last message and print
        os.system("cls")
        print(display)

    def init_window(self):
        """Initialize linux display window"""
        
        if os.name == "posix" and self.displaying:
            # Postition of cursor
            self.padPos = 0
            
            # Configure curses window
            self.stdscr = curses.initscr()

            # to be able to use colors
            curses.start_color()
            curses.use_default_colors()
            
            # turn-off automatic echoing of keys to the sceen
            curses.noecho()
            
            # react to the keys instantly ==> cbreak mode
            curses.cbreak()

            # don't wait for the user
            self.stdscr.nodelay(True)

            # get rid of the flashing cursor
            self.stdscr.leaveok(True)

    def display_linux(self):
        """ display function for Linux """
        
        size = self.stdscr.getmaxyx()
        self.pad=curses.newpad(self.alerts.count("\n")+50,200) #otherwise printing errors will occur when too much alerts
        
        title="********************************\n     Welcome to HTTP Monitor\
                \n********************************\nPress Q to quit\n\n"
        self.pad.addstr(0, 0, title, curses.A_BOLD)
        
        parameters="Parameters used:\
                    \n Alert Threshold = %d hits/min\
        Refresh= %ds\
        Monitoring Rate= %ds \n\n" % (self.alertThreshold,self.refresh,
                                                self.monitoringRate)
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        self.pad.addstr(parameters, curses.color_pair(1))
        self.pad.addstr("Summary:\n", curses.A_BOLD)
        self.pad.addstr("Average hits/min: ")
        self.pad.addstr(str(int(self.hits/self.monitoringRate*60)),
                            curses.A_BOLD)

        if self.alertStatus:
            self.pad.addstr((" > %d " % self.alertThreshold))
            self.pad.addstr("                  ")
            self.pad.addstr("/!\*****ALERT******/!\\", curses.A_STANDOUT)

        else:
            curses.init_pair(2, curses.COLOR_GREEN, -1)
            self.pad.addstr("               Traffic is OK", curses.color_pair(2))

        stats="\n\nSections : "+ self.statistics(self.sections)
        stats+="\nUsers : "+self.statistics(self.users)
        stats+="\nStatus : "+self.statistics(self.status)
        stats+="\nMethods : "+self.statistics(self.methods)
        stats+="\nAverage data : " + self.average_traffic()
        self.pad.addstr(stats)
        
        self.pad.addstr("\n\nAlerts in alert.log:\n", curses.A_BOLD)
        self.pad.addstr(self.alerts)
        
        self.pad.refresh(self.padPos, 0, 0, 0, size[0]-1, size[1]-1)

    def check_user(self):
        if os.name=="posix" and self.displaying:
            q=self.stdscr.getch()
            if q==ord('q'):
                self.stop()

    def run(self):
        """ function that starts the monitoring """
        
        self.init_window()
        while self.running:
            self.check_user()
            
            if self.lastReadTime + self.refresh < int(time.time()):
                self.reader()
                self.delete_old_lines()
                Average_hits= int(self.hits/self.monitoringRate*60)
                
                if Average_hits > self.alertThreshold and not self.alertStatus:
                    self.start_alert()
                    if os.name=="posix" and self.displaying:
                        curses.beep()
                    
                elif Average_hits < self.alertThreshold and self.alertStatus:
                    self.stop_alert()
                    
                self.display()

    def stop(self):
        """ stops the monitoring """
        
        self.running=False
        if os.name=="posix" and self.displaying:
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            
                    
        
        
                    
