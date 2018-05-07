## Example Radio Astronomy Integrate Spectra tools built with Gnuradio Companion (GRC)

### These blocks are useful for Radio Astronomy Spectral Line Observations, particularly observations of our Milky Way Galaxy.

The GRC files are:

1. vectordemo.grc - Simple test block comparing the simulated data before and after averaging and medianing.

1. Integrate_test.grc - More complicated test function using all blocks in the NsfIntegrate Designs except
the osmosdr block.

1. NsfIntegrate60.grc - Block configured to use an AIRSPY mini with 6.0 MHz bandwidth for Radio Astronomy Observations

1. NsfIntegrate20.grc - Block configured to use an RTL SDR dongle with 2.0 MHz bandwidth for Radio Astronomy Observations

The '*.ast' files contain example spectral line observations. 

The '*.hot' files contains hot-load calibration observations.  The NsfIntegrate blocks can overwrite these files.

The Watch.conf is a configuration file for the Nsf*.grc blocks

The Watch.not is a *Note File* describing the astronomical setup.  This file also contains a spectrum observation,
as the goal of the data header is to allow a complete re-observtion, based on the previous header values.

### To use these blocks, without installing into the standard GRC path, use these commands:

`cd examples`

`export PYTHONPATH=../python:$PYTHONPATH`

and update your ~/.gnuradio/config.conf file with this path:

`local_blocks_path = ./:../grc:/usr/local/share/gnuradio/grc/blocks/`

