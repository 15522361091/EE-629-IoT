# Lab2
## Lab 2A: General-purpose input/output (GPIO) and serial communication
Connect GPIO14 to GPIO15 via jump wire 
Install and run minicom  
## Lab 2B: Serial peripheral interface (SPI)
Connect MOSI(GPIO10) to MISO(GPIO9) via jump wire  
Run commands:  
```
wget https://raw.githubusercontent.com/raspberrypi/linux/rpi-3.10.y/Documentation/spi/spidev_test.c  
gcc -o spidev_test spidev_test.c  
./spidev_test -D /dev/spidev0.0  
```
## Lab 2C: Breadboard
Connet circuit on breadboard
## Lab 2D: Light-emitting diode (LED)
Run [led.py](led.py)
