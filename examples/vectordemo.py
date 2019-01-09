#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Vector averaging and median comparison
# Author: Glen Langston
# Description: This GRC demo compares the outputs of average and median with straght vector plotting
# Generated: Wed Jan  9 14:45:50 2019
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from optparse import OptionParser
import ra_vave
import ra_vmedian
import sip
import sys


class vectordemo(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Vector averaging and median comparison")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Vector averaging and median comparison")
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "vectordemo")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1e6
        self.fftsize = fftsize = 2048

        ##################################################
        # Blocks
        ##################################################
        self.ra_vmedian_0_2 = ra_vmedian.ra_vmedian(fftsize, 4)
        self.ra_vmedian_0_1 = ra_vmedian.ra_vmedian(fftsize, 4)
        self.ra_vmedian_0_0_1 = ra_vmedian.ra_vmedian(fftsize, 4)
        self.ra_vmedian_0_0 = ra_vmedian.ra_vmedian(fftsize, 4)
        self.ra_vmedian_0 = ra_vmedian.ra_vmedian(fftsize, 4)
        self.ra_vave_0_0 = ra_vave.ra_vave(fftsize, 4)
        self.ra_vave_0 = ra_vave.ra_vave(fftsize, 4)
        self.qtgui_vector_sink_f_0_0 = qtgui.vector_sink_f(
            fftsize,
            0,
            1.0,
            "x-Axis",
            "y-Axis",
            "",
            1 # Number of inputs
        )
        self.qtgui_vector_sink_f_0_0.set_update_time(0.5)
        self.qtgui_vector_sink_f_0_0.set_y_axis(0, 150)
        self.qtgui_vector_sink_f_0_0.enable_autoscale(False)
        self.qtgui_vector_sink_f_0_0.enable_grid(True)
        self.qtgui_vector_sink_f_0_0.set_x_axis_units("")
        self.qtgui_vector_sink_f_0_0.set_y_axis_units("")
        self.qtgui_vector_sink_f_0_0.set_ref_level(0)
        
        labels = ['One in 4', 'Average', 'Median', '', '',
                  '', '', '', '', '']
        widths = [1, 2, 2, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["black", "blue", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_vector_sink_f_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_vector_sink_f_0_0.set_line_label(i, labels[i])
            self.qtgui_vector_sink_f_0_0.set_line_width(i, widths[i])
            self.qtgui_vector_sink_f_0_0.set_line_color(i, colors[i])
            self.qtgui_vector_sink_f_0_0.set_line_alpha(i, alphas[i])
        
        self._qtgui_vector_sink_f_0_0_win = sip.wrapinstance(self.qtgui_vector_sink_f_0_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_vector_sink_f_0_0_win)
        self.qtgui_vector_sink_f_0 = qtgui.vector_sink_f(
            fftsize,
            0,
            1.0,
            "x-Axis",
            "y-Axis",
            "",
            3 # Number of inputs
        )
        self.qtgui_vector_sink_f_0.set_update_time(0.25)
        self.qtgui_vector_sink_f_0.set_y_axis(0, 150)
        self.qtgui_vector_sink_f_0.enable_autoscale(False)
        self.qtgui_vector_sink_f_0.enable_grid(True)
        self.qtgui_vector_sink_f_0.set_x_axis_units("")
        self.qtgui_vector_sink_f_0.set_y_axis_units("")
        self.qtgui_vector_sink_f_0.set_ref_level(0)
        
        labels = ['One in 4', 'Average', 'Median', '', '',
                  '', '', '', '', '']
        widths = [1, 2, 2, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["black", "blue", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(3):
            if len(labels[i]) == 0:
                self.qtgui_vector_sink_f_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_vector_sink_f_0.set_line_label(i, labels[i])
            self.qtgui_vector_sink_f_0.set_line_width(i, widths[i])
            self.qtgui_vector_sink_f_0.set_line_color(i, colors[i])
            self.qtgui_vector_sink_f_0.set_line_alpha(i, alphas[i])
        
        self._qtgui_vector_sink_f_0_win = sip.wrapinstance(self.qtgui_vector_sink_f_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_vector_sink_f_0_win)
        self.fft_vxx_0 = fft.fft_vcc(fftsize, True, (window.blackmanharris(fftsize)), False, 1)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_float*fftsize, samp_rate,True)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fftsize)
        self.blocks_keep_one_in_n_0_0 = blocks.keep_one_in_n(gr.sizeof_float*fftsize, 4)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_float*fftsize, 4)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(fftsize)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.blocks_add_const_vxx_0_1 = blocks.add_const_vff(([100.]*fftsize))
        self.blocks_add_const_vxx_0_0 = blocks.add_const_vff(([0.]*fftsize))
        self.blocks_add_const_vxx_0 = blocks.add_const_vff(([50.]*fftsize))
        self.analog_sig_source_x_0_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 2e5, .05, 0)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 3e5, .1, 0)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, 1, 0)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 2))    
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_add_xx_0, 0))    
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_add_xx_0, 1))    
        self.connect((self.blocks_add_const_vxx_0, 0), (self.qtgui_vector_sink_f_0, 1))    
        self.connect((self.blocks_add_const_vxx_0_0, 0), (self.qtgui_vector_sink_f_0, 2))    
        self.connect((self.blocks_add_const_vxx_0_1, 0), (self.qtgui_vector_sink_f_0, 0))    
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_stream_to_vector_0, 0))    
        self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_throttle_0, 0))    
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.blocks_keep_one_in_n_0_0, 0))    
        self.connect((self.blocks_keep_one_in_n_0_0, 0), (self.blocks_add_const_vxx_0_1, 0))    
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))    
        self.connect((self.blocks_throttle_0, 0), (self.blocks_keep_one_in_n_0, 0))    
        self.connect((self.blocks_throttle_0, 0), (self.ra_vave_0, 0))    
        self.connect((self.blocks_throttle_0, 0), (self.ra_vmedian_0, 0))    
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_0, 0))    
        self.connect((self.ra_vave_0, 0), (self.ra_vave_0_0, 0))    
        self.connect((self.ra_vave_0_0, 0), (self.blocks_add_const_vxx_0, 0))    
        self.connect((self.ra_vmedian_0, 0), (self.ra_vmedian_0_0, 0))    
        self.connect((self.ra_vmedian_0_0, 0), (self.blocks_add_const_vxx_0_0, 0))    
        self.connect((self.ra_vmedian_0_0, 0), (self.ra_vmedian_0_1, 0))    
        self.connect((self.ra_vmedian_0_0_1, 0), (self.qtgui_vector_sink_f_0_0, 0))    
        self.connect((self.ra_vmedian_0_1, 0), (self.ra_vmedian_0_2, 0))    
        self.connect((self.ra_vmedian_0_2, 0), (self.ra_vmedian_0_0_1, 0))    

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "vectordemo")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)

    def get_fftsize(self):
        return self.fftsize

    def set_fftsize(self, fftsize):
        self.fftsize = fftsize
        self.blocks_add_const_vxx_0_1.set_k(([100.]*self.fftsize))
        self.blocks_add_const_vxx_0_0.set_k(([0.]*self.fftsize))
        self.blocks_add_const_vxx_0.set_k(([50.]*self.fftsize))


def main(top_block_cls=vectordemo, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
