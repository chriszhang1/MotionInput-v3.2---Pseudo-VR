'''
Authors: Fawziyah Hussain and Eva Miah
Partially based on MotionInput v2 Touch code by Chenuka Ratwatte
'''

from ctypes import *
from ctypes.wintypes import *
import pydirectinput

#Structs Needed (from win32 API docs)

class POINTER_INFO(Structure):
    _fields_=[("pointerType",c_uint32),
              ("pointerId",c_uint32),
              ("frameId",c_uint32),
              ("pointerFlags",c_int),
              ("sourceDevice",HANDLE),
              ("hwndTarget",HWND),
              ("ptPixelLocation",POINT),
              ("ptHimetricLocation",POINT),
              ("ptPixelLocationRaw",POINT),
              ("ptHimetricLocationRaw",POINT),
              ("dwTime",DWORD),
              ("historyCount",c_uint32),
              ("inputData",c_int32),
              ("dwKeyStates",DWORD),
              ("PerformanceCount",c_uint64),
              ("ButtonChangeType",c_int)
              ]

class POINTER_TOUCH_INFO(Structure):
    _fields_=[("pointerInfo",POINTER_INFO),
              ("touchFlags",c_int),
              ("touchMask",c_int),
              ("rcContact", RECT),
              ("rcContactRaw",RECT),
              ("orientation", c_uint32),
              ("pressure", c_uint32)]


class POINTER_PEN_INFO(Structure):
    _fields_=[("pointerInfo",POINTER_INFO),
            ("penFlags",c_int),
            ("penMask",c_int),
            ("pressure", c_uint32),
            ("rotation",c_uint32),
            ("tiltX",c_int32),
            ("tiltY",c_int32)]

#These two classes below are needed for pen input to work
class PEN_TOUCH_UNION(Union):
    _fields_=[("touchInfo",POINTER_TOUCH_INFO),("penInfo",POINTER_PEN_INFO)]

class POINTER_TYPE_INFO(Structure):
    _fields_=[("type",c_uint32),
            ("DUMMYUNIONNAME",PEN_TOUCH_UNION)]
            
