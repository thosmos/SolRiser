from collections import deque
import time

class SolShow(object):

    def send_viewer_data(self):
        dd = ''.join([chr(int(i)) for i in self.networks[1].data])
        f = open('/tmp/dmxpipe', 'wb', 0)
        pad_dd = dd.ljust(512, '\x00')
        f.write(pad_dd)
        f.close()

    def __init__(self):
        super(SolShow, self).__init__()
        self.networks = []
        self.effects = []
        self.frame_rate = 40
        # self.scenemanager = SceneManager()
        self.frame_delay = 1 / self.frame_rate
        self.running = True
        self.named_elements = {}
#        self.default_network = DefaultNetwork()
#        self.networks.append(self.default_network)
        self.time_delta = 0
        self.recent_frames = deque()
        self.average_framerate = self.frame_delay
        self.frame = 0
        self.elements = []

    def add_element(self, element, network=None):
        if network:
            network.add_element(element)
            if network not in self.networks:
                self.networks.append(network)
        if element not in self.elements:
            self.elements.append(element)

    def remove_element(self, element, network=None):
        if hasattr(element, 'elements') and element.elements:
            for sub_element in element.elements:
                self.remove_element(sub_element)
        for network in self.networks:
            network.remove_element(element)
        try:
            self.elements.remove(element)
            return True
        except ValueError:
            return False

    def blackout(self):
        for n in self.networks:
            for e in n.elements:
                e.trigger(0)
                if hasattr(e, 'intensity'):
                    e.intensity = 0

    def get_named_element(self, name):
        if name in self.named_elements:
            # a simple cache
            return self.named_elements[name]
        for network in self.networks:
            named_light = network.get_named_element(name)
            if named_light:
                self.named_elements[name] = named_light
                return named_light
        return False

    def init_show(self):
        # needed as params may be changed between __init__ and run_live
        for n in self.networks:
            n.init_data()
        self.frame_delay = 1.0 / self.frame_rate

    def frame_average(self, frame):
        self.recent_frames.append(frame)
        frame_count = len(self.recent_frames)
        if frame_count > 8:
            self.recent_frames.popleft()
            frame_count -= 1
        elif frame_count == 0:
            return frame
        return sum(self.recent_frames) / frame_count

    def step(self, count=1, speed=1):
        """
        Simulate a step or steps in main loop
        """
        for i in range(count):
            self.timecode += self.frame_delay
            self.time_delta = self.frame_delay
            self.update()
            for n in self.networks:
                n.send_data()
            if speed and count > 1 and i < (count - 1):
                time.sleep((1 / speed) * self.frame_delay)

    def run(self):
        self.init_show()
        self.show_start = time.time()
        self.timecode = self.frame_delay
        self.time_delta = self.frame_delay;
        while self.running:
            self.update()
            post_update = time.time() - self.show_start
            # how long did this update actually take
            frame_time = post_update - (self.timecode - self.frame_delay)
            avg_frame_time = self.frame_average(frame_time)
            
            frame_diff = self.timecode - post_update
            
            if frame_diff < 0.0:
                print "Too slow"
            
            self.frame += 1
            
            if frame_diff > 0.0:
                # we finished early, wait to send the data
                # TODO this wait could/should happen in another thread that
                # handles the data sending - but currently sending the data
                # is fast enough that this can be investigated later
                self.time_delta = self.frame_delay
                time.sleep(frame_diff)
            else:
                self.time_delta = self.frame_delay - frame_diff
                
            self.timecode = self.timecode + self.time_delta
                
            for n in self.networks:
                n.send_data()
            if self.frame == 40:
                # print [e.channels for e in self.networks[1].elements]
                print('frame_time: ', avg_frame_time, ", frame_diff: ", frame_diff)
                self.frame = 0            
            
        
    def run_live(self):
        self.init_show()
        self.show_start = time.time()
        self.timecode = 0
        while self.running:
            # projected frame event time
            now = time.time() + self.frame_delay
            timecode = now - self.show_start
            self.time_delta = timecode - self.timecode
            self.timecode = timecode
            self.update()
            post_update = time.time()
            # how long did this update actually take
            effective_frame = post_update - (now - self.frame_delay)
            effective_framerate = self.frame_average(effective_frame)
            discrepancy = effective_framerate - self.frame_delay
            if discrepancy > .01:
                self.frame_delay += .01
                if discrepancy > .3:
                    warnings.warn("Slow refresh")
            elif discrepancy < -.01 and self.frame_delay > 1 / self.frame_rate:
                # we can speed back up
                self.frame_delay -= .01
            self.frame += 1
            remainder = self.frame_delay - effective_frame
            if remainder > 0:
                # we finished early, wait to send the data
                # TODO this wait could/should happen in another thread that
                # handles the data sending - but currently sending the data
                # is fast enough that this can be investigated later
                time.sleep(remainder)
            # pre_send = time.time()
            for n in self.networks:
                n.send_data()
            if self.frame == 40:
                # print [e.channels for e in self.networks[1].elements]
                print('framerate: ', 1 / self.frame_delay, " Remainder: ",
                        remainder)
                self.frame = 0

    def update(self):
        """The main show update command"""
        # self.scenemanager.update(self)
        for element in self.elements:
            if element.last_update != self.timecode:
                # avoid updating the same element twice
                element.update(self)
                element.last_update = self.timecode
            else:
                print "tried to show.update again"
        for e in self.effects:
            e.update(self)