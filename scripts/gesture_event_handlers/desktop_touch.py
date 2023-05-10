'''
Authors: 
Siam Islam (Two Touchpoints and Dragging)
Carmen Meinson (Port from MotionInput v2)
Developed from legacy code by Chenuka Ratwatte
'''

from ctypes import *
from ctypes.wintypes import *
from typing import Tuple

import pyautogui
import pydirectinput
from pynput.mouse import Controller

from scripts.gesture_event_handlers.area_of_interest import AreaOfInterest
from scripts.gesture_event_handlers.desktop_mouse import Smoother
from scripts.tools import Config


class DesktopTouch:
    def __init__(self, aoi: AreaOfInterest):
        pydirectinput.FAILSAFE = False
        config = Config()
        self._aoi = aoi

        finger_radius = config.get_data("handlers/touch/radius")
        self._touch = Touch(finger_radius)

        self._mouse = Controller()
        self._coords = None
        smoothing_frames = config.get_data("handlers/touch/smoothing")
        self._mouse_x_smoother = Smoother(smoothing_frames)
        self._mouse_y_smoother = Smoother(smoothing_frames)
        self._off_hand_x_smoother = Smoother(smoothing_frames)
        self._off_hand_y_smoother = Smoother(smoothing_frames)
        pyautogui.FAILSAFE = False

    def move_cursor(self, cam_x:float, cam_y:float):
        """Translate the camera coordinates into the AOI coordinates. Smooth the movement of the mouse by averaging out the coordinates of the last few frames (as configured). Move the mouse accordingly."""
        # translate palm center coords to screen coordinates
        x, y = self._aoi.convert_xy(cam_x, cam_y)
        # update cursor
        self._coords = self._smooth_mouse(x, y)
        self._mouse.position = (self._coords[0], self._coords[1])
        #print("Mouse position: ", self._mouse.position)
        #print("Coords: ", self._coords)


    def _smooth_mouse(self, x: float, y: float) -> Tuple[float, float]:
        return self._mouse_x_smoother.smooth(x), self._mouse_y_smoother.smooth(y)

    def _smooth_off_hand(self, x: float, y: float) -> Tuple[float, float]:
        return self._off_hand_x_smoother.smooth(x), self._off_hand_y_smoother.smooth(y)
    
    def singletap(self):
        '''Single tap at specified coordinates and immediately release. Currently not being used.'''
        self._touch.singletap(self._mouse.position)

    def tap(self):
        '''Perform a touch down at specified coordinates'''
        self._touch.update([self._mouse.position], False)

    def press(self, off_hand_coords):
        '''Allows dragging and zooming in/out with touchpoints
        
        :param off_hand_coords: coordinates of offhand index finger, needed for zooming
        :type off_hand_coords: float[]
        '''
        if self._coords is None:
            return

        coords = (int(self._coords[0]), int(self._coords[1])) 
        #print("Coords: ", coords)
        if off_hand_coords is not None:
            x, y = self._aoi.convert_xy(off_hand_coords[0], off_hand_coords[1])
            x, y = self._smooth_off_hand(x, y)
            self._touch.update([coords, (int(x), int(y))], True)
        else:
            self._touch.update([coords], True)

    def triple_swipe(self, *args):
        if self._coords is not None:
            x, y = self._coords
            x, y = int(x), int(y)
            self._touch.update([(x, y), (x+50, y), (x-50, y)], True)

    def release(self):
        self._touch.touchup(self._mouse.position)


#Structs Needed (from win32 API)

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


