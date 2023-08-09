"""Python wrapper for the SC2_Cam.dll library

Only supports pco.edge 4.2 camera as of now.
Based off code from https://github.com/AndrewGYork/tools/blob/master/pco.py
which was trimmed down to only work for our limited usecase

  Typical usage example:

  camera = PCOCamera()
  camera.apply_settings(trigger = 'external_trigger', exposure_time = 200)
  camera.arm(num_images)
  # Experimental physics happens
  images = camera.get_images(num_images)
  camera.close()
"""

import ctypes as C
import numpy as np
import logging

logging.basicConfig()

try:
    dll = C.oledll.LoadLibrary('SC2_Cam')
except WindowsError:
    print('Failed to load SC2_Cam.dll')
    raise
    
dll.open_camera = dll.PCO_OpenCamera
dll.open_camera.argtypes = [C.POINTER(C.c_void_p), C.c_uint16]

dll.close_camera = dll.PCO_CloseCamera
dll.close_camera.argtypes = [C.c_void_p]

dll.arm_camera = dll.PCO_ArmCamera
dll.arm_camera.argtypes = [C.c_void_p]

dll.allocate_buffer = dll.PCO_AllocateBuffer
dll.allocate_buffer.argtypes = [
    C.c_void_p,
    C.POINTER(C.c_int16),
    C.c_uint32,
    C.POINTER(C.POINTER(C.c_uint16)),
    C.POINTER(C.c_void_p)]

dll.add_buffer = dll.PCO_AddBufferEx
dll.add_buffer.argtypes = [
    C.c_void_p,
    C.c_uint32,
    C.c_uint32,
    C.c_int16,
    C.c_uint16,
    C.c_uint16,
    C.c_uint16]

dll.get_buffer_status = dll.PCO_GetBufferStatus
dll.get_buffer_status.argtypes = [
    C.c_void_p,
    C.c_int16,
    C.POINTER(C.c_uint32),
    C.POINTER(C.c_uint32)]

dll.set_image_parameters = dll.PCO_CamLinkSetImageParameters
dll.set_image_parameters.argtypes = [C.c_void_p, C.c_uint16, C.c_uint16]

dll.set_recording_state = dll.PCO_SetRecordingState
dll.set_recording_state.argtypes = [C.c_void_p, C.c_uint16]

dll.get_sizes = dll.PCO_GetSizes
dll.get_sizes.argtypes = [
    C.c_void_p,
    C.POINTER(C.c_uint16),
    C.POINTER(C.c_uint16),
    C.POINTER(C.c_uint16),
    C.POINTER(C.c_uint16)]

dll.get_sensor_format = dll.PCO_GetSensorFormat
dll.get_sensor_format.argtypes = [C.c_void_p, C.POINTER(C.c_uint16)]

dll.get_camera_health = dll.PCO_GetCameraHealthStatus
dll.get_camera_health.argtypes = [
    C.c_void_p,
    C.POINTER(C.c_uint32),
    C.POINTER(C.c_uint32),
    C.POINTER(C.c_uint32)]

dll.get_temperature = dll.PCO_GetTemperature
dll.get_temperature.argtypes = [
    C.c_void_p,
    C.POINTER(C.c_int16),
    C.POINTER(C.c_int16),
    C.POINTER(C.c_int16)]

dll.get_trigger_mode = dll.PCO_GetTriggerMode
dll.get_trigger_mode.argtypes = [C.c_void_p, C.POINTER(C.c_uint16)]

dll.get_delay_exposure_time = dll.PCO_GetDelayExposureTime
dll.get_delay_exposure_time.argtypes = [
    C.c_void_p,
    C.POINTER(C.c_uint32),
    C.POINTER(C.c_uint32),
    C.POINTER(C.c_uint16),
    C.POINTER(C.c_uint16)]

dll.set_delay_exposure_time = dll.PCO_SetDelayExposureTime
dll.set_delay_exposure_time.argtypes = [
    C.c_void_p,
    C.c_uint32,
    C.c_uint32,
    C.c_uint16,
    C.c_uint16]

