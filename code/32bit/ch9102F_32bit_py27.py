from ctypes import *
from serial import win32
from time import sleep


class ChipPropertyS(Structure):
    _fields_ = [("ChipType", c_uint8),
                ("ChipTypeStr", c_char * 32),
                ("FwVerStr", c_char * 32),
                ("GpioCount", c_uint8),
                ("IsEmbbedEeprom", c_int),
                ("IsSupportMcuBootCtrl", c_int),
                ("ManufacturerString", c_char * 64),
                ("ProductString", c_char * 64),
                ("bcdDevice", c_ushort),
                ("PortIndex", c_uint8),
                ("IsSupportGPIOInit", c_int),
                ("PortName", c_char * 32)]


class GpioCtrlS(Structure):
    _fields_ = [("GpioMask", c_ulong),
                ("EnId", c_ulong),
                ("FuncId", c_ulong),
                ("DirId", c_ulong),
                ("StaId", c_ulong)]


if __name__ == '__main__':

    GpioCtrl = []
    for i in range(4):
        GpioCtrl.append(GpioCtrlS())
        GpioCtrl[-1].GpioMask = 0x0001 << i
        GpioCtrl[-1].EnId = 1043 + i
        GpioCtrl[-1].FuncId = 1027 + i
        GpioCtrl[-1].DirId = 1015 + 2 * i
        GpioCtrl[-1].StaId = 1036 + i

    dll = windll.LoadLibrary("CH343PT.dll")

    port = r"\\.\COM26"

    AfxPortH = win32.CreateFile(port,
                                win32.GENERIC_READ | win32.GENERIC_WRITE,
                                0,  # exclusive access
                                None,  # no security
                                win32.OPEN_EXISTING,
                                0,
                                0)

    if AfxPortH != win32.INVALID_HANDLE_VALUE:
        iStatus = c_ulong()
        AfxGpioEnable = c_ulong()
        AfxGpioDir = c_ulong()
        AfxGpioSta = c_ulong()

        AfxUsbSer = ChipPropertyS()
        AfxIcModel = dll.CH343PT_GetChipProperty(AfxPortH, byref(AfxUsbSer))
        print(AfxUsbSer.ChipType)
        print(AfxUsbSer.ChipTypeStr)
        print(AfxUsbSer.PortName)

        RetVal = (AfxIcModel != 0xFF)
        print('Error' if not RetVal else 'Normal')

        RetVal = dll.CH910x_GetGpioConfig(AfxPortH,
                                          byref(AfxUsbSer),
                                          byref(AfxGpioEnable),
                                          byref(AfxGpioDir),
                                          byref(AfxGpioSta)) & 0xFF
        print(RetVal)

        RetVal = dll.CH910x_GpioGet(AfxPortH, byref(AfxUsbSer), byref(iStatus))
        AfxGpioSta = iStatus.value
        print(AfxGpioSta)
        for i in range(4):
            print('GPIO status: {}'.format('ON' if GpioCtrl[i].GpioMask & AfxGpioSta else 'OFF'))

        iFuncSet = c_ulong(0)
        iSetDirOut = c_ulong(0)
        iSetDataOut = c_ulong(0)
        iEnable = c_ulong(31)

        RetVal = dll.CH910x_GetGpioEepromConfig(AfxPortH,
                                                byref(iFuncSet),
                                                byref(iSetDirOut),
                                                byref(iSetDataOut)) & 0xFF
        print(RetVal)

        RetVal = dll.CH910x_GpioConfig(AfxPortH, byref(AfxUsbSer), iEnable, iFuncSet, iSetDirOut) & 0xFF
        print(RetVal)

        RetVal = dll.CH910x_GpioSet(AfxPortH, byref(AfxUsbSer), iEnable, iSetDataOut) & 0xFF
        print(RetVal)

        RetVal = dll.CH910x_GpioGet(AfxPortH, byref(AfxUsbSer), byref(iStatus)) & 0xFF
        AfxGpioSta = iStatus.value
        print(AfxGpioSta)
        for i in range(4):
            print('GPIO status: {}'.format('ON' if GpioCtrl[i].GpioMask & AfxGpioSta else 'OFF'))

        for i in range(12):
            iSetDataOut = c_ulong(0x01 << (i % 4))
            RetVal = dll.CH910x_GpioSet(AfxPortH, byref(AfxUsbSer), iEnable, iSetDataOut) & 0xFF
            print(RetVal)

            RetVal = dll.CH910x_GpioGet(AfxPortH, byref(AfxUsbSer), byref(iStatus)) & 0xFF
            AfxGpioSta = iStatus.value
            print(AfxGpioSta)
            for i in range(4):
                print('GPIO status: {}'.format('ON' if GpioCtrl[i].GpioMask & AfxGpioSta else 'OFF'))
            print(RetVal)

            sleep(1)

        win32.CloseHandle(AfxPortH)
