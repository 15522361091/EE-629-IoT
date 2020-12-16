#Gestures Control LED(on RPi)
#Shichao Li 12/13/2020
#coding:utf-8
import socket
import time
import sys
import RPi.GPIO

#Initialization
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setwarnings(False)
RPi.GPIO.setup(17,RPi.GPIO.OUT)
RPi.GPIO.setup(22,RPi.GPIO.OUT)
RPi.GPIO.setup(27,RPi.GPIO.OUT)
pwm0 = RPi.GPIO.PWM(17,80)
pwm1 = RPi.GPIO.PWM(22,80)
pwm2 = RPi.GPIO.PWM(27,80)

pwmNumAll = 50
pwmNum0 = pwmNum1 = pwmNum2 = 100

pwm0.start(round(pwmNum0*pwmNumAll)/100)
pwm1.start(round(pwmNum1*pwmNumAll)/100)
pwm2.start(round(pwmNum2*pwmNumAll)/100)

#ColorSet = [[1,1,1],[0,0,1],[0,1,0],[0,1,1],[1,0,0],[1,0,1],[1,1,0]]
ColorChange = [[0,-1,0],[0,0,-1],[0,1,1],[0,0,-1],[-1,0,0],[1,0,1],[-1,0,0],[0,-1,0],[1,1,0]]
color = 0


def main():
	host_addr = ("192.168.10.106",8888)
	print("Starting socket: TCP...")
	#create socket object:socket=socket.socket(family,type)
	socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("TCP server listen" )
	#bind socket to addr:socket.bind(address)
	socket_tcp.bind(host_addr)
	#listen connection request:socket.listen(backlog)
	socket_tcp.listen(1)
	#wait for PC:connection,address=socket.accept()
	socket_con, (client_ip, client_port) = socket_tcp.accept()
	print("Connection accepted from %s." %client_ip)
	socket_con.send("Welcome to Pi")
	print("Waiting Command...")

	while True:
		try:
			command=socket_con.recv(512).decode()
			if len(command)>0:
				print("Received:%s"%command)
				try:
					run(command)
				except  Exception:
					print("Invalid Command")
				time.sleep(1)
				continue
		except Exception:
			socket_tcp.close()
			sys.exit(1)

#Use received command to control LED
def run(command):
	if command == "Brightness Down":
		global pwmNumAll
		if pwmNumAll > 0:
			for i in xrange(pwmNumAll,pwmNumAll-10,-1):
				pwm0.ChangeDutyCycle(round(pwmNum0*i/100))
				pwm1.ChangeDutyCycle(round(pwmNum1*i/100))
				pwm2.ChangeDutyCycle(round(pwmNum2*i/100))
				time.sleep(0.1)
			pwmNumAll = pwmNumAll - 10
		print(pwmNumAll)
	elif command == "Brightness Up":
		global pwmNumAll
		if pwmNumAll < 100:
			for i in xrange(pwmNumAll,pwmNumAll+10,1):
				pwm0.ChangeDutyCycle(round(pwmNum0*i/100))
				pwm1.ChangeDutyCycle(round(pwmNum1*i/100))
				pwm2.ChangeDutyCycle(round(pwmNum2*i/100))
				time.sleep(0.1)
			pwmNumAll = pwmNumAll + 10
		print(pwmNumAll)
	elif command == "Color Left":
		global color, pwmNum0, pwmNum1, pwmNum2
		if (ColorChange[color][0] == -1 and pwmNum0 <= 0) or (ColorChange[color][0] == 1 and pwmNum0 >= 100)\
				or (ColorChange[color][1] == -1 and pwmNum1 <= 0) or (ColorChange[color][1] == 1 and pwmNum1 >= 100)\
				or (ColorChange[color][2] == -1 and pwmNum2 <= 0) or (ColorChange[color][2] == 1 and pwmNum2 >= 100):
			color = (color+1)%9
		else:
			for i in range(20):
				pwmNum0 += ColorChange[color][0]
				pwmNum1 += ColorChange[color][1]
				pwmNum2 += ColorChange[color][2]
				pwm0.ChangeDutyCycle(round(pwmNum0*pwmNumAll/100))
				pwm1.ChangeDutyCycle(round(pwmNum1*pwmNumAll/100))
				pwm2.ChangeDutyCycle(round(pwmNum2*pwmNumAll/100))
				time.sleep(0.05)
			print([pwmNum0,pwmNum1,pwmNum2])
	elif command == "Color Right":
		global color, pwmNum0, pwmNum1, pwmNum2
		if (ColorChange[color][0] == 1 and pwmNum0 <= 0) or (ColorChange[color][0] == -1 and pwmNum0 >= 100) \
				or (ColorChange[color][1] == 1 and pwmNum1 <= 0) or (ColorChange[color][1] == -1 and pwmNum1 >= 100) \
				or (ColorChange[color][2] == 1 and pwmNum2 <= 0) or (ColorChange[color][2] == -1 and pwmNum2 >= 100):
			color = (color - 1) % 9
		else:
			for i in range(50):
				pwmNum0 -= ColorChange[color][0]
				pwmNum1 -= ColorChange[color][1]
				pwmNum2 -= ColorChange[color][2]
				pwm0.ChangeDutyCycle(round(pwmNum0 * pwmNumAll / 100))
				pwm1.ChangeDutyCycle(round(pwmNum1 * pwmNumAll / 100))
				pwm2.ChangeDutyCycle(round(pwmNum2 * pwmNumAll / 100))
				time.sleep(0.05)
			print([pwmNum0, pwmNum1, pwmNum2])
		# global color
		# global pwm_num
		# color_new = (color+1)%7
		# print(color)
		# print(color_new)
		# print(ColorSet[color])
		# print(ColorSet[color_new])
		# if ColorSet[color][0] != ColorSet[color_new][0]:
		# 	if ColorSet[color_new][0]==0:
		# 		pwm0.stop()
		# 	else:
		# 		pwm0.start(pwm_num)
		# if ColorSet[color][1] != ColorSet[color_new][1]:
		# 	if ColorSet[color_new][1]==0:
		# 		pwm1.stop()
		# 	else:
		# 		pwm1.start(pwm_num)
		# if ColorSet[color][2] != ColorSet[color_new][2]:
		# 	if ColorSet[color_new][2]==0:
		# 		pwm2.stop()
		# 	else:
		# 		pwm2.start(pwm_num)
		# color = color_new

main()

