Piece of code for managing HID devices using [hidapi](https://github.com/libusb/hidapi) via [pyhidapi](https://pypi.org/project/hid) (required). Im still working on it.

To use it properly, you'll likely need to include the appropriate calls to `update` in your main loop. The library's logic minimizes the reading of USB input frames by reading only where necessary, ensuring that the overhead is minimal. Of course, you can use `read` to read directly from the device in real time, but you'll usually want to use the provided API, which requires calling `update`.

## History

To develop this, I consulted the HID documentation available at [Human Interface Devices (HID) Specifications and Tools](https://www.usb.org/hid). I’m sure there’s still a lot left to implement, since my goal was to provide enough functionality to read and interpret raw data. To do this, I had to study how to read the HID Descriptor and how to use it to interpret the USB input frame.

The library will likely encounter errors if you try to use it with devices containing descriptors I haven’t accounted for—especially when those descriptors contain “long” items. Let me know about any errors, and I may end up expanding the library’s functionality. You’re also free to create your own fork.

Write operations are supported through pyhidapi, but my library can’t help you with that—at least for now.

## Install

You can install hidutils using pip, specifying that it should be installed directly from this repository.

```
pip install git+https://github.com/arrecio/pyhidutils.git
```

For hidapi, I can mention Arch Linux, where you need to run `pacman -S install hidapi`. On Windows, you can download the binaries (hidapi.dll) from its GitHub repository [here](https://github.com/libusb/hidapi/releases/tag/hidapi-0.15.0) and place them in the Windows directory or the directory where the Python executable is located.

For pyhidapi just `pip install hidapi`.

## Usage

Look for available devices:

```python
import hidutils

utils = hidutils.HidUtils()
devices = utils.get_devices()
for device in devices:
    print("Device found:", device)
    print("  Usages:", devices[device]['usages'])
```

“Usage” is the term used in HID (Human Interface Device) documentation to refer to device capabilities. These are names from a list and should be used as references. Once the device has been identified, the VendorID and ProductID cant be used to instantiate a HidDevice. If a single physical device offers different features, you'll probably prefer to use the `path` instead. Using the VendorId and ProductId pair will select the first device in the list that matches those criteria. For example, look in the list above for a device designated as a mouse and grab vendor and product id and use it for initialice a HidDevice:

```python
import hidutils

hiddevice = hidutils.HidDevice(0x0123, 0xABCD)
# if no valid vendor/product HIDException is raised
hiddevice.dump_hid_descriptor() # shows the Hid Descriptor of the device
```

My R.A.T.Z mouse reports something like this:

```
Usage Page (Generic Desktop Page (0x01))
Usage (Generic Desktop Page (0x01)[Mouse])
Collection (Application)
  Usage (Generic Desktop Page (0x01)[Pointer])
  Collection (Physical)
    Usage Page (Button Page (0x09))
    Usage Minimun (1)
    Usage Maximun (13)
    Logical Minimun (0)
    Logical Maximun (1)
    Report Size (1)
    Report Count (13)
    Input (Data, Variable, Absolute, No Wrap, Linear, Preferred State, No Null position, Bit Field)
    Report Size (1)
    Report Count (3)
    Input (Constant, Array, Absolute)
    Usage Page (Generic Desktop Page (0x01))
    Usage (Generic Desktop Page (0x01)[X])
    Usage (Generic Desktop Page (0x01)[Y])
    Logical Minimun (-32768)
    Logical Maximun (32767)
    Report Size (16)
    Report Count (2)
    Input (Data, Variable, Relative, No Wrap, Linear, Preferred State, No Null position, Bit Field)
    Usage (Generic Desktop Page (0x01)[Wheel])
    Logical Minimun (-128)
    Logical Maximun (127)
    Report Size (8)
    Report Count (1)
    Input (Data, Variable, Relative, No Wrap, Linear, Preferred State, No Null position, Bit Field)
  End of Collection (None)
End of Collection (None)
```

At first, this information might seem overwhelming, but the documentation is quite good—I encourage you to learn on your own.

> [!NOTE]
> Add `debug=True` argument in HidDevice constructor to see data input changes.

### Watching events and look for data

I created this library so I wouldn't have to rely on Xinput or similar libraries when detecting button presses on my game controller or checking the status of the joysticks. I'm not very interested in other HID features, but I haven't ruled out expanding its functionality. To detect events, you must first listen for them. You can also read the status directly.
Calling `device.dump_hid_descriptor` with `debug=True` will list the device’s data sources (Usages). The name is the first piece of information displayed; the rest is information used internally to read the data within the USB input frame.

> [!NOTE]
> An event occurs when a monitored value changes from its previous state. Keep in mind that, in the case of axes, countless events may be triggered and need to be processed every second (or even in every update call), so you will most likely prefer to check the value directly when you need to.

```python
import hidutils
import time

hiddevice = hidutils.HidDevice(0x0738, 0x1718) # my mouse
print("Buttons available: ", hiddevice.usageButtons)
# to watch events: device.watch(usage1, usage2, ...)
# we watch all available buttons here
hiddevice.watch(*hiddevice.usageButtons)

events = []
last = 0
while True:
    hiddevice.update(events)
    axis = hiddevice.get_state('X')
    if last != axis:
        print("X:", axis)
        last = axis
    for event in events:
        print(event) # event is a tuple with (hiddevice, usage, newVal, oldVal)
    events.clear()
    time.sleep(0.016)
```

### Using HidDeviceManager

A small HID device manager is provided, whose functionality should be sufficient in most cases; however, you will still need to call its `update` method to update the managed devices.  An example that automatically opens all joystick devices and displays the changes using debug mode:

```python
import os
from hidutils import *
import time
def onHidPlug(manager, device):
    print("Device found:", device["path"], device["product_string"], device["usage"])
    if device["usage"] == "Joystick":
        manager.open(path=device["path"], debug=True)
    pass
try:
    os.system("stty -echo")
    manager = HidDeviceManager(
        onPlug=onHidPlug,
        onUnplug=lambda self, device: print(
            "Device unpluged", device["path"], device["product_string"], device["usage"]
        ),
    )
    while True:
        manager.update()
        time.sleep(0.16)
except KeyboardInterrupt:
    print("Interrupted")
    try:
        sys.exit(130)
    except SystemExit:
        os._exit(130)
```

## More usages

You can also use the library to look up the HID Usage Tables. Keep in mind that I've changed some names—especially on the keyboard page—so some results may not match the official documentation.

```python
import hidutils

print(HidUtils.get_page_name(0x09))
print(HidUtils.get_usage_name(0x09, 0x22))
print(HidUtils.get_usage_name(0x09, 0x13, includePage=True))
```

