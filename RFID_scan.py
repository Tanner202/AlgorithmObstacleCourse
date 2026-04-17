from machine import Pin, SPI
from mfrc522 import MFRC522
import time

print("READY - SCAN TAG")

spi = SPI(0,
          baudrate=1000000,
          polarity=0,
          phase=0,
          sck=Pin(18),
          mosi=Pin(19),
          miso=Pin(16))

rdr = MFRC522(spi=spi, cs=Pin(17), rst=Pin(20))

last = None

while True:

    stat, _ = rdr.request(rdr.REQIDL)

    if stat == rdr.OK:

        stat, uid = rdr.anticoll()

        if stat == rdr.OK:

            if uid != last:
                print("UID:", uid)
                last = uid
                time.sleep(1.5)

    time.sleep(0.1)