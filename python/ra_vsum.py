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
# 18SEP02 GIL Changed arguments to on Channels and Off CHannels
# 18AUG30 GIL Initial version after a number of pylint tests

import numpy as np
from gnuradio import gr

class ra_vsum(gr.sync_block):
    """
    Vector Summation.   Only two scalers are returned for vector input.
    The sums can be used to compute an on-signal and an off-signal, but
    the two ranges are calculated in the same manner.
    This block is intended to reduce the downstream CPU load.
    """
    def __init__(self, vlen, achannels, bchannels):
        gr.sync_block.__init__(self, name="ra_vave",
                               in_sig=[(np.float32, int(vlen))],   # in 1 spectrum
                               out_sig=[np.float32, np.float32])   # out 2 scalar values
        self.vlen = int(vlen)
        self.asum = 0.0
        self.bsum = 0.0
        self.achannels = int(achannels)
        self.bchannels = int(bchannels)
        self.anchan = len(self.achannels)
        self.bnchan = len(self.bchannels)
        na, indices = self.setIndices(self.achannels)
        self.aindices = indices
        self.oneoverna = 1./max(float(na, 1.))
        nb, indices = self.setIndices(self.bchannels)
        self.bindices = indices
        self.oneovernb = 1./max(float(nb, 1.))

    def setIndices(self, channels):
        """
        Set the channel ranges for intensity sums.  A number of options are defined
        1: A channel provided return that channel in output A and channel B contains (A-1 + A+1)/2.
        2: Two channels provided A1:A2: return average of range and DA = A2-A1
           Then B chan contains average of A1-DA:A1-1 and A2+1:A2+DA
        3: Three channels provided A1:A2, B1   - A contains average of A1:A2; B contains B1
        4: Four channels provided A1:A2, B1:B2 - A contains average of A1:A2; B average of B1:B2
        5: Five == 4
        6: Six channels provided A1:A2, B1:B2, C1:C2 - A contains average of A1:A2;
             B Contains average of B1:B2, C1:C2
        >6: 6
        """

        nchan = len(channels)
        nindices = 1
        if nchan <= 0:
            indices = self.vlen/2
        else:
            indices = channels[0]

        if nchan == 1:
            return nindices, indices

        i = 0
        # if here, then more than one channel
        a1 = channels[i]
        a2 = channels[1+1]
        da = a2 - a1
        # swap flippled indices
        if da < 0:
            temp = a1
            a1 = a2
            a2 = temp
        indices = np.arange(da) + a1
        if nchan == 3:
            print "Not an even number of channel ranges:", nchan
        return nindices, indices

    def setARange(self, channels):
        """
        Set the channel ranges for intensity sums.  A number of options are defined
        1: A channel provided return that channel in output A and channel B contains (A-1 + A+1)/2.
        2: Two channels provided A1:A2: return average of range and DA = A2-A1
           Then B chan contains average of A1-DA:A1-1 and A2+1:A2+DA
        3: Three channels provided A1:A2, B1   - A contains average of A1:A2; B contains B1
        4: Four channels provided A1:A2, B1:B2 - A contains average of A1:A2; B average of B1:B2
        5: Five == 4
        6: Six channels provided A1:A2, B1:B2, C1:C2 - A contains average of A1:A2;
             B Contains average of B1:B2, C1:C2
        >6: 6
        """
        nindices, indices = self.setIndices(channels)
        self.oneoverna = 1.0/max(float(nindices), 1.)
        self.aindices = indices

    def setBRange(self, channels):
        """
        Set the channel ranges for intensity sums.  A number of options are defined
        1: A channel provided return that channel in output A and channel B contains (A-1 + A+1)/2.
        2: Two channels provided A1:A2: return average of range and DA = A2-A1
           Then B chan contains average of A1-DA:A1-1 and A2+1:A2+DA
        3: Three channels provided A1:A2, B1   - A contains average of A1:A2; B contains B1
        4: Four channels provided A1:A2, B1:B2 - A contains average of A1:A2; B average of B1:B2
        5: Five == 4
        6: Six channels provided A1:A2, B1:B2, C1:C2 - A contains average of A1:A2;
             B Contains average of B1:B2, C1:C2
        >6: 6
        """
        nindices, indices = self.setIndices(channels)
        self.oneovernb = 1.0/max(float(nindices), 1.)
        self.bindices = indices

    def forecast(self, noutput_items, ninput_items):
        """
        Indicate the number of inputs required to get 1 output spectrum
        """
        noutput_items = ninput_items
        return noutput_items

    def work(self, input_items, output_items):
        """
        Work averages all input vectors and outputs one vector for each N inputs
        """
        inn = input_items[0]

        # get the number of input vectors
        nv = len(inn)          # number of vectors in this port
        ini = inn[0]           # first input vector

        noutports = len(output_items)
        if noutports != 2:
            print '!!!!!!! Unexpected number of output ports: ', noutports
        outa = output_items[0]  # all outputs in PORT 0
        outb = output_items[1]  # all outputs in PORT 1

        for i in range(nv):
            # get the length of one input
            ini = inn[i]
            # now save this vector until all are received
            a = ini[self.aindices].sum()*self.oneoverna
            b = ini[self.bindices].sum()*self.oneovernb
            outa[i] = a
            outb[i] = b
        # end for all input vectors
        output_items[0] = outa  # put all vectors in output port 0
        output_items[1] = outb  # put all vectors in output port 1
#        print 'N outputs: ', len(output_items[0]), iout
        return nv
    # end vsum()
