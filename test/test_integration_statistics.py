# test_integration_statistics.py

import pytest
from Monaco.integration_statistics import integration_error, integration_n_from_err, max_variance, max_stdev

def test_integration_error():
    assert integration_error([1, 0, 2], conf=0.95, samplemethod='random', runningError=False) == pytest.approx(1.1315857)
    assert integration_error([1, 0, 2], conf=0.95, samplemethod='random', runningError=True) == pytest.approx([1.1315857, 0.9799819, 1.1315857])
    assert integration_error([1, 0, 2], conf=0.95, dimension=1, samplemethod='sobol', runningError=False) == pytest.approx(0.7177468)
    assert integration_error([1, 0, 2], conf=0.95, dimension=1, samplemethod='sobol', runningError=True) == pytest.approx([0.7177468, 0.4803176, 0.7177468])


def test_integration_n_from_err():
    assert integration_n_from_err(error=0.01, volume=1, stdev=1, conf=0.95, samplemethod='random') == 38415
    assert integration_n_from_err(error=0.01, volume=1, dimension=1, stdev=1, conf=0.95, samplemethod='sobol') == 1424


def test_max_variance():
    assert max_variance(low=0, high=1) == pytest.approx(0.25)


def test_max_stdev():
    assert max_stdev(low=0, high=1) == pytest.approx(0.5)


### Inline Testing ###
# Can run here or copy into bottom of main file
#'''
if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt
    from Monaco.mc_sampling import mc_sampling

    print(integration_error([1, 0, 2], conf=0.95, samplemethod='random', runningError=False))                  # Expected: 1.1315857
    print(integration_error([1, 0, 2], conf=0.95, samplemethod='random', runningError=True))                   # Expected: [1.1315857, 0.9799819, 1.1315857]
    print(integration_error([1, 0, 2], conf=0.95, dimension=1, samplemethod='sobol', runningError=False))      # Expected: 0.7177468
    print(integration_error([1, 0, 2], conf=0.95, dimension=1, samplemethod='sobol', runningError=True))       # Expected: [0.7177468, 0.4803176, 0.7177468]
    print(integration_n_from_err(error=0.01, volume=1, dimension=1, stdev=1, conf=0.95, samplemethod='sobol')) # Expected: 1424
    print(integration_n_from_err(error=0.01, volume=1, stdev=1, conf=0.95, samplemethod='random'))             # Expected: 38415
    print(max_variance(low=0, high=1))  # Expected: 0.25
    print(max_stdev(low=0, high=1))     # Expected: 0.5
    
    n = int(2**15)
    conf = 0.95
    seed = 25106011
    midpoint = 1
    x1 = mc_sampling(ndraws=n, method='random', ninvar=1, seed=seed)*midpoint*2
    x2 = mc_sampling(ndraws=n, method='sobol', ninvar=1, seed=seed)*midpoint*2
    
    cummean1 = np.cumsum(x1)/np.arange(1 ,n+1)
    cummean2 = np.cumsum(x2)/np.arange(1 ,n+1)
    err1 = integration_error(x1, volume=1, conf=conf, samplemethod='random', runningError=True)
    err2 = integration_error(x2, volume=1, conf=conf, dimension=1, samplemethod='sobol', runningError=True)
    alpha = 0.85
    plt.figure()
    plt.hlines(midpoint, 0, n, 'k')
    h1, = plt.plot(cummean1, 'r', alpha=alpha)
    h3, = plt.plot(cummean1+err1, 'b', alpha=alpha)
    plt.plot(cummean1-err1, 'b', alpha=alpha)
    h2, = plt.plot(cummean2, 'darkred', alpha=alpha)
    h4, = plt.plot(cummean2+err2, 'darkblue', alpha=alpha)
    plt.plot(cummean2-err2, 'darkblue', alpha=alpha)
    plt.ylim((midpoint*0.975, midpoint*1.025))
    plt.ylabel(f'{round(conf*100, 2)}% Confidence Integration Bounds')
    plt.xlabel('Sample #')
    plt.legend([h3, h1, h4, h2], ['Random Error Bound', 'Random True Error', 'Sobol Error Bound', 'Sobol True Error'])
    
    plt.figure()
    h1, = plt.plot(np.abs(cummean1 - midpoint), 'r', alpha=alpha)
    h2, = plt.plot(np.abs(cummean2 - midpoint), 'darkred', alpha=alpha)
    h3, = plt.loglog(err1, 'b', alpha=alpha)
    h4, = plt.loglog(err2, 'darkblue', alpha=alpha)
    plt.ylabel(f'{round(conf*100, 2)}% Confidence Absolute Error')
    plt.xlabel('Sample #')
    plt.legend([h3, h1, h4, h2], ['Random Error Bound', 'Random True Error', 'Sobol Error Bound', 'Sobol True Error'])
    
#'''