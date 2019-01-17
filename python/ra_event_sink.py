#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Glen Langston, Quiet Skies <+YOU OR YOUR COMPANY+>.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# HISTORY
# 19JAN15 GIL initial version based on ra_ascii_sink

import os
import sys
import datetime
import numpy as np
from gnuradio import gr
import radioastronomy

try:
    import jdutil
except:
    print "jdutil is needed to compute Modified Julian Days"
    print "try:"
    print "git clone https://github.com/jiffyclub/jdutil.py"
    print ""
    print "Good Luck! -- Glen"

class ra_event_sink(gr.sync_block):
    """
    Write Event File.  The input
    1) Time Sequence (vector) of I/Q complex samples
    2) Event Modified Julian Date (complex, for precision)
    The real and imaginary parts of the MJD sum to the actual MJD.
    Precision is lost during optimization in gnuradio value transfers.
    Parameters are
    1) ConfigFileName
    2) Vector length in Channels
    3) Bandwidth (Hz)
    4) Record Flag
    This block is intended to reduce the downstream CPU load.
    """
    def __init__(self, noteName, vlen, bandwidth, record):
        gr.sync_block.__init__(self,
                               name="ra_event_sink",              
                               # inputs: time sequence of I,Q values,
                               # peak, rms, Event MJD
                               in_sig=[(np.complex64, int(vlen)),
                                       np.float32, np.float32, np.complex64],
                               out_sig=[np.float32], )
        vlen = int(vlen)
        self.vlen = vlen
        self.ecount = 1
        self.record = int(record)
        self.obs = radioastronomy.Spectrum()
        self.lastmjd = 0.
        self.setupdir = "./"
        noteParts = noteName.split('.')
        self.noteName = noteParts[0]+'.not'
        if len(noteParts) > 2:
            print '!!! Warning, unexpected Notes File name! '
            print '!!! Using file: ', self.noteName
        else:
            if os.path.isfile( self.noteName):
                print 'Setup File       : ', self.noteName
            else:
                if os.path.isfile( "Watch.not"):
                    try:
                        import shutil
                        shutil.copyfile( "Watch.not", self.noteName)
                        print "Created %s from file: Watch.not" % (self.noteName)
                    except:
                        pformat = "! Create the Note file %s, and try again !" 
                        print pformat % (self.noteName)
        self.obs.read_spec_ast(self.noteName)    # read the parameters
        self.obs.datadir = "../events/"          # writing events not spectra
        self.obs.noteB = "Event Detection"
        if not os.path.exists(self.obs.datadir):
            os.makedirs(self.obs.datadir)
        nd = len(self.obs.datadir)
        if self.obs.datadir[nd-1] != '/':
            self.obs.datadir = self.obs.datadir + "/"
            print 'DataDir          : ', self.obs.datadir
        self.obs.nSpec = 0             # not working with spectra
        self.obs.nChan = 0
        self.obs.nTime = 1             # working with time series
        self.obs.nSamples = vlen
        vlen2 = int(vlen/2)
        self.obs.refSample = vlen2 + 1 # event is in middle of time sequence
        self.obs.ydataA = np.zeros(vlen, dtype=np.complex64)
        self.obs.xdata = np.zeros(vlen)
        now = datetime.datetime.utcnow()
        self.eventutc = now
        self.obs.utc = now
        self.set_sample_rate( bandwidth)

    def forecast(self, noutput_items, ninput_items): #forcast is a no op
        """
        The work block always processes all inputs
        """
        ninput_items = noutput_items
        return ninput_items

    def set_sample_rate(self, bandwidth):
        bandwidth = np.float(bandwidth)
        if bandwidth == 0:
            print "Invalid Bandwidth: ", bandwidth
            return
        self.obs.bandwidthHz = bandwidth
        print "Setting Bandwidth: %10.0f Hz" % (self.obs.bandwidthHz)
        self.obs.dt = 1./np.fabs(self.obs.bandwidthHz)
        t = -self.obs.dt * self.obs.refSample
        for iii in range(self.vlen):
            self.obs.xdata[iii] = t
            t = t + self.obs.dt

    def set_setup(self, noteName):
        """
        Read the setup files and initialize all values
        """
        self.noteName = str(noteName)
        self.obs.read_spec_ast(self.noteName)    # read the parameters 
        self.obs.datadir = "../events/"          # writing events not spectra
        self.obs.nSpec = 0             # not working with spectra
        self.obs.nChan = 0
        self.obs.nTime = 1             # working with time series
        self.obs.refSample = vlen/2    # event is in middle of time sequence
        self.obs.nSamples = vlen
        self.obs.ydataA = np.zeros(vlen, dtype=np.complex64)
        self.obs.xdata = np.zeros(vlen)
        now = datetime.datetime.utcnow()
        self.eventutc = now
        self.obs.utc = now
        self.setupdir = "./"
        self.set_sample_rate( self.bandwidth)
    
    def set_record(self, record):
        """ 
        When changing record status, need to update counters
        """
        if record == radioastronomy.INTWAIT: 
            print "Stop  Recording  : "
            self.obs.writecount = 0
            self.ecount = 1
        # if changing state from recording to not recording
        elif self.record == radioastronomy.INTWAIT and record != radioastronomy.INTWAIT:
            print "Start Recording  : "
        self.record = int(record)

    def get_record(self):
        """
        return the recording state (WAIT, RECORD, SAVE)
        """
        return self.record

    def work(self, input_items, output_items):
        """
        Work averages all input vectors and outputs one vector for each N inputs
        """
        inn = input_items[0]    # vectors of I/Q (complex) samples
        peak = input_items[1]   # peak magnitudes of events
        rms  = input_items[2]   # rmss of samples near events
        mjd  = input_items[3]   # Modified Julian Dates of events (complex)
        
        # get the number of input vectors
        nv = len(inn)           # number of events in this port
        samples = inn[0]        # first input vector
        li = len(samples)       # length of first input vector
        t = 0

