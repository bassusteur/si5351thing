from machine import I2C, Pin, Timer
import time
import framebuf
import ssd1306
import si5351
import gc
from menu import *

i2c = I2C(0, scl=machine.Pin(1), sda=machine.Pin(0))
display = ssd1306.SSD1306_I2C(128, 64, i2c)
clkgen = si5351.SI5351(i2c)
si5351stat = clkgen.init(si5351.CRYSTAL_LOAD_0PF, 25000000, -4000)

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

freq=1000000000
clkgen.set_freq(si5351.CLK2, freq)
clkgen.output_enable(si5351.CLK2, True)

def sanitycheck(timer, ccount):
    global b1count, b2count, tcheck, b1pressdb, b2pressdb
    if(tcheck is True):
        print("c1c {} b1c {} c2c {} b2c {}".format(c1count, b1count,c2count,b2count))
        if(b1count is ccount+1):
            print("double")
            b1count+=1
            b1pressbd=True
        elif(b2count is ccount+1):
            print("double")
            b2count+=1
            b2pressbd=True
        tcheck = False
        print("end of tcheck")
    gc.collect()

last_time = 0

def handler(bt):
    global last_time, tcheck, b1press, b2press, b1count, b2count
    if(bt is 0):
            b1.irq(handler=None)
    if(bt is 1):
            b2.irq(handler=None)
    new_time = time.ticks_ms()
    if (new_time - last_time) > 200:
        print("{} {}".format(b1press,b2press))
        print("press {}".format(new_time))
        if(bt is 0):
            b1press=True
            b1count+=1
        if(bt is 1):
            b2press=True
            b2count+=1
        last_time = new_time
    if(bt is 0):
            b1.irq(handler=b1f, trigger=Pin.IRQ_RISING)
    if(bt is 1):
            b2.irq(handler=b2f, trigger=Pin.IRQ_RISING)

b1f = lambda a: handler(0)
b2f = lambda a: handler(1)

b1.irq(handler=b1f, trigger=Pin.IRQ_RISING)
b2.irq(handler=b2f, trigger=Pin.IRQ_RISING)

mmain = Menu("SI5351",[["si5351: ",si5351stat,70],["f: ",freq,45]],True)
msettings = Menu("Settings",[["si5351: ",si5351stat,50]],False)

menulist = [mmain,msettings]
menulist[0].item[1][1] = freq / 100000000

while True:
    if(b1press is True):
        b1press=False
        freq = freq+10000000
        clkgen.set_freq(si5351.CLK2, freq)
        clkgen.output_enable(si5351.CLK2, True)
        menulist[0].item[1][1] = freq / 100000000
    elif(b2press is True):
        b2press=False
        freq = freq-10000000
        clkgen.set_freq(si5351.CLK2, freq)
        clkgen.output_enable(si5351.CLK2, True)
        menulist[0].item[1][1] = freq / 100000000
    for i in range(len(menulist)):
        if(menulist[i].active is True):
            menulist[i].draw(display)


