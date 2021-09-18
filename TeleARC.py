from mappings import (
    CHANNELS, PPM_OUTPUT_PIN)

import logging
import pygame
import signal
import threading
import time

try:
    import pigpio
except ImportError as e:
    logging.warn(e, exc_info=True)
    logging.warn("Failed to load pigpio library, running in debug mode")
    pigpio = None

_running = False

_output = ()


def shutdown(signum, frame):
    global _running
    _running = False


def main():
    global _output

    pygame.init()

    # Reading only "clicks" via events. These are used for advanced
    # mappings. Events to avoid tracking state manually. Axes are read
    # by snapshotting.
    pygame.event.set_allowed([pygame.JOYBUTTONDOWN,
                              pygame.JOYHATMOTION])

    pi_gpio = 1 << PPM_OUTPUT_PIN
	
    if pigpio:
        pi = pigpio.pi()
        pi.set_mode(PPM_OUTPUT_PIN, pigpio.OUTPUT)
        pi.wave_add_generic([pigpio.pulse(pi_gpio, 0, 2000)])
        # padding to make deleting logic easier
        waves = [None, None, pi.wave_create()]
        pi.wave_send_repeat(waves[-1])
    else:
        pi = None

    prev = None

    while _running:
        # clicks for advanced mapping
        clicks, hats = [], []
        for evt in pygame.event.get():
            if evt.type == pygame.JOYBUTTONDOWN:
                #print "JOYBUTTONDOWN: %r\n%s" % (evt, dir(evt))
                clicks.append(evt)
            elif evt.type == pygame.JOYHATMOTION and any(evt.value):
                #print "JOYHATMOTION: %r\n%s" % (evt, dir(evt))
                hats.append(evt)

        # tuple to enforce immutability "CHANNELS(1,2,3,4,5,6..)"
        _output = tuple(max(min(ch((clicks, hats)), 1.), -1.)
                        for ch in CHANNELS)

        if _output == prev:
            # do nothing
            pass
			
        elif pigpio:
            pulses, pos = [], 0
            for value in _output:
                us = int(round(1500 + 398 * value))
                pulses += [pigpio.pulse(0, pi_gpio, 300),
                           pigpio.pulse(pi_gpio, 0, us - 300)]
                pos += us

            pulses += [pigpio.pulse(0, pi_gpio, 300),
                       pigpio.pulse(pi_gpio, 0, 22000 - 300 - pos - 1)]

            pi.wave_add_generic(pulses)
            waves.append(pi.wave_create())
            pi.wave_send_using_mode(waves[-1], pigpio.WAVE_MODE_REPEAT_SYNC)

            last, waves = waves[0], waves[1:]
            if last:
                pi.wave_delete(last)

        else:
            # debugging
            print (_output)

        prev = _output
		
        # NO BUSYLOOPING. And locking with ``pygame.event.wait`` doesn't sound
        # very sophisticated. (At this point, at least.)
        time.sleep(.02)
		
	#print(_output)

    if pi:
        pi.stop()

if __name__ == '__main__':
    _running = True
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    main()
