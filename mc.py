# from multiprocessing.spawn import import_main_path
# import aiomcrcon
# import asyncio

# async def main():
#     client = aiomcrcon.Client("192.168.1.200", 4444, "123456")
#     await client.connect()
#     resp = await client.send_cmd("execute as Merlyn at @s run summon zombie ~ ~ ~ {CustomName:Zombie}")
#     print(resp)

# asyncio.run(main())
from mcserverbase import ServerBase
from functools import wraps

class NotLoggedInError(Exception):
    pass

class Server(ServerBase):
    def __init__(self):
        super().__init__()

    def exec_as():

        def wrapper():
            def wrap():
                pass
    
    def say(self, msg):
        self.command("say " + msg)
        pass
    
    def summon(self, entity_type, x, y, z):
        self.command("summon " + entity_type + " " + str(x) + " " + str(y) + " " + str(z))
        pass

    def setblock():
        pass

    def give():
        pass

    def getdata():
        pass


        
