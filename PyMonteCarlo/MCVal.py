import numpy as np
from itertools import chain
from copy import copy

### MCVal Base Class ###
class MCVal():
    def __init__(self, name, ncase, isnom):
        self.name = name    # name is a string
        self.ncase = ncase  # ncase is an integer
        self.isnom = isnom  # isnom is a boolean

        self.val = None
        self.valmap = None
        self.num = None
        self.nummap = None
        self.isscalar = None
        self.size = None



### MCInVal Class ###
class MCInVal(MCVal):
    def __init__(self, name, ncase, num, dist, nummap=None, isnom=False):
        super().__init__(name, ncase, isnom)
        self.dist = dist      # dist is a scipy.stats.rv_discrete or scipy.stats.rv_continuous
        self.num = num        # num is a scalar, list, or list of lists, all of which have numeric values
        self.nummap = nummap  # nummap is a dict
        self.isscalar = True
        self.size = (1, 1)
        
        self.mapNum()
        self.genValMap()


    def mapNum(self):
        if self.nummap == None:
            self.val = self.num
        elif self.isscalar:
            self.val = self.nummap[self.num]
        else:
            val = copy(self.num)
            if self.size[0] == 1:
                for i in range(self.num[1]):
                        val[i] = self.nummap[self.num[i]]
            else:
                for i in range(self.size[0]):
                    for j in range(self.size[1]):
                        val[i][j] = self.nummap[self.num[i][j]]
            self.val = val


    def genValMap(self):
        if self.nummap == None:
            self.valmap = None
        else:
            self.valmap = {val:num for num, val in self.nummap.items()}



### MCOutVal Class ###
class MCOutVal(MCVal):
    def __init__(self, name, ncase, val, valmap=None, isnom=False):
        super().__init__(name, ncase, isnom)
        self.val = val          # val can be anything
        self.valmap = valmap    # valmap is a dict
        
        if valmap == None:
            self.extractValMap()
            
        self.mapVal()
        self.genNumMap()


    def extractValMap(self):
        if isinstance(self.val,(list, tuple, np.ndarray)):
            self.isscalar = False
            if isinstance(self.val[0],(list, tuple, np.ndarray)):
                self.size = (len(self.val), len(self.val[0]))
                if all(isinstance(x, str) for x in chain(*self.val)):
                    self.valmap = {key:idx for idx, key in enumerate(set(chain(*self.val)))}
            else:
                self.size = (1, len(self.val))
                if all(isinstance(x, str) for x in self.val):
                    self.valmap = {key:idx for idx, key in enumerate(set(self.val))}
        else:
            self.isscalar = True
            self.size = (1, 1)
            if isinstance(self.val, str):
                self.valmap = {self.val:0}
                
                
    def mapVal(self):
        if self.valmap == None:
            self.num = self.val
        elif self.isscalar:
            self.num = self.valmap[self.val]
        else:
            num = copy(self.val)
            if self.size[0] == 1:
                for i in range(self.size[1]):
                        num[i] = self.valmap[self.val[i]]
            else:
                for i in range(self.size[0]):
                    for j in range(self.size[1]):
                        num[i][j] = self.valmap[self.val[i][j]]
            self.num = num


    def genNumMap(self):
        if self.valmap == None:
            self.nummap = None
        else:
            self.nummap = {num:val for val, num in self.valmap.items()}


    def split(self):
        mcvals = dict()
        if self.size[0] > 1:
            for i in range(self.size[0]):
                name = self.name + f' [{i}]'
                mcvals[name] = MCOutVal(name=name, ncase=self.ncase, val=self.val[i], valmap=self.valmap, isnom=self.isnom)
        return mcvals


'''
### Test ###
from scipy.stats import norm
a = MCInVal(name='Test', ncase=1, num=0, dist=norm, isnom=True)
print(a.val)
b = MCOutVal(name='Test', ncase=1, val=[[0,0],[0,0],[0,0]], isnom=True)
print(b.size)
print(b.val)
bsplit = b.split()
print(bsplit['Test [0]'].val)
c = MCOutVal(name='Test', ncase=1, val=[['a','a'],['b','b'],['a','b']], isnom=True)
print(c.valmap)
print(c.num)
#'''
