from birdfish.colors import DIYC_DIM
import colorsys

class SolRgb(object):
    def __init__(self, start_channel=1, name="unnamed", *args, **kwargs):
        """
        start_channel: The first channel this device occupies in a
        network.

        The channels dictionary contains a mapping of channel numbers to object
        attributes.
        """

        self.start_channel = start_channel
        self.name = name

        self._intensity = 0
        self._hue = 0.0
        self._saturation = 0
        self.red = 0
        self.green = 0
        self.blue = 0
        self.gamma = DIYC_DIM

        self.channels = {}
        self.channels[self.start_channel] = 'red'
        self.channels[self.start_channel + 1] = 'green'
        self.channels[self.start_channel + 2] = 'blue'
        
        self.normalize = False
        self.changed = False
        self.last_update = -1
        self.device = self

        

    def update_gamma(self):
        # apply dimming or other adjustments
        if self.gamma:
            # TODO for now gamma is as an 8 bit lookup
            dmx_val = int(self.intensity * 255)
            val = self.gamma[dmx_val]
            self.intensity = val / 255

    def get_intensity(self):
        return self._intensity

    def set_intensity(self, intensity):
        #print "SolRgb.set_intensity", intensity
        #self.update_gamma();
        self._intensity = intensity
        self.changed = True
    
    def get_hue(self):
        return self._hue

    def set_hue(self, hue):
        self._hue = hue
        self.changed = True

    def get_saturation(self):
        return self._saturation

    def set_saturation(self, saturation):
        self._saturation = saturation
        self.changed = True
        
    hue = property(get_hue, set_hue)
    saturation = property(get_saturation, set_saturation)
    intensity = property(get_intensity, set_intensity)
    
    def update_data(self, data):
        """
        This method is called by the network containing this item in order to
        retrieve the current channel values.

        Data is an array of data (ie DMX) that should be updated
        with this light's channels
        """
        #self.update_channels()
        for channel, value in self.channels.items():
            try:
                # targeted optimization:
                val = self.__dict__[value]
            except AttributeError:
                val = getattr(self, value)
            # TODO current design flaw/limitation
            # using byte arrays instead of float arrays for base
            # data structure - means forcing to bytes here instead
            # of output network level - practically this is OK as all
            # networks are using 1 byte max per channel
            # Here the channel values are highest value wins
            # print 'data: ', data, ', channel: ', channel, ', value: ', value, ', val: ', val
            # data[channel - 1] = max(data[channel - 1], int(val * 255))
            data[channel - 1] = int(val * 255)
            # print 'data: ', data, ', channel: ', channel, ', value: ', value, ', val: ', val

    def update(self, show):
        """
        The update method is called once per iteration of the main show loop.
        """
        if self.changed:
            self.update_rgb()
            self.changed = False

        return self._intensity
        
    def update_rgb(self):
        # print 'update_rgb'
        hue = self._hue
        saturation = self._saturation
        intensity = self._intensity
        
        # this funct takes all 0-1 values
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, intensity)
        if self.normalize and any((r, g, b)):
            maxval = max((r, g, b))
            adj = maxval / 1
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, intensity * adj)
        self.red = r
        self.green = g
        self.blue = b

    def trigger(self, intensity, **kwargs):
        self.set_intensity(intensity)

    def off(self):
        """convenience for off, synonym for trigger(0)"""
        self.trigger(0)

