# integration_statistics.py

import numpy as np
from typing import Union
from Monaco.gaussian_statistics import pct2sig

def integration_error(isUnderCurve : Union[list[int], list[bool]],  # List of 0 and 1, or False and True values
                      volume       : float     = 1,  # By default, returns an unscaled error
                      runningError : bool      = False,
                      conf         : float     = 0.95,
                      ) -> Union[float, list[float]]:
    
    isUnderCurve = np.array([int(x) if x in [True, False] else x for x in isUnderCurve]) # Convert True and False to 1 and 0
    if set(isUnderCurve) - {0, 1} != set():
        raise ValueError('isUnderCurve must be a list of either all True/False, or 1/0')
    
    n = isUnderCurve.size
    if n == 1:
        error1sig = volume*1
    
    if not runningError:
        stdev = np.std(isUnderCurve, ddof=1)
        error1sig = volume*stdev/np.sqrt(n)
    
    else:
        cummean = np.cumsum(isUnderCurve)/np.arange(1 ,n+1)
        variances = (cummean - cummean**2)*n/(n-1) # Sample varaince eqn. which holds true only for values of only 0 and 1, where x == x**2
        stdevs = np.sqrt(variances)
        stdevs[stdevs == 0] = pct2sig(0.5) # Leading zeros will throw off plots, fill with reasonable dummy data
        error1sig = volume*stdevs/np.sqrt(np.arange(1, n+1))
    
    error = error1sig*pct2sig(conf)
    return error


def integration_n_from_err(error  : float,
                           volume : float,
                           conf   : float = 0.95,
                           stdev  : float = 1, 
                           ) -> int:
    # We generally do not know a-priori what the standard deviation will be, so
    # stdev defaults to 1 as the max for integration on {0,1}. If a better stdev
    # is computed on a lower number of cases, that can be subsituted in here to
    # bootleg a more efficient computation.
    # Note that sobol sampling should converge much faster than this, at a rate
    # of log(n)^d/n, rather than the 1/sqrt(n) given by random sampling. For 
    # sobol sampling, remember to round n to the next power of 2. 
    # helper_functions.next_power_of_2(n) can help with this 
    
    n = int(np.ceil((volume*conf*stdev/error)**2))
    
    return n
