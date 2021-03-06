'''

Animesh Mangu
SURF 2017

'''

import serial
import serial.tools.list_ports

import sys
import os
import time

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

ports = list(serial.tools.list_ports.comports())

# MOONLITE SCAN
portName = ""
moonlite = False
for m in ports:
    if "FTDIBUS" in m[2]:
        portName = str(m[0])
        moonlite = True

if(moonlite == False):
    print "Moonlite not connected."

port = serial.Serial(portName);

# RELAY SCAN
relay = False
relayName = ""
for r in ports:
    if "SNR=5" in r[2]:
        relayName = str(r[0])
        relay = True

if(relay == False):
    print "Relay not connected."

# Create GUI Window
app = QApplication(sys.argv)
w = QWidget()
w.setWindowTitle('Moonlite Scanner')
file_name = QLineEdit(w)
logOutput = QTextEdit(w)
delay = QLineEdit(w)

# Positive Step / Position Lists
course = list()
fine = list()
positive = list()

# Negative Step / Position Lists
course_2 = list()
fine_2 = list()
negative = list()

# Coordinates for Simulation Plot
xcoords = list()
ycoords = list()

# Stop the Motor
def stop():
        port.write(":FQ#")
        logOutput.append("Stopped.\n")

# Convert Steps -> Inches
def stepConverter(inches):
        steps = inches * 6250
        return int(steps)

# Convert Inches -> Steps
def inchConverter(steps):
        inches = steps * 0.00016
        return inches

# Displace Motor to a Position (inches)
def goto(pos):
        hexed_pos = str(format(int(pos), '04x')).upper()
        port.write(":SF#")
        port.write(":SN" + hexed_pos + "#")
        port.write(":FG#")

# Get Current Position (inches or steps)
def getCurrent(mode):
        port.write(":GP#")
        inp = port.read(5)
        pos = int(inp.translate(None, '#'), 16)

        if(mode == "steps"):
                return pos
        elif(mode == "inches"):
                return inchConverter(pos)

# Change Current Relay State
def relay(num):
        relayNum = num
        relayPort = serial.Serial(relayName, 921600, timeout=1)

        relayPort.write("relay read "+ str(relayNum) + "\n\r")
        response = relayPort.read(25)

        if(response.find("on") > 0):
                relayPort.write("relay off " + str(relayNum) + "\n\r")
        elif(response.find("off") > 0):
	        relayPort.write("relay on " + str(relayNum) + "\n\r")

        relayPort.close()

# Scanner Main
def scanner(pos, xmax):
        center = stepConverter(float(pos))
        domain = stepConverter(float(xmax))
        negative_domain = center - (domain - center)
        initial = getCurrent("steps")

        log = open(str(file_name.text()),"w")

        # SETTING TO BEST FOCUS POSITION
        if(initial == center):
                message = "Already at Best Focus Position."
                logOutput.append(message)
                log.write(message)

                relay(0) # On
                time.sleep(float(delay.text()))
                relay(0) # Off
        else:
                message = "Repositioning at Best Focus Position..."
                logOutput.append(message)
                log.write(message)

                goto(center)

                while True:
                        app.processEvents()
                        current = getCurrent("steps")
                        if(current == center):
                                message = "Best Focus Position reached.\n"
                                logOutput.append(message)
                                log.write(message)

                                relay(0) # On
                                time.sleep(float(delay.text()))
                                relay(0) # Off

                                break

        # MOVING TO AND BACK FROM POSITIVE MAXIMUM
        message = "Moving towards Positive Maximum...\n"
        logOutput.append(message)
        log.write(message)

        goto(domain)

        while True:
                app.processEvents()
                if(getCurrent("steps") == domain):
                        message = "Positive maximum reached.\n"
                        logOutput.append(message)
                        log.write(message)

                        relay(0) # On
                        time.sleep(float(delay.text()))
                        relay(0) # Off

                        break

        message = "Stepping back to Best Focus Position..."
        logOutput.append(message)
        log.write(message)

        for i in range(len(positive)):
                app.processEvents()

                goto(stepConverter(positive[i]))
                relay(0) # On

                while True:
                        app.processEvents()
                        if(getCurrent("steps") == stepConverter(positive[i])):
                                message = "Position: " + str(getCurrent("inches")) + " inches"
                                logOutput.append(message)
                                log.write(message)

                                relay(0) # Off
                                time.sleep(float(delay.text()))

                                break

        message = "Returned to Best Focus Position.\n"
        logOutput.append(message)
        log.write(message)

        relay(0) # On
        time.sleep(float(delay.text()))
        relay(0) # Off

        # MOVING TO AND BACK FROM NEGATIVE MAXIMUM
        logOutput.append("Moving towards Negative Maximum...")
        goto(negative_domain)

        while True:
                app.processEvents()
                current = getCurrent("steps")
                if(current == negative_domain):
                        message = "Negative maximum reached.\n"
                        logOutput.append(message)
                        log.write(message)

                        relay(0) # On
                        time.sleep(float(delay.text()))
                        relay(0) # Off

                        break

        message = "Stepping back to Best Focus Position..."
        logOutput.append(message)
        log.write(message)

        for j in range(len(negative)):
                app.processEvents()

                goto(stepConverter(negative[j]))
                relay(0) # On

                while True:
                        app.processEvents()
                        if(getCurrent("steps") == stepConverter(negative[j])):
                                message = "Position: " + str(getCurrent("inches")) + " inches"
                                logOutput.append(message)
                                log.write(message)

                                relay(0) # Off
                                time.sleep(float(delay.text()))

                                break

        while True:
                app.processEvents()
                current = getCurrent("steps")
                if(current == center):
                        message = "Best Focus Position reached.\n"
                        logOutput.append(message)
                        log.write(message)

                        relay(0) # On
                        time.sleep(float(delay.text()))
                        relay(0) # Off

                        break

        message = "Scan Complete."
        logOutput.append(message)
        log.write(message)

        log.close()

