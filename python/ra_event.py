"""
Vector Sum channel ranges for radio astronomy
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
# 18OCT12 GIL Initial version of event capture
# 18SEP02 GIL Changed arguments to on Channels and Off CHannels
# 18AUG30 GIL Initial version after a number of pylint tests

import datetime
import numpy as np
from gnuradio import gr

class ra_event(gr.sync_block):
    """
    Event Capture of a data stream.  The Peak outlier and the RMS are returned.
    Write an event if the peak exceeds the number of sigma of RMS
    This is defined as: stdev = sqrt((sum_x2 / n) - (mean * mean))
    For RF signals the mean is zero, so the calculation is simplified.
    Input:
    Stream of complex I/Q samples
    Output:
    Peak magnitude^2
    SigmaSquared^
    """
    def __init__(self, vlen, nsigma, sampleRate, configFileName):
        """
        Initialize the event class, zero sample buffer
        """
        gr.sync_block.__init__(self, name="ra_event",
                               in_sig=[np.complex32],   # in 1 spectrum
                               out_sig=[np.float32, np.float32])   # out 2 scalar values
        self.vlen = int(vlen)
        self.vlen2 = int(vlen/2)
        self.nsigma = float( nsigma)
        self.nsigma2 = self.nsigma*self.nsigma
        self.sampleRate = float( sampleRate)
        if self.sampleRate < 10.:
            print 'Invalid Sample Rate: ',self.sampleRate, ' Hz' 
            exit()
        # compute time offset between current time and event
        self.dt = float(self.vlen2)/self.sampleRate
        print 'ra_event Vlen, Nsigma, dt: ',self.vlen, self.nsigma, self.dt
        if self.vlen < 16:
            print 'Not Enough samples (<16) to measure RMS: ', self.vlen
            exit()
        self.initBuffer( self.vlen)
        self.configFileName = str( configFileName)
            
    def initBuffer( self, vlen):
        """
        Initialize the circular buffer at start and after each event is detected
        """
        # define variables to keep track of the circular buffer
        self.n = int(0) # n is the number of samples in the circular buffer
        self.next = int(0) # next is where the next sample will be placed 
        self.next2 = int(self.vlen2)  # next2 sample examined for an event
        # keep magnitudes
        self.mags = np.zeros( vlen, dtype=np.complex)
        self.rmss = np.zeros( vlen, dtype=np.complex)
        self.ave = 0.
        self.rms = 0.
        self.sum = 0.
        self.sum2 = 0.
        self.oneovern = 1./float(vlen)
        self.full = False              # start with circular buffer empty
        self.event = False             # start assuming no events
        self.utcend = datetime.datetime.utcnow() 
        self.utcevent = self.utcend - self.dt
        self.utcstart = self.utcvent - self.dt

    def writeevent():
        """
        writeevent() writes an ascii file containing the observing setup
        and the data stream
        """
        self.utcend = datetime.datetime.utcnow() 
        self.utcevent = self.utcend - self.dt
        self.utcstart = self.utcvent - self.dt
        
    def forecast(self, noutput_items, ninput_items):
        """
        Indicate the number of inputs required to get 1 output spectrum
        """
        noutput_items = ninput_items
        return noutput_items

    def work(self, input_items, output_items):
        """
        Work takes the input data and computes the average peak and RMS
        """
        inn = input_items[0]

        # get the number of input samples
        ns = len(inn)          # number of samples in this port

        noutports = len(output_items)
        if noutports != 2:
            print '!!!!!!! Unexpected number of output ports: ', noutports
        outa = output_items[0]  # all outputs in PORT 0
        outb = output_items[1]  # all outputs in PORT 1

        # get the length of one input
        for j in range (ns):
            # if buffer is already full, must replace value with new
            if (self.full):
#                self.sum = self.sum - self.values[self.next]
                self.rmssum = self.rmssum - self.value2s[self.next]
                    
            # record the new values (maybe on top of previous
            v = inn[j]
            v2 = (v.real*v.real) + (v.imag*v.imag)
            self.values[self.next] = nd[j]
            self.value2s[self.next] = v2
#            self.sum = self.sum + nd[j]
            self.rmssum = self.rmssum + v2

            # now handle circular buffer and detect full buffer
            self.next = self.next + 1
            if self.next >= self.vlen:
                self.full = True
                self.next = 0

            # upate the check point index
            self.next2 = self.next2 + 1
            if self.next2 >= self.vlen:
                self.next2 = 0
                    
            if (self.full):
#                self.ave = self.sum*self.oneovern
                self.rms2 = self.rmssum*self.oneovern
#                self.rms = sqrt(self.rms2)

                # now store until all samples processed
                v2check = self.value2s[self.next2]
                outa[j] = v2check
                outb[j] = self.rms2
                # finally if full buffer and event found
                if v2check > self.nsigma2*self.rms2:
                    self.writeevent()      # record
                    self.initbuffer()      # start again
        # end for all input samples
        output_items[0] = outa  # put all vectors in output port 0
        output_items[1] = outb  # put all vectors in output port 1
#        print 'N outputs: ', len(output_items[0]), iout
        return ns
    # end vsum()