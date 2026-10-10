Piece of code for managing HID devices using [hidapi](https://github.com/libusb/hidapi) via [pyhidapi](https://pypi.org/project/hid) (required). Im still working on it.

To use it properly, you'll likely need to include the appropriate calls to `update` in your main loop. The library's logic minimizes the reading of USB input frames by reading only where necessary, ensuring that the overhead is minimal.

## History

To develop this, I consulted the HID documentation available at [Human Interface Devices (HID) Specifications and Tools](https://www.usb.org/hid). I’m sure there’s still a lot left to implement, since my goal was to provide enough functionality to read and interpret raw data. To do this, I had to study how to read the HID Descriptor and how to use it to interpret the USB input frame.

The library will likely encounter errors if you try to use it with devices containing descriptors I haven’t accounted for—especially when those descriptors contain “long” items. Let me know about any errors, and I may end up expanding the library’s functionality. You’re also free to create your own fork.

Write operations are supported through pyhidapi, but my library can’t help you with that—at least for now.

## Usage

Look for available devices:

```python

import hidutils

hidutils = hidutils.HidUtils()
devices = hidutils.get_devices()
for device in devices:
    print("Device found:", device)
    print("  Usages:", devices[device]['usages'])
```

“Usage” is the term used in HID (Human Interface Device) documentation to refer to device capabilities. These are names from a list and should be used as references. Once the device has been identified, the VendorID and ProductID must be used to instantiate a HidDevice. For example, look in the list above for a device designated as a mouse and grab vendor and product id and use it for initialice a HidDevice:

```python
import hidutils

hidutils = hidutils.HidUtils()
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

> [!WARNING]
> Only button events are allowed at this moment.

I created this library so I wouldn't have to rely on Xinput or similar libraries when detecting button presses on my game controller or checking the status of the joysticks. I'm not very interested in other HID features, but I haven't ruled out expanding its functionality. To detect events, you must first listen for them. You can also read the status directly.
Calling `device.dump_hid_descriptor` with `debug=True` will list the device’s data sources (Usages). The name is the first piece of information displayed; the rest is information used internally to read the data within the USB input frame.

```python
import hidutils

hidutils = hidutils.HidUtils()
hiddevice = hidutils.HidDevice(0x0123, 0xABCD)
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
```

## More usages

You can also use the library to look up the HID Usage Tables. Keep in mind that I've changed some names—especially on the keyboard page—so some results may not match the official documentation.

```python
import hidutils

print(HidUtils.get_page_name(0x09))
print(HidUtils.get_usage_name(0x09, 0x22))
print(HidUtils.get_usage_name(0x09, 0x13, includePage=True))
```

