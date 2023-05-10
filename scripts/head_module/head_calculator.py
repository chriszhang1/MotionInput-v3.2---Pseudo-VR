def lessThan(a, b):
    return a < b

def greaterThan(a, b):
    return a > b

def lessThanEq(a, b):
    return a <= b

def greaterThanEq(a, b):
    return a >= b

def equal(a, b):
    return a == b

class PrimitivePredicate:

    CONFIDENCE = 0.7
    HISTORICAL_FRAME_COUNT = 5

    def __init__(self, test_metric, comparator, cal_metric):

        self.test_metric = test_metric
        self.cal_metric = cal_metric

        self.comparator = comparator

        self.frames = [0 for i in range(PrimitivePredicate.HISTORICAL_FRAME_COUNT)]

    def _compare_historic(self, test_metric, cal_metric):

        current_value = 1 if self.comparator(test_metric, cal_metric) else 0

        self.frames.pop(0)
        self.frames.append(current_value)

        return sum(self.frames) / PrimitivePredicate.HISTORICAL_FRAME_COUNT > PrimitivePredicate.CONFIDENCE

    def compare(self, test_metric, cal_metric):
        
        return self._compare_historic(test_metric, cal_metric)

class RangePrimitivePredicate(PrimitivePredicate):

    def __init__(self, test_metric, comparator, cal_metric):

        super().__init__(test_metric, comparator, cal_metric)

    def compare(self, test_metric, cal_metric):

        return self._compare_historic(test_metric, cal_metric["range_val"])

class PrimitiveCalculator:

    def __init__(self, predicates):

        self.predicates = predicates

        self.requirements = []

        for predicate in self.predicates:

            if predicate.test_metric not in self.requirements:
                self.requirements.append(predicate.test_metric)

    def calculate(self, biometrics):

        result = True

        for predicate in self.predicates:

            test_metric = biometrics.get_frame_metric(predicate.test_metric)
            
            cal_metric = biometrics.get_calib_metric(predicate.cal_metric)
    
            result = result and predicate.compare(test_metric, cal_metric)

        return result

class GestureCalculator:

    def __init__(self, name):

        self.name = name

    def calculate(self, biometrics):

        return self.name == biometrics.get_frame_metric("predicted_gesture")

smiling_calculator = GestureCalculator("smiling")
fish_face_calculator = GestureCalculator("fish_face")
open_mouth_calculator = GestureCalculator("open_mouth")
raise_eyebrows_calculator = GestureCalculator("raise_eyebrows")


nose_point_calculator = PrimitiveCalculator(())

nose_left_calculator = PrimitiveCalculator((
    PrimitivePredicate("nose_box_left_offset", greaterThan, "nose_box_percentage_size"),
))

nose_right_calculator = PrimitiveCalculator((
    PrimitivePredicate("nose_box_right_offset", greaterThan, "nose_box_percentage_size"),
))

nose_up_calculator = PrimitiveCalculator((
    PrimitivePredicate("nose_box_top_offset", greaterThan, "nose_box_percentage_size"),
))

nose_down_calculator = PrimitiveCalculator((
    PrimitivePredicate("nose_box_bottom_offset", greaterThan, "nose_box_percentage_size"),
))

head_turn_left_calculator = PrimitiveCalculator((
    RangePrimitivePredicate("head_turn_ratio", lessThan, "turn_left"),
))

head_turn_right_calculator = PrimitiveCalculator((
    RangePrimitivePredicate("head_turn_ratio", greaterThan, "turn_right"),
))

head_tilt_left_calculator = PrimitiveCalculator((
    RangePrimitivePredicate("head_tilt_angle", lessThan, "tilt_left"),
))

head_tilt_right_calculator = PrimitiveCalculator((
    RangePrimitivePredicate("head_tilt_angle", greaterThan, "tilt_right"),
))
