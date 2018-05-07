Example Radio Astronomy Integrate Spectra tools built with Gnuradio Companion (GRC)

These blocks are useful for Radio Astronomy Spectral Line Observations,
particularly observations of our Mikly Way Galaxy.

The GRC files are:

vectordemo.grc - Simple test block comparing the simulated data before and after averaging.

Integrate_test.grc - More complicated test function using all blocks in the NsfIntegrate Designs except
the osmosdr block.

NsfIntegrate60.grc - Block configured to use an AIRSPY mini with 6.0 MHz bandwidth for Radio Astronomy Observations

NsfIntegrate20.grc - Block configured to use an RTL SDR dongle with 2.0 MHz bandwidht for Radio Astronomy Observations

The *.ast contain example spectra.
The *.hot file contains a hot-load calibration observation.  The Nsf* blocks can overwrite these files.

The Watch.conf is a configuration file for the Nsf*.grc blocks

The Watch.not is a Note file describing the astronomical setup.  This is also a spectrum observation,
as the goal of the data header was to allow a complete re-observtion based on the header values

To use these blocks, without installing into the standard GRC path, type:

export PYTHONPATH=../python:$PYTHONPATH

and update your ~/.gnuradio/config.conf file with this path:

[grc]

local_blocks_path = ./:../grc:/usr/local/share/gnuradio/grc/blocks/

