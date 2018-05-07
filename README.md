## gr-nsf
### Nsf-Integrate: library of Gnuradio Companion (GRC) blocks and Python code for Radio Astronomy

This repository contains relatively simple GRC blocks to improving averaging of
noisy radio astronomy spectra in a manner resistant to short term interference.

1. grc - directory of GRC xml files, which provide an iterface between GRC and the new python code

1. python - directory of python functions implimenting median filtering (with decimation) of spectra and observing interfaces.

1. examples - directoy of test GRC programs and the observing interface.

1. images - directory of images for documenting the code

Note that a data directory will be created when recording data.

### Observer Interface: NsfIntegrate60.grc

![Observer Interface](/images/IntegrateSpectralAlias2.png)

### Documentation

http://www.opensourceradiotelescopes.org/wk

Glen Langston -- glen.i.langston@gmail.com


