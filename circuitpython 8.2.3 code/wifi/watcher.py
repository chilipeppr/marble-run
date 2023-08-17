# This is a wifi watcher
# It does an endless loop to see if our wifi is actually connected
import asyncio
import wifi

class WifiWatcher:

    def __init__(self) -> None:
        
        print("Initting WifiWatcher...")

    async def asyncWifiWatcherTask(self):
        print("Starting infinite async wifi watcher loop")

        while True:

            # print("In wifi watcher async loop, checking on wifi state...")

            if wifi.radio.enabled:
                print("Wifi radio enabled")
            else:
                print("Wifi radio NOT enabled??")
                
            if wifi.radio.ipv4_address != None:
                print("Wifi ip addr:", wifi.radio.ipv4_address)
            else:
                print("Wifi ipv4 not availble, so must NOT be connected")

            # sleep 2 seconds
            await asyncio.sleep(20)

# async def testAsyncTask():

#     # Create our display hardware object
#     ww = WifiWatcher()

#     ww_task = asyncio.create_task(ww.asyncWifiWatcherTask())

#     await asyncio.gather(ww_task)

#     print("Done watching wifi")

# asyncio.run(testAsyncTask())