#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Calculate thermodynamic variables

This module was developed by CEMAC as part of the ACRoBEAR
project.

.. module:: thermo
   :synopsis: Calculate thermodynamic variables

.. moduleauthor:: Tamora D. James <t.d.james1@leeds.ac.uk>, CEMAC (UoL)

:copyright: © 2022 University of Leeds.
:license: BSD 3-clause (see LICENSE)

"""
# standard library imports
#import math

# third party imports
import numpy as np


def equ_pot(t, q, p):
    '''Calculate equivalent potential temperature (K).

    Parameters
    ----------

    t : float
        Temperature (K)

    q : float
        Specific humidity

    p : float
        Pressure (hPa)

    Returns
    -------
    float
        Equivalent potential temperature (K).

    '''

    if t <= 0:
        raise ValueError("Temperature value %d out of range" % (t,))
    
    if q < 0 or q >= 1:
        raise ValueError("Specific humidity value %d out of range" % (q,))

    if p <= 0:
        raise ValueError("Pressure value %d out of range" % (p,))
    
    # Convert specific humidity to mass mixing ratio (mass of water
    # divided by the mass of dry air in a given air parcel)
    z = q/(1.0-q)
    a = np.where(z < 1.0e-10, 1.0e-10, z)

    # Compute potential temperature
    ap = t*(1000./p)**(0.2854*(1.0-0.28*q))*np.exp(
        (
            3.376/(
                2840.0/(
                    3.5*np.log(t)-np.log(100.*p*a/(0.622+0.378*q))-0.1998
                )+55.0
            )-0.00254
        )*1.0e3*a*(1.0+0.81*q)
    )

    return ap
