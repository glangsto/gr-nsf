## Radio Astronomy Integrate Spectra tools built with/for Gnuradio Companion (GRC)

### These blocks are useful for Radio Astronomy Spectral Line Observations, particularly observations of our Milky Way Galaxy.

The GRC files are:

1. vectordemo.grc - Simple test block comparing the simulated data after averaging and medianing (no data source needed).

1. Integrate_test.grc - More complicated test function using all blocks in the NsfIntegrate Designs except
the *Osmosdr* block.

1. NsfIntegrate60.grc - Block configured to use an AIRSPY mini with 6.0 MHz bandwidth for Radio Astronomy Observations

1. NsfIntegrate20.grc - Block configured to use an RTL SDR dongle with 2.0 MHz bandwidth for Radio Astronomy Observations

The '*.ast' files contain example spectral line observations. 

The '*.hot' files contains hot-load calibration observations.  The NsfIntegrate blocks can overwrite these files.

The Watch.conf is a configuration file for the Nsf*.grc blocks

The Watch.not is a *Note File* describing the astronomical setup.  This file also contains a spectrum observation,
as the goal of the data header is to allow a complete re-observation, based on the previous header values.

### To test these blocks, without installing into the standard GRC path, use these commands:

`cd examples`

`export PYTHONPATH=../python:$PYTHONPATH`

and update your ~/.gnuradio/config.conf file with this path:

`local_blocks_path = ./:../grc:/usr/local/share/gnuradio/grc/blocks/`

Finally run the GRC files:

`gnuradio-companion vectordemo.grc`

or 

`gnuradio-companion NsfIntegrate60.grc`

### Example data, formated:

![Example Data Shown after an Observation](images/LightWork20Figure1.png)

Figure 1 of LightWork Memo 20: Overview of our place in the Milky Way Galaxy (Left) and 10 Minutes of Observations of the Perseus Arm. The sketch at left shows our Sun (and us) far from the center of the Milky Way. The image was drawn as if we are way above our galaxy. Our galaxy is a disk and the coordinate of the center of our galaxy is at Galactic Longitude = 0. The galactic longitude, latitude coordinates are centered on us. The plot at right shows 9 beautiful minutes of data. With some research, you can figure out that you’ve discovered the Perseus Arm of our Galaxy. The plot shows calibrated intensity (Kelvins) versus the velocity of the hydrogen measured. The observations were taken with telescope Azimuth=180 degrees, and different Elevations (A,E =). The GRC block calculates the Longitude and Latitude (L,L=) for the time of the observations (21:06 to 21:15 UTC).
 
### Documentation

http://www.opensourceradiotelescopes.org/wk

Glen Langston -- glen.i.langston@gmail.com

