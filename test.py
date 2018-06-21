import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

# Crunch Input Data to Create Scanner Positions + Plot Coordinates
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
        liveGather(center, fine_range, fine_n, course_range, course_n)
                   
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
    
ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
