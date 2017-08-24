import numpy as np
from ctypes import WinDLL, c_int, c_float, c_char_p, byref, POINTER, c_uint, \
    create_string_buffer, c_double
    
#------------------------------------------------------------------------------ 
# SifError
#------------------------------------------------------------------------------
    
class SifError:
    """This is a helper class to handle error codes produced by SIFReaderSDK.
        
    """
    
    ATSIF_SUCCESS = "ATSIF_SUCCESS"
    ATSIF_SIF_FORMAT_ERROR = "ATSIF_SIF_FORMAT_ERROR"
    ATSIF_NO_SIF_LOADED = "ATSIF_NO_SIF_LOADED"
    ATSIF_FILE_NOT_FOUND = "ATSIF_FILE_NOT_FOUND"
    ATSIF_FILE_ACCESS_ERROR = "ATSIF_FILE_ACCESS_ERROR"
    ATSIF_DATA_NOT_PRESENT = "ATSIF_DATA_NOT_PRESENT"
    ATSIF_P1INVALID = "ATSIF_P1INVALID"
    ATSIF_P2INVALID = "ATSIF_P2INVALID"
    ATSIF_P3INVALID = "ATSIF_P3INVALID"
    ATSIF_P4INVALID = "ATSIF_P4INVALID"
    ATSIF_P5INVALID = "ATSIF_P5INVALID"
    ATSIF_P6INVALID = "ATSIF_P6INVALID"
    ATSIF_P7INVALID = "ATSIF_P7INVALID"
    ATSIF_P8INVALID = "ATSIF_P8INVALID"
    
    ERROR_STR = {22002: ATSIF_SUCCESS,
                 22003: ATSIF_SIF_FORMAT_ERROR,
                 22004: ATSIF_NO_SIF_LOADED,
                 22005: ATSIF_FILE_NOT_FOUND,
                 22006: ATSIF_FILE_ACCESS_ERROR,
                 22007: ATSIF_DATA_NOT_PRESENT,
                 22101: ATSIF_P1INVALID,
                 22102: ATSIF_P2INVALID,
                 22103: ATSIF_P3INVALID,
                 22104: ATSIF_P4INVALID,
                 22105: ATSIF_P5INVALID,
                 22106: ATSIF_P6INVALID,
                 22107: ATSIF_P7INVALID,
                 22108: ATSIF_P8INVALID}
    
    @staticmethod
    def FromCode(errorCode):
        """Converts SIFReaderSDK error code to string.
        
        Parameters
        ----------
        errorCode : int
            Error code number
        
        Returns
        -------
        str
            Corresponding error string.
        
        """
        
        if errorCode in SifError.ERROR_STR:
            return SifError.ERROR_STR[errorCode]
        else:
            return "Unknown error (%d)" % (errorCode)

    @staticmethod
    def ProcessErrorCode(errorCode):
        """Processes error codes, raises RuntimeError if the error code indicate
        problems. In case of success, does nothing.
        
        Parameters
        ----------
        errorCode : int
            Error code number
        
        """
        errorStr = SifError.FromCode(errorCode)
        if errorStr != SifError.ATSIF_SUCCESS:
            raise RuntimeError("Error: %s" % (errorStr))
    
#------------------------------------------------------------------------------ 
# AndorSifFile
#------------------------------------------------------------------------------
 
