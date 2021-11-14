from scipy.stats import norm, uniform
from monaco.MCSim import MCSim
from monaco.mc_plot import mc_plot, mc_plot_cov_corr
import matplotlib.pyplot as plt
import numpy as np

from retirement_example_run import retirement_example_run
from retirement_example_preprocess import retirement_example_preprocess
from retirement_example_postprocess import retirement_example_postprocess
fcns ={'preprocess' :retirement_example_preprocess,   \
       'run'        :retirement_example_run,          \
       'postprocess':retirement_example_postprocess}

ndraws = 1024
seed=12362397

def retirement_example_monte_carlo_sim():

    sim = MCSim(name='retirement', ndraws=ndraws, fcns=fcns, firstcaseismedian=True, samplemethod='sobol_random', seed=seed, cores=4, savecasedata=False, verbose=True, debug=True)
    
    sp500_mean = 0.114
    sp500_stdev = 0.197
    inflation = 0.02
    nyears = 30
    
    for i in range(nyears):
        sim.addInVar(name=f'Year {i} Returns', dist=norm, distkwargs={'loc':(sp500_mean - inflation), 'scale':sp500_stdev})
    
    sim.addInVar(name='Beginning Balance', dist=uniform, distkwargs={'loc':1000000, 'scale':100000})
    sim.addConstVal(name='nyears', val=nyears)    
    
    sim.runSim()
    
    wentbrokecases = [i for i, e in enumerate(sim.mcoutvars['Went Broke'].vals) if e == 'Yes']
    
    mc_plot(sim.mcinvars['Year 0 Returns'], sim.mcoutvars['Final Balance'], highlight_cases=0, cov_plot=False)
    mc_plot(sim.mcoutvars['Went Broke'])
    mc_plot(sim.mcinvars['Beginning Balance'], highlight_cases=0)
    fix, ax = mc_plot(sim.mcoutvars['Date'], sim.mcoutvars['Ending Balance'], highlight_cases=wentbrokecases, title='Yearly Balances')
    ax.set_yscale('symlog')
    ax.set_ylim(bottom=1e4)
    
    sim.genCovarianceMatrix()
    plt.figure()
    yearly_return_broke_corr = []
    for i in range(nyears):
        yearly_return_broke_corr.append(sim.covs[sim.covvarlist.index('Went Broke')][sim.covvarlist.index(f'Year {i} Returns')])
    plt.plot(range(nyears), yearly_return_broke_corr, 'k')
    plt.plot(range(nyears), np.zeros(nyears), 'k--')
    plt.title('Correlation Between Yearly Return and Going Broke')
    plt.ylabel('Correlation Coeff')
    plt.xlabel('Year')

    return sim


if __name__ == '__main__':
    sim = retirement_example_monte_carlo_sim()
    