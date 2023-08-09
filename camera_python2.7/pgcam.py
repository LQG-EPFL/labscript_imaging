import cv2
import PyCapture2 as pc2
import numpy as np
import struct
from time import sleep
#import matplotlib
#matplotlib.use('Qt4Agg')
#from matplotlib import pyplot as pt


class PointGreyCamera():  
    """
    Basic PointGrey Camera interface class
    Tested only with a Chameleon3 camera
    """

    def __init__(self, camera_id = 0):
        """
        @camera_id (int): the id of the PointGrey camera one wishes to instantiate
        In case of multiple cameras, first figure out which one corresponds to which id
        """

        # Retrieve the pgcam guid
        self.pgcam_id = camera_id
        self.bus = pc2.BusManager()
        
        self.pxmode = 'MONO16'
        self.modes  = {'MONO8': -2147483648, 'MONO12': 1048576, 'RAW12': 524288, 'MONO16': 67108864, 'RAW16': 2097152, 'RAW12': 524288}
        
        try:
            self.pgcam_guid = self.bus.getCameraFromIndex(self.pgcam_id)
        except:
            print("Bus error. Make sure the camera is connected and/or it has the correct camera_id")
        
        # Connect to the camera
        self.pgcam = pc2.Camera()
        try:
            self.pgcam.connect(self.pgcam_guid)
        except:
            print("Could not connect to the PointGrey camera")
        else:
            self.pgcam_info = self.pgcam.getCameraInfo()
            print("Successfully connected to " + self.pgcam_info.modelName +\
            ", SN: " + str(self.pgcam_info.serialNumber))
        
        self.images = []
        
        self.setPixelFormat(self.pxmode)
        
        
    def startAcquisition(self):
        """
        Starts the acquisition
        Doesn't currently support the Callback function system
        """
        
        self.pgcam.startCapture()
        
    def stopAcquisition(self):
        """
        Stops the acquisition
        Make sure to read the buffer during acquisition
        """
        
        self.pgcam.stopCapture()

    def getPixelFormat(self):
        """
        Get the pixel format from the camera
        """
        
        pxlfrmt = self.pgcam.getFormat7Configuration()#.pixelFormat
        
        return pxlfrmt
      
       
    def setPixelFormat(self, pmode):
        """
        Set the pixel format mode for the camera
        """
    
        settngs = self.pgcam.getFormat7Configuration()[0]
        settngs.pixelFormat = self.modes[pmode]
        
        self.pgcam.setFormat7Configuration(100.0, settngs)

    def softwareTrigger(self):
        """
        Fires a software trigger to the camera (USB-mediated)
        It has quite a delay, use for testing purposes
        """
        
        self.pgcam.fireSoftwareTrigger()
        
    def setTriggerMode(self, trig = False, p = 0, s = 0, m = 0):
        """
        Configures the trigger mode of the camera
    
        @trig (bool): sets the use of a trigger
        @p (int): trigger polarity, 0 for falling
        @s (int): source of the trigger signal
        = x, for GPIO line x with x in [0,3]
        = 4, no source 
        @m (int): trigger mode, see manual
        https://www.ptgrey.com/support/downloads/10431/, p39-44   
        """
        
        try:
            self.pgcam.setTriggerMode(onOff = trig, polarity = p, source = s, mode = m)
        except pc2.Fc2error as err:
            print("There was an error setting the trigger mode:\n" , err)
        
    def getTriggerMode(self):
        """
        Feedback function for debugging purposes
        Displays the current trigger settings
        """
        
        print("=== Trigger mode ===")
        for attr, value in self.pgcam.getTriggerMode().__dict__.iteritems():
            print attr, value
        
    def setGrabMode(self, mode = 1):
        """
        Configures the way the camera buffer is read when self.readBuffer() is called
    
        @mode (int):
        = 0, drop every frame from the buffer and read the newest one
        = 1, grab the oldest frame then discard it, allowing to read the older ones
        = 2, unspecified mode, do not use
        """
    
        try:
            self.pgcam.setConfiguration(config  =  None, grabMode = mode, grabTimeout = 1)
        except:
            print("There was an error when setting the " + self.pgcam_info.modelName +\
            " buffer grab mode")
    
    def setExposureTime(self, t = 1):
        """
        Sets the exposure time of the camera
        
        @t (float): time in ms during which the camera should expose
        It seems that the lowest possible time is around 50us
        """
        
        self.pgcam.setProperty(type = pc2.PROPERTY_TYPE.SHUTTER, absValue = t)
    
    
    def grabImages(self, n_images):
        """
        Image retrieval method
        Call this one before stopping the acquisition
        
        @n_images (int): number of images one wishes to retrieve
        starting from the last image taken
        
        returns an numpy array of 2D numpy arrays
        """
        
        self.images = []
        for _ in xrange(n_images):
            try:
                _image = self.pgcam.retrieveBuffer()
            except pc2.Fc2error:
                print("Error retrieving buffer")
                continue
            else:
                _img = _image
                _imdat = np.array(_img.getData())
                l = len(_imdat)
                
                _i1 = _imdat[::2]
                _i2 = _imdat[1::2]
                
                #_imd = np.array([struct.unpack('<H', _imdat[k:k+2])[0] & 0xffff\
                #                 for k in range(0, len(_imdat), 2)])
               
                """              
                #_imd2 = np.array([int('0'*(8-len(bin(_imdat[k+1])[2:]))+bin(_imdat[k+1])[2:]+'0'*(8-len(bin(_imdat[k])[2:]))+bin(_imdat[k])[2:],2)\
                                # for k in range(0, len(_imdat), 2)])
                """
                
                #_imd3 = np.array([_imdat[k]+256*_imdat[k+1] for k in range(0, l, 2)])
                
                _imd4 = _i1 + 256*_i2
                
                _rows = _img.getRows()
                _cols = _img.getCols()
                _stride = _img.getStride()

                self.images.append(_imd4.reshape((_rows, _cols)))
                
        print(self.pgcam_info.modelName + " successfully retrieved "+ str(n_images) + "images")
        return np.array(self.images)
    
