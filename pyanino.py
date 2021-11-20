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
        if isinstance(time, float) or isinstance(time, int):
            time = (0, time)
        self.secs = time[1] - time[0]
        assert self.secs > 0, "finish time must be more then start"
        self.sr = 48000
        self.length = round(self.secs*self.sr)

        self.K = [K] if isinstance(K, int) else K
        self.time = list(time)
        self.A1 = 440
        self.X = np.arange(self.length)/self.length
        Y = 0
        for k in self.K:
            Y += np.sin(2*np.pi*self.secs*self.X*self.A1*2**(k/12))
        self.Y = Y/len(self.K)

    def new(self, K=None, time=None, Y=None):
        if K == None:
            K = self.K
        if time == None:
            time = self.time
        new_self = Track(K, time)
        if Y is not None:
            new_self.Y = Y
        return new_self

    def __repr__(self):
        T = np.linspace(*self.time, self.length)
        plt.plot(T, self.Y)
        plt.ylabel('Amplitude')
        plt.xlabel('time on seconds')
        return ''
    
    def __mul__(self, object):
        new_self = self.new()
        if isinstance(object, float) or isinstance(object, int):
            new_self.Y *= object
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
        A = self.new()
        if isinstance(obj, Track):
            B = obj.new()
            Dy_0 = np.zeros(self.sr*(relu(A.time[0]-B.time[0])))
            Dy_1 = np.zeros(self.sr*(relu(B.time[1]-A.time[1])))
            Dz_0 = np.zeros(self.sr*(relu(B.time[0]-A.time[0])))
            Dz_1 = np.zeros(self.sr*(relu(A.time[1]-B.time[1])))
            Y = np.concatenate((Dy_0, A.Y, Dy_1,))
            Z = np.concatenate((Dz_0, B.Y, Dz_1,))
            Y += Z
            all_time = (min(A.time[0], B.time[0]), max(A.time[1], B.time[1]))
            return self.new(time=all_time, Y=Y)
    
    def __getitem__(self, s):
        Y = self.Y.copy()
        Y = Y[s]
        new_self = Track(self.K, len(Y)/self.sr)
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
    
    def normal(self, a=1):
        Y = self.Y.copy()
        X = np.linspace(*self.time, self.length)
        x_0 = sum(self.time)/2
        Y *= np.exp(-a*(X-x_0)**2)
        new_self = Track(self.K, self.time)
        new_self.Y = Y
        return new_self