dll.get_roi = dll.PCO_GetROI
dll.get_roi.argtypes = [
    C.c_void_p,
    C.POINTER(C.c_uint16),
    C.POINTER(C.c_uint16),
    C.POINTER(C.c_uint16),
    C.POINTER(C.c_uint16)]

dll.set_roi = dll.PCO_SetROI
dll.set_roi.argtypes = [
    C.c_void_p,
    C.c_uint16,
    C.c_uint16,
    C.c_uint16,
    C.c_uint16]

dll.get_camera_name = dll.PCO_GetCameraName
dll.get_camera_name.argtype = [
    C.c_void_p,
    C.c_char_p,
    C.c_uint16]

dll.reset_settings_to_default = dll.PCO_ResetSettingsToDefault
dll.reset_settings_to_default.argtypes = [C.c_void_p]

dll.set_recording_state = dll.PCO_SetRecordingState
dll.set_recording_state.argtypes = [C.c_void_p, C.c_uint16]

dll.remove_buffer = dll.PCO_RemoveBuffer
dll.remove_buffer.argtypes = [C.c_void_p]

dll.cancel_images = dll.PCO_CancelImages
dll.cancel_images.argtypes = [C.c_void_p]

dll.free_buffer = dll.PCO_FreeBuffer
dll.free_buffer.argtypes = [C.c_void_p, C.c_int16]

dll.set_trigger_mode = dll.PCO_SetTriggerMode
dll.set_trigger_mode.argtypes = [C.c_void_p, C.c_uint16]

dll.get_num_cnt = dll.PCO_GetHWIOSignalCount
dll.get_num_cnt.argtypes = [C.c_void_p, C.POINTER(C.c_uint16)]

class PCO_Signal(C.Structure):
    _fields_=[  ('wSize', C.c_uint16),
                ('wSignalNum', C.c_uint16),
                ('wEnabled', C.c_uint16),
                ('wType', C.c_uint16),
                ('wPolarity', C.c_uint16),
                ('wFilterSetting', C.c_uint16),
                ('wSelected', C.c_uint16),
                ('ZZwReserved', C.c_uint16),
                ('dwParameter', C.c_uint32*4),
                ('dwSignalFunctionality',  C.c_uint32*4),
                ('ZZdwReserved',  C.c_uint32*3),]
    
PCO_Signal_star = C.POINTER(PCO_Signal)
    
dll.get_hwio_signal = dll.PCO_GetHWIOSignal
dll.get_hwio_signal.argtypes = [C.c_void_p, C.c_uint16, PCO_Signal_star]

dll.set_hwio_signal = dll.PCO_SetHWIOSignal
dll.set_hwio_signal.argtypes = [C.c_void_p, C.c_uint16, PCO_Signal_star]

