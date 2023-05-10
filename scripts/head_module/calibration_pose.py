import time

class PoseStage:

    def __init__(self, name, duration):

        self.name = name
        self.duration = duration

class Pose:

    AWAITING = PoseStage("awaiting", 3)
    RECORDING = PoseStage("recording", 3)
    TUNING = PoseStage("tuning", 6)
    SAVING = PoseStage("saving", 3)

    STAGE_SEQUENCE = ( AWAITING, RECORDING, TUNING, SAVING)

    def __init__(self, name, biometrics, ranges, hint, prompt, friendly_name=""):

        self.name = name
        self.friendly_name = friendly_name

        self.biometric_sources = [s for s, _ in biometrics]
        self.biometric_targets = [t for _, t in biometrics]

        self.ranges = ranges

        self.hint = hint
        self.prompt = prompt

        self._started = False
        self._saved = False

        self._threshold = None

        self._paused = False

        self._stage_index = None

        self._stage_last_polled = None
        self._stage_elapsed = None

        self._latest_frame = None

        self._frames = {}
        self._results = {}

        self._last_confidences = None

    def start(self, initial_threshold):

        self._started = True
        self._saved = False

        self._paused = False

        self._stage_last_polled = time.time()
        self._stage_index = 0
        self._stage_elapsed = 0

        self._frames = {}
        self._results = {}

        self._last_confidences = {}

        self.set_threshold(initial_threshold)

        for target in self.biometric_targets:
            self._frames[target] = []

    def restart(self, initial_threshold):

        self.start(initial_threshold)

    def update(self, metric_values):

        self._latest_frame = {}
        for target, val in zip(self.biometric_targets, metric_values):
            self._latest_frame[target] = val

        if self._paused:
            return self.get_state(), False

        self._stage_elapsed += time.time() - self._stage_last_polled

        changed_state = False

        if self._stage_elapsed >= Pose.STAGE_SEQUENCE[self._stage_index].duration:

            changed_state = self.set_next_state()

        if self.get_state() == Pose.RECORDING:

            for target in self._latest_frame:
                self._frames[target].append(self._latest_frame[target])

        self._stage_last_polled = time.time()

        return self.get_state(), changed_state

    def pause(self):

        if self._started and not self._paused:

            self._paused = True

    def resume(self):

        if self._started and self._paused:

            self._paused = False
            self._stage_last_polled = time.time()

    def get_progress(self):

        duration = Pose.STAGE_SEQUENCE[self._stage_index].duration

        state = self.get_state()

        progress = (0, 0)

        if duration > 0:

            stage_progress = min(1, self._stage_elapsed / duration)
            stage_remaining = max(0, duration - self._stage_elapsed)

            progress = (stage_progress, stage_remaining)

        return state, progress
    
    def get_state(self):

        return Pose.STAGE_SEQUENCE[self._stage_index]

    def get_results(self):

        return self._results

    """
        Map the current biometric value each specified range
        to the range that was calibrated just prior,
        creating a pose confidence value between 0 and 1.
    """
    def update_confidences(self, results):

        confidences = {}

        for (range_ref, range_min, range_max) in self.ranges:

            current_val = self._latest_frame[range_ref]
            calibrated_range = (results[range_max] - results[range_min])

            confidence = (current_val - results[range_min]) / calibrated_range

            activated = confidence > self._threshold

            changed = False
            if range_ref in self._last_confidences:
                changed = self._last_confidences[range_ref]["activated"] != activated

            confidences[range_ref] = { "parameter": max(0, min(1, confidence)), "activated": activated, "changed": changed }

        self._last_confidences = confidences

        return confidences

    def get_last_confidences(self):

        return self._last_confidences

    def set_threshold(self, threshold):

        self._threshold = threshold

    def get_threshold(self):

        return self._threshold

    def is_paused(self):

        return self._paused

    def is_saved(self):

        return self._saved

    def save(self):

        for target in self._frames.keys():

            self._results[target] = sum(self._frames[target]) / len(self._frames[target])

        self._saved = True

        return self.get_results()

    def set_previous_state(self):

        if self._stage_index > 0:

            self._stage_index -= 1
            self._stage_start_time = time.time()
            self._stage_elapsed = 0

            changed_state = True

    def set_next_state(self):

        changed_state = False

        if self._stage_index < len(Pose.STAGE_SEQUENCE) - 1:
            self._stage_index += 1
            self._stage_start_time = time.time()
            self._stage_elapsed = 0

            changed_state = True

        else:

            self.pause()

        return changed_state

"""
Define poses for calibration, in terms of the parameters they target, and the onscreen prompts to give.

In the next version, these pose bindings could be easily moved into JSON.
"""

baseline = Pose(
    name="baseline",
    biometrics=(
        ("head_tilt_angle", "head_tilt_centre"),
        ("head_turn_ratio", "head_turn_centre")
    ),
    ranges=(), 
    hint="look straight ahead with a\nneutral expression",
    prompt="Look straight ahead!",
)

turn_left = Pose(
    name="turn_left",
    biometrics=(("head_turn_ratio", "head_turn_left"),),
    ranges=(("head_turn_left", "head_turn_centre", "head_turn_left"),),
    hint="turn your head to your left as if\n to look over your left shoulder",
    prompt="Turn head left!",
    friendly_name="looking left"
)

turn_right = Pose(
    name="turn_right",
    biometrics=(("head_turn_ratio", "head_turn_right"),), 
    ranges=(("head_turn_right", "head_turn_centre", "head_turn_right"),),
    hint="turn your head to your right as if\n to look over your right shoulder",
    prompt="Turn head right!",
    friendly_name="looking right"
)

tilt_left = Pose(
    name="tilt_left",
    biometrics=(("head_tilt_angle", "head_tilt_left"),),
    ranges=(("head_tilt_left", "head_tilt_centre", "head_tilt_left"),),
    hint="tilt your head towards your\n left shoulder",
    prompt="Tilt head left!",
    friendly_name="tilting left"
)

tilt_right = Pose(
    name="tilt_right",
    biometrics=(("head_tilt_angle", "head_tilt_right"),), 
    ranges=(("head_tilt_right", "head_tilt_centre", "head_tilt_right"),),
    hint="tilt your head towards your\n right shoulder",
    prompt="Tilt head right!",
    friendly_name="tilting right"
)
