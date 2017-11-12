HTTP log monitoring console program (python 3)
-----------------------------------------------.


* Create a simple console program that monitors HTTP traffic on your machine:
* Consume an actively written-to w3c-formatted HTTP access log
* Every 10s, display in the console the sections of the web site with the most hits (a section is defined as being what's before the second '/' in a URL. i.e. the section for "http://my.site.com/pages/create' is "http://my.site.com/pages"), as well as interesting summary statistics on the traffic as a whole.
* Make sure a user can keep the console app running and monitor traffic on their machine
* Whenever total traffic for the past 2 minutes exceeds a certain number on average, add a message saying that ???High traffic generated an alert - hits = {value}, triggered at {time}???
* Whenever the total traffic drops again below that value on average for the past 2 minutes, add another message detailing when the alert recovered
* Make sure all messages showing when alerting thresholds are crossed remain visible on the page for historical reasons.
* Write a test for the alerting logic
* Explain how you???d improve on this application design


--------Description and Architecture :

This console program monitors HTTP traffic (it uses python 3).
it displays useful statistics about the general traffic on the server.
Whenever the traffic exceeds a threshold (ex: 100 hits/min), alert_mode is turned on and alerts are automatically stored in alert.log. You have nicer visulasations on Linux (+ it beeps when alert turns on)

The files are :

-Monitoring.py 
-LogGenerator.py
-Parseline.py
-Test.py
-Main.py
-Readme.md

*LogGenerator class creates random loglines stored in logpath

*Parseline class parses a log line to be able to calculate statistics

*Monitoring class calls Parseline and handles monitoring process : display (we use curses python library for Linux display), calculate and refresh statistics, alerts.

*Main starts log generation and monitoring

*Test uses unnitest to check the classes and the alerting logic



---------Run the program:

-Set log path and parameters in parameters.cfg
-Run 'python3 Main.py'

-On Linux, please press Q to exit the display.
-On windows, please press ctrl+c to exit the display.

---------Improvements:

- we could add another LogGenerator to handle several servers at the same time
- we could display interesting statistics as section with most errors (status 4 or 5)
- change a bit the Main so that we could monitor a real server without generating log lines ourselves 
- we could handle the timezone in the calculations (we got rid of it)
- could use cx_Freeze to get a .exe file with no need to have python if we want to launch the program (the drawback is if we send it by mail, it goes directly to spam)
- we could use ncurses to draw nice data-visualisations
- just like pressing q to quit, we could add modifications while monitoring
for example ; changing rates (generation, monitoring, threshold)

