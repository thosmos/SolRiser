import sys
import random

from birdfish.input.osc import OSCDispatcher
from birdfish.effects import Blink, Pulser
from birdfish.lights import LightElement, RGBLight, PulseChase, LightShow
from birdfish.output.solriserdmx import SolRiserDmx
from birdfish import tween


# create a light show - manages the updating of all lights
show = LightShow()

# Create a network - in this case, universe 3
dmx = SolRiserDmx('/dev/ttyATH0')
#dmx = SolRiserDmx('/dev/tty.usbmodem1d21')

# add the network to the show
show.networks.append(dmx)

# create an input interface
# dispatcher = MidiDispatcher("MidiKeys")
dispatcher = OSCDispatcher(('0.0.0.0', 8998))


## create a single channel light element
#single = LightElement(
#        start_channel=1,
#        name="singletest",
#        attack_duration=1,
#        release_duration=1.5,
#        )

# add the light to a network
#show.add_element(single, network=dmx)

# the effect is configured by how many times it should pulse per second
# 1 is the default
pulser = Pulser()

# if you wanted to give the pulse a different characteristic
# pulser = Pulser(on_shape=tween.IN_CIRC, off_shape=tween.OUT_CIRC)

# we append the effect to the elements own list of effects
#single.effects.append(pulser)

# set the input interface to trigger the element
# midi code 41 is the "Q" key on the qwerty keyboard for the midikeys app
#dispatcher.add_observer((0,41), single)
#dispatcher.add_trigger('/1/push1', single)


#single = RGBLight(
#        start_channel=1,
#        name="singletestb",
##        attack_duration=0,
##        decay_duration=0,
##        release_duration=0,
##        sustain_value=0,
#        simple=True
#        )
#
#single.hue = random.random()
#single.saturation = 1
##single.bell_mode = True
#single.update_rgb()
#
#
## add the light to a network
#show.add_element(single, network=dmx)
#
## set the input interface to trigger the element
## midi code 41 is the "Q" key on the qwerty keyboard for the midikeys app
#dispatcher.add_trigger('/1/toggle1', single)
#dispatcher.add_map('/1/fader2', single, 'hue')
#dispatcher.add_map('/1/fader1', single, 'saturation')
##dispatcher.add_map('/1/faderA', single, 'saturation', in_range=(0,4))
#
## set the input interface to trigger the element
## midi code 41 is the "Q" key on the qwerty keyboard for the midikeys app
## midi_dispatcher.add_observer((0,41), single)
#dispatcher.add_trigger('/1/push1', single)



#p = PulseChase(name="greenpulse",
#        start_pos=1,
#        end_pos=12,
#        speed=3,
#        move_tween=tween.IN_OUT_CUBIC,
#        )
#
elementid = 0
for i in range(1,27,3):
    elementid += 1
    l = RGBLight(
            start_channel=i,
            name="pulse_%s" % elementid,
            attack_duration=0,
            release_duration=0,
            sustain_value=1,
            #simple=True
            )
    #l.hue = random.random() # * 255
    l.hue = .74
    l.saturation = 1
    l.update_rgb()
    show.add_element(l, network=dmx)
    #l.simple = True
    # add the light to the network
    #dmx.add_element(l)
    #p.elements.append(l)
    dispatcher.add_map('/1/fader1', l, 'hue')
    dispatcher.add_map('/1/fader2', l, 'intensity')
#    l.effects.append(pulser)

    # set the input interface to trigger the element
    # midi code 41 is the "Q" key on the qwerty keyboard for the midikeys app
    #dispatcher.add_observer((0,41), single)
    dispatcher.add_trigger('/1/push1', l)
    dispatcher.add_trigger('/1/toggle1', l)

#
#
#p.start_pos = 1
## p.left_width = p.right_width = 10
#p.left_width = 1
#p.right_width = 1 
#p.left_shape = p.right_shape = tween.OUT_CIRC
#p.speed = 3
#p.moveto = p.end_pos = 12
##p.trigger_toggle = True
#
#show.add_element(p)
#
## set the input interface to trigger the element
## midi code 70 is the "J" key on the qwerty keyboard for the midikeys app
## dispatcher.add_observer((0,70),p)
#dispatcher.add_map('/1/fader1', p, 'speed', in_range=(0,1), out_range=(.5, 10))
#
##dispatcher.add_trigger('/1/push1', p)
#dispatcher.add_trigger('/1/toggle1', p)

# startup the midi communication - runs in its own thread
# dispatcher.start()
dispatcher.start()

# start the show in a try block so that we can catch ^C and stop the midi
# dispatcher thread
try:
    show.run_live()
except KeyboardInterrupt:
    # cleanup
    # dispatcher.stop()
    dispatcher.stop()
    sys.exit(0)


