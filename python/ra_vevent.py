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
# 19JAN08 GIL Initial version of vector version of event capture
# 18OCT12 GIL Initial version of event capture

import datetime
import numpy as np
from gnuradio import gr

EVENT_MONITOR = 1
EVENT_DETECT = 2
EVENT_WRITE = 3

class ra_vevent(gr.decim_block):
    """
    Event Capture of a data stream.  The Peak outlier and the RMS are returned.
    Write an event if the peak exceeds the number of sigma of RMS
    This is defined as: stdev = sqrt((sum_x2 / n) - (mean * mean))
    For RF signals the mean is zero, so the calculation is simplified.
    Input:
    1: Stream of complex I/Q samples
    2: vector length - number of complex samples to save
    3: mode - 1: monitor - 2: detect - 3: detect and write
    3: nsigma - Number of Sigma required to declare an event
    4: sample-rate - Hz
    5: configFileName - File describing the observing setup
    Output:
    Vector of complex samples - Latest data if no events
    Peak magnitude
    Sigma of latest detection.
    """
    def __init__(self, vlen, mode, nsigma, sample_rate, configFileName):
        """
        Initialize the event class, zero sample buffer
        """
        gr.decim_block.__init__(self, name="ra_event",
                                in_sig=[np.complex],   # in put samples 1 at a time
                                # output vector and  2 scalar values
                                out_sig=[(np.complex, int(vlen)),
                                         np.float32, np.float32],
                                decim=int(vlen))        
        self.vlen = int(vlen)
        self.vlen2 = int(vlen/2)
        self.mode = int(mode)
        self.nsigma = float(nsigma)
        self.nsigma2 = self.nsigma*self.nsigma
        self.sample_rate = float(sample_rate)
        # initialize event times
        self.values = np.zeros(self.vlen, dtype=np.complex)  # vector of data currently stored
        self.vevent = np.zeros(self.vlen, dtype=np.complex)# vector of last event found
        self.nin = 0     # counter for samples for outputting next vector (<= vlen)
        self.ecount = 0  # count of events detected so far
        if self.sample_rate < 1000.:
            print 'Invalid Sample Rate: ', self.sample_rate, ' Hz'
            exit()
        # compute time offset between current time and event
        self.dt = float(self.vlen2)/self.sample_rate
        self.dutc = datetime.timedelta(seconds=self.dt)
        self.eventutc = datetime.datetime.utcnow() - self.dutc
        print 'ra_event Vlen, Nsigma, dt: ', self.vlen, self.nsigma, self.dt
        if self.vlen < 16:
            print 'Not Enough samples (<16) to measure RMS: ', self.vlen
            exit()
        self.init_buffer()
        self.configFileName = str(configFileName)

    def init_buffer(self):
        """
        Initialize the circular buffer at start and after each event is detected
        """
        # define variables to keep track of the circular buffer
        self.n = int(0) # n is the number of samples in the circular buffer
        self.next = int(0) # next is where the next sample will be placed
        self.next2 = int(self.vlen2)  # next2 sample examined for an event
        # keep magnitudes
        self.values = np.zeros(self.vlen, dtype=np.complex)
        self.value2s = np.zeros(self.vlen, dtype=np.complex)
        self.rms = 0.
        self.rms2 = 0.
        self.rmssum = 0.
        self.oneovern = 1./float(self.vlen)
        self.full = False              # start with circular buffer empty
        self.ecount = 0

    def set_mode(self, mode):
        """ 
        Set the event detection mode: One of 
        EVENT_MONITOR: report magnitude and RMS of every vector of data
        EVENT_DETECT:  report only the magnitude and RMS of signficant events
        EVENT_WRITE:   Report and Write signficant Events
        """
        mode = int(mode)
        if (mode < EVENT_MONITOR) or (mode > EVENT_WRITE):
            print "Invalid Mode value: ", mode
            mode = EVENT_MONITOR
        self.mode = mode

    def set_nsigma(self, nsigma):
        """
        Set the Sigma detection threshold level
        """
        nsigma = float(nsigma)
        if nsigma < 1: 
            print "Invalid Nsigma value: ", nsigma
            nsigma = 7
            print "Using   Nsigma value: ", nsigma
        self.nsigma = nsigma
        self.nsigma2 = self.nsigma*self.nsigma

    def set_sampleRate(self, sample_rate):
        sample_rate = float(sample_rate)
        if sample_rate < 1000.:
            print "Invalid Sample Rate: ", sample_rate
            sample_rate = 1.E6
            print "Using   Sample Rate: ", sample_rate
        self.sample_rate = sample_rate
        self.dt = float(self.vlen2)/self.sample_rate

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
        print 'Utc event: ', self.utcevent, self.magnitude, ' +/- ', self.stddev
        print 'Magnitude: ', self.magnitude, ' +/- ', self.stddev

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
        mag2s = np.einsum('...i,...i', inn, inn)

        # get the number of input samples
        ns = len(inn)           # number of samples in this port

        noutports = len(output_items)
        if noutports != 3:
            print '!!!!!!! Unexpected number of output ports: ', noutports
        outa = output_items[0]  # all outputs in PORT 0
        outb = output_items[1]  # all outputs in PORT 1
        outc = output_items[2]  # all outputs in PORT 2
        nout = 0                # count number of output items

        # run through all input samples
        for j in range(ns):
            # if buffer is already full, must replace value with new
            if self.full:
                self.rmssum = self.rmssum - self.value2s[self.next]
                
            # record the new values (maybe on top of previous
            self.values[self.next] = inn[j]
            self.value2s[self.next] = mags[j]
            self.rmssum = self.rmssum + mags[j]

            # now handle circular buffer and detect full buffer
            self.next = self.next + 1
            # determine when buffer is full.  always write an event,
            # end cycling around the buffer
            if self.next >= self.vlen:
                self.full = True
                self.next = 0
                # only work with squares until event is found
                self.rms2 = self.rmssum2*self.oneovern

                # if no events yet or monitoring, output latest vector
                if self.ecount <= 0 or self.mode <= EVENT_MONITOR: 
                    self.vevent = self.values
                    self.emagnitude = np.sqrt(max( self.value2s))
                    self.erms = np.sqrt(rms2)
                    self.eventutc = datetime.datetime.utcnow() - self.dutc
                
                outa[nout] = self.vevent  # ouput vector of samples
                outb[nout] = self.emagnitude
                outc[nout] = self.erms
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
                    self.magnitude = np.sqrt(self.values2[self.next2])
                    self.stddev = np.sqrt(self.rms2)
                    # deal with circular buffer in centering output event:
                    iout = self.vlen2
                    iin = self.next2
                    self.eventutc = datetime.now() - dt
                    # must transfer an entire event, lenght vlen
                    for iii in range(self.vlen):
                        self.event[iout] = self.values[iin]
                        iout = iout + 1
                        iin = iin + 1
                        if iout >= self.vlen:
                            iout = 0
                        if iin >= self.vlen:
                            iin = 0
                    # if writing evevents
                    if self.mode >= EVENT_WRITE:
                        self.writeevent()  # record
                    self.ecount = self.ecount + 1   # keep event count
                    self.initbuffer()      # start again

        if nout > 0:
            output_items[0] = outa
            output_items[1] = outb
            output_items[2] = outc
        print 'N outputs: ', nout, self.rms2
        # end for all input samples
        
        return nout
    # end ra_event work()
