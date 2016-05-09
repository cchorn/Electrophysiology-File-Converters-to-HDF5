# this script is version 1.0, 5/8/2016
# Contributors: Charles Horn, David Rosenberg

# Use the "import2spike2" function
'''
importSpike2(filename, newfilename, gain, sample_rate, start_save, end_save, start_display, end_display)
Parameters:
filename = name of Spike2 file
newfilename = name of new HDF5 file
gain = amplification correction to convert to uV (this depends on your I/O setttings)
... ours is 50 = multiplication factor for 20K amp
........... 25 = multiplication factor for 10K amp
........... 12.5 = multipication factor for 5K amp
sample_rate = sampling rate in Hz
save_start = start time for saving data to file (sec)
save_end = end time for saving data to file (sec)
display_start = start time for displaying data in a plot (sec)
display_end = end time for displaying data in a plot (sec)
'''
# load modules
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import neo
# use a plotting style in the notebook that is similar to ggplot2, see http://ggplot2.org/
plt.style.use('ggplot')

def importSpike2(filename, newfilename, gain, sample_rate, save_start, save_end, display_start, display_end):
    # print todays date and time
    import time
    ## dd/mm/yyyy format
    print (time.strftime("%d/%m/%Y"))
    ## 12 hour format ##
    print (time.strftime("%I:%M:%S"))
    print '\n===================='
    # import a Spike2 file (CED)
    r= neo.Spike2IO(filename)
    bl = r.read()[0]
    asig = bl.segments[0].analogsignals[0]
    # keep the signal as a 16 bit float
    asig = np.float16(asig)
    asig = asig * gain
    datatype = asig.dtype
    pts = round(float(np.prod(asig.shape)), 0)
    secs = round(pts/sample_rate, 2)
    mins = round(secs/60.0, 2)
    hrs = round(mins/60, 3)
    print('{}:\n===================='.format(filename.split('/')[-1]))
    print('{} data points\n{} sec\n{} min\n{} hr\n20,000 Hz'.format(pts, secs, mins, hrs))
    print datatype
    # plot data
    fig, ax = plt.subplots(1, 1, figsize=(8, 3))
    asig_display = asig[display_start*sample_rate: display_end * sample_rate ]
    time = np.arange(display_start, display_end, 1.0/sample_rate)
    ax.plot(time, asig_display, 'b') #b = blue
    start = display_start * sample_rate
    end = display_end * sample_rate
    ax.set_xlabel('seconds', fontsize=12)
    ax.set_ylabel('microvolts', fontsize=12)
    plt.grid()
    plt.tight_layout()
    # save data to an HDF5 file type to share
    # first remove any previously created files from running this cell
    try:
        os.remove(newfilename)
    except OSError:
        pass
    # convert sec to pts using the sampling rate
    start1 = save_start * sample_rate
    end1 = save_end * sample_rate
    # create the new array
    new_asig = asig[start1:end1]
    # Write a new Block>Segment>AnalogSignal Hierarchy from the ground up
    # make a segment
    seg = neo.Segment()
    seg.name = 'New segment'
    seg.description = 'Sample'
    seg.index = 0
    seg.analogsignals = []
    seg.analogsignals.append(new_asig)
    # make a recording channel
    rec = neo.RecordingChannel()
    rec.analogsignals = []
    rec.analogsignals.append(new_asig)
    # make a recording channel group
    recg = neo.RecordingChannelGroup()
    recg.recordingchannels = []
    recg.recordingchannels.append(rec)
    recg.name = 'New group'
    # make a block ... finally!
    b = neo.Block()
    b.name = 'New block'
    b.segments = []
    b.segments.append(seg)
    b.recordingchannelgroups = []
    b.recordingchannelgroups.append(recg)
    # Write the block to a new HDF5 file:
    w = neo.io.NeoHdf5IO(newfilename)
    w.write_block(b)
    w.close()
    print '\n===================='
    print "wrote %s" % newfilename