#        noutports = len(output_items)
#        if noutports != 1:
#            print '!!!!!!! Unexpected number of output ports: ', noutports
        counts = output_items[0]  # all vectors in PORT 0
        nout = 0
            
        iout = 0 # count the number of output vectors
        for i in range(nv):
            # get the length of one input
            samples = inn[i]
            peaks = peak[i]
            rmss = rms[i]
            # if same mjd as last time
            # on ra_event side days is truncated to 10ths of days 
            days = np.round(mjd[i].real * 10.)
            fdays = np.float(days)/10.
            hours = mjd[i].imag  # rest of days is in the hours part
            eventmjd = fdays + hours
            if eventmjd > self.lastmjd:
                self.lastmjd = eventmjd
                self.obs.samples = samples
                self.obs.nSamples = len(samples)
                utc = jdutil.mjd_to_datetime( eventmjd)
                self.obs.utc = utc
                # create file name from event time
                strnow = utc.isoformat()
                datestr = strnow.split('.')
                daypart = datestr[0]
                yymmdd = daypart[2:19]
                peak 
                print 'Sink Event: ', self.ecount
                print 'Sink Utc : ', self.obs.utc
                print 'Sink MJD : %12.6f' % (eventmjd)
#                print 'Sink days: %12.6f + %12.6f ' % (fdays, hours)
                print 'Sink Magnitude: ', peaks, ' +/- ', rmss
                if self.record == radioastronomy.INTRECORD:
                    #remove : from time
                    yymmdd = yymmdd.replace(":", "")
                    outname = yymmdd + '.eve'   # tag as an event
                    self.obs.writecount = self.obs.writecount + 1
                    # need to keep track of total number of spectra averaged
                    tempcount = self.obs.count
                    self.obs.write_ascii_file( self.obs.datadir, outname)
                    print('\a')  # ring the terminal bell
                self.ecount = self.ecount + 1
            # output latest event count
            counts[iout] = np.float(self.ecount)
            iout = iout+1
        if iout > 0:
            output_items[0] = counts
        return iout
    # end event_sink()


