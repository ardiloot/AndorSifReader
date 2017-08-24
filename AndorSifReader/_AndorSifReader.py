import numpy as np
from ctypes import WinDLL, c_int, c_float, c_char_p, byref, POINTER, c_uint, \
    create_string_buffer, c_double
    
class SifError:
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
        if errorCode in SifError.ERROR_STR:
            return SifError.ERROR_STR[errorCode]
        else:
            return "Unknown error (%d)" % (errorCode)

    @staticmethod
    def ProcessErrorCode(errorCode):
        errorStr = SifError.FromCode(errorCode)
        if errorStr != SifError.ATSIF_SUCCESS:
            raise RuntimeError("Error: %s" % (errorStr))
    
class AndorSifFile():
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
    
    ATSIF_CONV = {ATSIF_AT_8: np.int8,
              ATSIF_AT_U8: np.uint8,
              ATSIF_AT_32: np.int32,
              ATSIF_AT_U32: np.uint32,
              ATSIF_AT_64: np.int64,
              ATSIF_AT_U64: np.uint64,
              ATSIF_Float: np.float,
              ATSIF_Double: np.double,
              ATSIF_String: str
              }
    
    # Calib axes
    ATSIF_CalibX        = 0x40000000
    ATSIF_CalibY        = 0x40000001
    ATSIF_CalibZ        = 0x40000002

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
            self.signal = SifFrame(self, self.ATSIF_Signal)
        finally:
            self._Close()
        
        pixelCal = c_double()
        print(self.dll.ATSIF_GetPixelCalibration(self.ATSIF_Signal, self.ATSIF_CalibX, 10, byref(pixelCal)))
        print("pixelCal", pixelCal.value)
        
        
        
        spectum = (c_float * 1600)()
        print(self.dll.ATSIF_GetFrame(self.ATSIF_Signal, 0, spectum, 1600))

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
        
class SifFrame:
    
    def __init__(self, sif, source):
        self._sif = sif
        self._source = source
        self.dll = self._sif.dll
        
        # Load data
        self.nrPixels = self._GetNumberOfPixels()
        
        print("nrPixels", self.nrPixels)
        print("ExposureTime", self._GetProperty("TriggerSource"))
        
        
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

        
if __name__ == "__main__":
    sif = AndorSifFile(r"C:\Users\Ardi\Dropbox\LABOR\Projektid\Crystalsol\eksperiment\220817\led spekter.sif")
    
    
