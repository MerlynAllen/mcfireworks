# from multiprocessing.spawn import import_main_path
# import aiomcrcon
# import asyncio

# async def main():
#     client = aiomcrcon.Client("192.168.1.200", 4444, "123456")
#     await client.connect()
#     resp = await client.send_cmd("execute as Merlyn at @s run summon zombie ~ ~ ~ {CustomName:Zombie}")
#     print(resp)

# asyncio.run(main())
# %%
import time
from mcserverbase import ServerBase
from functools import wraps
import nbtlib
from nbtlib import serialize_tag
from nbtlib.tag import *
import copy
import numpy as np
from PIL import Image
from threading import Thread, Timer
from contextlib import contextmanager


class NotLoggedInError(Exception):
    pass



class EventHandler():
    def __init__(self, name, timestart):
        self.events=[]
        self.name = name
        self.timestart = timestart
        pass
    def append(self, func, obj, args, kwargs):
        # print((func, args, kwargs))
        self.events.append((func, obj, args, kwargs))
    def run(self):
        while time.time() <= time.mktime(time.strptime(self.timestart, "%Y-%m-%d %H:%M:%S")): # wait until scheduled time
            time.sleep(0.5)
        for func, obj, args, kwargs in self.events:
            print(f"running {func} with args {args} and kwargs {kwargs}")
            func(obj, *args, **kwargs)
        self.events.clear()
    def start(self):
        self.thread = Thread(target=self.run)
        self.thread.start()
    def join(self):
        self.thread.join()


class Server(ServerBase):
    def __init__(self):
        super().__init__()
        self.event_handlers = {}
        self.active_eventhandler = None

    def doas(self, user, pos="@s"):
        copy_self = copy.copy(self)
        copy_self.command = lambda cmd: self.command(
            f"execute as {user} at {pos} run {cmd}")
        return copy_self

    def exec_as(self, username, pos="@s"):
        def wrapper(func):
            @wraps(func)
            def wrap(*args, **kwargs):
                origin_command = self.command
                self.command = lambda cmd: origin_command(
                    f"execute as {username} at {pos} run {cmd}")
                result = func(*args, **kwargs)
                self.command = origin_command
                return result
            return wrap
        return wrapper

    def record(func): # CONFLICT WITH *DOAS* !
        @wraps(func)
        def wrap(self, *args, **kwargs):
            if self.active_eventhandler:
                # print(f"Scheduled {func.__name__} with args {args} and kwargs {kwargs}")
                self.active_eventhandler.append(func, self, args, kwargs) # Capture functions and the arguments
                return f"Recorded {func.__name__} with args {args} and kwargs {kwargs}" # Return a message
            else:
                result = func(self, *args, **kwargs)
                return result
        return wrap

    @contextmanager
    def serie(self, name, timestart):
        self.active_eventhandler = EventHandler(name, timestart)
        try:
            yield self
        finally:
            self.event_handlers[name] = self.active_eventhandler
            self.active_eventhandler = None


    @record
    def say(self, msg):
        self.command("say " + msg)
        pass

    @record
    def summon(self, entity_type, x, y, z, tag=""):
        self.command(
            f"summon {entity_type} {str(x)} {str(y)} {str(z)} {serialize_tag(tag)}")
        pass

    @record
    def setblock():
        pass

    @record
    def give():
        pass

    @record
    def getdata():
        pass

    @record
    def kill(self, target):
        self.command(f"kill {target}")

    @record
    def sleep(self, t):
        time.sleep(t)

    def action(self, name):
        self.event_handlers[name].start()
    
    def wait(self):
        for e in self.event_handlers.values():
            e.join()



# %%

YXY = '"##unnamed##"'
MERLYN = "Merlyn"
# %%
START_POS = "0 -60 -70"


def firework():
    pass


def rgb2decimal(r, g, b):
    return r * 0x10000 + g * 0x100 + b

# def dec_colorlist(colors):
#     return f"[I; {','.join([str(rgb2decimal(*c)) for c in colors])}]"


def make_firework_rocket(timefly, isflicker, trail, type, colors, fadecolors, v=[0, 1, 0]):
    return Compound({
        "Motion": List[Double](v),
        "LifeTime": Byte(timefly),
        "LeftOwner": Byte(1),
        "HasBeenShot": Byte(1),
        "Fire": Byte(-1),
        "FireworksItem": Compound({
            "id": String("minecraft:firework_rocket"),
            "Count": Byte(53),
            "tag": Compound({
                "Fireworks": Compound({
                    # "Flight": Byte(timefly),
                    "Explosions": List[Compound]([
                        Compound({
                            "Type": Byte(type),
                            "Trail": Byte(trail),
                            "Flicker": Byte(isflicker),
                            "Colors": IntArray([rgb2decimal(*c) for c in colors]),
                            "FadeColors": IntArray([rgb2decimal(*c) for c in fadecolors])
                        })
                    ])
                })
            })
        }),
        "Life": Byte(0),
        "ShotAtAngle": Byte(1)
    })


