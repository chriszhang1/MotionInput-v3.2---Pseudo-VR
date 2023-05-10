import cv2
import sounddevice as sd
import numpy as np
import time

class Tone:

    def __init__(self, frequency, duration, volume):

        self.frequency = frequency

        self.sample_rate = 44100
        self.duration = duration

        self.volume = max(0, min(1, volume**10))

        self._last_started = 0

        self._build()
    
    def _build(self):

        sample_count = self.duration * self.sample_rate
        cycles = self.frequency/self.sample_rate

        self.data = np.sin(2*np.pi*np.arange(sample_count)*cycles) * self.volume

    def play(self):

        if time.time() - self._last_started > self.duration:

            sd.play(self.data, self.sample_rate)
            self._last_started = time.time()

class Colour:

    """
    BGR Colours
    """
    WHITE = (255, 255, 255)
    LIGHT_GREY = (220, 220, 220)
    DARK_GREY = (80, 80, 80)
    BLACK = (0, 0, 0)

    RED = (130, 130, 255)
    GREEN = (130, 255, 130)
    BLUE = (255, 130, 130)

    PURPLE = (255, 0, 200)
    YELLOW = (120, 240, 230)


class Element:

    def __init__(self):

        self.visible = True

    def update(self, frame):

        if self.visible:

            self._draw(frame)

    def _draw(self):
        pass

class TextBox(Element):

    INNER_THICKNESS = 2.2
    OUTER_THICKNESS = 4

    LINE_SPACING = 1.4

    def __init__(self, content, location, size, colour, centred=True):

        super().__init__()

        self.location = location
        self.content = content

        self.size = size
        self.colour = colour

        self.centred = centred

    """
    Draw light text outlined on black for readability in variable lighting conditions
    """
    def _draw(self, frame):

        inner_thickness = int(TextBox.INNER_THICKNESS * self.size)
        outer_thickness = int(TextBox.OUTER_THICKNESS * self.size)

        font = cv2.FONT_HERSHEY_SIMPLEX

        lines = self.content.split("\n")

        line_offset_y = 0
        for line in lines:

            text_origin = self.location

             # Calculate text size in order to centre on 'location', as opencv expects bottom-left coordinate
            text_bounds, _ = cv2.getTextSize(line, font, self.size, outer_thickness)

            if self.centred:
                text_origin = (self.location[0] - text_bounds[0] / 2, self.location[1] + text_bounds[1] / 2)

            # Round to integer coodinate as OpenCV expects
            line_origin = (int(text_origin[0]), int(text_origin[1] + line_offset_y))

            cv2.putText(frame, line, line_origin, font, self.size, Colour.BLACK, outer_thickness, cv2.LINE_AA)
            cv2.putText(frame, line, line_origin, font, self.size, self.colour, inner_thickness, cv2.LINE_AA)

            line_offset_y += text_bounds[1] * TextBox.LINE_SPACING

class Rectangle(Element):

    def __init__(self, origin=(0, 0), size=(0, 0), colour=Colour.WHITE):

        super().__init__()

        self.origin = origin
        self.size = size
        self.colour = colour

    def _draw_box(self, frame, start, end, colour):

        thickness = -1
        cv2.rectangle(frame, (int(start[0]), int(start[1])), (int(end[0]), int(end[1])), colour, thickness)

    def _draw(self, frame, start, end, colour):

        self._draw_box(frame, start, end, colour)

class StepBar(Rectangle):

    def __init__(self, origin=(0, 0), size=(0, 0), gap_ratio=0.1, index=0, divisions=2, colour=Colour.WHITE, accent_colour=Colour.YELLOW):

        super().__init__(origin, size, colour)

        self.gap_ratio = gap_ratio
        self.index = 0
        self.divisions = divisions

        self.accent_colour = accent_colour

    def _draw(self, frame):

        gap_parameter = (1 + self.gap_ratio/self.divisions)

        bar_gap_width = ((self.size[0] * gap_parameter) / self.divisions)
        gap_width = bar_gap_width * (self.gap_ratio/gap_parameter)
        bar_width = bar_gap_width - gap_width

        start_offset = [self.origin[0], self.origin[1]]
        end_offset = [start_offset[0]+bar_width, start_offset[1] + self.size[1]]

        for i in range(self.divisions):

            colour = self.colour
            if i <= self.index:
                colour = self.accent_colour

            self._draw_box(frame, start_offset, end_offset, colour)

            start_offset[0] += bar_width + gap_width
            end_offset[0] += bar_width + gap_width

class ParameterBar(Rectangle):

    def __init__(self, origin=(0, 0), size=(0, 0), parameter=0, colour=Colour.WHITE):

        super().__init__(origin, size, colour)

        self.parameter = parameter

    def _draw_solid_bar(self, frame, parameter):

        start = self.origin
        end = (self.origin[0] + self.size[0] * parameter, self.origin[1] + self.size[1])

        self._draw_box(frame, start, end, self.colour)

        return start, end

    def _draw(self, frame):

        self._draw_solid_bar(frame, self.parameter)


class ThresholdSlider(ParameterBar):

    def __init__(self, origin=(0, 0), size=(0, 0), toggle_size=(0, 0), min_value=0, max_value=1, bar_value=0, toggle_value=0, clip_start=0, clip_end=0, colour=Colour.WHITE, toggle_colour=Colour.WHITE, accent_colour=Colour.WHITE):

        super().__init__(origin, size, colour)

        self.toggle_size = toggle_size

        self.min_value = min_value
        self.max_value = max_value

        self.range = self._get_range()

        self.bar_value = bar_value
        self.toggle_value = toggle_value
        self.clip_start_value = clip_start
        self.clip_end_value = clip_end

        self.toggle_colour = toggle_colour
        self.accent_colour = accent_colour

    def _get_parameter(self, value):
        return max(0, min(1, (value - self.min_value) / self.range))

    def _get_range(self):
        return self.max_value - self.min_value

    def _draw_toggle(self, frame, value, colour):

        """
        Draw a toggle, centred on the parameterised value
        """
        centre_x = self.origin[0] + self.size[0] * self._get_parameter(value)
        centre_y = self.origin[1] + self.size[1] / 2

        toggle_start = (centre_x - self.toggle_size[0] / 2, centre_y - self.toggle_size[1] / 2)
        toggle_end = (toggle_start[0] + self.toggle_size[0], toggle_start[1] + self.toggle_size[1])

        self._draw_box(frame, toggle_start, toggle_end, colour)

    def _draw(self, frame):

        self.range = self._get_range()

        self._draw_solid_bar(frame, self._get_parameter(self.bar_value))

        self._draw_toggle(frame, self.clip_start_value, self.accent_colour)
        self._draw_toggle(frame, self.clip_end_value, self.accent_colour)

        clipped_value = max(self.clip_start_value, min(self.clip_end_value, self.toggle_value))
        self._draw_toggle(frame, clipped_value, self.toggle_colour)


class Overlay:

    def __init__(self):

        self._frame = None
        self._elements = []

    def add_element(self, element):

        self._elements.append(element)

        return element

    def update(self, frame):

        self._frame = frame

        for element in self._elements:

            element.update(self._frame)
