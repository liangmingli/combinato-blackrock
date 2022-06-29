# Combinato Spike Sorting -- with native Blackrock NSx files support! 

## version: alpha 1.0.  June 27 2022

## usage:  
python C:\Users\user\combinato\css-extract.py --ns5 --ns5_elec_start 193 --ns5_elec_end 200 --jobs test_ns5.txt --ns5jname [TaskName] --ns5file [NSxFileName]

## tricks:
when selecting subclusters, use keyboard, but not the mouse. Otherwise the selection index is off. (bug?)

edit options.py for raster_options and folder_patterns

raster_options= {'frame_name':'raster_test.csv','meta_prefix':'stimuli_images','T_PRE':1000,'T_POST':30000}

as folder_patterns, add in the prefix of your data folders.

## caveats:
if the NSx recordings are too long, it may crash the RAM. Currently still working to support reading segments or subset of electrodes from the whole data.

## complete commands for spike sorting
cd D:\datafolder
%spike detection
python C:\Users\user\combinato\css-extract.py --ns5 --ns5_elec_start 193 --ns5_elec_end 200 --jobs test_ns5.txt --ns5jname [TaskName] --ns5file [NSxFile]
 
% artifact rejection prior to sorting
python C:\Users\user\combinato\css-find-concurrent.py
python  C:\Users\user\combinato\css-mask-artifacts.py

% look at extracted spikes
python C:\Users\user\combinato\css-overview-gui.py
%save action to files, generate do_sort_neg.txt

% sort channels
python C:\Users\user\combinato\css-prepare-sorting.py --neg --jobs do_sort_neg.txt 
python C:\Users\user\combinato\css-cluster.py --jobs sort_neg_ml2.txt

% combine sessions
Python C:\Users\ml2866\combinato\css-combine.py --jobs sort_neg_ml2.txt --no-plots
Python C:\Users\ml2866\combinato\css-combine.py --jobs sort_neg_ml2.txt 

% prepare for manual clustering
copy do_sort_neg.txt do_manual_neg.txt

% inspect results
python C:\Users\ml2866\combinato\css-gui.py


## below are the original introduction.

Credits to Combinato by Johannes Niediek,  and NeoIO (https://github.com/NeuralEnsemble/python-neo)

## Introduction
_Combinato Spike Sorting_ is a software for spike extraction, automatic spike sorting, manual improvement of sorting, artifact rejection, and visualization of continuous recordings and spikes. It offers a toolchain that transforms raw data into single/multi-unit spike trains. The software is largely modular, thus useful also if you are interested in just extraction or just sorting of spikes.

Combinato Spike Sorting works very well with large raw data files (tested with 100-channel, 15-hour recordings, i.e. > 300 GB of raw data). Most parts make use of multiprocessing and scale well with tens of CPUs.

Combinato is a collection of a few command-line tools and two GUIs, written in Python and depending on a few standard modules. It is being developed mostly for Linux, but it works on Windows and OS X, too.

The documentation of Combinato is maintained as a [Wiki](../../wiki). 

## Installing Combinato
- [Installation on Linux](../../wiki/Installation-on-Linux) (recommended)
- [Installation on Windows](../../wiki/Installation-on-Windows)
- [Installation on OS X](../../wiki/Installation-on-OSX)

## Tutorial
Please walk through our instructive Tutorial.
- [Part I](../../wiki/Tutorial-Synthetic-Data)
- [Part II](../../wiki/Tutorial-Synthetic-Data-II)
- [Part III](../../wiki/Tutorial-Real-Data)

## More Information
- [FAQ](../../wiki/FAQ)
- [Details](../../wiki/Details)

## Citing Combinato 

When using Combinato in your work, please cite [this paper](http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0166598):

Johannes Niediek, Jan Boström, Christian E. Elger, Florian Mormann. „Reliable Analysis of Single-Unit Recordings from the Human Brain under Noisy Conditions: Tracking Neurons over Hours“. PLOS ONE 11 (12): e0166598. 2016. [doi:10.1371/journal.pone.0166598](doi:10.1371/journal.pone.0166598).

## Contact
Please feel free to use the GitHub infrastructure for questions, bug reports, feature requests, etc.

Johannes Niediek, 2016-2020, `jonied@posteo.de`.
