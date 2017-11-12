#! /usr/bin/env python3
import unittest
import time
from LogGenerator import LogGenerator
from Monitoring import Monitoring
from Parseline import Parseline


class TestLogGenerator(unittest.TestCase):

    def test_LogGenerator(self):
        """Tests if the log generator works"""
        
        print("test_LogGenerator")
        logPath = "test.log"
        rate=100
        log_Generator = LogGenerator(logPath, rate)
        log_Generator.start()
        time.sleep(1)
        log_Generator.stop()
        log_Generator.join()
        with open(logPath, "r") as f:
            lines = f.readlines()
            
        self.assertTrue(len(lines) > 0)

class TestParser(unittest.TestCase):

    def test_Parser(self):
        """Tests if the parser works"""

        print("test_Parser")
        line=Parseline(r'192.168.7.6 - user3 [22/11/2016:20:11:21 +0000] "DELETE /game_02 HTTP/1.0" 500 5000')
        date=time.strptime('22/11/2016:20:11:21',"%d/%m/%Y:%H:%M:%S")
        datesec=time.mktime(date)
        
        self.assertEqual(line.host,"192.168.7.6")
        self.assertEqual(line.rfc1413,"-")
        self.assertEqual(line.user,"user3")
        self.assertEqual(line.method,"DELETE")
        self.assertEqual(line.section,"/game_02/")
        self.assertEqual(line.version,"HTTP/1.0")
        self.assertEqual(line.status,5)
        self.assertEqual(line.size,5000)
        self.assertEqual(line.time,datesec)

class TestMonitor_Alert(unittest.TestCase):

    def test_Alert_ON(self):
        """Tests if the alert is triggered when the Threshold is exceeded"""
        

        print("test_Alert_ON")
        
        # we create a logfile with 20 lines to be read by Monitoring
        date= time.strftime("%d/%m/%Y:%H:%M:%S +0000", time.localtime())
        line='192.168.7.6 - user3 [%s] "DELETE /game_02 HTTP/1.0" 500 5000'% date
        
        with open("test2.log","w") as f:
            for i in range(20):
                f.write(line)
                f.write("\n")
                f.flush
                
        # monitor will read all 20 lines, which is above the threshold 10 : alertStatus becomes True        
        monitor= Monitoring("test2.log",1, 10, 5) # refresh,alertThreshold,MonitoringRate
        monitor.stop_displaying()
        self.assertFalse(monitor.alertStatus)
        monitor.start()
        time.sleep(0.9)
        self.assertTrue(monitor.alertStatus)
        monitor.stop()
        monitor.join()
        

    def test_Alert_OFF(self):
        """Tests if the alert is turned off below the Threshold :
        we repeat the same process as above to trigger alert
        and then simply wait to recover from alert"""
        
        print("test_Alert_OFF")

        date= time.strftime("%d/%m/%Y:%H:%M:%S +0000", time.localtime())
        line='192.168.7.6 - user3 [%s] "DELETE /game_02 HTTP/1.0" 500 5000'% date
        
        with open("test3.log","w") as f:
            for i in range(20):
                f.write(line)
                f.write("\n")
                f.flush
                
        monitor= Monitoring("test3.log",1, 10, 1) # refresh, alertThreshold, MonitoringRate
        monitor.stop_displaying()
        self.assertFalse(monitor.alertStatus)
        monitor.start()
        time.sleep(0.9)
        self.assertTrue(monitor.alertStatus)
        time.sleep(3)
        self.assertFalse(monitor.alertStatus)
        monitor.stop()
        monitor.join()
               
            
        
if __name__ == '__main__':
    unittest.main()
