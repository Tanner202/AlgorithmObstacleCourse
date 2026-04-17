
from machine import Pin, PWM
import time
import random

# servo pins
servo3 = PWM(Pin(0))
servo2 = PWM(Pin(1))
servo1 = PWM(Pin(2))

servo1.freq(50)
servo2.freq(50)
servo3.freq(50)

# servo positions
HOME1 = 4000
HOME2 = 4050
HOME3 = 3800

OFFSET = 2500

DISP1 = HOME1 + OFFSET
DISP2 = HOME2 + OFFSET
DISP3 = HOME3 + OFFSET + 150

# button pins
button1 = Pin(10, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(11, Pin.IN, Pin.PULL_DOWN)
button3 = Pin(12, Pin.IN, Pin.PULL_DOWN)

# initial probabilities
weights = [1,1,1]

# servo motion
def home():
    
    servo1.duty_u16(HOME1)
    servo2.duty_u16(HOME2)
    servo3.duty_u16(HOME3)
    
    time.sleep(1)

def dispense(servo, disp, home):
    
    servo.duty_u16(disp)
    time.sleep(0.5)
    servo.duty_u16(home)
    time.sleep(1.8)

# probability logic
def weighted_pick(weights):
    
    total = sum(weights)
    
    r = random.uniform(0, total)
    
    cumulative = 0
    
    for i in range(len(weights)):
        cumulative += weights[i]
        if r <= cumulative:
            return i

def dispense_round(round_num):
    
    print("Round", round_num)
    
    if round_num == 1:
        pattern = [1,1,1]
    
    else:
        pattern = [0,0,0]
        
        for _ in range(3):
            pick = weighted_pick(weights)
            pattern[pick] += 1
    
    print("Card Output:", pattern)
    
    for i in range(pattern[0]):
        dispense(servo1, DISP1, HOME1)
        
    for i in range(pattern[1]):
        dispense(servo2, DISP2, HOME2)
        
    for i in range(pattern[2]):
        dispense(servo3, DISP3, HOME3)
        
        
# user preference
def wait_for_selection():
    
    print("Select a topic to see more of")
    
    while True:
        
        if button1.value():
            while button1.value():
                pass
            time.sleep(0.15)
            return 0
            
        if button2.value():
            while button2.value():
                pass
            time.sleep(0.15)
            return 1
            
        if button3.value():
            while button3.value():
                pass
            time.sleep(0.15)
            return 2

# round logic
home()

rounds = 20

for r in range(1, rounds+1):
    
    dispense_round(r)
    
    choice = wait_for_selection()
    
    # learning preferences
    weights[choice] += 8
    
    print("Updated Weights:", weights)

print("Algorithm Demo Complete")