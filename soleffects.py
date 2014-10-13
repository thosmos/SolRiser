import random
from birdfish.envelope import (Envelope, EnvelopeSegment,
        ColorEnvelope)
from birdfish.lights import BaseLightElement, LightElement
from birdfish import tween

# TODO There should probably be a base element - then BaseData or BaseLight
# element

class SolLightElement(object):
    """
    This class handles trigger events, and is updated with the show timeline.
    """

    # TODO need to factor the ADSR related parts out of this class

    def __init__(self,
            name="unamed_LightElements",
            *args, **kwargs):
        """
        name is used for retrieving elements from the show

        bell_mode is a boolean that determines how the element proceeds through
        the Attack-Decay-Sustain-Release envelope in response to triggers. When
        bell_mode is True, the envelope continues through the end of release on
        the "on" trigger alone. When bell_mode is False the ADSR envelope halts
        at sustain, until an off trigger event.

        simple is an attribute, which will disable the update process, allowing
        the elements attributes to be set directly.  This can be useful for
        situations where a parent object manages all the attribute changes for
        child elements.

        trigger_toggle determines the way on and off triggers are handled. When
        True, only 'on' trigger events are responded to, and they toggle the
        element on and off. This can be useful if the device only supports
        momentary push buttons.

        Effects contain an array of :class:`~birdfish.effects.BaseEffect`
        objects.
        """

        self.name = name
        # a simple element has values set externally and does not update
        self.last_update = -1
        self.effects = []
        self.pre_update_effects = []
        self._intensity = 0
        self.changed = False

    def update(self, show):
        """
        The update method is called once per iteration of the main show loop.
        """
        return self.intensity

    def set_intensity(self, intensity):
        # mostly to be overridden by subclasses
#        print "BaseLightElement.set_intensity", intensity
        self._intensity = intensity
        self.changed = True

    def get_intensity(self):
        return self._intensity

    intensity = property(get_intensity, set_intensity)

    def _on_trigger(self, intensity, **kwargs):
        pass

    def _off_trigger(self):
        self.trigger_state = 0
        #self.adsr_envelope.trigger(state=0)
        # note can not set trigger_intensity to 0 here

    def trigger(self, intensity, **kwargs):
        self.set_intensity(intensity)
        return

    def off(self):
        """convenience for off, synonym for trigger(0)"""
        self.trigger(0)


class SolEffect(SolLightElement):
    def __init__(self, *args, **kwargs):
        super(SolEffect, self).__init__(*args, **kwargs)
        self.targets = kwargs.get('targets', [])
        # TODO shoud triggered default be T or F?
        triggered = kwargs.get('triggered', True)
        if triggered:
            self.trigger_state = 0
        else:
            self.trigger_state = 1
        #self.envelope_filters = []

    def trigger(self, intensity, **kwargs):
        if intensity:
            self.trigger_state = 1
            self._on_trigger(intensity, **kwargs)
        else:
            self.trigger_state = 0
            self._off_trigger(intensity, **kwargs)

    def _off_trigger(self, intensity, **kwargs):
        # Since effects can act on lights during release - after off-trigger
        # they may be responsible for turning element intensity off
        super(SolEffect, self)._off_trigger()
#        for element in self.targets:
#            element.set_intensity(0)

    def add_element(self, element):
        self.targets.append(element)
        self.reset()

    def reset(self):
        return