class PCOCamera:
    """Class to handle PCO Cameras."""
    
    def __init__(self, verbose = False, logger = None, trigger_line = 0):
        """Initializes the camera.

        Opens connection with the camera and instantiate a logger 
        unless the use has specified one.

        Args:
            verbose          (bool):  Indicates if user wants more info at runtime.
            logger (logging.logger):  A logging.logger object in case the user wants 
                                       to use his own.
            trigger_line      (int):  To which hardware input is the trigger signal sent.

        Raises:
            WindowsError, AssertionError: Could not connect to the camera.
        """
            
        if logger is None:
            self.logger = logging.getLogger('pcoLogger')
            self.logger.setLevel(logging.INFO)
            if verbose: self.logger.setLevel(logging.DEBUG)
        else:
            self.logger = logger
        self.camera_handle = C.c_void_p(0)
        self.camera_type = 'edge 4.2' 
        self.logger.info('Opening camera...')
        try:
            dll.open_camera(self.camera_handle, 0)
            assert self.camera_handle.value is not None
        except (WindowsError, AssertionError):
            self.logger.exception('Failed to open pco camera.')
        self.logger.info('pco.%s camera open.' % self.camera_type)
        #dll.reset_settings_to_default(self.camera_handle)
        self.disarm()
        self.HWIO_trigger = C.c_uint16(trigger_line)
        self.HWIO_struct  = PCO_Signal()
        self.HWIO_struct.wSize = C.sizeof(self.HWIO_struct)
        dll.get_hwio_signal(self.camera_handle, self.HWIO_trigger, C.byref(self.HWIO_struct))
        return None
    
    def close(self):
        """Closes conenction to the camera
        
        In case that's not previously done, disarm it.
        """
        
        self.disarm()
        self.logger.info('Closing pco.%s camera...' % self.camera_type)
        dll.close_camera(self.camera_handle)
        self.logger.info('Camera closed.')
        return None
    
    def apply_settings(self, trigger = 'external_exposure', trigger_polarity = 'raising', exposure_time = 107, roi = None):
        """Apply user specified settings to the camera
        
        Has to be called prior to arming the device.
        
        Args:
            trigger          (str):  Desired trigger mode chosen between:
                                      - 'auto_trigger', acquiring images as soon a sensor is ready 
                                      - 'software_trigger' 
                                      - 'external_trigger' 
                                      - 'external_exposure', pulse-gated acquisition
            trigger_polarity (str):  Desired trigger polarity chosen between:
                                      - 'raising'
                                      - 'falling'
            exposure_time    (int):  Integration time in microseconds.
            roi             (dict):  Region of interest for hardware cropping.
        """
        
        # Pro advice; never use mutable default arguments ;)
        if roi is None:
            roi = {'left':1, 'top': 1, 'right': 2048, 'bottom': 2048}
        if self.armed: self.disarm()
        self.logger.info('Applying settings to camera...')
        self._set_trigger_mode(trigger)
        #self._set_trigger_polarity(trigger_polarity)
        self._set_exposure_time(exposure_time)
        self._set_roi(roi)
        return None
    
    def arm(self, num_buffers = 3):
        """Readies the camera for image acquisition
        
        Arms the camera, provides it with pointers to pre-defined buffers
        to store images and puts it in acquisition mode.
                
        Args:
            num_buffers (int): Number of buffers that should be allocated 
                                to store images. For optimal perfomances, 
                                this should be equal to the num_images arg
                                of the self.get_images() function.
                                Never provide fewer buffers than the number
                                of images, because I didnt want to have to deal
                                with permanent camera polling as this goes
                                against having a fast experimental cycle time.
        """
    
        assert 1 <= num_buffers <= 16
        if self.armed:
            self.logger.warning('Arm requested, but the pco camera is already armed. Disarming...')
            self.disarm()
        self.logger.info('Arming camera...')
        dll.arm_camera(self.camera_handle)
        wXRes, wYRes, wXResMax, wYResMax = (C.c_uint16(), C.c_uint16(), C.c_uint16(), C.c_uint16())
        dll.get_sizes(self.camera_handle, wXRes, wYRes, wXResMax, wYResMax)
        self.width, self.height = wXRes.value, wYRes.value
        self.bytes_per_image = self.width * self.height * 2 # 16bit images
        self.logger.debug(' Camera ROI dimensions: '+str(self.width)+' (l/r) by '+str(self.height)+' (u/d)')

        self.buffer_pointers = []
        for i in range(num_buffers):
            buffer_number = C.c_int16(-1)
            self.buffer_pointers.append(C.POINTER(C.c_uint16)())
            buffer_event = C.c_void_p(0)
            dll.allocate_buffer(self.camera_handle, buffer_number, self.bytes_per_image,\
                                self.buffer_pointers[-1], buffer_event)
            assert buffer_number.value == i
            self.logger.debug(' Buffer number '+str(i)+' allocated, pointing to '+str(self.buffer_pointers[-1].contents)+\
                              ', linked to event '+str(buffer_event.value))
        dll.set_image_parameters(self.camera_handle, self.width, self.height)
        dll.set_recording_state(self.camera_handle, 1)
        self.armed = True
        self.logger.info(' Camera armed.')

        self.added_buffers = []
        for buf_num in range(len(self.buffer_pointers)):
            dll.add_buffer(self.camera_handle, 0, 0, buf_num, self.width, self.height, 16)
            self.added_buffers.append(buf_num)
        self._dll_status = C.c_uint32()
        self._driver_status = C.c_uint32()
        self._image_datatype = C.c_uint16 * self.width * self.height
        return None

    def disarm(self):
        """Disarms the camera
        
        If it was recording, stops. Removes any buffer.
        """
        
        if not hasattr(self, 'armed'):
            self.armed = False
        self.logger.info('Disarming camera...')
        dll.set_recording_state(self.camera_handle, 0)
        dll.cancel_images(self.camera_handle)
        if hasattr(self, 'buffer_pointers'):
            for buf in range(len(self.buffer_pointers)):
                dll.free_buffer(self.camera_handle, buf)
            self.buffer_pointers = []
        self.armed = False
        self.logger.info('Camera disarmed.')
        return None

    def get_images(self, num_images):
        """Grabs images that were stored in the specified buffers
                
        Args:
            num_images (int): Number of images that should be retrieved
                               from the buffers. This has to be at least 
                               equal to the number of allocated buffers.
        
        Returns:
            out   (np.array): Array of shape (num_images, height, width)
                               containing the images.
                               
        Raises:
            AssertError: Not enough buffers assigned.
        """
        
        if not self.armed: self.arm()
        out = np.ones((num_images, self.height, self.width),
                          dtype=np.uint16)
        try:
            assert len(self.added_buffers) >= num_images
        except:
            self.logger.exception('Not enough buffers assigned.')
            self.logger.exception('Current implementation requires at least one buffer per image taken.')
            raise 
            
        w = ' image'
        if num_images > 1: w = w + 's'
        self.logger.info('Acquiring ' + str(num_images) + w)
        num_acquired = 0
        for which_im in range(num_images):
            dll.get_buffer_status(self.camera_handle, self.added_buffers[0], self._dll_status,\
                                  self._driver_status)

            if self._dll_status.value == 0xc0008000: # If buffer event is set
                buffer_number = self.added_buffers.pop(0)
                self.logger.debug(' Buffer '+ str(buffer_number) +' is ready.')

            try:
                image = np.ctypeslib.as_array(self._image_datatype.from_address(C.addressof(self.buffer_pointers[buffer_number].contents)))
                out[which_im, :, :] = image
                num_acquired += 1
            finally:
                dll.add_buffer(self.camera_handle, 0, 0, buffer_number, self.width, self.height, 16)
                self.added_buffers.append(buffer_number)
                
        w = ' image'
        if num_acquired > 1: w = w + 's'
        self.logger.info('Done acquiring ' + str(num_acquired) + w)
        return out
    
    def _refresh_camera_setting_attributes(self):
    
        self.logger.info('Retrieving settings from camera...')
        self._get_trigger_mode()
        self._get_exposure_time()
        self._get_roi()
        self._get_temperature()
        return None

    def _get_temperature(self):

        ccdtemp, camtemp, powtemp = (
            C.c_int16(), C.c_int16(), C.c_int16())
        dll.get_temperature(self.camera_handle, ccdtemp, camtemp, powtemp)
        self.logger.info(' Temperatures:\n'+
                  '    CCD: '+str(ccdtemp.value * 0.1)+ 'C\n'+
                  '    camera: '+str(camtemp.value)+ 'C\n'+
                  '    power supply: '+str(powtemp.value)+'C')
        self.temperature = {
            'ccd_temp': ccdtemp.value * 0.1,
            'camera_temp': camtemp.value,
            'power_supply_temp': powtemp.value}
        return self.temperature

    def _get_trigger_mode(self):

        trigger_mode_names = {0: 'auto_trigger',
                              1: 'software_trigger',
                              2: 'external_trigger',
                              3: 'external_exposure'}
        wTriggerMode = C.c_uint16()
        dll.get_trigger_mode(self.camera_handle, wTriggerMode)
        self.logger.info(' Trigger mode: '+trigger_mode_names[wTriggerMode.value])
        self.trigger_mode = trigger_mode_names[wTriggerMode.value]
        return self.trigger_mode

    def _set_trigger_mode(self, mode = 'auto_trigger'):
        """Sets trigger mode
        
        For mode definitions see self.apply_settings() docstring.
        """

        trigger_mode_numbers = {
            'auto_trigger': 0,
            'software_trigger': 1,
            'external_trigger': 2,
            'external_exposure': 3}
        self.logger.info(' Setting trigger mode to: '+ mode)
        dll.set_trigger_mode(self.camera_handle, trigger_mode_numbers[mode])
        assert self._get_trigger_mode() == mode
        return self.trigger_mode
        
    def _get_trigger_polarity(self):
        
        trigger_polarity_names = {
            4: 'raising',
            8: 'falling'}
        dll.get_hwio_signal(self.camera_handle, self.HWIO_trigger, C.byref(self.HWIO_struct))
        self.logger.info(' Trigger polarity: '+trigger_polarity_names[self.HWIO_struct.wPolarity])
        self.trigger_polarity = trigger_polarity_names[self.HWIO_struct.wPolarity]
        return self.trigger_polarity     
        
    def _set_trigger_polarity(self, polarity = 'raising'):
        
        trigger_polarity_numbers = {
            'raising': 4,
            'falling': 8}
        self.logger.info(' Setting trigger polarity to: ' + polarity)
        self.HWIO_struct = C.c_uint16(trigger_polarity_numbers[polarity])
        dll.set_hwio_signal(self.camera_handle, self.HWIO_trigger, C.byref(self.HWIO_struct))
        assert self._get_trigger_polarity() == polarity
        return self.trigger_polarity    

    def _get_exposure_time(self):
    
        dwDelay = C.c_uint32(0)
        wTimeBaseDelay = C.c_uint16(0)
        dwExposure = C.c_uint32(0)
        wTimeBaseExposure = C.c_uint16(1)
        dll.get_delay_exposure_time(
            self.camera_handle,
            dwDelay,
            dwExposure,
            wTimeBaseDelay,
            wTimeBaseExposure)
        time_base_mode_names = {0: 'ns',
                                1: 'us',
                                2: 'ms'}
        self.logger.info(' Exposure: ' + str(dwExposure.value) + time_base_mode_names[wTimeBaseExposure.value])
        self.logger.debug(' Delay: '+ str(dwDelay.value) + time_base_mode_names[wTimeBaseDelay.value])
        self.exposure_time_microseconds = (dwExposure.value * 10.**(3*wTimeBaseExposure.value - 3))
        self.delay_time = dwDelay.value
        return self.exposure_time_microseconds

    def _set_exposure_time(self, exposure_time_microseconds=2200):
    
        exposure_time_microseconds = int(exposure_time_microseconds)
        if self.camera_type is 'edge 4.2':
            assert 1e2 <= exposure_time_microseconds <= 1e7
        self.logger.info(' Setting exposure time to '+ str(exposure_time_microseconds)+ 'us')
        dll.set_delay_exposure_time(
            self.camera_handle, 0, exposure_time_microseconds, 1, 1)
        self._get_exposure_time()
        assert self.exposure_time_microseconds == exposure_time_microseconds
        return self.exposure_time_microseconds

    def _get_roi(self):
    
        wRoiX0, wRoiY0, wRoiX1, wRoiY1 = (
            C.c_uint16(), C.c_uint16(),
            C.c_uint16(), C.c_uint16())
        dll.get_roi(self.camera_handle, wRoiX0, wRoiY0, wRoiX1, wRoiY1)
        self.logger.info(' Camera ROI:')
        self.logger.info('  From pixel '+str(wRoiX0.value)+' to pixel '+str(wRoiX1.value)+ ' (left/right)')
        self.logger.info('  From pixel '+str(wRoiY0.value)+' to pixel '+str(wRoiY1.value)+ ' (up/down)')
        self.roi = {
            'left': wRoiX0.value,
            'top': wRoiY0.value,
            'right': wRoiX1.value,
            'bottom': wRoiY1.value}
        if self.camera_type == 'edge 4.2':
            max_lines = 1024
            full_chip_rolling_time = 1e4
        chip_fraction = max(wRoiY1.value - max_lines,
                            max_lines + 1 - wRoiY0.value) / max_lines
        self.rolling_time_microseconds =  full_chip_rolling_time * chip_fraction
        return self.roi

    def _set_roi(self, region_of_interest):
    
        roi = region_of_interest
        self.roi = roi
        dll.set_roi(self.camera_handle, roi['left'], roi['top'], roi['right'], roi['bottom'])
        #assert self._get_roi() == roi
        return self.roi