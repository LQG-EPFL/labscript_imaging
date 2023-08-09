import sys
import time
import zprocess
from labscript_utils import check_version
import labscript_utils.shared_drive
import datetime
from hcam import HamamatsuCamera
from pgcam import PointGreyCamera
from pcoedge import PCOCamera
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot as pt
# importing this wraps zlock calls around HDF file openings and closings:
import labscript_utils.h5_lock
import h5py
import numpy as np
import ctypes
import ctypes.util
import visa
import binascii

class GenericServer(zprocess.ZMQServer):
    def __init__(self, port):
           zprocess.ZMQServer.__init__(self, port, type='string')
           self._h5_filepath = None
           self.enable = True

    def handler(self, request_data):
        try:
            print(request_data)
            if request_data == 'hello':
                return 'hello'
            elif request_data.endswith('.h5'):
                self._h5_filepath = labscript_utils.shared_drive.path_to_local(request_data)
                self.send('ok')
                self.recv()
                self.transition_to_buffered(self._h5_filepath)
                return 'done'
            elif request_data == 'done':
                self.send('ok')
                self.recv()
                self.transition_to_static(self._h5_filepath)
                self._h5_filepath = None
                return 'done'
            elif request_data == 'abort':
                self.abort(self, self._h5_filepath)
                self._h5_filepath = None
                return 'ok'
            else:
                raise ValueError('invalid request: %s'%request_data)
        except Exception:
            if self._h5_filepath is not None and request_data != 'abort':
                try:
                    self.abort()
                except Exception as e:
                    sys.stderr.write('Exception in self.abort() while handling another exception:\n{}\n'.format(str(e)))
            self._h5_filepath = None
            raise

    def transition_to_buffered(self, h5_filepath):
        print('transition to buffered')

    def transition_to_static(self, h5_filepath):
        print('transition to static')

    def abort(self):
        print('abort')


