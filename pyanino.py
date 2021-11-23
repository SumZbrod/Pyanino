import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np

def relu(x):
    return x if x >= 0 else 0

def is_number(x):
    return isinstance(x, float) or isinstance(x, int)

class Sample():
    def __init__(self, K=0, time=None, Y=None, A1=440):
        '''
        K - number of note, or list of nums
        '''
        self.sr = 48000
        
        if time == None:
            if Y is not None:
                time = [0, Y.size/self.sr]
            else:
                time = (0, 1)
        elif is_number(time):
            time = (0, time)
        
        self.secs = time[1] - time[0]
        assert self.secs > 0, "finish time must be more then start"
        self.length = round(self.secs*self.sr)
        self.time = list(time)

        if Y is None:
            K = [K] if is_number(K) else K
            X = np.arange(self.length)/self.length
            Y = 0
            for k in K:
                Y += np.sin(2*np.pi*self.secs*X*A1*2**(k/12))
            self.Y = Y/len(K)
        else:
            self.Y = Y
            
    def __len__(self):
        return self.length

    def new(self, K=None, time=None, Y=None):
        if time == None:
            time = self.time
        if K == None:
            if Y is None:
                return Sample(Y=self.Y, time=time)
            else:
                return Sample(Y=Y, time=time)
        else:
            return Sample(K=K, time=time)

    def __repr__(self):
        T = np.linspace(*self.time, len(self))
        plt.plot(T, self.Y)
        plt.ylabel('Amplitude')
        plt.xlabel('time on seconds')
        return ''
    
    def __mul__(self, obj):
        new_self = self.new()
        if is_number(obj):
            new_self.Y *= obj
        return new_self
    
    def __rmul__(self, obj):
        return self * obj

    def __truediv__(self, obj):
        if is_number(obj):
            self *= 1/obj
        return self
    
    def __floordiv__(self, obj):
        if is_number(obj):
            self *= 1/obj
        return self

    def __add__(self, obj):
        
        A = self.new()
        if isinstance(obj, Sample):
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
        new_self = Sample(time=len(Y)/self.sr)
        new_self.Y = Y
        return new_self

    def play(self):
        sd.play(self.Y/10, self.sr)

    def stop(self):
        sd.stop()
    
    def to_track(self):
        return Track(sample=self)

class Track(Sample):
    def __init__(self, K=0, time=None, Y=None, A1=440, sample=None):
        if sample is not None:
            time = sample.time
            Y = sample.Y
        super().__init__(K=K, time=time, Y=Y, A1=A1)
        
    def apply(self, func):
        sample = self.copy()
        sample = func(sample.Y)
        new_self = Track(sample)
        new_self.sample = sample
        return new_self
    
    def normal(self, a=1):
        Y = self.Y.copy()
        X = np.linspace(*self.time, self.length)
        x_0 = sum(self.time)/2
        Y *= np.exp(-a*(X-x_0)**2)
        new_self = Track(time=self.time, Y=Y)
        return new_self
    
    def __add__(self, obj):
        if obj == 0:
            return self
        A = self.new()
        B =  obj.new()
        Y = np.concatenate((A.Y, B.Y))
        time_c = list(A.time)
        time_c[1] += sum(B.time)
        C = Track(time=time_c, Y=Y)
        return C

    def __radd__(self, obj):
        return self + obj

    def __rmul__(self, obj):
        new_self = self.new()
        int_l = int(obj//1)
        post_l = round((obj - int_l)*len(self))
        new_self.Y = np.tile(new_self.Y, int_l)
        new_self.Y = np.concatenate((new_self.Y, new_self.Y[:post_l]))
        new_time = list(new_self.time)
        time_delta = new_time[1] - new_time[0]
        new_time[1] += time_delta*(int_l-1)
        new_time[1] += post_l/new_self.sr
        return Track(time=new_time, Y=new_self.Y)

    def to_sample(self):
        return Sample(time=self.time, Y=self.Y)
        
    