'''
Copyright (c) 2023 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

Sophie robot project:

Motor test module

A micropython program for the lower level pi PICO to test the omni direction drive of the platform. This is rough get it working code. The plan is to write up code that takes more of a
vector and magnitude commands from the higher controller (also make sure to have it stop and remove drive power if it does not recive a heartbeat
from main computer as a safety feature) 
'''

import utime
from machine import Pin
import math

# define stepper motor pins
motor1_step = Pin(1, Pin.OUT)
motor1_dir = Pin(2, Pin.OUT)
motor2_step = Pin(3, Pin.OUT)
motor2_dir = Pin(4, Pin.OUT)
motor3_step = Pin(5, Pin.OUT)
motor3_dir = Pin(6, Pin.OUT)

# function to move the motor by a given number of steps with given direction
def move_motor(motor_step, motor_dir, steps):
    # set the direction of the motor
    motor_dir.value(1 if steps < 0 else 0)
    return abs(steps)

def perform_square_movement():
    for _ in range(4):
        # Move forward
        control_motors(x=0, y=1, rotation=0, speed=10)
        utime.sleep(forward_duration)  # Duration to move forward one side of the square

        # Stop
        control_motors(x=0, y=0, rotation=0, speed=0)
        utime.sleep(1)  # Short pause

        # Turn 90 degrees
        control_motors(x=0, y=0, rotation=1, speed=10)  # Adjust rotation direction as needed
        utime.sleep(turn_duration)  # Duration for 90-degree turn

        # Stop before next movement
        control_motors(x=0, y=0, rotation=0, speed=0)
        utime.sleep(1)  # Short pause
        
# Define the durations for forward movement and turning
forward_duration = 4  # Adjust this time based on your robot's speed
turn_duration = 2  # Adjust this time for a precise 90-degree tur

# function to control the three motors simultaneously with given direction and rotation
def control_motors(x, y, rotation, speed):
    # convert speed to steps per second (assuming 100 steps per revolution)
    steps_per_second = speed * 100 

    # calculate motor speeds based on x, y, and rotation
    motor1_speed = -x * 0.5 + y * 0.866 + rotation
    motor2_speed = x * 0.5 - y * 0.866 + rotation
    motor3_speed = -x + rotation

    # convert speeds to steps
    motor1_steps = move_motor(motor1_step, motor1_dir, round(motor1_speed * steps_per_second))
    motor2_steps = move_motor(motor2_step, motor2_dir, round(motor2_speed * steps_per_second))
    motor3_steps = move_motor(motor3_step, motor3_dir, round(motor3_speed * steps_per_second))

    # find the maximum number of steps
    max_steps = max(motor1_steps, motor2_steps, motor3_steps)

    # move each motor simultaneously
    for i in range(max_steps):
        if i < motor1_steps:
            motor1_step.value(1)
        if i < motor2_steps:
            motor2_step.value(1)
        if i < motor3_steps:
            motor3_step.value(1)

        utime.sleep_us(1000000 // steps_per_second)

        motor1_step.value(0)
        motor2_step.value(0)
        motor3_step.value(0)

        utime.sleep_us(1000000 // steps_per_second)

# Move forward at speed 10
#control_motors(x=0, y=1, rotation=0, speed=10) 

# Move backward at speed 10
control_motors(x=0, y=1, rotation=0, speed=20)

# Strafe right at speed 10
#control_motors(x=1, y=0, rotation=0, speed=10)

# Strafe left at speed 10
#control_motors(x=-1, y=0, rotation=0, speed=10)

# Rotate 360 degrees at a specified rotational speed
#control_motors(x=0, y=0, rotation=1, speed=10)

# You need to determine how long to run this command for a full 360-degree rotation.
# This would depend on the specifics of your robot's design and the 'speed' parameter.
# For example, you might find through experimentation that it takes 5 seconds for a full rotation.
#utime.sleep(4)  # Adjust the duration based on your robot's characteristics

# Stop the rotation after the duration has elapsed
#control_motors(x=0, y=0, rotation=0, speed=0)

# Perform the square movement
#perform_square_movement()
