'''

Animesh Mangu
SURF 2017

'''

import serial
import sys
import time

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Moonlite Motor Connection
port = serial.Serial('/dev/ttyUSB0')

# Create GUI Window
app = QApplication(sys.argv)
w = QWidget()
w.setWindowTitle('Moonlite Scanner')
logOutput = QTextEdit(w)

# Scanner Input Fields
center = QLineEdit(w)
cnum = QLineEdit(w)
cdomain = QLineEdit(w)
fnum = QLineEdit(w)
fdomain = QLineEdit(w)
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

# Live Plot
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

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
        relayName = '/dev/ttyACM0'
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

        log = open("log.txt","w")
        
        # SETTING TO BEST FOCUS POSITION
        if(initial == center):
                logOutput.append("Already at Best Focus Position.")
        else:
                goto(center)
                logOutput.append("Repositioning at Best Focus Position...")

                while True:
                        app.processEvents()
                        current = getCurrent("steps")
                        if(current == center):
                                logOutput.append("Best Focus Position reached.\n")
                                time.sleep(float(delay.text()) + 1.7)
                                break
        
        log.write(str(getCurrent("inches")) + "\n")

        # MOVING TO AND BACK FROM POSITIVE MAXIMUM
        logOutput.append("Moving towards Positive Maximum...")
        goto(domain)
        
        while True:
                app.processEvents()
                if(getCurrent("steps") == domain):
                        log.write(str(getCurrent("inches")) + "\n")
                        logOutput.append("Positive maximum reached.\n")
                        time.sleep(float(delay.text()) + 1.7)
                        break
                
        logOutput.append("Stepping back to Best Focus Position...")
        
        for i in range(len(positive)):
                app.processEvents()
                
                goto(stepConverter(positive[i]))
                relay(0)
                
                while True:
                        app.processEvents()
                        if(getCurrent("steps") == stepConverter(positive[i])):
                                log.write(str(getCurrent("inches")) + "\n")
                                relay(0)
                                logOutput.append("Position: " + str(getCurrent("inches")) + " inches")
                                time.sleep(float(delay.text()) + 1.7)
                                break

        logOutput.append("Returned to Best Focus Position.\n")
        time.sleep(float(delay.text()) + 1.7)

        # MOVING TO AND BACK FROM NEGATIVE MAXIMUM
        logOutput.append("Moving towards Negative Maximum...")
        goto(negative_domain)
        
        while True:
                app.processEvents()
                current = getCurrent("steps")
                if(current == negative_domain):
                        log.write(str(getCurrent("inches")) + "\n")
                        logOutput.append("Negative maximum reached.\n")
                        time.sleep(float(delay.text()) + 1.7)
                        break

        logOutput.append("Stepping back to Best Focus Position...")
                
        for j in range(len(negative)):
                app.processEvents()

                goto(stepConverter(negative[j]))
                relay(0)

                while True:
                        app.processEvents()
                        if(getCurrent("steps") == stepConverter(negative[j])):
                                log.write(str(getCurrent("inches")) + "\n")
                                relay(0)
                                logOutput.append("Position: " + str(getCurrent("inches")) + " inches")
                                time.sleep(float(delay.text()) + 1.7)
                                break

        while True:
                app.processEvents()
                current = getCurrent("steps")
                if(current == center):
                        logOutput.append("Best Focus Position reached.\n")
                        time.sleep(float(delay.text()))
                        break

        logOutput.append("Scan Complete.")
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

def liveGather(center, fine_range, fine_n, course_range, course_n):
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
        positive_list.sort(reverse = True)
        
        for i in range(len(positive_list)):
                while True:
                        if(getCurrent("steps") == stepConverter(positive_list[i])):
                                positive.append(positive_list[i])
                                break

        # NEGATIVE LIST
        negative_list = course_2 + fine_2
        negative_list.sort(reverse = False)
        
        for j in range(len(negative_list)):
                while True:
                        if(getCurrent("steps") == stepConverter(positive_list[i])):
                                negative.append(negative_list[j])
                                break
def animate(i):
        dataGather(float(center.text()), float(fdomain.text()), float(fnum.text()), float(cdomain.text()), float(cnum.text()))
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
        ax1.clear()
        ax1.plot(xcoords, ycoords)
                                                 
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

        center_label = QLabel("Best Focus Position: ", w)
        center_label.move(20, 170)
        center.setText("0.6819") # default
        center.move(160, 160)
        center.resize(70, 30)

        cdomain_label = QLabel("Course Step Range: ", w)
        cdomain_label.move(270, 210)
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
                ani = animation.FuncAnimation(fig, animate, interval=1000)
                plt.show()
                scanner(float(center.text()), float(cdomain.text()))

        def reset():
                goto(0)
                logOutput.append("Resetting to 0 inches.\n")

        def repos():
                value = float(position.text())
                goto(stepConverter(value))
                logOutput.append("Focusing to " + str(value) + " inches.\n")

        def updater():
                position.setText(str(getCurrent("inches")))

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

                plt.ylabel('Position (Inches)')
                plt.xlabel('Time (s)')

                # refresh canvas
                canvas.draw()
                canvas.show()
                

        # Connect signals to buttons
        scan_button.clicked.connect(start_scan)
        stopper.clicked.connect(stop)
        resetter.clicked.connect(reset)

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
