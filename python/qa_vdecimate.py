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

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from vdecimate import *
import numpy as np

class qa_vdecimate (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        vectorsize = 1024L
        nave = 4L
        xin = numpy.zeros(vectorsize)
        xbig = numpy.zeros(vectorsize*nave)

        for iii in range(vectorsize):
            xin[iii] = float(iii)   
            xbig[iii] = float(iii)
            xbig[iii + vectorsize] = xbig[iii]
            xbig[iii + (2*vectorsize)] = xbig[iii]
            xbig[iii + (3*vectorsize)] = xbig[iii]

        expected_result = xin
        
        print "Raw input size", len(xbig)

        x = 10.0

        src = blocks.vector_source_f(xin, True, vectorsize)
        snk = blocks.vector_sink_f( vectorsize)
        print "In Test setup vector,n: ", vectorsize, nave
        x = raw_input('Enter a character to continue: ')
        vdec = vdecimate( vectorsize, nave)
        self.tb.connect( src, vdec)
        self.tb.connect( vdec, snk)
        self.tb.run ()
        # check data

        dout = 0
        while dout == 0:
            result_data = snk.data()
            dout = numpy.array(result_data)
            print 'Result data length:', len(dout)

        self.assertFloatTuplesAlmostEqual (expected_result, dout, 6)

if __name__ == '__main__':
    gr_unittest.run(qa_vdecimate, "qa_vdecimate.xml")
