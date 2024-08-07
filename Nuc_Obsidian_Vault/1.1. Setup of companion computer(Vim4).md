
1. Use serial port setup, which can be found [here](https://docs.px4.io/main/en/companion_computer/pixhawk_companion.html) or direct to jumpers like it was done with the [RaspsberryPi](https://docs.px4.io/main/en/companion_computer/pixhawk_rpi.html)
		1. Might  need USB to Serial breakout board:
			- https://www.robotics.org.za/W6170?search=ftdi%20usb%20to%20serial
			- https://www.mantech.co.za/ProductInfo.aspx?Item=15M0301 needs soldering
		2. OR: Connect directly to companion
	1. Decide to use either MAVLink or  uXRCE-DDS between companion and Flight controller (First thought = MAVLink: Seems simpler to implement)
	2. PX4 expects companion computers to connect via TELEM2 for offboard control. The port is configured by default to interface using MAVLink
	3. To use [ROS 2/uXRCE-DDS](https://docs.px4.io/main/en/ros/ros2_comm.html) instead of MAVLink on `TELEM2`, disable MAVLink on the port and then enable the uXRCE-DDS client on `TELEM2`

Check out [this computer vision link](https://docs.px4.io/main/en/computer_vision/)
