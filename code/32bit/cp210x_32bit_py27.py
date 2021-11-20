from ctypes import *
from serial import win32
from time import sleep

d_status = {
    0: 'CP210x_SUCCESS',
    1: 'CP210x_INVALID_HANDLE',
    2: 'CP210x_INVALID_PARAMETER',
    3: 'CP210x_DEVICE_IO_FAILED',
    4: 'CP210x_FUNCTION_NOT_SUPPORTED',
    5: 'CP210x_GLOBAL_DATA_ERROR',
    6: 'CP210x_FILE_ERROR',
    8: 'CP210x_COMMAND_FAILED',
    9: 'CP210x_INVALID_ACCESS_TYPE',
    255: 'CP210x_DEVICE_NOT_FOUND'}

if __name__ == '__main__':
    dll = windll.LoadLibrary("CP210xRuntime.dll")

    port = r"\\.\COM8"

    hDevice = win32.CreateFile(port,
                               win32.GENERIC_READ | win32.GENERIC_WRITE,
                               0,  # exclusive access
                               None,  # no security
                               win32.OPEN_EXISTING,
                               win32.FILE_ATTRIBUTE_NORMAL | win32.FILE_FLAG_OVERLAPPED,
                               0)

    if hDevice != win32.INVALID_HANDLE_VALUE:
        bDevice = c_byte()
        status = dll.CP210xRT_GetPartNumber(hDevice, byref(bDevice))
        print(status)
        print('CP21{:02}'.format(bDevice.value))

        pStr = create_string_buffer(b'\000' * 256)
        bStrLen = c_byte()
        bToAscii = c_bool(True)
        status = dll.CP210xRT_GetDeviceProductString(hDevice, byref(pStr), byref(bStrLen), bToAscii)
        print(d_status[status])
        print(pStr.value)

        status = dll.CP210xRT_GetDeviceSerialNumber(hDevice, byref(pStr), byref(bStrLen), bToAscii)
        print(d_status[status])
        print(pStr.value)

        # Start get and set the GPIO
        bMask = c_uint16(0x000f)

        status = dll.CP210xRT_ReadLatch(hDevice, byref(bMask))
        print(d_status[status])
        print('0x{:04x}'.format(bMask.value))

        bMask = c_uint16(0x000f)
        bLatch = c_uint16(0x000e)
        status = dll.CP210xRT_WriteLatch(hDevice, bMask, bLatch)
        print(d_status[status])
        sleep(1)

        bLatch = c_uint16(0x000d)
        status = dll.CP210xRT_WriteLatch(hDevice, bMask, bLatch)
        print(d_status[status])
        sleep(1)

        bLatch = c_uint16(0x000b)
        status = dll.CP210xRT_WriteLatch(hDevice, bMask, bLatch)
        print(d_status[status])
        sleep(1)

        bLatch = c_uint16(0x0007)
        status = dll.CP210xRT_WriteLatch(hDevice, bMask, bLatch)
        print(d_status[status])
        sleep(1)

        win32.CloseHandle(hDevice)
