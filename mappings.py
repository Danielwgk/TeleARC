from conf_models import *

wheel = Joystick(0)
PPM_OUTPUT_PIN = 4

"""
Axis 0 is Steering
Axis 1 is Clutch
Axis 2 is Throttle
Axis 3 is Brake
Button 12 is First Gear
Button 13 is Second Gear
Button 22 is Reverse
Button 9 is Front Diff Lock
Button 10 is Rear Diff Lock
Output Values need to be between 903 and 2097
"""

steer_trim = wheel.hat_switch(hat=0, axis=0, positions=41, initial=20)
steering = wheel.axis(0) + steer_trim * 0.5
throttle_trim = wheel.hat_switch(hat=0, axis=1, positions=41, initial=20)
throttle = (-+wheel.axis(2) + 1.0) * -wheel.button(22)
shifter = +wheel.button(12) + -(+wheel.button(13)) + +wheel.button(22)
front_diff = wheel.button(9)
rear_diff = wheel.button(10)

# Output (PPM) channels.
CHANNELS = (
    # CHANNEL 1: Steering
    steering,
    #wheel.axis(0) * 0.5,
    # CHANNEL 2: Absolute Value Throttle with Reverse Gear
    #+-wheel.axis(2) * -wheel.button(22),
	throttle,
    # CHANNEL 3: Shifter
    shifter,
    # CHANNEL 4: Front Diff Lock
    front_diff,
	#wheel.button(9),
    # CHANNEL 5: 
    rear_diff,
	#wheel.button(10),
	# CHANNEL 6: 
    wheel.button(16),
)