class HamamatsuCameraServer(GenericServer):
    """
    Implementation of a server to handle the Hamamatsu camera.
    
    The specified port during the instantiation of the class should match the
    one written in the connection table (and therefore in BLACS).
    """
    
    def __init__(self, port, cam_name):
        GenericServer.__init__(self, port)
        self.hcam = HamamatsuCamera(0)
        self.name = cam_name
    
    def transition_to_buffered(self, h5_filepath):
        """
        Method called when BLACS is engaged and before the execution of 
        the labscript sequence.
        Hardware parameters for the camera are loaded here and the camera is
        then put in acquisition mode.
        """

        with h5py.File(h5_filepath) as p:
            trig_source = int(p['globals']['hcam_parameters'].attrs['hcam_trigger_source'])
            trig_polarity = int(p['globals']['hcam_parameters'].attrs['hcam_trigger_polarity'])
            roix = int(p['globals']['hcam_parameters'].attrs['hcam_ROIx'])     
            roiy = int(p['globals']['hcam_parameters'].attrs['hcam_ROIy'])
            cx = int(p['globals']['hcam_parameters'].attrs['hcam_cx'])     
            cy = int(p['globals']['hcam_parameters'].attrs['hcam_cy'])
            exp_time = float(p['globals']['hcam_parameters'].attrs['hcam_exposure_time'])
            self.exposures = p['devices'][self.name].get('EXPOSURES')
        
        if self.exposures is not None:
            self.enable = True
            self.hcam.setPropertyValue("trigger_source", trig_source)
            self.hcam.setPropertyValue("trigger_polarity", trig_polarity)
            self.hcam.setPropertyValue("trigger_global_exposure", 5) # Global reset edge trigger
            self.hcam.setPropertyValue("exposure_time", exp_time)
            
            #self.hcam.setPropertyValue("subarray_hsize", roix)
            #self.hcam.setPropertyValue("subarray_vsize", roiy)
            #self.hcam.setPropertyValue("subarray_hpos", cx)
            #self.hcam.setPropertyValue("subarray_vpos", cy)
            #self.hcam.setSubArrayMode()
            
            params = ["trigger_polarity",
                      "trigger_source",
                      "trigger_global_exposure",
                      "exposure_time"]
            
            for param in params:
                print(param, self.hcam.getPropertyValue(param)[0])
            
            self.hcam.startAcquisition()
        else:
            self.enable = False
            
        # Feedback
        print (self.name+' transition to buffered at %s' %(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f"'))))

    def transition_to_static(self, h5_filepath):
        """
        Method called when the sequence is over.
        Images are retrieved from the camera buffer and stored in a new dataset
        in the sequence h5 file named after the camera (self.name).
        """
        start_time = time.time()
        print "hcam start static"
        if self.enable:
            print "hcam try to get frames"
            [frames, dims] = self.hcam.getFrames()
            end_time = time.time()
            print("Get frame time was %g seconds" % (end_time - start_time))
            self.hcam.stopAcquisition()
            with h5py.File(h5_filepath) as f:
                f['data'].create_group(self.name)
                exposures = f['devices'][self.name].get('EXPOSURES')
                end_time = time.time()
                print("prepare h5 time was %g seconds" % (end_time - start_time))
                img = [np.reshape(frame.getData(), (dims[1], dims[0])) for frame in frames]
                end_time = time.time()
                print("reshape data time was %g seconds" % (end_time - start_time))
                for k, image in enumerate(img):
                    image_name = str(exposures[k][0])
                    #np.save(image_name, image)
                    f['data'][self.name].create_dataset(image_name, data=image)      
        
        # Feedback
        end_time = time.time()
        print("Elapsed time was %g seconds" % (end_time - start_time))
        print (self.name+' transition to static at %s' %(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f"'))))

    def abort(self):
        pass
     
class PointGreyCameraServer(GenericServer):
    """
    Implementation of a server to handle the PointGrey cameras.
    
    The specified port during the instantiation of the class should match the
    one written in the connection table (and therefore in BLACS).
    """
    
    def __init__(self, port, cam_name):
        GenericServer.__init__(self, port)
        self.pgcam = PointGreyCamera(0)
        self.name = cam_name
    
    def transition_to_buffered(self, h5_filepath):
        """
        Method called when runmanager is engaged and before the execution of 
        the labscript sequence.
        Hardware parameters for the camera are loaded here and the camera is
        then put in acquisition mode.
        """
        
        with h5py.File(h5_filepath) as p:
            self.exp_time = float(p['globals']['PointGrey_parameters'].attrs['pg_exposure_time'])
            self.exposures = p['devices'][self.name].get('EXPOSURES')
        
        if self.exposures is not None:
            self.enable = True            
            self.pgcam.setTriggerMode(trig = True, p = 0, s = 0, m = 0)
            self.pgcam.setExposureTime(t = self.exp_time*1000.)
            self.pgcam.setGrabMode(mode = 1)
            
            self.pgcam.startAcquisition()
        else:
            self.enable = False
            
        # Feedback
        print (self.name+' transition to buffered at %s' %(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f"'))))

    def transition_to_static(self, h5_filepath):
        """
        Method called when the sequence is over.
        Images are retrieved from the camera buffer and stored in a new dataset
        in the sequence h5 file named after the camera (self.name).
        """
        start_time = time.time()
        if self.enable:
            with h5py.File(h5_filepath) as f:
                exposures = f['devices'][self.name].get('EXPOSURES')
                images = self.pgcam.grabImages(len(exposures))
                f['data'].create_group(self.name)
                for k, image in enumerate(images):
                    image_name = str(exposures[k][0])
                    f['data'][self.name].create_dataset(image_name, data=image)      
                self.pgcam.stopAcquisition()
        # Feedback
        print (self.name+' transition to static at %s' %(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f"'))))

    def abort(self):
        pass
        
class pcoedgeCameraServer(GenericServer):
    """
    Implementation of a server to handle the pco.edge camera.
    
    The specified port during the instantiation of the class should match the
    one written in the connection table (and therefore in BLACS).
    """
    
    def __init__(self, port, cam_name):
        GenericServer.__init__(self, port)
        self.pcoecam = PCOCamera(verbose=True)
        self.name = cam_name
    
    def transition_to_buffered(self, h5_filepath):
        """
        Method called when BLACS is engaged and before the execution of 
        the labscript sequence.
        Hardware parameters for the camera are loaded here and the camera is
        then put in acquisition mode.
        """

        with h5py.File(h5_filepath) as p:
            self.exposure_time = int(p['globals'].attrs['pcoe_exposure_time'])
            self.exposures = p['devices'][self.name].get('EXPOSURES')
        
        if self.exposures is not None:
            self.enable = True
            # We dont allow for user-specified hardware cropping (region of interest)
            # because all the internal delays of the camera seem to depend on that parameter
            # and therefore adjusting the roi on the fly would require tweaking the sequence
            # timings; which nobody wants to do :-)
            self.pcoecam.apply_settings(trigger = 'external_trigger', exposure_time = self.exposure_time,\
            roi = {'left': 800, 'right': 1400, 'top': 750, 'bottom': 1300})
            self.pcoecam.arm(num_buffers = 3)
            
        else:
            self.enable = False
            
        # Feedback
        print (self.name+' transition to buffered at %s' %(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f"'))))

    def transition_to_static(self, h5_filepath):
        """
        Method called when the sequence is over.
        Images are retrieved from the camera buffer and stored in a new dataset
        in the sequence h5 file named after the camera (self.name).
        """
        if self.enable:
            images = self.pcoecam.get_images(3)
            self.pcoecam.disarm()
            with h5py.File(h5_filepath) as f:
                f['data'].create_group(self.name)
                exposures = f['devices'][self.name].get('EXPOSURES')
                for k, image in enumerate(images):
                    image_name = str(exposures[k][0])
                    #np.save(image_name, image)
                    f['data'][self.name].create_dataset(image_name, data=image)      
        
        # Feedback
        print (self.name+' transition to static at %s' %(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f"'))))

    def abort(self):
        pass

def start_main_cams():
    port = 7
    print('Starting Hamamatsu camera server on port %d' % port)
    h_server = HamamatsuCameraServer(port, "HCAM_1")
    
    port = 77
    print('Starting pco.edge camera server on port %d' % port)
    pcoe_server = pcoedgeCameraServer(port, "PCOEDGE")
    
    port = 777
    print('Starting PointGrey camera server on port %d' % port)
    pg_server = PointGreyCameraServer(port, "PGCAM")
    
    pg_server.shutdown_on_interrupt()
    h_server.shutdown_on_interrupt()
    pcoe_server.shutdown_on_interrupt()  
   
        
if __name__ == '__main__':
    start_main_cams()



