"""
Event Detection, outputting a time sequence vector, centered on the event
Glen Langston (National Science Foundation)
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Quiet Skies LLC
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
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#
# History
# 19JAN13 GIL Working version of vector version of event capture
# 19JAN08 GIL Initial version of vector version of event capture
# 18OCT12 GIL Initial version of event capture

import datetime
import numpy as np
from gnuradio import gr
import copy
try:
    import jdutil
except:
    print "jdutil is needed to compute Modified Julian Days"
    print "try:"
    print "git clone https://github.com/jiffyclub/jdutil.py"
    print ""
    print "Good Luck! -- Glen"
    
EVENT_MONITOR = 1
EVENT_DETECT = 2

class ra_vevent(gr.decim_block):
    """
    Event Capture in a data stream.  The Peak magnitude of the outlier and 
    the RMS are returned along with a vector of samples centered on the evet.
    Detect an event if the peak exceeds the number of sigma of RMS
    Input:
    1: Stream of complex (I/Q) samples
    2: vector length - number of complex samples to save
    3: mode - 1: monitor - 2: detect
    3: nsigma - Number of Sigma required to declare an event
    4: sample-rate - Hz
    Output:
    1: Vector of complex samples - Latest data if no events yet
    2: Peak magnitude
    3: RMS of data with event
    4: Modified julian Date of Event
    Glen Langston - National Science Foundation - 2019 Januar 13
    """
    def __init__(self, vlen, mode, nsigma, sample_rate):
        """
        Initialize the event class, zero sample buffer
        """
        gr.decim_block.__init__(self, name="ra_vevent",
                                in_sig=[np.complex64],   # input I/Q pairs
                                # output vector and  3 scalar values
                                out_sig=[(np.complex64, int(vlen)),
                                         np.float32, np.float32, np.float32],
                                decim=int(vlen))        
        self.vlen = int(vlen)
        self.vlen2 = int(vlen/2)
        self.mode = int(mode)
        self.nsigma = float(nsigma)
        self.nsigma2 = self.nsigma*self.nsigma
        self.sample_rate = float(sample_rate)
        self.rmssum2 = 0.
        self.rms2 = 0.
        # initialize event times
        self.values = np.zeros(self.vlen, dtype=np.complex64)  # vector of data currently stored
        self.value2s = np.zeros(self.vlen)  # vector of data currently stored
        self.vevent = np.zeros(self.vlen, dtype=np.complex64)# vector of last event found
        self.nin = 0     # counter for samples for outputting next vector (<= vlen)
        self.ecount = np.int_(0)  # count of events detected so far
        if self.sample_rate < 1000.:
            print 'Invalid Sample Rate: ', self.sample_rate, ' Hz'
            exit()
        # compute time offset between current time and event
        self.dt = float(self.vlen2)/self.sample_rate
        self.dutc = datetime.timedelta(seconds=self.dt)
        self.eventutc = datetime.datetime.utcnow() - self.dutc
        self.eventmjd = jdutil.datetime_to_mjd(self.eventutc)
        self.emagnitude = 0.            # event magnitude
        self.erms = 0.                  # event RMS
        print 'ra_event Vlen, Nsigma, dt: ', self.vlen, self.nsigma, self.dt
        if self.vlen < 16:
            print 'Not Enough samples (<16) to measure RMS: ', self.vlen
            exit()
        self.init_buffer()

    def init_buffer(self):
        """
        Initialize the circular buffer at start and after each event is detected
        """
        # define variables to keep track of the circular buffer
        self.n = int(0) # n is the number of samples in the circular buffer
        self.next = int(0) # next is where the next sample will be placed
        self.next2 = int(self.vlen2)  # next2 sample examined for an event
        # keep magnitudes
        self.values = np.zeros(self.vlen, dtype=np.complex64)
        self.value2s = np.zeros(self.vlen)
        self.rms2 = 0.
        self.rmssum2 = 0.
        self.oneovern = 1./float(self.vlen)
        self.full = False              # start with circular buffer empty

    def set_mode(self, mode):
        """ 
        Set the event detection mode: One of 
        EVENT_MONITOR: report magnitude and RMS of every vector of data
        EVENT_DETECT:  report only the magnitude and RMS of signficant events
        """
        mode = int(mode)
        if (mode < EVENT_MONITOR) or (mode > EVENT_DETECT):
            print "Invalid Mode value: ", mode
            mode = EVENT_MONITOR
        self.mode = mode

    def set_nsigma(self, nsigma):
        """
        Set the Sigma detection threshold level
        """
        nsigma = float(nsigma)
        if nsigma < 0.1: 
            print "Invalid Nsigma value: ", nsigma
            nsigma = 5.
        self.nsigma = nsigma
        self.nsigma2 = self.nsigma*self.nsigma
        print "Using   Nsigma value: ", self.nsigma

    def set_sampleRate(self, sample_rate):
        sample_rate = float(sample_rate)
        if sample_rate < 1000.:
            print "Invalid Sample Rate: ", sample_rate
            sample_rate = 1.E6
            print "Using   Sample Rate: ", sample_rate
        self.sample_rate = sample_rate
        self.dt = float(self.vlen2)/self.sample_rate
        print "Using    Sample Rate: ", self.sample_rate

    def set_vlen(self, vlen):
        vlen = int(vlen)
        if vlen < 10:
            print "Invalid Vector Length: ", vlen
            vlen = 100
            print "Using   Vector Length: ", vlen
        self.vlen = vlen
        self.vlen2 = self.vlen/2
        self.oneovern = 1./float(self.vlen)
        self.dt = float(self.vlen2)/self.sample_rate
        self.init_buffer()

    def writeevent(self):
        """
        writeevent() writes an ascii file containing the observing setup
        and the data stream
        """
        print 'Utc event: ', self.eventutc
        print 'Magnitude: ', self.emagnitude, ' +/- ', self.erms

    def forecast(self, noutput_items, ninput_items):
        """
        forecast the number of spectra required to get an output
        """
        if noutput_items is None:
            ninput_items[0] = self.vlen
        else:
            for i in range(len(noutput_items)):
                ninput_items[i] = noutput_items[i]*self.vlen
        return ninput_items

    def work(self, input_items, output_items):
        """
        Work takes the input data and computes the average peak and RMS
        """
        inn = input_items[0]    # input complex samples
        # vector optimized magnitude calculator
        mag2s = inn.real**2 + inn.imag**2

        # get the number of input samples
        ns = len(inn)           # number of samples in this port

        noutports = len(output_items)
        if noutports != 4:
            print '!!!!!!! Unexpected number of output ports: ', noutports
        outa = output_items[0]  # all outputs in PORT 0
        outb = output_items[1]  # all outputs in PORT 1
        outc = output_items[2]  # all outputs in PORT 2
        outd = output_items[3]  # all outputs in PORT 3
        nout = 0                # count number of output items

        # run through all input samples
        for j in range(ns):
            # if buffer is already full, must replace value with new
            if self.full:
                self.rmssum2 = self.rmssum2 - self.value2s[self.next]
                
            # record the new values (maybe on top of previous
            self.values[self.next] = inn[j]
            self.value2s[self.next] = mag2s[j]
            self.rmssum2 = self.rmssum2 + mag2s[j]

            # now handle circular buffer and detect full buffer
            self.next = self.next + 1
            # determine when buffer is full.  always output an event,
            # end cycling around the buffer
            if self.next >= self.vlen:
                self.full = True
                self.next = 0
                # only work with squares until event is found
                self.rms2 = self.rmssum2*self.oneovern

                # if no events yet or monitoring, output latest vector
                if self.ecount <= 0 or self.mode <= EVENT_MONITOR: 
                    self.vevent = copy.deepcopy(self.values)
                    self.emagnitude = np.sqrt(max( self.value2s))
                    self.erms = np.sqrt(self.rms2)
                    self.eventutc = datetime.datetime.utcnow() - self.dutc
                    self.eventmjd = jdutil.datetime_to_mjd(self.eventutc)

                outa[nout] = self.vevent  # ouput vector of samples
                outb[nout] = self.emagnitude
                outc[nout] = self.erms
                outd[nout] = self.eventmjd
                nout = nout + 1

            # once vector is full, next2 is the place to look for the last event
            self.next2 = self.next2 + 1
            if self.next2 >= self.vlen:
                self.next2 = 0

            # only start detecting events if the buffer is full
            if self.full:
                # finally if full buffer and event found
                if self.value2s[self.next2] > (self.nsigma2*self.rms2):
                    # an event is found!
                    self.emagnitude = np.sqrt(self.value2s[self.next2])
                    self.erms = np.sqrt(self.rms2)
                    # deal with circular buffer in centering output event:
                    iout = self.vlen2
                    iin = self.next2
                    self.eventutc = datetime.datetime.utcnow() - self.dutc
                    self.eventmjd = jdutil.datetime_to_mjd(self.eventutc)

                    # must transfer an entire event, lenght vlen
                    for iii in range(self.vlen):
                        self.vevent[iout] = self.values[iin]
                        iout = iout + 1
                        iin = iin + 1
                        if iout >= self.vlen:
                            iout = 0
                        if iin >= self.vlen:
                            iin = 0
                    # if writing evevents
                    self.ecount = self.ecount + 1   # keep event count
                    print 'Event: ', self.ecount
                    print 'Utc event: ', self.eventutc
                    print 'Utc MJD  : ', self.eventmjd
                    print 'Magnitude: ', self.emagnitude, ' +/- ', self.erms
                    self.init_buffer()      # start again

        if nout > 0:
            output_items[0] = outa
            output_items[1] = outb
            output_items[2] = outc
            output_items[3] = outd
        # end for all input samples
        
        return nout
    # end ra_event work()
