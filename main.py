from machine import I2C, Pin, Timer
import time
import framebuf
import ssd1306
import si5351
import gc

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
c1count = 0
c2count = 0
tcheck = False

si5351stat = clkgen.init(si5351.CRYSTAL_LOAD_0PF, 25000000, -4000)

def sanitycheck(timer):
    global b1count, b2count, c1count, c2count, tcheck, b1pressdb, b2pressdb
    if(tcheck is True):
        tcheck = False
        print("c1c {} b1c {} c2c {} b2c {}".format(c1count, b1count,c2count,b2count))
        if(b1count is c1count+1):
            print("double")
            b1count+=1
            b1pressbd=True
        elif(b2count is c2count+1):
            print("double")
            b2count+=1
            b2pressbd=True
    gc.collect()

def b1_handler(pin):										# handler function for the button press interrupt on the rising edge
    global b1count, b1press, new_time, b1last_time, c1count, tcheck
    new_time = time.ticks_ms()
    b1.irq(handler=None)
    c1count = b1count
    if (new_time - b1last_time) > 200:
        print("tcheck {}".format(tcheck))
        print("b1 single press\n")
        b1press = True
        b1count+=1
        if(tcheck is False):
            tcheck = True
            timer = Timer(period=200, mode=Timer.ONE_SHOT, callback=sanitycheck)
        b1last_time = new_time
    b1.irq(handler=b1_handler, trigger=Pin.IRQ_RISING)

def b2_handler(pin):										# handler function for the button press interrupt on the rising edge
    global b2count, b2last_time, b2press, b1press, menu, b2pressdb, c2count, tcheck
    new_time = time.ticks_ms()
    #print("b2 time {}".format(new_time))
    b2.irq(handler=None)
    c2count = b2count
    if (new_time - b2last_time) > 200:						#if current time and last time the button was pressed are higher than 200ms count it as one button press
        b2press=True
        b2pressdb=False
        b2count+=1
        print("b1 {} b2 {}".format(b1press,b2press))
        #print("{}".format((new_time - b2last_time)))
        if(tcheck is False):
            tcheck = True
            timer = Timer(period=200, mode=Timer.ONE_SHOT, callback=sanitycheck)
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
    
    if(b1press is True):
        #print("b1 press")
        if(x-1 is -1 or x is -1):
            x=x
        else:
            x-=1
    if(b1pressdb is True):
        print("db press true")
        display.text("!", 100, xr)
        #if(x is 0):
        #   display.text("!", 100, xr)
    """
    if(b2press is True and b2pressdb is False):
        #print("press true db not")
        if(x+1 is 4 or x is 4):
            x=x
        else:
            print("decrease")
            x+=1
    """
    display.text("<", 120, xr)
    
    display.show()

while True:
    if(menu is True):
        if(b1press is True and b2press is True):
            print("menu switch")
            menu=False
        drawmenu(msettings)
        b1press=False
        b2press=False
    if(menu is False):
        if(b1press is True and b2press is True):
            print("menu switch")
            menu=True
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
