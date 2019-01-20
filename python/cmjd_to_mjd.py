"""
Class defining a Radio Frequency Spectrum
Includes reading and writing ascii files
HISTORY
19JAN20 GIL add function to return mjd, seconds, microseconds from cmjd
19JAN16 GIL add Event Reading and Writing
18MAY20 GIL code cleanup
18APR18 GIL add NAVE to save complete obsevering setup
18MAR10 GIL add labels for different integration types
18APR01 GIL add labels for different observing types
18MAR28 GIL merge in iplatlon with gnuradio companion upates
18MAR05 GIL add device parameter
18JAN25 GIL add all info included in the notes (.not) file
16JAN01 GIL initial version
"""

##################################################
# Imports
##################################################
import numpy as np

EPSILON = 0.0001
FACTOR = 100.

def mjd_to_cmjd( mjd):
    """
    mjd_to_cmjd breaks the Modified Julian Day into two parts:
    days+100ths of days -> real part of cmjd
    remainder of day   -> imag part of cmjd
    !!! HACK ALERT !!!
    """
    mjd = np.float(mjd)
    days = mjd*FACTOR               # add two digits to days
    idays = np.int(np.round(days,decimals=0))
    partdays = days - idays
    partdays = partdays/FACTOR        # fraction of days
    # floating point fraction
    # conver back to days
    days = np.round(np.float(idays)+EPSILON,decimals=0)/FACTOR 
    cmjd = days + partdays*1j# complex mjd for precision
    return cmjd
# end of mjd_to_cmjd

def print_cmjd( cmjd):
    """
    Diagnostic printout of complex MJD to full accuracy
    """
#    print 'cmjd: ', cmjd.real, cmjd.imag
    days = np.round(cmjd.real*FACTOR, decimals=0)
    idays = np.int(days)
    partdays = (days - idays)/FACTOR  # digits of fraction of a day
    partdays = partdays + cmjd.imag
    idays = idays / FACTOR
    if partdays > 1.:
        print 'cmjd Error: partdays: ',partdays, ' days: ', days
    seconds = partdays*86400.
    iseconds = np.int(seconds)
    microseconds = 1.E6 * (seconds-iseconds)
    print 'cmjd: %6d days + %5d s + %10.9f' % (idays, iseconds, microseconds)
    return

def cmjd_to_mjd_seconds_micro( cmjd):
    """
    Diagnostic printout of complex MJD to full accuracy
    """
#    print 'cmjd: ', cmjd.real, cmjd.imag
    mjd = cmjd_to_mjd( cmjd)
    imjd = np.int( mjd)
    partdays = (mjd - imjd)
    seconds = partdays*86400.
    iseconds = np.int(seconds)
    microseconds = 1.E6 * (seconds-iseconds)
    return (imjd, iseconds, microseconds)

def print_mjd( mjd):
    """
    Diagnostic printout of MJD to full accuracy
    """
    print '_mjd: %15.9f' % ( mjd)
    mjd = np.real(mjd)
    idays = np.int(mjd)
    partdays = mjd - idays
    if partdays >= 1. or partdays < 0.:
        print 'cmjd Error: partdays: ', partdays, ' days: ', days
    seconds = partdays * 86400.
    iseconds = np.int(seconds)
    microseconds = 1.E6 * (seconds-iseconds)
    print '_mjd: %6d days + %5d s + %15.9f' % (idays, iseconds, microseconds)
    return

    
def cmjd_to_mjd( cmjd):
    """
    cmjd_to_mjd combines the two parts of cmjd into Modified Julian Day
    days+100ths of days -> real part of cmjd
    remainder of day   -> imag part of cmjd
    !!! HACK ALERT !!!
    """
    # only accurate to digits
    days = (cmjd.real+EPSILON) * FACTOR
    days = np.round(days, decimals=0)
    idays = np.int(days)
    fdays = np.float(idays)/FACTOR
    partdays = cmjd.imag  # rest of days is in the hours part
    mjd = fdays + partdays
    return mjd

