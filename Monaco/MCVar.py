import numpy as np
from scipy.stats import rv_continuous, rv_discrete, describe
from Monaco.MCVal import MCInVal, MCOutVal
from Monaco.MCVarStat import MCVarStat
from copy import copy
from typing import Dict, List, Union, Any


### MCVar Base Class ###
class MCVar:
    def __init__(self, 
                 name           : str, 
                 ndraws         : int, 
                 firstcaseisnom : bool,
                 ):
        self.name = name 
        self.ndraws = ndraws 
        self.firstcaseisnom = firstcaseisnom
        
        self.ncases = ndraws + 1
        self.setFirstCaseNom(firstcaseisnom)
        self.vals = []
        self.valmap = None
        self.nums = []
        self.nummap = None
        self.size = None
        self.isscalar = None
        self.mcvarstats = []
        

    def setFirstCaseNom(self, 
                        firstcaseisnom : bool,
                        ):
        if firstcaseisnom:
           self.firstcaseisnom = True
           self.ncases = self.ndraws + 1
        else:
           self.firstcaseisnom = False
           self.ncases = self.ndraws


    def stats(self):
        stats = describe(self.nums)
        return stats
    
    
    def addVarStat(self, 
                   stattype   : str, 
                   statkwargs : Dict[str, Any]   = dict(), 
                   name       : Union[None, str] = None,
                   ):
        self.mcvarstats.append(MCVarStat(mcvar=self, stattype=stattype, statkwargs=statkwargs, name=name))


    def clearVarStats(self):
        self.mcvarstats = []


    def getVal(self, 
               ncase : int,
               ):
        raise NotImplementedError() # abstract method

    def getNom(self):
        raise NotImplementedError() # abstract method



### MCInVar Class ###
class MCInVar(MCVar):
    def __init__(self, 
                 name           : str, 
                 ndraws         : int, 
                 dist           : Union[rv_discrete, rv_continuous], 
                 distkwargs     : dict                        = dict(), 
                 nummap         : Union[None, Dict[int, Any]] = None,
                 seed           : int                         = np.random.get_state()[1][0], 
                 firstcaseisnom : bool                        = True,
                 ):
        super().__init__(name=name, ndraws=ndraws, firstcaseisnom=firstcaseisnom)
        self.dist = dist  
        self.distkwargs = distkwargs
        self.seed = seed 
        self.nummap = nummap 
        
        self.isscalar = True
        self.size = (1, 1)
        
        self.genValMap()
        self.draw()


    def mapNums(self):
        self.vals = copy(self.nums)
        if self.nummap is not None:
            for i in range(self.ncases):
                self.vals[i] = self.nummap[self.nums[i]]
            
            
    def genNumMap(self):
        if self.nummap is None:
            self.nummap = {val:num for num, val in self.nummap.items()}


    def genValMap(self):
        if self.nummap is None:
            self.valmap = None
        else:
            self.valmap = {val:num for num, val in self.nummap.items()}


    def setNDraws(self, 
                  ndraws : int,
                  ):
        self.ndraws = ndraws
        self.setFirstCaseNom(self.firstcaseisnom)
        self.draw()
        
        
    def draw(self):
        self.nums = []
        dist = self.dist(**self.distkwargs)

        if self.firstcaseisnom:
            self.ncases = self.ndraws + 1
            self.nums.append(self.getNom())
  
        self.nums.extend(dist.rvs(size=self.ndraws, random_state=self.seed).tolist())
        
        if any(np.isnan(num) for num in self.nums):
            raise ValueError(f'Invalid draw. Check distribution and parameters: {self.dist}, {self.distkwargs}')

        self.mapNums()


    def getNom(self):
        dist = self.dist(**self.distkwargs)
        ev = dist.expect()
        
        if isinstance(self.dist, rv_continuous):
            return ev

        # For a discrete distribution, we take the nearest discrete value closest to the expected value
        elif isinstance(self.dist, rv_discrete):
            eps = np.finfo(float).eps
            p = dist.cdf(ev)
            ev_candidates = dist.ppf([p - eps, p, p + eps])
            ev_candidates_dist = abs(ev_candidates - ev)
            ev_closest = ev_candidates[np.nanargmin(ev_candidates_dist)]
            return ev_closest
        
        else:
            return None


    def getVal(self, 
               ncase : int,
               ):
        isnom = False
        if (ncase == 0) and self.firstcaseisnom:
            isnom = True
            
        val = MCInVal(name=self.name, ncase=ncase, num=self.nums[ncase], dist=self.dist, nummap=self.nummap, isnom=isnom)
        return val



