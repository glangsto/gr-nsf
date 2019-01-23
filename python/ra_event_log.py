#!/usr/bin/env python
# This python program logs detected events, within the Gnuradio Companion environment
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
# 19JAN19 GIL initial version based on ra_event_sink

import os
import sys
import datetime
import numpy as np
from gnuradio import gr
import pmt

class ra_event_log(gr.sync_block):
    """
    Event Log writes a summary of detected events to a log file.  The input
    1) Peak of detected event
    2) RMS of samples near in time to detected event
    3) Event Modified Julian Date (complex, for precision)
    The real and imaginary parts of the MJD sum to the actual MJD.
    Precision is lost during optimization in gnuradio value transfers.
    Parameters are
    1) LogFileName
    2) Note on Purpose of event detection
    2) Vector length in Channels
    3) Bandwidth (Hz)
    This block is intended to reduce the downstream CPU load.
    """
    def __init__(self, logname, note, vlen, bandwidth):
        gr.sync_block.__init__(self,
                               name="ra_event_log",              
                               # inputs: 
                               # peak, rms, Event MJD
                               in_sig=[(np.complex64, int(vlen))],
                               # no outputs
                               out_sig=None, )
        vlen = int(vlen)
        self.vlen = vlen
        self.ecount = 0
        self.lastmjd = 0.
        self.bandwidth = bandwidth
        now = datetime.datetime.utcnow()
        self.startutc = now
        self.setupdir = "./"
        self.logname = str(logname)
        self.eventmjd = 0.
        self.emagnitude = 0.
        self.erms = 0.
        self.note = str(note)
        self.pformat = "%04d %15.9f %05d %10.3f %10.6f %10.6f\n" 
        self.set_note( note)          # should set all values before opening log file
        self.set_sample_rate( bandwidth)
        self.set_logname(logname)

    def forecast(self, noutput_items, ninput_items): #forcast is a no op
        """
        The work block always processes all inputs
        """
        ninput_items = noutput_items
        return ninput_items

    def set_sample_rate(self, bandwidth):
        """
        Set the sample rate to know the time resolution
        """
        bandwidth = np.float(bandwidth)
        if bandwidth == 0:
            print "Invalid Bandwidth: ", bandwidth
            return
        self.bandwidth = bandwidth
        print "Setting Bandwidth: %10.0f Hz" % (self.bandwidth)

    def get_sample_rate(self):
        """
        Return the sample rate to know the time resolution
        """
        return self.bandwidth

    def get_event_count(self):
        """
        Return the count of events so far logged
        """
        return self.ecount

    def set_logname(self, logname):
        """
        Read the setup files and initialize all values
        """
        logname = str(logname)
        if len(logname) < 1:   # if no log file name provided
            strnow = self.startutc.isoformat()
            datestr = strnow.split('.')  # get rid of fractions of a second
            daypart = datestr[0]         
            yymmdd = daypart[2:19]       # 2019-01-19T01:23:45 -> 19-01-19T01:23:45
            yymmdd = yymmdd.replace(":", "")  # -> 19-01-19T012345

            logname = "Event-%s.log" % (yymmdd)  # create from date
        self.logname = logname

        with open( self.logname, "w") as f:
            outline = "# Event Log Opened on %s\n" % (self.startutc.isoformat())
            f.write(outline)
            outline = "# %s\n" % (self.note)
            f.write(outline)
            outline = "# bandwidth = %15.6f\n" % (self.bandwidth)
            f.write(outline)
            outline = "# vlen      = %6d\n" % (self.vlen)
            f.write(outline)
            outline = "#  N      MJD       second  micro sec.    Peak       RMS\n"
            f.write(outline)
            f.close()
#        except:
#            print "!"
#            print "! Can not write to log file: %s" % (self.logname)
#            print "!"
#            continue

        return
    
    def set_note(self, note):
        """
        Update the note for the event log
        """
        self.note = str(note)
        return

    def work(self, input_items, output_items):
        """
        Work averages all input vectors and outputs one vector for each N inputs
        """
        inn = input_items[0]    # vectors of I/Q (complex) samples
        
        # get the number of input vectors
        nv = len(inn)           # number of events in this port
        
        # get the number of input vectors
        tags = self.get_tags_in_window(0, 0, +self.vlen, pmt.to_pmt('event'))
        if len(tags) > 0:
#            print 'Event Tags detected in sink: ', len(tags)
            for tag in tags:
#                print 'Tag: ', tag
                value = pmt.to_python(tag.value)
                if value[0] == 'MJD':
                    self.eventmjd = value[1]
#                    print 'Tag MJD : %15.9f' % (self.eventmjd)
                elif value[0] == 'PEAK':
                    self.emagnitude = value[1]
#                    print 'Tag PEAK: %7.4f' % (self.emagnitude)
                elif value[0] == 'RMS':
                    self.erms = value[1]
#                    print 'Tag RMs : %7.4f' % (self.erms)
                else:
                    print 'Unknown Tag: ', value
        # for all input events
        for i in range(nv):
            # get the length of one input
            # convert complex mjd into mjd
            # if same mjd as last time
            if self.eventmjd > self.lastmjd:
                self.ecount = self.ecount + 1
                print "\nEvent   Logged: %15.9f (MJD) %9.4f %8.4f" % (self.eventmjd, self.emagnitude, self.erms)
                imjd = np.int(self.eventmjd)
                seconds = (self.eventmjd - imjd)*86400.
                isecond = np.int(seconds)
                microseconds = (seconds - isecond) * 1.e6
                self.lastmjd = self.eventmjd
                outline = self.pformat % (self.ecount, self.eventmjd, isecond, microseconds, self.emagnitude, self.erms)
                try:
                    with open( self.logname, "a+") as f:
                        f.write(outline)
                        f.close()
                except:
                    continue
            # end for all input events
        return nv
    # end event_log()


