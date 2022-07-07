# JN 2017-04-07 adding scaling factor for matfiles
# JN 2020-03-06 Python3 compatibility


from __future__ import division, print_function, absolute_import
import os
from argparse import ArgumentParser, FileType
import tables
from .mp_extract import mp_extract
from .. import NcsFile
import numpy as np

def get_nrecs(filename):
    fid = NcsFile(filename)
    return fid.num_recs

def get_h5size(filename):
    fid = tables.open_file(filename, 'r')
    n = fid.root.h5data.shape[0]
    fid.close()
    return n


def main():
    """standard main function"""
    # standard options
    nWorkers = 5
    blocksize = 10000

    parser = ArgumentParser(prog='css-extract',
                            description='spike extraction from .ncs files',
                            epilog='Johannes Niediek (jonied@posteo.de)')
    parser.add_argument('--files', nargs='+',
                        help='.ncs files to be extracted')
    parser.add_argument('--start', type=int,
                        help='start index for extraction')
    parser.add_argument('--stop', type=int,
                        help='stop index for extraction')
    parser.add_argument('--jobs', nargs=1,
                        help='job file contains one filename per row')
    parser.add_argument('--matfile', nargs=1,
                        help='extract data from a matlab file')
    parser.add_argument('--h5', action='store_true', default=False,
                        help='assume that files are h5 files')
    parser.add_argument('--h5sr', nargs=1,
                        help='sample rate if not specified')
    parser.add_argument('--h5alignstart', action='store_true', default=False,
                        help='realign start values in mp_extract')
    parser.add_argument('--ns5', action='store_true', default=False,
                        help='boolean, whether ns5')
    parser.add_argument('--ns5jname',nargs=1,
                        help='task name for blackrock')
    parser.add_argument('--ns5file',nargs=1,
                        help='blackrock ns5 filename')
    parser.add_argument('--ns5_elec_start', nargs=1,
                        help='for blackrock ns5 files')
    parser.add_argument('--ns5_elec_end', nargs=1,
                        help='for blackrock ns5 files')
    parser.add_argument('--matfile-scale-factor', nargs='?', type=float,
                        help='rescale matfile data by this factor'
                             ' (to obtain microvolts)', default=1)
    parser.add_argument('--destination', nargs=1,
                        help='folder where spikes should be saved')
    parser.add_argument('--refscheme', nargs=1, type=FileType(mode='r'),
                        help='scheme for re-referencing')
    args = parser.parse_args()

    if ((args.files is None) and 
        (args.matfile is None) and 
        (args.jobs is None)):

        parser.print_help()
        print('Supply either files or jobs or matfile.')
        return

    if args.destination is not None:
        destination = args.destination[0]
    else:
        destination = ''

    # special case for a matlab file
    if args.matfile is not None:
        jname = os.path.splitext(os.path.basename(args.matfile[0]))[0]
        jobs = [{'name': jname,
                 'filename': args.matfile[0],
                 'is_matfile': True,
                 'count': 0,
                 'destination': destination,
                 'scale_factor': args.matfile_scale_factor}]
        mp_extract(jobs, 1)
        return


    if args.jobs:
        with open(args.jobs[0], 'r') as f:
            files = [a.strip() for a in f.readlines()]
        f.close()
    else:
        files = args.files

    if args.ns5: 
        jobs = []
        f = args.ns5file[0]
        start_elec = int(args.ns5_elec_start[0])
        end_elec = int(args.ns5_elec_end[0])+1 # include the last channel
        for ii in np.arange(start_elec,end_elec):
            jdict = {'name': args.ns5jname[0],
                    'filename': f,
                    'start_elec':start_elec,
                    'end_elec':end_elec,
                    'count': ii - start_elec,
                    'is_ns5': True,
                    'scale_factor': args.matfile_scale_factor,
                    'destination': destination}
            jobs.append(jdict)
        mp_extract(jobs, 1)
        return

    if args.h5:
        sr = int(args.h5sr[0])
        jobs = []
        h5alignstart = args.h5alignstart
        for f in files:
            if args.start:
                start = int(args.start)
            else:
                start = 0

            size = get_h5size(f)
            if args.stop:
                stop = int(args.stop)
                size = int(args.stop)
            else:
                stop = size

            starts = list(range(start, stop, sr*5*60))
            stops = starts[1:] + [size]
            name = os.path.splitext(os.path.basename(f))[0]

            for i in range(len(starts)):

                jdict = {'name': name,
                     'filename': f,
                     'start': starts[i],
                     'stop': stops[i],
                     'is_h5file': True,
                     'h5alignstart': h5alignstart,
                     'scale_factor': args.matfile_scale_factor,
                     'sr':sr,
                     'count': i,
                     'destination': destination}

                jobs.append(jdict)

        mp_extract(jobs, nWorkers)
        return


    if files[0] is None:
        print('Specify files!')
        return

    # construct the jobs
    jobs = []

    references = None
    if args.refscheme:
        import csv
        reader = csv.reader(args.refscheme[0], delimiter=';')
        references = {line[0]: line[1] for line in reader}

    for f in files:
        if args.start:
            start = args.start
        else:
            start = 0

        nrecs = get_nrecs(f)
        if args.stop:
            stop = min(args.stop, nrecs)
        else:
            stop = nrecs

        if stop % blocksize > blocksize/2:
            laststart = stop-blocksize
        else:
            laststart = stop

        starts = list(range(start, laststart, blocksize))
        stops = starts[1:] + [stop]
        name = os.path.splitext(os.path.basename(f))[0]
        if references is not None:
            reference = references[f]
            print('{} (re-referenced to {})'.format(f, reference))

        else:
            reference = None
            print(name)

        for i in range(len(starts)):
            jdict = {'name': name,
                     'filename': f,
                     'start': starts[i],
                     'stop': stops[i],
                     'count': i,
                     'destination': destination,
                     'reference': reference}

            jobs.append(jdict)


    mp_extract(jobs, nWorkers)
