import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np
def relu(x):
    return x if x >= 0 else 0

class Track():
    def __init__(self, K=0, time=1):
        '''
        K - number of note, or list of nums
        '''
        self.secs = time[1] - time[0]
        assert self.secs > 0, "finish time must be more then start"
        self.sr = 48000
        self.length = self.secs*self.sr

        self.K = [K] if isinstance(K, int) else K
        self.time = list(time)
        self.A1 = 440
        self.X = np.arange(self.length)/self.length
        Y = 0
        for k in self.K:
            Y += np.sin(2*np.pi*self.secs*self.X*self.A1*2**(k/12))
        self.Y = Y/len(self.K)

    def __repr__(self):
        T = np.linspace(*self.time, self.length)
        plt.plot(T, self.Y)
        plt.ylabel('Amplitude')
        plt.xlabel('time on seconds')
        return ''
    
    def __mul__(self, object):
        Y = self.Y.copy()
        if isinstance(object, float) or isinstance(object, int):
            Y *= object
        new_self = Track(self.K, self.time)
        new_self.Y = Y
        return new_self
    
    def __rmul__(self, object):
        return self * object

    def __truediv__(self, obj):
        if isinstance(obj, float) or isinstance(obj, int):
            self *= 1/obj
        return self
    
    def __floordiv__(self, obj):
        if isinstance(obj, float) or isinstance(obj, int):
            self *= 1/obj
        return self

    def __add__(self, obj):
        Y = self.Y.copy()
        time_y = self.time.copy()
        if isinstance(obj, Track):
            Z = obj.Y.copy()
            time_z = obj.time.copy()
            Dy_0 = np.zeros(self.sr*(relu(time_y[0]-time_z[0])))
            Dy_1 = np.zeros(self.sr*(relu(time_z[1]-time_y[1])))
            Dz_0 = np.zeros(self.sr*(relu(time_z[0]-time_y[0])))
            Dz_1 = np.zeros(self.sr*(relu(time_y[1]-time_z[1])))
            Y = np.concatenate((Dy_0, Y, Dy_1,))
            Z = np.concatenate((Dz_0, Z, Dz_1,))
            Y += Z
            all_time = (min(time_y[0], time_z[0]), max(time_y[1], time_z[1]))
            new_self = Track(self.K, all_time)
            new_self.Y = Y
            return new_self
    
    def play(self):
        sd.play(self.Y/10, self.sr)

    def stop(self):
        sd.stop()

    def apply(self, func):
        Y = self.Y.copy()
        Y = func(Y)
        new_self = Track(self.K, self.time)
        new_self.Y = Y
        return new_self
    
    def normal(self, a):
        Y = self.Y.copy()
        X = np.linspace(*self.time, self.length)
        x_0 = sum(self.time)/2
        Y *= np.exp(-a*(X-x_0)**2)
        new_self = Track(self.K, self.time)
        new_self.Y = Y
        return new_self