# Crunch Input Data to Create Scanner Positions + Plot Coordinates
def dataGather(center, fine_range, fine_n, course_range, course_n):
        # RESETTING OLD DATA
        while len(fine) > 0 : fine.pop()
        while len(course) > 0 : course.pop()

        while len(fine_2) > 0 : fine_2.pop()
        while len(course_2) > 0 : course_2.pop()

        while len(positive) > 0 : positive.pop()
        while len(negative) > 0 : negative.pop()

        # RESETTING PLOT COORDINATES
        while len(xcoords) > 0 : xcoords.pop()
        while len(ycoords) > 0 : ycoords.pop()

        # STEPS
        fine_step = (fine_range - center) / fine_n
        course_step = (course_range - center) / course_n

        # NEGATIVE RANGE
        fine_neg_range = center - (fine_range - center)
        course_neg_range = center - (course_range - center)

        # POSITIVE POSITIONS
        pos = course_range
        while(pos > fine_range):
                pos = round(pos, 3)
                course.append(pos)
                pos -= course_step

        pos = fine_range
        fine.append(pos)
        while(pos > center):
                pos -= fine_step
                pos = round(pos, 3)
                fine.append(pos)
        fine[-1] = center

        # NEGATIVE POSITIONS
        neg = course_neg_range
        while(fine_neg_range > neg):
                neg = round(neg, 3)
                course_2.append(neg)
                neg += course_step

        neg = fine_neg_range
        neg = round(neg, 3)
        fine_2.append(neg)
        while(center > neg):
                neg += fine_step
                neg = round(neg, 3)
                fine_2.append(neg)
        fine_2[-1] = center

        # POSITIVE LIST
        positive_list = course + fine
        for i in range(len(positive_list)):
                positive.append(positive_list[i])
        positive.sort(reverse = True)

        # POSTIVE LIST
        negative_list = course_2 + fine_2
        for j in range(len(negative_list)):
                negative.append(negative_list[j])
        negative.sort(reverse = False)

        # CREATING Y-COORDINATES
        for a in range(2):
                ycoords.append(center)

        for i in range(len(positive)):
                ycoords.append(positive[i])
                ycoords.append(positive[i])

        for j in range(len(negative)):
                ycoords.append(negative[j])
                ycoords.append(negative[j])

        # CREATING X-COORDINATES
        xcoords.append(0)

        time_delay = float(delay.text())

        for x in range((len(ycoords) / 2) + 1):
                if(x > 0):
                        if((len(ycoords) - len(xcoords)) == 1):
                                xcoords.append(time_delay * x)
                                break

                        xcoords.append(time_delay * x)
                        xcoords.append(time_delay * x)

