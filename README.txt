**To edit program code, change "Scanner" file extension from ".pyw" to ".py"


FUNCTION DESCRIPTIONS: 

stop(): stops the motor immediately

stepConverter(inches): converts inches to steps

inchConverter(steps): converts steps to inches

goto(pos): repositions pinhole to certain position (inches)
- Positions are absolute, NOT relative
- 0 position defined as Moonlite motor extended all the way out

getCurrent(mode): returns current mode (inches or steps) of pinhole

relay(num): switches relay #num to opposite state

dataGather(center, fine_range, fine_n, course_range, course_n): calculate step sizes, 
create negative and positive positions lists, create X and Y simulation plot coordinates

scanner(pos, xmax): run scanner algorithm given best focus position and max range

main(): run GUI


****For any questions email: amangu98@g.ucla.edu
