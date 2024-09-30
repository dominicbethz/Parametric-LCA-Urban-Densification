#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 17:30:27 2024

@author: dominicbuettiker
"""

from typing import Dict, Optional, Union
import numpy as np
from scipy.stats import qmc #quasi monte carlo 
import warnings
import scipy as sp

"""
INPUT: Uncertianty dict: 
problem = {'sampling_technique':'sobol',
           'names': [List of all variable names],
           'bounds': [List of the bounds corresponding to the variables distributions, according to SALib convention],
           'dists':  [List of the distributions corresponding to the variables, according to SALib convention],
           }
N, size of sample
detailed specifications (seed, scramble)


RETURNS: 
Sampled Array based on specifications: columns are the problem parameters. N rows, size of sample
"""


"""SAMPLING TECHNIQUE"""

def sample(problem: Dict,
           N: int,
           scramble: bool = True,
           seed: Optional[Union[int, np.random.Generator]] = None):
    
    
    
    #Sanity checks: 
    if not (len(problem["names"]) == len(problem["bounds"]) == len(problem["dists"])):
       raise ValueError( "names, bounds and dists do not have the same lenght, check for missing entires")

        
    D = len(problem["names"])


    # Create base sequence - could be any type of sampling
    if problem["sampling_technique"]=='sobol':
        if np.log(N)/np.log(2)%1 !=0:
            raise ValueError("Sample size N must be in form of N = 2**n, else no guarantee for convergence of Sobol Sequences!")
            
        qrng = qmc.Sobol(d=D, scramble=scramble, seed=seed)
        base_sequence = qrng.random(N)
        scaled_sequence = base_sequence
        scaled_sequence = scale_samples(scaled_sequence, problem)
        
    elif problem["sampling_technique"]=='montecarlo':
        rng = np.random.default_rng()
        base_sequence = rng.random(size=(N, D))
        scaled_sequence = base_sequence
        scaled_sequence = scale_samples(scaled_sequence, problem)
    else: 
        raise ValueError(
            " qmc Sampling method not avaliable, check for spelling errors or choose a avaliable qmc sampling method. Available: 'sobol', monte carlo ")
        
    return scaled_sequence






"""SCALING of quasi montecarlo samples, to the desired distributions, based on 'A set of utility functions' of SALib, July 2024 """

def scale_samples(params: np.ndarray, problem: Dict):
    """Scale samples based on specified distribution (defaulting to uniform).

    Adds an entry to the problem specification to indicate samples have been
    scaled to maintain backwards compatibility (`sample_scaled`).

    Parameters
    ----------
    params : np.ndarray,
        numpy array of dimensions `num_params`-by-:math:`N`,
        where :math:`N` is the number of samples
    problem : dictionary,
        SALib problem specification

    Returns
    -------
    np.ndarray, scaled samples
    """
    bounds = problem["bounds"]
    dists = problem.get("dists")

    if params.shape[1] != len(dists):
        msg = "Mismatch in number of parameters and distributions.\n"
        msg += "Num parameters: {}".format(params.shape[1])
        msg += "Num distributions: {}".format(len(dists))
        raise ValueError(msg)

    params = _nonuniform_scale_samples(params, bounds, dists)

    problem["sample_scaled"] = True

    return params


def _nonuniform_scale_samples(params, bounds, dists):
    """Rescale samples in 0-to-1 range to other distributions

    Parameters
    ----------
    params : numpy.ndarray
        numpy array of dimensions num_params-by-N,
        where N is the number of samples
    dists : list
        list of distributions, one for each parameter
            unif: uniform with lower and upper bounds
            triang: triangular with lower and upper bounds, as well as
                    location of peak
                    The location of peak is in percentage of width
                    e.g. :code:`[1.0, 3.0, 0.5]` indicates 1.0 to 3.0 with a
                    peak at 2.0

                    A soon-to-be deprecated two-value format assumes the lower
                    bound to be 0
                    e.g. :code:`[3, 0.5]` assumes 0 to 3, with a peak at 1.5
            norm: normal distribution with mean and standard deviation
            truncnorm: truncated normal distribution with upper and lower
                    bounds, mean and standard deviation
            lognorm: lognormal with ln-space mean and standard deviation
    """
    b = np.array(bounds, dtype=object)

    # initializing matrix for converted values
    conv_params = np.empty_like(params)

    # loop over the parameters
    for i in range(conv_params.shape[1]):
        # setting first and second arguments for distributions
        b1 = b[i][0]  # ending
        b2 = b[i][1]  # 0-1

        if dists[i] == "triang":
            if len(b[i]) == 3:
                loc_start = b[i][0]  # loc start
                b1 = b[i][1]  # triangular distribution end
                b2 = b[i][2]  # 0-1 aka c (the peak)
            elif len(b[i]) == 2:
                msg = (
                    "Two-value format for triangular distributions detected.\n"
                    "To remove this message, specify the distribution start, "
                    "end, and peak (three values) "
                    "instead of the current two-value format "
                    "(distribution end and peak, with start assumed to be 0)\n"
                    "The two-value format will be deprecated in SALib v1.5"
                )
                warnings.warn(msg, DeprecationWarning, stacklevel=2)

                loc_start = 0
                b1 = b[i][0]
                b2 = b[i][1]
            else:
                raise ValueError(
                    "Unknown triangular distribution specification. Check"
                    " problem specification."
                )

            # checking for correct parameters
            if b1 < 0 or b2 < 0 or b2 >= 1 or loc_start > b1:
                raise ValueError(
                    """Triangular distribution bound error: Scale must be
                    greater than zero; peak on interval [0,1], triangular
                    start value must be smaller than end value"""
                )
            else:
                conv_params[:, i] = sp.stats.triang.ppf(
                    params[:, i], c=b2, scale=b1 - loc_start, loc=loc_start
                )

        elif dists[i] == "unif":
            if b1 >= b2:
                raise ValueError(
                    """Uniform distribution: lower bound
                    must be less than upper bound"""
                )
            else:
                conv_params[:, i] = params[:, i] * (b2 - b1) + b1

        elif dists[i] == "norm":
            if b2 <= 0:
                raise ValueError("""Normal distribution: stdev must be > 0""")
            else:
                conv_params[:, i] = sp.stats.norm.ppf(params[:, i], loc=b1, scale=b2)

        # Truncated normal distribution
        # parameters are lower bound and upper bound, mean and stdev
        elif dists[i] == "truncnorm":
            b3 = b[i][2]
            b4 = b[i][3]
            if b4 <= 0:
                raise ValueError(
                    """Truncated normal distribution: stdev must
                    be > 0"""
                )
            if b1 >= b2:
                raise ValueError(
                    """Truncated normal distribution: lower bound
                    must be less than upper bound"""
                )
            else:
                conv_params[:, i] = sp.stats.truncnorm.ppf(
                    params[:, i], (b1 - b3) / b4, (b2 - b3) / b4, loc=b3, scale=b4
                )

        # lognormal distribution (ln-space, not base-10)
        # paramters are ln-space mean and standard deviation
        elif dists[i] == "lognorm":
            # checking for valid parameters
            if b2 <= 0:
                raise ValueError("""Lognormal distribution: stdev must be > 0""")
            else:
                conv_params[:, i] = np.exp(
                    sp.stats.norm.ppf(params[:, i], loc=b1, scale=b2)
                )

        else:
            valid_dists = ["unif", "triang", "norm", "truncnorm", "lognorm"]
            raise ValueError("Distributions: choose one of %s" % ", ".join(valid_dists))

    return conv_params




    
    