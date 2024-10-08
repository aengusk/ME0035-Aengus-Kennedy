import time
import network
from mqtt import MQTTClient

import sensor
import time
import math

SSID = "Tufts_Robot"  # Network SSID
KEY = ""  # Network key

# Init wlan module and connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

while not wlan.isconnected():
    print('Trying to connect to "{:s}"...'.format(SSID))
    time.sleep_ms(1000)

# We should have a valid IP now via DHCP
print("WiFi Connected", wlan.ifconfig())

mqtt_broker = "broker.hivemq.com" 
port = 1883     # this reads anything sent to ME35
topic_pub = "ME35-24/prius5"
        
client = MQTTClient("ME35_chris", mqtt_broker, port, keepalive=60)
client.connect()

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # must turn this off to prevent image washout...
sensor.set_auto_whitebal(False)  # must turn this off to prevent image washout...
clock = time.clock()


while True:
    clock.tick()
    img = sensor.snapshot()
    for tag in img.find_apriltags():
        img.draw_rectangle(tag.rect, color=(255, 0, 0))
        img.draw_cross(tag.cx, tag.cy, color=(0, 255, 0))
        print_args = (tag.name, tag.id, (180 * tag.rotation) / math.pi)
        r = (180 * tag.rotation) / math.pi
        distance = tag.z_translation  # z_translation gives an estimate of the distance
        #print("Tag Family %s, Tag ID %d, rotation %f (degrees)" % print_args)
        #print(r)
        #print("Distance from tag: %f" % distance)
        
        msg = ""
        if 150 <= r <= 210:
            msg = "f"
        elif 240 <= r <= 300:
            msg = "r"
        elif r <= 30 or r >= 330:
            msg = "b"
        elif 60 <= r <= 120:
            msg = "l"
            
        command = msg + ", " + str(distance)
        
        client.publish(topic_pub, command)
        time.sleep_ms(10)
        
    #print(clock.fps())