class Touch():
    def __init__(self,FingerRadius=5):
        #Constants
        self._touchup_on_fail = Config().get_data("general/touchup_on_fail")
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

        #Touch feedback constants
        self.TOUCH_FEEDBACK_DEFAULT=   0x00000001
        self.TOUCH_FEEDBACK_INDIRECT=  0x00000002
        self.TOUCH_FEEDBACK_NONE=      0x00000003

        self.finger_radius = FingerRadius

        self.multitouch_activated = False
        self.multiple_flags_updated = False

        #Initialise Pointer and Touch info
        self.num_touches = 0x3  # Set to 2 touchpoints (currently most optimal/usable number)

        #Initialising the structure for pointerInfo
        self.pointerInfo=POINTER_INFO(pointerType=self.PT_TOUCH,
                         pointerId=0,
                         ptPixelLocation=POINT(950,540))

        #Array of fingers to be tracked
        self.contacts = (POINTER_TOUCH_INFO * self.num_touches)()

        self.initialise_contacts()

        #Initialize Touch Injection
        if (windll.user32.InitializeTouchInjection(self.num_touches,self.TOUCH_FEEDBACK_DEFAULT) != 0):
            print("Initialized Touch Injection")


    def initialise_contacts(self):
        for i in range(self.num_touches):
            self.contacts[i]= POINTER_TOUCH_INFO(
                                    pointerInfo= POINTER_INFO(
                                        pointerType=self.PT_TOUCH,
                                        pointerId=0x0 + i,
                                        ptPixelLocation=POINT(950,540) #default value for where the contact will be touched
                                    ),
                                    touchFlags=self.TOUCH_FLAG_NONE,
                                    touchMask=self.TOUCH_MASK_ALL,
                                    rcContact=RECT(
                                        self.pointerInfo.ptPixelLocation.x-self.finger_radius,
                                        self.pointerInfo.ptPixelLocation.y-self.finger_radius,
                                        self.pointerInfo.ptPixelLocation.x+self.finger_radius,
                                        self.pointerInfo.ptPixelLocation.y+self.finger_radius
                                    ),
                                    orientation=90,
                                    pressure=32000)


    #NOTE: singletap function currently not being used
    def singletap(self,coordinates: Tuple):
        '''Peforms a touch down and then immediately releases on the specified coordinates'''
        self.set_contacts(coordinates, 0)

        self.contacts[0].pointerInfo.pointerFlags=(self.POINTER_FLAG_DOWN|self.POINTER_FLAG_INRANGE|self.POINTER_FLAG_INCONTACT)

        if (windll.user32.InjectTouchInput(1, byref(self.contacts[0]))==0):
            print(" Failed with Error: "+ FormatError())

        #Pull Up
        self.contacts[0].pointerInfo.pointerFlags=self.POINTER_FLAG_UP
        if (windll.user32.InjectTouchInput(c_uint32(1),byref(self.contacts[0]))==0):
            print("Failed with Error: "+FormatError())

        self.mousejiggle(coordinates)


    def update(self, coordinates: Array, press: bool):
        '''Activates touchpoint at the given coordinates, or if touchpoint already active, updates coordinates to allow dragging'''
        fingers = (POINTER_TOUCH_INFO * len(coordinates))()
        self.check_number_of_touchpoints(coordinates)
        #print("Pointer FLAG: ", self.contacts[0].pointerInfo.pointerFlags)
        for i,coordinate in enumerate(coordinates):
            if not press:
                self.contacts[i].pointerInfo.pointerFlags=(self.POINTER_FLAG_INRANGE|self.POINTER_FLAG_INCONTACT|self.POINTER_FLAG_DOWN)
            else:
                if self.multitouch_activated and len(coordinates) > 1 and not self.multiple_flags_updated:
                    self.contacts[i].pointerInfo.pointerFlags=(self.POINTER_FLAG_INRANGE|self.POINTER_FLAG_INCONTACT|self.POINTER_FLAG_DOWN)
                else:
                    if self.contacts[i].pointerInfo.pointerFlags != (self.POINTER_FLAG_INRANGE|self.POINTER_FLAG_INCONTACT|self.POINTER_FLAG_UPDATE):
                        self.contacts[i].pointerInfo.pointerFlags = (self.POINTER_FLAG_INRANGE|self.POINTER_FLAG_INCONTACT|self.POINTER_FLAG_UPDATE)

            self.set_contacts(coordinate, i)
            fingers[i] = self.contacts[i]
        
        if self._touchup_on_fail:
            if (windll.user32.InjectTouchInput(c_uint32(len(fingers)), byref(fingers))==0):
                self.touchup(coordinates[0])
        else:
            windll.user32.InjectTouchInput(c_uint32(len(fingers)), byref(fingers))


    def check_number_of_touchpoints(self, coordinates: Array) -> None:
        '''Updates state depending on the number of coordinates being passed in.
        A touchup is performed if it is the first time multiple coordinates are in the array since the last update.
        This is to reset the contacts before all contacts are updated simultaneously in the next touch injection.
        '''

        if len(coordinates) > 1:
            if not self.multitouch_activated:
                self.touchup([coordinates[0]])
                self.multitouch_activated = True
            else:
                self.multiple_flags_updated = True
        elif len(coordinates) == 1:
            self.multitouch_activated = False
            self.multiple_flags_updated = False


    def set_contacts(self, coordinate: Tuple, index: int) -> None:
        '''Sets contact parameters for the specified index based on the coordinate passed in'''
        x=coordinate[0]
        y=coordinate[1]

        self.contacts[index].pointerInfo.ptPixelLocation.x=x
        self.contacts[index].pointerInfo.ptPixelLocation.y=y

        self.contacts[index].rcContact.left=x-self.finger_radius
        self.contacts[index].rcContact.right=x+self.finger_radius
        self.contacts[index].rcContact.top=y-self.finger_radius
        self.contacts[index].rcContact.bottom=y+self.finger_radius


    def touchup(self, coordinates: Array) -> None:
        '''Releases all touchpoints on the screen'''
        for i in range(self.num_touches):
            if self.contacts[i].pointerInfo.pointerFlags != self.POINTER_FLAG_UP:
                self.contacts[i].pointerInfo.pointerFlags = self.POINTER_FLAG_UP

        if not self.multitouch_activated:
            if (windll.user32.InjectTouchInput(c_uint32(1),byref(self.contacts[0]))==0):
                print("Failed with Error: "+FormatError())
        else:
            windll.user32.InjectTouchInput(self.num_touches, byref(self.contacts))

        self.mousejiggle(coordinates)


    def mousejiggle(self, coordinates: Array) -> None:
        '''Reactivate mouse cursor since it disappears after touch is made'''
        try:
            if len(coordinates) == 2:
                pydirectinput.moveTo(coordinates[0],y=coordinates[1])
        except Exception as e:
            print("Error when trying to perform pydirectinput action: ", e)
