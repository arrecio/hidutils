
import asyncio
from logging import debug
import hid
import hidutils

class Controls:
    def __init__(self):
        self.__actions = {}
        self.__devices = []
        utils = hidutils.HidUtils()
        devices = utils.get_devices() 
        for device in devices:
            print("Device found:", device)
            print("  Usages:", devices[device]['usages'])

        #hidDevice = hidutils.HidDevice(0x1532, 0x0214, debug=True)
        hidDevice = hidutils.HidDevice(0x0738, 0x1718, debug=True)
        hidDevice.watch("Button 1")
#        hidDevice = hidutils.HidDevice(0x0738, 0x1718, debug=True)
        hidDevice.dump_hid_descriptor()
        self.__devices.append(hidDevice)
        self._queue = []

    def setAction(self, event, actionName):
        self.__actions[event] = actionName

    async def async_update(self):
        while True:
            for device in self.__devices:
                device.update(self._queue)
            for event in self._queue:
                if event in self.__actions:
                    pass
#                    self.__app.doAction(self.__actions[event])
            self._queue = []
            await asyncio.sleep(4e-3)

    def run(self):
        while True:
            for device in self.__devices:
                # print(device.get_state('Button1'))
                device.update(self._queue)
            for event in self._queue:
                print(event)
                if event in self.__actions:
                    pass
#                    self.__app.doAction(self.__actions[event])
            self._queue = []

import sys, os
if __name__ == '__main__':
    try:
        os.system("stty -echo")
        print(hidutils.HidUtils.get_page_name(0x09))
        print(hidutils.HidUtils.get_usage_name(0x07, 0x22))
        print(hidutils.HidUtils.get_usage_name(0x07, 0x13, includePage=True))
        hiddevice = hidutils.HidDevice(0x0738, 0x1718)
        hiddevice.watch('Button 1')
        hiddevice.watch('Button 2')
        events = []
        last = 0
        while True:
            hiddevice.update(events)
            axis = hiddevice.get_state('X')
            if last != axis:
                print("X:", axis)
                last = axis
            for event in events:
                print(event)
            events.clear()

        # controls = Controls()
        # controls.run()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
