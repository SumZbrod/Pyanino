import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np

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
        if isinstance(obj, Track):
            self.Y += obj.Y
        return self
    
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

if __name__ == '__main__':
    C2 = Track(3 , time=(0, 3))
    E2 = Track(7 , time=(0, 3))
    G2 = Track(10, time=(0, 3))

    Y = (C2 + E2 + G2)/3
