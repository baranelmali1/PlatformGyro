import ctypes
import os
import time
import math
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial


def main():
    ser = serial.Serial('COM10', 115200, timeout=1) #Please specify here the derial port of the hardware, Example: COM10
    angles = np.ndarray((0,3))
    dllfilename = os.path.relpath('lib/amd64/vJoyInterface.dll')
    # http://stackoverflow.com/questions/252417/how-can-i-use-a-dll-file-from-python
    __vjoy = ctypes.cdll.LoadLibrary(dllfilename)

    joy = ctypes.c_uint(1)
    __vjoy.AcquireVJD(joy)
    
    Fs = 100; #samples
    stopTime = 10; #seconds
  #  roll = move(stopTime,1/7,25, Fs);  
  #  pitch = move(stopTime,1/10,10, Fs);  
    t = [];
    exRoll = [];
    exPitch =[];

    try:
        __vjoy.SetAxis(ctypes.c_long(int(5000)), joy, ctypes.c_uint(50)) #Give Throttle
        while 1:
            ln = ser.readline().decode('utf-8', errors='ignore').replace('\r\n','').split()
            print(ln)
            if len(ln) == 0:
                continue
            elif ln[0] == 'Send':
                ser.write(b'a')
                time.sleep(10)
                continue
            elif ln[0] != 'ypr':
                continue
            angs = [float(i) for i in ln[1:]]
            angles = np.concatenate((angles, [angs]))
            
            t.append(time.time());
            __vjoy.SetAxis(ctypes.c_long(val(angs[2])), joy, ctypes.c_uint(48)) #X Axis for Roll
            exRoll.append(val(angs[2]));
            __vjoy.SetAxis(ctypes.c_long(val(angs[1])), joy, ctypes.c_uint(49)) #Y Axis for Pitch
            exPitch.append(val(angs[1]));
#           line.set_ydata(exRoll[i])
#           line.set_xdata(t[i])# update the data
#           ani = animation.FuncAnimation(fig, animate, interval=100);
#           plt.show();

    except KeyboardInterrupt:
        __vjoy.SetAxis(ctypes.c_long(int(0)), joy, ctypes.c_uint(50)) #Reset Throttle
        __vjoy.RelinquishVJD(joy)
        t[:] = [x - min(t) for x in t];
        sio.savemat('data.mat', {'t':t, 'exRoll':exRoll, 'exPitch':exPitch, 'sensorAngles':angles})
        ser.close()
        
def val(angle):
    #16384 mid
    #0-32767 range
    y = math.radians(angle)
    return int((math.sin(y) + 1) * 16384)

def move(Duration, Frequency, angle, Fs):
    #Frequency: hertz, frequency of platform
    #angle    : max angle of platform  
                     
    dt = 1/Fs;                     # seconds per sample
    t = np.arange(0,Duration,dt);
                                         
    x = np.cos(2*math.pi*Frequency*t)*angle;
    # pyplot.plot(x)
    
    return np.round(16384 + 16384/90*x)
#    
#def animate(i):
#    return

#ani = animation.FuncAnimation(fig, animate, interval=1000)
#plt.show()
main()