class Pen():
    def __init__(self):
        pydirectinput.FAILSAFE = False
        #Constants

        #For touchMask
        self.TOUCH_MASK_NONE=          0x00000000 #Default
        self.TOUCH_MASK_CONTACTAREA=   0x00000001
        self.TOUCH_MASK_ORIENTATION=   0x00000002
        self.TOUCH_MASK_PRESSURE=      0x00000004
        self.TOUCH_MASK_ALL=           0x00000007

        #For touchFlag
        self.TOUCH_FLAG_NONE=          0x00000000

        #For pointerType
        self.PT_POINTER=               0x00000001#All
        self.PT_TOUCH=                 0x00000002
        self.PT_PEN=                   0x00000003
        self.PT_MOUSE=                 0x00000004

        #For pointerFlags
        self.POINTER_FLAG_NONE=        0x00000000#Default
        self.POINTER_FLAG_NEW=         0x00000001
        self.POINTER_FLAG_INRANGE=     0x00000002
        self.POINTER_FLAG_INCONTACT=   0x00000004
        self.POINTER_FLAG_FIRSTBUTTON= 0x00000010
        self.POINTER_FLAG_SECONDBUTTON=0x00000020
        self.POINTER_FLAG_THIRDBUTTON= 0x00000040
        self.POINTER_FLAG_FOURTHBUTTON=0x00000080
        self.POINTER_FLAG_FIFTHBUTTON= 0x00000100
        self.POINTER_FLAG_PRIMARY=     0x00002000
        self.POINTER_FLAG_CONFIDENCE=  0x00004000
        self.POINTER_FLAG_CANCELED=    0x00008000
        self.POINTER_FLAG_DOWN=        0x00010000
        self.POINTER_FLAG_UPDATE=      0x00020000
        self.POINTER_FLAG_UP=          0x00040000
        self.POINTER_FLAG_WHEEL=       0x00080000
        self.POINTER_FLAG_HWHEEL=      0x00100000
        self.POINTER_FLAG_CAPTURECHANGED=0x00200000

        #Pointer feedback constants
        self.POINTER_FEEDBACK_DEFAULT=   0x00000001
        self.POINTER_FEEDBACK_INDIRECT=  0x00000002
        self.POINTER_FEEDBACK_NONE=      0x00000003

        #Pen flags
        self.PEN_FLAG_NONE =          0x00000000
        self.PEN_FLAG_BARREL =        0x00000001
        self.PEN_FLAG_INVERTED =      0x00000002
        self.PEN_FLAG_ERASER =        0x00000004

        #Pen masks:
        self.PEN_MASK_NONE =            0x00000000
        self.PEN_MASK_PRESSURE =        0x00000001
        self.PEN_MASK_ROTATION =        0x00000002
        self.PEN_MASK_TILT_X =          0x00000004
        self.PEN_MASK_TILT_Y =          0x00000008

        #Initialize Pointer and Touch/Pen info

        #Initialising the structure for pointerInfo
        self.pointerInfo_touch=POINTER_INFO(pointerType=self.PT_TOUCH,
                         pointerId=0,
                         ptPixelLocation=POINT(950,540))

        self.pointerInfo_pen=POINTER_INFO(pointerType=self.PT_PEN,
                         pointerId=0,
                         ptPixelLocation=POINT(950,540))

        self.touchInfo=POINTER_TOUCH_INFO(pointerInfo=self.pointerInfo_touch,
                             touchFlags=self.TOUCH_FLAG_NONE,
                             touchMask=self.TOUCH_MASK_ALL,
                             rcContact=RECT(self.pointerInfo_touch.ptPixelLocation.x-5,
                                  self.pointerInfo_touch.ptPixelLocation.y-5,
                                  self.pointerInfo_touch.ptPixelLocation.x+5,
                                  self.pointerInfo_touch.ptPixelLocation.y+5),
                             orientation=90,
                             pressure=1000)

        self.penInfo=POINTER_PEN_INFO(pointerInfo=self.pointerInfo_pen,
                                    penFlags=self.PEN_FLAG_NONE,
                                    penMask=self.PEN_MASK_PRESSURE,
                                    pressure=1000,
                                    rotation=0,tiltX=0,tiltY=0)

        #pen_touch_union and pointer_type_info needed for pen input
        self.dmyUnion = PEN_TOUCH_UNION ( touchInfo = self.touchInfo,penInfo = self.penInfo)

        self.pointerTypeInfo = POINTER_TYPE_INFO(type = self.PT_PEN, DUMMYUNIONNAME = self.dmyUnion)

        #Initialise pen device
        self.dev = windll.user32.CreateSyntheticPointerDevice(self.PT_PEN,1,self.POINTER_FEEDBACK_DEFAULT)
        if (self.dev) is not None:
            print("Initalised Pen Input")

    #NOTE: pentap function not currently being used
    def pentap(self,coordinates : Array,pressure,erase):
        '''Single pen tap at given coordinates'''

        if erase is True:
            self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.penFlags = self.PEN_FLAG_ERASER
        else:
            self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.penFlags = self.PEN_FLAG_NONE

        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pointerInfo.ptPixelLocation.x=coordinates[0]
        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pointerInfo.ptPixelLocation.y=coordinates[1]
        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pressure = pressure
        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.penMask = self.PEN_MASK_PRESSURE   #allows pressure to work

        #Press Down
        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pointerInfo.pointerFlags=(self.POINTER_FLAG_DOWN|
                                            self.POINTER_FLAG_INRANGE|
                                            self.POINTER_FLAG_INCONTACT)

        if (windll.user32.InjectSyntheticPointerInput (self.dev , self.pointerTypeInfo,1)==0):
            print("Failed with Error: "+ FormatError())
        else:
            print("Pen Down Succeeded!")

        self.mousejiggle(coordinates)

    def pendown(self,coordinates:Array, pressure, erase):
        '''Initialises a pen down event for ink strokes/drag events'''
        if erase is True:
            self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.penFlags = self.PEN_FLAG_ERASER
        else:
            self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.penFlags = self.PEN_FLAG_NONE
            
        x=coordinates[0]
        y=coordinates[1]

        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pointerInfo.ptPixelLocation.x=x
        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pointerInfo.ptPixelLocation.y=y
        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pressure = pressure
        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.penMask = self.PEN_MASK_PRESSURE

        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pointerInfo.pointerFlags=(self.POINTER_FLAG_DOWN|self.POINTER_FLAG_INRANGE|self.POINTER_FLAG_INCONTACT)

        #pen makes contact with screen
        windll.user32.InjectSyntheticPointerInput (self.dev , self.pointerTypeInfo,1)

        #update flag so pen stays in contact with surface
        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pointerInfo.pointerFlags=(self.POINTER_FLAG_UPDATE|self.POINTER_FLAG_INRANGE|self.POINTER_FLAG_INCONTACT)

    def penup(self,coordinates: Array):
        '''Lifts pen up after taps or drags'''
        if self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pointerInfo.pointerFlags != self.POINTER_FLAG_UP:
            self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pointerInfo.pointerFlags=self.POINTER_FLAG_UP

        windll.user32.InjectSyntheticPointerInput (self.dev , self.pointerTypeInfo,1)
        print("released pen")

        self.mousejiggle(coordinates)

    def update_pen_info(self, coordinates: Array, pressure):
        '''Sets updated coordinates and pressure for ink strokes'''
        x = coordinates[0]
        y = coordinates[1]

        if self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pointerInfo.pointerFlags != (self.POINTER_FLAG_UPDATE|self.POINTER_FLAG_INRANGE|self.POINTER_FLAG_INCONTACT):
            self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pointerInfo.pointerFlags=(self.POINTER_FLAG_UPDATE|self.POINTER_FLAG_INRANGE|self.POINTER_FLAG_INCONTACT)

        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pressure = pressure #allows pressure changes

        #updated coordinates of where pen ink stroke should be
        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pointerInfo.ptPixelLocation.x=x
        self.pointerTypeInfo.DUMMYUNIONNAME.penInfo.pointerInfo.ptPixelLocation.y=y

        windll.user32.InjectSyntheticPointerInput (self.dev , self.pointerTypeInfo,1)

    def mousejiggle(self,coordinates:Array):
        '''The mouse cursor dissapears after pen down event, so we shall move the mouse a little to reactivate it'''
        pydirectinput.moveTo(coordinates[0],y=coordinates[1])