class ColorEnvelope(object):
    """
    Manages a set of envelopes in parallel related to color change
    """
    # TODO notes:
    # how does it handle the existing color of an element
    # can I handle explicit start color, or take current color and shift both
    # can we reset the color to the original?
    #
    def __init__(self, **kwargs):
        self.hue_envelope = Envelope(loop=-1)
        self.saturation_envelope = Envelope(loop=-1)
        self.intensity_envelope = Envelope(loop=-1)

    def _add_shift(self, start, end, duration, shape, envelope):
        if envelope is not None:
            change = end - start
            seg = EnvelopeSegment(
                    start=start,
                    change=change,
                    duration=duration,
                    tween=shape,
                    )
            envelope.segments.append(seg)
        else:
            warnings.warn("Envelope disabled")

    def set_loop(self, loop):
        for env in (self.hue_envelope, self.saturation_envelope,
                self.intensity_envelope):
            env.loop = loop

    def add_hue_shift(self, start=0, end=1, duration=5,
            shape=tween.LINEAR):
        self._add_shift(start, end, duration, shape, self.hue_envelope)

    def add_saturation_shift(self, start=1, end=1, duration=5,
            shape=tween.LINEAR):
        self._add_shift(start, end, duration, shape, self.saturation_envelope)

    def add_intensity_shift(self, start=1, end=1, duration=5,
            shape=tween.LINEAR):
        self._add_shift(start, end, duration, shape, self.intensity_envelope)

    def _color_update(self, time_delta):
        # if any of the shift envelopes have been disabled by being set to None
        # return None for those values
        if self.hue_envelope:
            hue = self.hue_envelope.update(time_delta)
        else:
            hue = None
        if self.saturation_envelope:
            sat = self.saturation_envelope.update(time_delta)
        else:
            sat = None
        if self.intensity_envelope:
            intensity = self.intensity_envelope.update(time_delta)
        else:
            intensity = None
        return (hue, sat, intensity)

    def update(self, time_delta):
        return self._color_update(time_delta)

    def reset(self):
        for env in [self.hue_envelope, self.saturation_envelope,
                self.intensity_envelope]:
            if env is not None:
                env.reset()

    @property
    def duration(self):
        hue_duration = sat_duration = int_duration = 0
        if self.hue_envelope:
            hue_duration = self.hue_envelope.duration
        if self.saturation_envelope:
            sat_duration = self.saturation_envelope.duration
        if self.intensity_envelope:
            int_duration = self.intensity_envelope.duration
        # TODO should we ensure they are all equal, could result in some
        # funky rendering if one is looping differently - maybe that is not bad
        return max(hue_duration, sat_duration, int_duration)

class ColorShift(SolEffect, ColorEnvelope):
    # TODO notes:
    # how does it handle the existing color of an element
    # can I handle explicit start color, or take current color and shift both
    # can we reset the color to the original?
    #
    def __init__(self, shift_amount=0, target=0, **kwargs):
        super(ColorShift, self).__init__(**kwargs)
        ColorEnvelope.__init__(self, **kwargs)
        self.hue = 0
        self.saturation = 1
        self.intensity = 1

    def _on_trigger(self, intensity, **kwargs):
        self.reset()

    def update(self, show, targets=None):
        if self.trigger_state:
            targets = self.get_targets(targets)
            # TODO need to make this anti duplicate calling logic
            # more effects generic - maybe effects specific stuff goes
            # in a render method
            if self.last_update != show.timecode:
                self.hue, self.saturation, self.intensity = self._color_update(
                        show.time_delta)
                self.last_update = show.timecode
            for target in targets:
                if self.hue is not None:
                    target.hue = self.hue
                if self.saturation is not None:
                    target.saturation = self.saturation
                if self.intensity is not None:
                    target.set_intensity(self.intensity)

class SolHueShift(SolEffect):
    #
    def __init__(self, duration = 5, speed = 0.25, width = 1.0, targets = [], **kwargs):
        super(SolHueShift, self).__init__(**kwargs)
        self.targets = targets
        self.duration = duration
        self.speed = speed
        self.width = width

    def update(self, show):
        targets = self.targets
        shift = (show.frame_delay / self.duration) ** (4 * self.speed)

        for target in targets:
            target.hue += shift
            if target.hue > 1.0:
                target.hue = 0.0

    def reset(self):
        print "SolHueShift.reset()"
        count = len(self.targets)
        for i in range(0,count):
            self.targets[i].hue = (1.0 * width / count) * (count - i)

    def set_width(self, width):
        self.width = width

    def get_width(self, width):
        return self.width

    width = property(get_width, set_width)

class SolSwiper(SolEffect):
    #
    def __init__(self, duration = 5, speed = 0.25, targets = [], **kwargs):
        super(SolSwiper, self).__init__(**kwargs)
        self.targets = targets
        self.duration = duration
        self.speed = speed

    def update(self, show):
        targets = self.targets
        shift = (show.frame_delay / self.duration) ** (4 * self.speed)

        for target in targets:
            target.hue += shift
            if target.hue > 1.0:
                target.hue = 0.0

    def reset(self):
        print "SolHueShift.reset()"
        count = len(self.targets)
        for i in range(0,count):
            self.targets[i].hue = (1.0 / count) * (count - i)

