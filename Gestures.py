"""
Gestures script using move_servo and delays
"""
# ------------------- Import Libraries -------------------

from cvzone.SerialModule import SerialObject  # Import the SerialObject for serial communication with Arduino
from time import sleep  # Import sleep to add delays between actions

# ------------------- Initializations -------------------

# Create a Serial object with three digits precision for sending servo angles
arduino = SerialObject(digits=3)

# Initialize the last known positions for the three servos: Left (LServo), Right (RServo), Head (HServo)
# LServo starts at 180 degrees, RServo at 0 degrees, and HServo at 90 degrees
last_positions = [180, 0, 90]


#                [LServo , RServo ,HServo ]


# ------------------- Functions -------------------

# Function to smoothly move servos to target positions
def move_servo(target_positions, delay=0.001):
    """
    Moves the servos smoothly to the target positions.

    :param target_positions: List of target angles [LServo, RServo, HServo]
    :param delay: Time delay (in seconds) between each incremental step
    """
    global last_positions  # Use the global variable to track servo positions
    # Calculate the maximum number of steps required for the largest position difference
    max_steps = max(abs(target_positions[i] - last_positions[i]) for i in range(3))

    # Incrementally move each servo to its target position over multiple steps
    for step in range(max_steps):
        # Calculate the current position of each servo at this step
        current_positions = [
            last_positions[i] + (step + 1) * (target_positions[i] - last_positions[i]) // max_steps
            if abs(target_positions[i] - last_positions[i]) > step else last_positions[i]
            for i in range(3)
        ]
        # Send the calculated positions to the Arduino
        arduino.sendData(current_positions)
        # Introduce a small delay to ensure smooth motion
        sleep(delay)

    # Update the last known positions to the target positions
    last_positions = target_positions[:]


# ---------------- Gestures for single servo ----------

def casual_rest():
    global last_positions
    # casual rest turns servo to rest positons..
    for _ in range(2):
        move_servo([170, 10,100])
        move_servo([180,0,90])


def hello_gesture():
    """
    Makes Nova wave hello by moving the right servo back and forth.
    """
    global last_positions
    # Move right arm to start waving
    move_servo([last_positions[0], 180, last_positions[2]])
    for _ in range(3):  # Perform the waving motion 3 times
        move_servo([last_positions[0], 150, last_positions[2]])  # Move arm slightly down
        move_servo([last_positions[0], 180, last_positions[2]])  # Move arm back up
    # Reset arm to original position
    move_servo([last_positions[0], 0, last_positions[2]])


def dizzy_gesture():
    while True:
        global last_positions
        print("Starting Playful Dance")
        for _ in range(4):
            move_servo([last_positions[0], last_positions[1], 140])  # Move servos to position for dance
            move_servo([last_positions[0], last_positions[1], 50])  # Move servos to another position

        move_servo([last_positions[0], 0, last_positions[2]])


# ------------ Gestures for 2 servos ---------------

def sleep_gesture():
    while True:
        # Move both arms
        for _ in range(2):
            print("Sleeping")
            move_servo([150, 0, last_positions[2]], delay=0.02)
            move_servo([180, 30, last_positions[2]], delay=0.02)


def sad_happy_gesture():
    while True:
        # Move both arms playfully
        for _ in range(4):
            print("Moving both arms")
            move_servo([100, 0, last_positions[2]])
            move_servo([180, 80, last_positions[2]])


# ------------------ Gestures for 3 servos -----------------

def surprised_gesture():
    while True:
        # Move both arms playfully
        for _ in range(4):
            print("Moving both arms")
            move_servo([10, 130, 80])
            move_servo([50, 170, 100])


def angry_gesture():
    while True:
        for _ in range(4):
            print("Moving both arms")
            move_servo([10, 100, 110])
            move_servo([80, 170, 80])


# ------------------ Custom Gesture

def fist_bump():
    global last_positions, switch_video
    print("Performing Fist Bump")
    move_servo([last_positions[0], 90, last_positions[2]])
    sleep(2)
    switch_video = True  # Signal to switch video
    for _ in range(4):
        move_servo([10, 130, 80])
        move_servo([50, 170, 100])
    move_servo([180, 0,last_positions[2]])


# ------------------- Main Loop -------------------

# hello_gesture()
angry_gesture()