class AndorSifFile():
    """This is main class to handle the reading of sif files. All the work is
    done in the constructor, the sif file is opened, data is read and the file
    is closed.
    
    Parameters
    ----------
    filename : str
        Path to .sif file to read
    
    Attributes
    ----------
    signal : :class:`_SifFrame`
        Instance of the :class:`_SifFrame` helper class to store signal information.
    bg : :class:`_SifFrame`
        Instance of the :class:`_SifFrame` helper class to store background information.
        
    """
    
    # Read mode
    ATSIF_ReadAll = 0x40000000
    ATSIF_ReadHeaderOnly = 0x40000001

    # Data source
    ATSIF_Signal = 0x40000000
    ATSIF_Reference = 0x40000001
    ATSIF_Background = 0x40000002
    ATSIF_Live = 0x40000003
    ATSIF_Source = 0x40000004
    
    # Data types
    ATSIF_AT_8 = 0x40000000
    ATSIF_AT_U8 = 0x00000001
    ATSIF_AT_32 = 0x40000002
    ATSIF_AT_U32 = 0x40000003
    ATSIF_AT_64 = 0x40000004
    ATSIF_AT_U64 = 0x40000005
    ATSIF_Float = 0x40000006
    ATSIF_Double = 0x40000007
    ATSIF_String = 0x40000008
    
    # Converters
    ATSIF_CONV = {ATSIF_AT_8: np.int8,
              ATSIF_AT_U8: np.uint8,
              ATSIF_AT_32: np.int32,
              ATSIF_AT_U32: np.uint32,
              ATSIF_AT_64: np.int64,
              ATSIF_AT_U64: np.uint64,
              ATSIF_Float: np.float,
              ATSIF_Double: np.double,
              ATSIF_String: lambda x: x.decode()
              }
    
    # Calib axes
    ATSIF_CalibX        = 0x40000000
    ATSIF_CalibY        = 0x40000001
    ATSIF_CalibZ        = 0x40000002
    
    # Property names
    ANTSIF_PROPS = [
        "Type",
        "Active",
        "Version",
        "Time",
        "FormattedTime",
        "FileName",
        "Temperature",
        "UnstabalizedTemperature",
        "Head",
        "HeadModel",
        "StoreType",
        "DataType",
        "SIDisplacement",
        "SINumberSubFrames",
        "PixelReadOutTime",
        "TrackHeight",
        "ReadPattern",
        "ReadPatternFullName",
        "ShutterDelay",
        "CentreRow",
        "RowOffset",
        "Operation",
        "Mode",
        "ModeFullName",
        "TriggerSource",
        "TriggerSourceFullName",
        "TriggerLevel",
        "ExposureTime",
        "Delay",
        "IntegrationCycleTime",
        "NumberIntegrations",
        "KineticCycleTime",
        "FlipX",
        "FlipY",
        "Clock",
        "AClock",
        "IOC",
        "Frequency",
        "NumberPulses",
        "FrameTransferAcquisitionMode",
        "BaselineClamp",
        "PreScan",
        "EMRealGain",
        "BaselineOffset",
        "SWVersion",
        "SWVersionEx",
        "MCP",
        "Gain",
        "VerticalClockAmp",
        "VerticalShiftSpeed",
        "OutputAmplifier",
        "PreAmplifierGain",
        "Serial",
        "DetectorFormatX",
        "DetectorFormatZ",
        "NumberImages",
        "NumberSubImages",
        "SubImageHBin",
        "SubImageVBin",
        "SubImageLeft",
        "SubImageRight",
        "SubImageTop",
        "SubImageBottom",
        "Baseline",
        "CCDLeft",
        "CCDRight",
        "CCDTop",
        "CCDBottom",
        "Sensitivity",
        "DetectionWavelength",
        "CountConvertMode",
        "IsCountConvert",
        "XAxisType",
        "XAxisUnit",
        "YAxisType",
        "YAxisUnit",
        "ZAxisType",
        "ZAxisUnit",
        "UserText",
        "IsPhotonCountingEnabled",
        "NumberThresholds",
        "Threshold1",
        "Threshold2",
        "Threshold3",
        "Threshold4",
        "AveragingFilterMode",
        "AveragingFactor",
        "FrameCount",
        "NoiseFilter",
        "Threshold",
        "TimeStamp",
        "OutputAEnabled",
        "OutputAWidth",
        "OutputADelay",
        "OutputAPolarity",
        "OutputBEnabled",
        "OutputBWidth",
        "OutputBDelay",
        "OutputBPolarity",
        "OutputCEnabled",
        "OutputCWidth",
        "OutputCDelay",
        "OutputCPolarity",
        "GateMode",
        "GateWidth",
        "GateDelay",
        "GateDelayStep",
        "GateWidthStep"]

    def __init__(self, filename):
        c_int_p = POINTER(c_int)
        c_uint_p = POINTER(c_uint)
        c_float_p = POINTER(c_float)
        c_double_p = POINTER(c_double)
        
        self._filename = filename
        self.dll = WinDLL(r"ATSIFIO64.dll")
        
        # Define library functions
        self.dll.ATSIF_SetFileAccessMode.argtypes = [c_int]
        self.dll.ATSIF_SetFileAccessMode.restype = c_uint
    
        self.dll.ATSIF_ReadFromFile.argtypes = [c_char_p]
        self.dll.ATSIF_ReadFromFile.restype = c_uint
        
        self.dll.ATSIF_CloseFile.argtypes = []
        self.dll.ATSIF_CloseFile.restype = c_uint
        
        self.dll.ATSIF_GetPropertyValue.argtypes = [c_int, c_char_p, c_char_p, c_uint]
        self.dll.ATSIF_GetPropertyValue.restype = c_uint        
        
        self.dll.ATSIF_GetPropertyType.argtypes = [c_int, c_char_p, c_int_p]
        self.dll.ATSIF_GetPropertyType.restype = c_uint        
        
        self.dll.ATSIF_GetPixelCalibration.argtypes = [c_int, c_int, c_int, c_double_p]
        self.dll.ATSIF_GetPixelCalibration.restype = c_uint
        
        self.dll.ATSIF_GetFrameSize.argtypes = [c_int, c_uint_p]
        self.dll.ATSIF_GetFrameSize.restype = c_uint
        
        self.dll.ATSIF_GetFrame.argtypes = [c_int, c_uint, c_float_p, c_uint]
        self.dll.ATSIF_GetFrame.restype = c_uint
        
        # Open file
        self._Open()
        
        # Read contents
        try:
            self.signal = _SifFrame(self, self.ATSIF_Signal)
            self.bg = _SifFrame(self, self.ATSIF_Background)
        finally:
            self._Close()

    def _Open(self):
        # Read all
        errorCode = self.dll.ATSIF_SetFileAccessMode(self.ATSIF_ReadAll)
        SifError.ProcessErrorCode(errorCode)
        
        # Open
        errorCode = self.dll.ATSIF_ReadFromFile(self._filename.encode())
        SifError.ProcessErrorCode(errorCode)
        
    def _Close(self):
        errorCode = self.dll.ATSIF_CloseFile()
        SifError.ProcessErrorCode(errorCode)
        