### MCOutVar Class ###
class MCOutVar(MCVar):
    def __init__(self, 
                 name           : str, 
                 vals           : List[Any], 
                 valmap         : Union[None, Dict[Any, int]] = None, 
                 ndraws         : Union[None, int]            = None, 
                 firstcaseisnom : bool                        = True,
                 ):
        if ndraws is None:
            ndraws = len(vals)
            if firstcaseisnom:
                ndraws = ndraws - 1
        
        super().__init__(name=name, ndraws=ndraws, firstcaseisnom=firstcaseisnom)
        self.vals = vals
        self.valmap = valmap
        if valmap is None:
            self.extractValMap()
        self.genSize()
        self.genNumMap()
        self.mapVals()


    def genSize(self):
        if isinstance(self.vals[0],(list, tuple, np.ndarray)):
            self.isscalar = False
            if isinstance(self.vals[0][0],(list, tuple, np.ndarray)):
                self.size = (len(self.vals[0]), len(self.vals[0][0]))
            else:
                self.size = (1, len(self.vals[0]))
        else:
            self.isscalar = True
            self.size = (1, 1)
            
    
    def extractValMap(self):
        Val0 = self.getVal(0)
        if Val0.valmap is not None:
            if Val0.valmapsource == 'auto':
                uniquevals = set()
                for i in range(self.ncases):
                    uniquevals.update(self.getVal(i).valmap.keys())
                self.valmap = dict()
                for i, val in enumerate(uniquevals):
                    self.valmap[val] = i
            else:
                self.valmap = Val0.valmap


    def genNumMap(self):
        if self.valmap is None:
            self.nummap = None
        else:
            self.nummap = {num:val for val, num in self.valmap.items()}


    def mapVals(self):
        self.nums = copy(self.vals)
        for i in range(self.ncases):
            self.nums[i] = self.getVal(i).num  


    def getVal(self, ncase):  # ncase is an integer
        isnom = False
        if (ncase == 0) and self.firstcaseisnom:
            isnom = True
            
        val = MCOutVal(name=self.name, ncase=ncase, val=self.vals[ncase], valmap=self.valmap, isnom=isnom)
        return val
        
    
    def getNom(self):
        val = None
        if self.firstcaseisnom:
            val = self.vals[0]            
        return val
    
    
    def split(self):
        mcvars = dict()
        if self.size[0] > 1:
            for i in range(self.size[0]):
                name = self.name + f' [{i}]'
                vals = []
                for j in range(self.ncases):
                    vals.append(self.vals[j][i])
                mcvars[name] = MCOutVar(name=name, vals=vals, ndraws=self.ndraws, \
                                        valmap=self.valmap, firstcaseisnom=self.firstcaseisnom)
                for mcvarstat in self.mcvarstats:
                    mcvars[name].addVarStat(stattype=mcvarstat.stattype, statkwargs=mcvarstat.statkwargs, name=mcvarstat.name)
        return mcvars



'''
### Test ###
if __name__ == '__main__':
    from scipy.stats import norm, randint
    generator = np.random.RandomState(74494861)
    invarseeds = generator.randint(0, 2**31-1, size=10)
    
    mcinvars = dict()
    mcinvars['randint'] = MCInVar('randint', ndraws=1000, dist=randint, distkwargs={'low':1, 'high':5}, seed=invarseeds[0])
    print(mcinvars['randint'].stats()) # expected: DescribeResult(nobs=1001, minmax=(1.0, 4.0), mean=2.5394605394605394, variance=1.2766913086913088, skewness=-0.056403119793934316, kurtosis=-1.382700726059828)
    mcinvars['norm'] = MCInVar('norm', ndraws=1000, dist=norm, distkwargs={'loc':10, 'scale':4}, seed=invarseeds[1])
    print(mcinvars['norm'].stats()) # expected: DescribeResult(nobs=1001, minmax=(-2.8212216855605874, 23.174036745569452), mean=9.984598648914597, variance=16.33843268728046, skewness=-0.07632259336623287, kurtosis=-0.19961999746619252)
    mcinvars['norm'].addVarStat(stattype='orderstatTI', statkwargs={'p':0.75, 'c':0.95, 'bound':'2-sided'})
    print(mcinvars['norm'].mcvarstats[0].vals) # expected: [ 4.97752429 14.93268084]
    xk = np.array([1, 5, 6])
    pk = np.ones(len(xk))/len(xk)
    custom = rv_discrete(name='custom', values=(xk, pk))
    mcinvars['custom'] = MCInVar('custom', ndraws=1000, dist=custom, distkwargs=dict(), seed=invarseeds[2])
    print(mcinvars['custom'].stats()) # expected: DescribeResult(nobs=1001, minmax=(1.0, 6.0), mean=4.105894105894106, variance=4.444775224775225, skewness=-0.7129149182621393, kurtosis=-1.3236396700106972)
    print(mcinvars['custom'].vals[1:10]) # expected: [5, 1, 1, 6, 6, 5, 5, 5, 5]
    print(mcinvars['custom'].getVal(0).val) # expected: 5.0
    mcinvars['map'] = MCInVar('map', ndraws=10, dist=custom, distkwargs=dict(), nummap={1:'a',5:'e',6:'f'}, seed=invarseeds[3])
    print(mcinvars['map'].vals) # expected: ['e', 'f', 'e', 'f', 'f', 'a', 'e', 'e', 'a', 'e', 'e']
    print(mcinvars['map'].stats()) # expected: DescribeResult(nobs=11, minmax=(1.0, 6.0), mean=4.545454545454546, variance=3.2727272727272734, skewness=-1.405456737852613, kurtosis=0.38611111111111107)
    
    mcoutvars = dict()
    mcoutvars['test'] = MCOutVar('test', [1, 0, 2, 2], firstcaseisnom=True)
    print(mcoutvars['test'].getVal(1).val) # expected: 0
    print(mcoutvars['test'].stats()) # expected: DescribeResult(nobs=4, minmax=(0, 2), mean=1.25, variance=0.9166666666666666, skewness=-0.49338220021815865, kurtosis=-1.371900826446281)
    
    v = np.array([[1,1],[2,2],[3,3]])
    mcoutvars['test2'] = MCOutVar('test2', [v, v, v, v, v])
    mcoutvars['test2'].addVarStat(stattype='orderstatTI', statkwargs={'p':0.33, 'c':0.50, 'bound':'1-sided'})
    mcoutvars.update(mcoutvars['test2'].split())
    print(mcoutvars['test2 [0]'].nums) # expected: [array([1, 1]), array([1, 1]), array([1, 1]), array([1, 1]), array([1, 1])]
    print(mcoutvars['test2 [0]'].mcvarstats[0].vals) # expected: [1. 1.]
#'''