import keyboard
from time import sleep

def hit(event):
    print(f'Typed {event.name}')

for i in range(100000):
    keyboard.on_press(hit)
    sleep(0.05)