# GUI Main Application
def main():
        pos_label = QLabel("Position: ", w)
        pos_label.move(35, 30)
        position = QLineEdit(str(getCurrent("inches")), w)
        position.move(102, 20)
        position.resize(70, 30)
        inches = QLabel("inches", w)
        inches.move(177, 30)

        go = QPushButton('Focus', w)
        go.move(100, 60)

        refresh = QPushButton('Refresh', w)
        refresh.move(20, 60)

        stopper = QPushButton('Stop', w)
        stopper.move(20, 100)

        resetter = QPushButton('Reset', w)
        resetter.move(100, 100)

        logger = QLabel("Log File: ", w)
        logger.move(245, 75)
        opener = QPushButton('Open', w)
        opener.move(377, 65)
        file_name.setText(str(time.strftime('%Y-%m-%d-%H-%M-%S')) + " - scanLog.txt") # default
        file_name.move(245, 100)
        file_name.resize(225, 30)

        center_label = QLabel("Best Focus Position: ", w)
        center_label.move(20, 170)
        center = QLineEdit(w)
        center.setText("0.6819") # default
        center.move(160, 160)
        center.resize(70, 30)

        cdomain_label = QLabel("Course Step Range: ", w)
        cdomain_label.move(270, 210)
        cdomain = QLineEdit(w)
        cdomain.setText("1") # default
        cdomain.move(400, 200)
        cdomain.resize(70, 30)

        cnum_label = QLabel("Course Step #: ", w)
        cnum_label.move(270, 250)
        cnum = QLineEdit(w)
        cnum.setText("4") # default
        cnum.move(400, 240)
        cnum.resize(70, 30)

        fnum_label = QLabel("Fine Step #: ", w)
        fnum_label.move(20, 250)
        fnum = QLineEdit(w)
        fnum.setText("3") # default
        fnum.move(160, 240)
        fnum.resize(70, 30)

        fdomain_label = QLabel("Fine Step Range: ", w)
        fdomain_label.move(20, 210)
        fdomain = QLineEdit(w)
        fdomain.setText("0.8") # default
        fdomain.move(160, 200)
        fdomain.resize(70, 30)

        time_delay = QLabel("Integration Time: ", w)
        time_delay.move(270, 170)
        delay.setText("2") # default time
        delay.move(400, 160)
        delay.resize(70, 30)

        simulate = QPushButton("Simulate Graph", w)
        simulate.move(20, 290)

        scan_stop = QPushButton("Stop Scan", w)
        scan_stop.move(295, 290)

        scan_button = QPushButton("Start Scan", w)
        scan_button.move(395, 290)

        figure = plt.figure(figsize = (20, 10))
        plt.ylabel('Distance')
        plt.xlabel('Time')
        canvas = FigureCanvas(figure)
        canvas.setWindowTitle("Simulated Graph")

        # Set window size.
        w.resize(490, 610)

        logOutput.setReadOnly(True)
        logOutput.setLineWrapMode(QTextEdit.NoWrap)
        logOutput.move(20, 340)
        logOutput.resize(450, 250)

        # Action Functions
        @pyqtSlot()
        def start_scan():
                dataGather(float(center.text()), float(fdomain.text()), float(fnum.text()), float(cdomain.text()), float(cnum.text()))
                scanner(float(center.text()), float(cdomain.text()))

        def stop_scan():
                stop()
                message = "Scan Stopped."
                logOutput.append(message)

                log = open(str(file_name.text()),"w")
                log.write(message)
                log.close()

        def reset():
                goto(0)
                logOutput.append("Resetting to 0 inches.\n")

        def repos():
                value = float(position.text())
                center.setText(str(value)) # Set BFP
                goto(stepConverter(value))
                logOutput.append("Focusing to " + str(value) + " inches.\n")

        def updater():
                position.setText(str(getCurrent("inches")))

        def open_log():
            os.startfile(str(file_name.text()))

        def plot():
                dataGather(float(center.text()), float(fdomain.text()), float(fnum.text()), float(cdomain.text()), float(cnum.text()))

                # create an axis
                ax = figure.add_subplot(111)
                ax.clear()

                ax.hold(False)

                ax.plot(xcoords, ycoords, '.-')

                ax.set_ylim([0, 1.8])
                # ax.set_xlim([0, 250])

                tick_spacing = 0.2
                ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

                plt.ylabel('Position (Inches)', fontsize = 20)
                plt.xlabel('Time (s)', fontsize = 20)

                # refresh canvas
                canvas.draw()
                canvas.show()


        # Connect signals to buttons
        scan_button.clicked.connect(start_scan)
        scan_stop.clicked.connect(stop_scan)
        stopper.clicked.connect(stop)
        resetter.clicked.connect(reset)

        opener.clicked.connect(open_log)

        refresh.clicked.connect(updater)
        go.clicked.connect(repos)
        simulate.clicked.connect(plot)

        # Show the window and run the app
        w.show()
        app.exec_()
        port.close()

# EXECUTION
if __name__ == "__main__":
        main()
