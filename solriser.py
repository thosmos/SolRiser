import sys
import random
import config
import time

from birdfish.input.osc import OSCDispatcher
from birdfish.effects import Blink, Pulser, ColorShift
from birdfish.lights import LightElement, RGBLight, PulseChase, LightShow
from birdfish.output.solriserdmx import SolRiserDmx
from birdfish import tween
from solrgb import SolRgb
from solshow import SolShow
from soleffects import SolHueShift

# 0.1 lighting is stable on both host and yun systems


NUM_ADDRESSES = 93
NUM_CHANNELS = 31

channel_names = {
    1: 'nose_front',
    2: 'nose_mid',
    3: 'nose_rear',
    4: 'nose_sides_lower',
    5: 'nose_sides_upper',
    6: 'wings',
    7: '',
    8: '',
    9: 'windshield',
    10: 'beak_front',
    11: 'beak_rear',
    12: 'ray_mid_inner',
    13: 'ray_midleft_inner',
    14: 'ray_midright_inner',
    15: 'ray_left_inner',
    16: 'ray_right_inner',
    17: 'ray_mid_outer',
    18: 'ray_midleft_outer',
    19: 'ray_midright_outer',
    20: 'ray_left_outer',
    21: 'ray_right_outer',
    22: 'arc',
    23: 'sides_front',
    24: 'sides_mid',
    25: 'sides_rear',
    26: 'rails_front',
    27: 'rails_mid',
    28: 'rails_rear',
    29: 'canopy_front',
    30: 'canopy_rear',
    31: 'stairs'
}


# create a light show - manages the updating of all lights
show = SolShow()

# Create a network - in this case, the SolRiser DMX shield over serial
#dmx = SolRiserDmx('/dev/ttyATH0')
dmx = SolRiserDmx(config.SERIAL_PORT)

# add the network to the show
show.networks.append(dmx)

# create an input interface
# dispatcher = MidiDispatcher("MidiKeys")
dispatcher = OSCDispatcher(('0.0.0.0', 8998))


# the effect is configured by how many times it should pulse per second
# 1 is the default
#pulser = Pulser()
hueShift = SolHueShift()
hueShift.width = 0.3
#raySwiper = SolSwiper()
#hueShift.add_hue_shift()

show.effects.append(hueShift)
#show.effects.append(raySwiper)

# if you wanted to give the pulse a different characteristic
# pulser = Pulser(on_shape=tween.IN_CIRC, off_shape=tween.OUT_CIRC)

for i in range(1,NUM_CHANNELS + 1):
    l = SolRgb(
            start_channel=i * 3 - 2,
            #name="pulse_%s" % elementid,
            name=channel_names[i],
            #attack_duration=0.5,
            #release_duration=0,
            #sustain_value=1,
            #simple=True
            )
    #l.hue = random.random() # * 255
    #l.hue = .74

    l.hue = (1.0 / NUM_CHANNELS) * (NUM_CHANNELS - (i - 1.0))
    l.intensity = 1
    l.saturation = 1

    #l.update_rgb()

    show.add_element(l, network=dmx)
    hueShift.add_element(l)

    # add the light to the network
    #dmx.add_element(l)
    #p.elements.append(l)

    dispatcher.add_map('/global/intensity', l, 'intensity')
    dispatcher.add_map('/1/fader1', l, 'intensity')
    dispatcher.add_map('/global/hue', l, 'hue')
    #l.effects.append(pulser)

    # set the input interface to trigger the element
    # midi code 41 is the "Q" key on the qwerty keyboard for the midikeys app
    #dispatcher.add_observer((0,41), single)
    dispatcher.add_trigger('/global/active', l)
    dispatcher.add_trigger('/1/push1', l)
    #dispatcher.add_trigger('/global/active', l)

#    if i in range(12,21):
#        raySwiper.add_element(l)

dispatcher.add_map('/global/speed', hueShift, 'speed')
dispatcher.add_map('/1/fader2', hueShift, 'speed')


inners = [15, 13, 12, 14, 16]
outers = [20, 18, 17, 19, 21]


# startup the midi communication - runs in its own thread
# dispatcher.start()
dispatcher.start()

# start the show in a try block so that we can catch ^C and stop the midi
# dispatcher thread
try:
    show.run()
except KeyboardInterrupt:
    # cleanup
    # dispatcher.stop()
    dispatcher.stop()
    sys.exit(0)


