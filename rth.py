import gpiod
import time
import threading

# Define the GPIO pins connected to the DRV8825
STEP_PIN = 17
DIR_PIN = 18
ENABLE_PIN = 23

STEP_PIN2 = 20
DIR_PIN2 = 21
ENABLE_PIN2 = 16

# Open the GPIO chip
chip = gpiod.Chip('gpiochip4')

# Get line handles for each pin
step_line = chip.get_line(STEP_PIN)
dir_line = chip.get_line(DIR_PIN)
enable_line = chip.get_line(ENABLE_PIN)

step2_line = chip.get_line(STEP_PIN2)
dir2_line = chip.get_line(DIR_PIN2)
enable2_line = chip.get_line(ENABLE_PIN2)

# Request the lines as output
for line in [step_line, dir_line, enable_line, step2_line, dir2_line, enable2_line]:
    line.request(consumer="stepper_control", type=gpiod.LINE_REQ_DIR_OUT)

def set_direction(motor, clockwise=True):
    if motor == 1:
        dir_line.set_value(1 if clockwise else 0)
    else:
        dir2_line.set_value(1 if clockwise else 0)

def enable_motor(motor, enable=True):
    if motor == 1:
        enable_line.set_value(0 if enable else 1)
    else:
        enable2_line.set_value(0 if enable else 1)

def step_motor(motor, steps, delay=0.005):
    line = step_line if motor == 1 else step2_line
    for _ in range(steps):
        line.set_value(1)
        time.sleep(delay)
        line.set_value(0)
        time.sleep(delay)

def run_motors(steps, clockwise=True):
    set_direction(1, clockwise)
    set_direction(2, clockwise)
    
    thread1 = threading.Thread(target=step_motor, args=(1, steps))
    thread2 = threading.Thread(target=step_motor, args=(2, steps))
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()

try:
    # Enable both motors
    enable_motor(1, True)
    enable_motor(2, True)

    # Rotate both motors clockwise for 200 steps
    print("Rotating both motors clockwise...")
    run_motors(20, True)
    time.sleep(1)
    
    # Rotate both motors counter-clockwise for 200 steps
    print("Rotating both motors counter-clockwise...")
    run_motors(20, False)

    # Disable both motors
    enable_motor(1, False)
    enable_motor(2, False)

except KeyboardInterrupt:
    print("Program stopped by user")

finally:
    # Release the GPIO lines
    for line in [step_line, dir_line, enable_line, step2_line, dir2_line, enable2_line]:
        line.release()