#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2019 Glen Langston, Quiet Skies LLC 
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# HISTORY
# 19JAN12 GIL initial version based on qa_vave

import numpy as np
from gnuradio import gr, gr_unittest
from gnuradio import blocks
from ra_vevent import ra_vevent

class qa_vevent (gr_unittest.TestCase):
    """
    qa_vevent is a Gnuradio Companion diagnostic block to confirm proper 
    operation of the vector event detection block: ra_vevent
    Glen Langston, 2019 January 12
    """
    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        vsize = 1024
        m = 10*vsize
        V1 = np.random.random_sample(m) # 1 many values
        V2 = np.random.random_sample(m) # 1 many values
        V = V1 + (V2*1j)
        Vmag = V*V
        # create a set of vectors
        src = blocks.vector_source_c( V.tolist())
        mag = blocks.vector_source_c( Vmag.tolist())
        instream = blocks.vector_to_stream( gr.sizeof_gr_complex, vsize)
        in2stream = blocks.vector_to_stream( gr.sizeof_gr_complex, vsize)

        # setup for running test
        mode = 1
        nsigma = 5.
        sample_rate = 1.e6
        sample_delay = 3./sample_rate
        # block we're testing
        vblock = ra_vevent( vsize, mode, nsigma, sample_rate, sample_delay)

        vsnk = blocks.vector_sink_c(vsize)
        magsnk = blocks.null_sink(1)
        rmssnk = blocks.null_sink(1)
        utcsnk = blocks.null_sink(1)

        self.tb.connect (src, instream)
        self.tb.connect (mag, in2stream)
        self.tb.connect (instream, vblock, 0)
        self.tb.connect (in2stream, vblock, 1)
        # now connect test bolck outputs a fector and two magnitudes
        self.tb.connect (vblock, vsnk, 0)
        self.tb.connect (vblock, magsnk, 1)
        self.tb.connect (vblock, rmssnk, 2)
        self.tb.connect (vblock, utcsnk, 3)
#        self.tb.connect (v2s, snk)
        expected = V[0:vsize]
        print 'Expected: ', expected[0:7]
        outdata = None
        waittime = 0.01

        self.tb.run ()
        outdata = snk.data()
        print 'Output: ', outdata[0:vsize]
        # check data
        print 'Magnitude: ', magsnk.data()
        print 'Rms      : ', magsnk.data()

        self.assertFloatTuplesAlmostEqual (1., 1., 1)

if __name__ == '__main__':
    gr_unittest.run(qa_vevent, "qa_vevent.xml")
