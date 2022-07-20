import mupif as mp
import numpy as np
import matplotlib.pyplot as plt
import typing
# use analytical field 
class AnalyticalField(object):
    func: typing.Callable[[float,float], float]
    def __init__(self, **kw):
        #super().__init__(**kw)
        print (kw.get('func')(3,2))
        self.func = kw['func']
        self.fieldID = kw['fieldID']
        self.unit=kw['unit']
        pass
    def evaluate(self, position, eps = 0.0):
        return mp.Quantity(value=(self.func(position[0], position[1]),), unit=self.unit)
    def plot2d (self, plane="xy", title=None, fieldComponent=0, warpField=None, warpScale=0., fileName=None, show=0, colorbar='horizontal'):
        x1_min = 0
        x1_max = 5
        x2_min = 0.0
        x2_max= 1.0
        x1,x2=np.meshgrid(np.arange(x1_min, x1_max, 0.1), np.arange(x2_min, x2_max, 0.1))
        y=self.func(x1,x2)
        plt.imshow(y, extent=[x1_min,x1_max,x2_min, x2_max], origin='lower')
        plt.colorbar()
        plt.show()
    def getFieldID(self):
        return self.fieldID
    def isInstance(self, classinfo: typing.Union[type, typing.Tuple[type, ...]]):
        if (classinfo == mp.Field):
            return True
        else:
            return False
