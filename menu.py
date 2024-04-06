import ssd1306

class Menu:
    def __init__(self, title, item, active):
        self.title = title
        self.item = item
        self.active = active if active is None else active
    
    def draw(submenu, display):
        display.fill(0)
        display.text("{}".format(submenu.title), 32,1)
        for i in range(len(submenu.item)):
            xa = submenu.item[i][2]
            ya = 19+i*10
            display.text("{}".format(submenu.item[i][0]), 10, ya)
            display.text("{}".format(submenu.item[i][1]), xa, ya)
        display.show()