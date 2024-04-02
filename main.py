from machine import I2C
from machine import Pin
from machine import Timer
import time
import framebuf
import ssd1306
import si5351

i2c = I2C(0, scl=machine.Pin(1), sda=machine.Pin(0))
display = ssd1306.SSD1306_I2C(128, 64, i2c)
clkgen = si5351.SI5351(i2c)

b1 = Pin(9, Pin.IN, Pin.PULL_DOWN)
b1count=0
b1press=False
b1pressdb=False

b2 = Pin(8, Pin.IN, Pin.PULL_DOWN)
b2count=0
b2press=False
b2pressdb=False

b1last_time=0
b2last_time=0

menu=False

si5351stat = clkgen.init(si5351.CRYSTAL_LOAD_0PF, 25000000, -4000)

def b1_handler(pin):										# handler function for the button press interrupt on the rising edge
    global b1count, b1last_time, b1press, b2press, menu
    new_time = time.ticks_ms()
    print("b1 time {}".format(new_time))
    b1.irq(handler=None)
    if (new_time - b1last_time) > 200:
        presstime=time.ticks_ms()
        if(presstime - b1last_time) < 300:
            b1pressdb=True
            print("b1 double press {}".format((presstime - b1last_time)))
            b1count+=2
        else:
            b1pressdb=False
            b1count+=1
        b1last_time = new_time
    b1.irq(handler=b1_handler, trigger=Pin.IRQ_RISING)

def b2_handler(pin):										# handler function for the button press interrupt on the rising edge
    global b2count, b2last_time, b2press, b1press, menu, b2pressdb
    new_time = time.ticks_ms()
    print("b2 time {}".format(new_time))
    b2.irq(handler=None)
    if (new_time - b2last_time) > 200:						#if current time and last time the button was pressed are higher than 200ms count it as one button press
        presstime=time.ticks_ms()
        if(presstime - b2last_time) < 300:
            b2pressdb=True
            print("b2 double press {}".format((presstime - b2last_time)))
            b2count+=2
        else:
            b2pressdb=False
            b2count+=1
        
        #print("b1 {} b2 {}".format(b1press,b2press))
        #print("{}".format((new_time - b2last_time)))
        time.sleep_ms(100)
        b2last_time = new_time
        
    b2.irq(handler=b2_handler, trigger=Pin.IRQ_RISING) # re-enable the interrupt

b1.irq(handler=b1_handler, trigger=Pin.IRQ_RISING)
b2.irq(handler=b2_handler, trigger=Pin.IRQ_RISING)

class Menu:
    def __init__(self, title, item):
            self.title = title
            self.item = item

mmain = Menu("Main",[["A Count",0,False],["A state",1,False],["B count",2,False],["B state",3,False]])
msettings = Menu("Settings",[["si5351: ",0,False],["A state",1,False],["B count",2,False],["B state",3,False]])

i=0
x=0

def drawmenu(menu):
    global i, b1press, b2press, b1pressdb, b2pressdb, x
    xr = 19+x*10
    display.fill(0)
    display.text("{}".format(menu.title), 32,1)
    for i in range(0,4):
        ir = 19+i*10
        display.text("{}".format(menu.item[i][0]), 32, 19+i*10)
   
    if(b1press is False):
        #print("b1 press")
        if(x-1 is -1 or x is -1):
            x=x
        else:
            x-=1

    if(b2pressdb is True):
        #print("db press true")
        display.text("!", 100, xr)
        #if(x is 0):
        #   display.text("!", 100, xr)
    elif(b2press is False and b2pressdb is False):
        #print("press true db not")
        if(x+1 is 4 or x is 4):
            x=x
        else:
            print("decrease")
            x+=1

    display.text("<", 120, xr)
    display.show()

while True:
        if(menu is True):
            drawmenu(msettings)
            b1press=False
            b2press=False
        elif(menu is False):
            display.fill(0)
            display.text("A Count={}".format(b1count), 0, 1)
            display.text("A state={}".format(b1press), 0, 10)
            display.text("B state={}".format(b2press), 0, 42) 
            fbuf = framebuf.FrameBuffer(bytearray(100 * 10 * 2), 100, 10, framebuf.MONO_VLSB)
            fbuf.text("B Count={}".format(b2count), 0, 1)
            display.blit(fbuf, 0, 32, 0)
            display.show()
            b1press=False
            b2press=False
        else:
            b1press=False
            b2press=False
            menu=False
            print("else reached")
