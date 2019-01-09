#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2018 <+YOU OR YOUR COMPANY+>.
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

import numpy as np
from gnuradio import gr, gr_unittest
from gnuradio import blocks
from ra_event import *
import radioastronomy

class qa_ascii_sink (gr_unittest.TestCase):
    """
    qa_ascii_sink is a test function to confirm proper operation of
    the radio astronomy data recording block ascii_sink GRC block vmedian
    Glen Langston, 2018 April 19
    """

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        vsize = 2048
        # setup for random distribution of samples with zero mean
        mu = 0.
        sigma = 0.01
        nsigma = 3.
        vtest = vsize/8
        vreal = np.random.normal( mu, sigma, vsize)
        vimg = np.random.normal( mu, sigma, vsize)
        vcomplex = (1j*vimg) + vreal
        # create a set of vectors
        src = blocks.vector_source_c( vcomplex.tolist(), False)
        snk1 = blocks.stream_to_vector(gr.sizeof_float, vsize)
        snk2 = blocks.stream_to_vector(gr.sizeof_float, vsize)
        # parameters we're setting
        bandwidth = 6.E6
        setupFile = "Watch.not"
        eventblock = ra_event( vtest, nsigma, bandwidth, setupFile)

        self.tb.connect (src, eventblock)
        self.tb.connect (eventblock, snk1, 0)
        self.tb.connect (eventblock, snk2, 1)
        self.tb.run ()

if __name__ == '__main__':
    gr_unittest.run(qa_ascii_sink, "qa_ascii_sink.xml")
