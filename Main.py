#! /usr/bin/env python3
import configparser
from time import sleep
from LogGenerator import LogGenerator
from Monitoring import Monitoring

# reads configuration
configuration=configparser.ConfigParser()
configuration.read("parameters.cfg")

# parsing the parameters:
logPath=str(configuration.get("Simulation","logPath"))
refresh = float(configuration.get("Simulation","refresh"))
alertThreshold = float(configuration.get("Simulation","alertThreshold"))
monitoringRate = float(configuration.get("Simulation","monitoringRate"))
rate = float(configuration.get("Simulation","generationRate"))

# defines loggenerator and monitor
log_generator = LogGenerator(logPath, rate)
monitor= Monitoring(logPath,refresh, alertThreshold, monitoringRate)

# starts the simulation and monitoring
log_generator.start()
sleep(1)
monitor.start()


# waits until monitor finishes to end generation of lines
monitor.join()
log_generator.stop()
log_generator.join()

