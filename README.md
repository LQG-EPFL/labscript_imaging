# labscript_imaging

This is our basic (prototype) integration of our cameras [ORCA-Flash4.0 V3 Digital CMOS camera C13440-20CU](https://www.hamamatsu.com/us/en/product/cameras/cmos-cameras/C13440-20CU.html), [pco.edge 4.2 LT](https://www.pco.de/scientific-cameras/pcoedge-42-lt/) and [Flir Chameleon 3](https://www.flir.de/products/chameleon3-usb3/?vertical=machine+vision&segment=iis) (former Point Grey) into [labscript](https://docs.labscriptsuite.org/en/latest/) for absorption imaging.

## Notes

- The device implementation consists of a two parts in a client-server architecture:
  - The labscript device 'camera.py', is placed in the folder 'labscript_suite/labscript_devices' and then imported in the labscript file as well as in the connection table
  - The independent worker 'camera_server.py' is to be run from command line (e.g. anaconda prompt) in python 2.7 and manages the communication with the specific device. In this way running a different python version and running it on a different machine is possible.
- This labscript device is written for an old version of labscript in python 2.7 (should be hopefully easily portable to python 3)

## Example

Labscript File:

```python
""" Import labscript device """
from labscript_devices.Camera import Camera
...
Camera(name = 'PCOEDGE', 
         parent_device = docard,
         connection = 'port2/line2',
         BIAS_port = 77,
         exposure_time = expose_t)
...
""" Take a picture """
    PCOEDGE.expose(name = 'test_pic', t = t, frametype = 'test')
```

Connection Table:

```python
""" Import labscript device """
from labscript_devices.Camera import Camera
...
Camera(name = 'PCOEDGE', 
         parent_device = docard,
         connection = 'port2/line2',
         BIAS_port = 77,
         exposure_time = expose_t)
```

