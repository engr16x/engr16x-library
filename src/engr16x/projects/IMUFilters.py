# coding: utf-8
## @package MPU9250
#  This is a FaBo9Axis_MPU9250 library for the FaBo 9AXIS I2C Brick.
#
#  http://fabo.io/202.html
#
#  Released under APACHE LICENSE, VERSION 2.0
#
#  http://www.apache.org/licenses/
#
#  FaBo <info@fabo.io>
from MPU9250 import MPU9250
import numpy as np
import sys
import smbus
import time

#Function tries to find constant bias of the accel and gyro	
def AvgCali(mpu9250, depth,dly):
        #Utilize a for loop to gather out biases
        biases=[0.0,0.0,0.0,0.0,0.0,0.0]
        print("\nCalibrating IMU...\n")
        for x in range(depth):
            accel = mpu9250.readAccel()
            gyro = mpu9250.readGyro()
            #mag = mpu9250.readMagnet()
            biases[0]=biases[0]+accel['x']/depth;
            biases[1]=biases[1]+accel['y']/depth;
            biases[2]=biases[2]+accel['z']/depth;
            biases[3]=biases[3]+gyro['x']/depth;
            biases[4]=biases[4]+gyro['y']/depth;
            biases[5]=biases[5]+gyro['z']/depth;
            time.sleep(dly)
        print("Calibration Complete\n")
        return biases;

#The window will be a structure
#Element 0 will be the filtered output
#and then element 1 is the width
#Element 2 is the current spot in the window
#Element 3 is a sub-list that is the whole set of data
def genWindow(width,input):
        window=[input,width,0]
        temp=list()
        for x in range(width):
            temp.append(input)
        window.append(temp)
        return window;

#This function dynamically filters the incoming data (pull)
#by including it in the windowed set and then averaging that
#data to produce the filtered output. This filter will smooth
#out any spikes, but will also trail the actual output by several
#steps, usually the width of the window. Playing with the window
#width and the delay between data draws will tweak the output.
def WindowFilterDyn(window,dly,pull):
        #Pulling new data into window set
        window[3][window[2]]=pull

        #Producing new filtered output from window
        window[0]=sum(window[3])/window[1]

        #Updating the position in the window
        window[2]=window[2]+1
        if window[2] == window[1]:
            window[2]=0
        time.sleep(dly)
        return window;
    
def KalmanFilter(mpu9250,state,flter,dly):
        accel = mpu9250.readAccel()
        gyro = mpu9250.readGyro()
        #mag = mpu9250.readMagnet()
        temp=[accel['x'],accel['y'],accel['z'],gyro['x'],gyro['y'],gyro['z']]
        for x in range(6):
            #Setting up initial variables
            r=flter[x][0]
            q=flter[x][1]
            #Setting up state
            ex=state[1][x]
            p=state[0][x]+q
            #Applying filter criteria
            k=p/(p+r)
            ex=ex+k*(temp[x]-ex)
            p=(1-k)*p
            #Put values into state
            state[1][x]=ex
            state[0][x]=p
        time.sleep(dly)
        return state;


#This function calculates the standard deviations
#of the data from every axis given the inputs of the
#central biases, the IMU object, and the delay.
def FindSTD(biases,mpu9250,dly):
        print("\nInitializing Filters\n")
        #Setting up initial variables
        depth=99
        data=[[0],[0],[0],[0],[0],[0]]
        std=[0,0,0,0,0,0]
        #Gathering data to analyze
        for x in range(depth):
                accel = mpu9250.readAccel()
                gyro = mpu9250.readGyro()
                #mag = mpu9250.readMagnet()
                data[0].append(accel['x']-biases[0])
                data[1].append(accel['y']-biases[1])
                data[2].append(accel['z']-biases[2])
                data[3].append(gyro['x']-biases[3])
                data[4].append(gyro['y']-biases[4])
                data[5].append(gyro['z']-biases[5])
        #Breaking out data
        accelx=np.array(data[0],dtype=np.float)
        accely=np.array(data[1],dtype=np.float)
        accelz=np.array(data[2],dtype=np.float)
        gyrox=np.array(data[3],dtype=np.float)
        gyroy=np.array(data[4],dtype=np.float)
        gyroz=np.array(data[5],dtype=np.float)
        #Setting up for output
        std[0]=np.std(accelx)
        std[1]=np.std(accely)
        std[2]=np.std(accelz)
        std[3]=np.std(gyrox)
        std[4]=np.std(gyroy)
        std[5]=np.std(gyroz)
        print("\nFilters Initialized\n")
        return std;

#This function zeros out any value that is
#within a certain number of standard
#deviations away from zero
def InvGaussFilter(adv, value, bias, std, count):
        if value < count*std-bias and value > -count*std-bias:
                if adv:
                        value = bias
                else:
                        value = 0
        return value;