def display(fname, anchor, axis="x", colorscheme={"colors": [(40, 210, 130), (0, 130, 210), (155, 255, 255)],
                                                  "fadecolors": [(255, 255, 170), (200, 200, 200)]}, delay=2):
    # Display area (y axis spread)
    # -10, -, 9, 13
    # anchor = [-123, -10, -36]
    # shape = [0, 13, 9]
    delay *= 20  # Covert to ticks
    if fname[-4:] == ".bmp":
        img = Image.open(fname).convert("L")
        img = np.where(np.array(img) > 0, "0", "1").tolist()
        strchr = "\n".join(["".join(row) for row in img])
    else:
        f_chr = open(fname)
        strchr = f_chr.read()
        f_chr.close()
    strchr = strchr.splitlines()
    shape = [len(strchr), len(strchr[0])]
    if axis == "z":
        for y in range(shape[0]):
            for z in range(shape[1]):
                if strchr[-y][z] == "1":
                    server.summon("minecraft:firework_rocket", anchor[0], HEIGHT, anchor[2] + z, make_firework_rocket(
                        delay, 0, 0, 4, colorscheme["colors"], colorscheme["fadecolors"], v=[0, (y+(anchor[1] - HEIGHT))/delay, 0]))
    elif axis == "x":
        for y in range(shape[0]):
            for x in range(shape[1]):
                if strchr[-y][x] == "1":
                    server.summon("minecraft:firework_rocket", anchor[0] + x, HEIGHT, anchor[2], make_firework_rocket(
                        delay, 0, 0, 4, colorscheme["colors"], colorscheme["fadecolors"], v=[0, (y+(anchor[1] - HEIGHT))/delay, 0]))


def anchor_step(anchor, delta):
    return [anchor[i] + delta[i] for i in range(3)]


if __name__ == "__main__":
    HEIGHT = -60  # y
    # DEFAULT_AREA = [50, 50, 50, 50] # x, z, dx, dz
    server = Server()
    server.login("192.168.1.200", 4444, "123456")
    # server.say("Script started.")
    # rocket = make_firework_rocket(40, 0, 0, 4, [(40, 210, 130), (0, 130, 210), (155, 255, 255)], [(255, 255, 170), (200, 200, 200)], v=[0,2,0])
    # server.doas("@e[type=armor_stand]").summon("minecraft:firework_rocket", "~", "~", "~", rocket)
    # server.say("Script finished.")
    def countdown():
        with server.serie("Countdown", "2022-01-29 09:10:00"):
            step = [0, 0, 5]
            anchor = [-123, -45, -36]

            colorscheme = {"colors": [(40, 210, 130), (0, 130, 210), (155, 255, 255)],
                        "fadecolors": [(255, 255, 170), (200, 200, 200)]}
            print(time.strftime("%X"))
            server.say(f"10")
            display("5", anchor, axis="x", colorscheme=colorscheme, delay=5)

            server.sleep(1)

            anchor = anchor_step(anchor, step)
            colorscheme = {"colors": [(210, 40, 130), (210, 130, 0), (255, 255, 155)],
                        "fadecolors": [(255, 255, 170), (200, 200, 200)]}

            print(time.strftime("%X"))
            server.say(f"9")
            display("4", anchor, axis="x", colorscheme=colorscheme, delay=5)

            server.sleep(1)

            anchor = anchor_step(anchor, step)
            colorscheme = {"colors": [(255, 221, 0), (255, 200, 200), (230, 120, 120)],
                        "fadecolors": [(255, 255, 170), (200, 200, 200)]}
            print(time.strftime("%X"))
            server.say(f"8")
            display("3", anchor, axis="x", colorscheme=colorscheme, delay=5)

            server.sleep(1)

            anchor = anchor_step(anchor, step)
            colorscheme = {"colors": [(40, 30, 210), (60, 30, 130), (200, 200, 255)],
                        "fadecolors": [(255, 255, 170), (200, 200, 200)]}
            print(time.strftime("%X"))
            server.say(f"7")
            display("2", anchor, axis="x", colorscheme=colorscheme, delay=5)

            server.sleep(1)

            anchor = anchor_step(anchor, step)
            colorscheme = {"colors": [(220, 240, 240), (210, 255, 255), (155, 255, 255)],
                        "fadecolors": [(255, 255, 170), (200, 200, 200)]}
            print(time.strftime("%X"))
            server.say(f"6")
            display("1", anchor, axis="x", colorscheme=colorscheme, delay=5)

            server.sleep(1)

            anchor = anchor_step(anchor, [-33, 0, 10])
            colorscheme = {"colors": [(255, 130, 30), (210, 30, 30), (255, 155, 155)],
                        "fadecolors": [(255, 255, 170), (200, 200, 200)]}
            print(time.strftime("%X"))
            server.say(f"5")
            display("happynewyear.bmp", anchor, axis="x", colorscheme=colorscheme, delay=5)
            server.sleep(1)
            server.say(f"4")
            server.sleep(1)
            server.say(f"3")
            server.sleep(1)
            server.say(f"2")
            server.sleep(1)
            server.say(f"1")
            server.sleep(1)
            server.say("新年快乐！")
    countdown()
    server.action("Countdown")
    server.wait()

