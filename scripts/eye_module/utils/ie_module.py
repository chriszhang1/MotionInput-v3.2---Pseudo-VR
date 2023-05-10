import os

# from openvino.inference_engine import IEPlugin
from openvino.inference_engine import IECore


def load_iecore(device, net_model_xml_path):
    ie = IECore()

    net_model_bin_path = os.path.splitext(net_model_xml_path)[0] + '.bin'
    net = ie.read_network(model=net_model_xml_path, weights=net_model_bin_path)
    ie = IECore()
    exec_net = ie.load_network(network=net, device_name=device)

    return exec_net


class Module(object):
    def __init__(self, model):
        self.model = model
        self.device_model = None

        self.max_requests = 0
        self.active_requests = 0

        self.clear()

    def deploy(self, queue_size=1):
        # self.context = context
        self.max_requests = queue_size
        # self.device_model = context.load_model(
        #     self.model, device, self.max_requests)
        self.device_model = self.model  ##
        self.model = None

    def enqueue(self, input):
        self.clear()

        if self.max_requests <= self.active_requests:
            # "Processing request rejected - too many requests"
            return False

        self.device_model.start_async(self.active_requests, input)
        self.active_requests += 1
        return True

    def wait(self):
        if self.active_requests <= 0:
            return

        self.perf_stats = [None, ] * self.active_requests
        self.outputs = [None, ] * self.active_requests
        for i in range(self.active_requests):
            self.device_model.requests[i].wait()
            self.outputs[i] = self.device_model.requests[i].outputs
            self.perf_stats[i] = self.device_model.requests[i].get_perf_counts()

        self.active_requests = 0

    def get_outputs(self):
        self.wait()
        return self.outputs

    def get_performance_stats(self):
        return self.perf_stats

    def clear(self) -> None:
        self.perf_stats = []
        self.outputs = []