#------------------------------------------------------------------------------ 
# _SifFrame
#------------------------------------------------------------------------------
        
class _SifFrame:
    """
    This is helper class to store single image/spectrum together with all the
    properties and calibration. The creation of this class is always through
    :class:`AndorSifFile`.
    
    Parameters
    ----------
    sif : :class:`AndorSifFile`
        Reference to :class:`AndorSifFile`
    source : int
        Andor code for signal/background/reference.
    
    Attributes
    ----------
    props : dict
        Contain all the properties of the measurement (e.g exposure time, etc)
    xValues : ndarray of floats
        The calibrated values of x-axis
    wls : ndarray of floats
        If the x-axis represents wavelength, then this array holds wavelength in
        meters.
    data: ndarray of floats
        The data array to contain image/spectrum.
        
    """
    def __init__(self, sif, source):
        self._sif = sif
        self._source = source
        self.dll = self._sif.dll
        self.props = {}
        
        # Get number of pixels
        self._nrPixels = self._GetNumberOfPixels()
        
        # Read all properties
        for prop in AndorSifFile.ANTSIF_PROPS:
            self.props[prop] = self._GetProperty(prop)
        
        # Read x-axis calibration
        self._ReadCalibration()
        
        # Read data
        self._ReadData()
        
        
    def _GetNumberOfPixels(self):
        res = c_uint()
        errorCode = self.dll.ATSIF_GetFrameSize(self._source, byref(res))
        SifError.ProcessErrorCode(errorCode)
        return res.value
    
    def _GetProperty(self, propertyName):
        resStr = create_string_buffer(260)
        errorCode = self.dll.ATSIF_GetPropertyValue(self._source, propertyName.encode(), resStr, len(resStr))
        SifError.ProcessErrorCode(errorCode)
        
        resType = c_int()
        errorCode = self.dll.ATSIF_GetPropertyType(self._source, propertyName.encode(), byref(resType))
        SifError.ProcessErrorCode(errorCode)
        
        res = self._ConvertToType(resStr.value, resType.value)
        return res
        
    def _ConvertToType(self, data, targetType):
        if targetType not in AndorSifFile.ATSIF_CONV:
            raise ValueError("Unknown target type.")
        res = AndorSifFile.ATSIF_CONV[targetType](data)
        return res
    
    def _ReadCalibration(self):
        self.xValues = np.zeros((self._nrPixels,))
        pixelCal = c_double()
        for i in range(1, self._nrPixels + 1):
            errorCode = self.dll.ATSIF_GetPixelCalibration(self._source, AndorSifFile.ATSIF_CalibX, i, byref(pixelCal))
            SifError.ProcessErrorCode(errorCode)
            self.xValues[i - 1] = pixelCal.value
        
        # If x-axis is in wavelength, then init wls array
        if self.props["XAxisUnit"].strip() == "nm":
            self.wls = 1e-9 * self.xValues
            
    def _ReadData(self):
        spectrum = (c_float * self._nrPixels)()
        errorCode = self.dll.ATSIF_GetFrame(self._source, 0, spectrum, self._nrPixels)
        SifError.ProcessErrorCode(errorCode)
        self.data = np.ctypeslib.as_array(spectrum)
        
if __name__ == "__main__":
    pass
