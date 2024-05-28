#!/usr/bin/env python
import argparse
import numpy as np
import logging
import matplotlib.pyplot as plt
import os
from optparse import OptionParser
import glob
import sys
try:
  import python_antenna_pattern.config as config
  from python_antenna_pattern.core import AntennaPattern
  from python_antenna_pattern.core import read_name_list
except ModuleNotFoundError:
  import config
  from core import *
  
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] %(message)s')
formatter = logging.Formatter('[%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class Pyap:
    def __init__(self, file_list=''):
        self.single_file_flag = False
        #self.parser = OptionParser()
        self.arg_parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        self.arg_parser.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            dest='verbose',
            default=False,
            help='show extra diagnostic messages during execution'
        )
        self.arg_parser.add_argument(
            '-s',
            '--show-fig',
            action='store_true',
            dest='show_fig',
            default=False,
            help='show figure, pause after each figure is generated'
        )
        self.arg_parser.add_argument(
            '-g',
            '--show-legend',
            action='store_true',
            dest='show_legend',
            default=False,
            help='show legend'
        )
        self.arg_parser.add_argument(
            '-3',
            '--show-3db',
            action='store_true',
            dest='show_3db',
            default=False,
            help='show half-power line (max - 3dB)'
        )
        self.arg_parser.add_argument(
            '--show-name',
            action='store_true',
            dest='show_name',
            default=False,
            help='show NAME attribute in caption'
        )
        self.arg_parser.add_argument(
            type=str,
            dest='pattern',
            help=(
                'use specified file or a directory with planet files'
            )
        )
        self.arg_parser.add_argument(
            '-r',
            '--rotation-offset',
            type=int,
            dest='rotation_offset',
            default=0,
            help='rotational offset when plotting the polar pattern'
        )
        self.arg_parser.add_argument(
            '-f',
            '--filetype',
            choices=['pdf', 'eps', 'png'],
            dest='filetype',
            default='pdf',
            help='file type of the output figure, pdf or eps or png'
        )
        self.arg_parser.add_argument(
            '-n',
            '--file-name-prefix',
            type=str,
            dest='file_name_prefix',
            default='PYAP_',
            help='prefix of the generated filename'
        )
        self.arg_parser.add_argument(
            '--fontsize',
            type=int,
            dest='fontsize',
            default=12,
            help='font size for texts on the chart'
        )
        self.arg_parser.add_argument(
            '--size',
            type=int,
            dest='imagesize',
            default=8,
            help='image size in 100px units'
        )


    def polar_pattern(self, args):
        #from config import *
        # manually adjust parameters
        # import shlex
        # (options, args) = self.arg_parser.parse_args(shlex.split(arg_input))

        self.plot_pattern(args)


    def wrapper(self, argv):
        # (options, args) = self.arg_parser.parse_args()
        args = self.arg_parser.parse_args()
        if args.verbose is True:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        logger.debug('args is %s', args)
        self.plot_pattern(args)



    # TODO: use optparse to add options rather than using config.py
    def plot_pattern(self, options, save_file=True):

        fontsize = options.fontsize
        imagesize = options.imagesize
        file_name_prefix = options.file_name_prefix
        file_format = options.filetype
        show_name = options.show_name
        show_3db = options.show_3db
        plt.rc('font', size=fontsize)
        if not os.path.isfile(options.pattern):
            src_files = glob.glob(options.pattern)
            if len(src_files) == 0:
                print(
                    'No files in directory {}'.format(options.pattern),
                    file=sys.stderr
                )
                sys.exit(os.EX_NOTFOUND)
            else:
                print('Files to be converted: {}'.format(src_files))

        elif os.path.isfile(options.pattern):
            print('Converting file {}'.format(options.pattern))
            src_files = [options.pattern, ]
        else:
            print('Cannot find file or directory {}'.format(options.pattern))
            sys.exit(70) # os.EX_SOFTWARE available only on UNIX platforms.


        degree = np.arange(0, 361, 1) # Set indexes 0..360 to draw 359-0
        theta = degree*2*np.pi/360
        p_list = []
        dir_path = []
        band = []
        name = []
        gain = []
        # TODO: syncup cli args and these configs. or at least be able to pass
        # the config file
        clipping = config.MAX_GAIN_CLIPPING
        tick_start = config.TICK_START
        tick_stop = config.TICK_STOP
        tick_spacing = config.TICK_SPACING
        line_width = config.LINE_WIDTH
        rlim_shift = config.RLIM_SHIFT
        gain_ticks_position = config.TICK_POSITION # good with 45 also

        if len(src_files) > 2:
            print(
                'PYAP currently does not support more than a pair of files at once',
                file=sys.stderr
            )
            sys.exit(70) # os.EX_SOFTWARE available only on UNIX platforms.

        if len(src_files) < 2:
            self.single_file_flag = True

        for file_path_original in src_files:
            file_path = file_path_original.replace('\\', '/')
            antenna_pattern = AntennaPattern()
            # parse the antenna gains by cut or by antenna
            antenna_pattern.parse_data(file_path) # config.PARSE_BY
            split_name = file_path.rsplit('/')
            file_name = split_name[-1]
            print('processing {}'.format(file_name))
            # temp now is a dictionary of the two antenna pattern in a file
            p_list.append(antenna_pattern)

            #b = parse_freq_band(file_name)
            band.append(antenna_pattern.frequency)
            name.append(antenna_pattern.name)
            gain.append(antenna_pattern.max_gain_db)
            # all but last element in the list
            dir_path.append('/'.join(split_name[0:-1]) + '/')

        if len(band) > 1:
            print('Frequency band list: {}'.format(band), file=sys.stderr)
            if band[0] != band[1]:
                print(
                    'Frequency band not match: {}'.format(band),
                    file=sys.stderr
                )
                sys.exit(70) # os.EX_SOFTWARE available only on UNIX platforms.

        max_gain_db_slist = []
        rho = {}
        counter = 0
        max_list = []

        for pval in p_list:

            if len(pval.pattern_dict.keys()) != 2:
                print('Invalid antenna pattern was loaded from ' + pval.file, file=sys.stderr)
                sys.exit(70) # os.EX_SOFTWARE available only on UNIX platforms.

            # in python 3.x keys() return a set-like object
            labels = list(pval.pattern_dict.keys())
            # clip the small values here
            for i in range(0, 360):
                # clip the horizontal and the vertical vectors
                for key in labels:
                    if pval.pattern_dict[key][i] > clipping:
                        pval.pattern_dict[key][i] = clipping

            # the vertical/horizontal antenna patterns across two files, i.e.,
            # two antennas, are aggregated here the way we aggregate is that
            # the vertial antenna pattern for the first file, is in rho[0:360]
            # and the antenna pattern for the second file is in rho[360:720],
            # and so on. Number of antenna to consider
            for key in list(pval.pattern_dict.keys()):
                if key in rho:
                    rho[key] = np.append(
                        rho[key],
                        pval.max_gain_db - np.asarray(pval.pattern_dict[key]) if config.ABSOLUTE_FLAG is True else -np.asarray(pval.pattern_dict[key])
                    )
                # initialize rho dictionary as empty lists
                else:
                    rho[key] = (
                        pval.max_gain_db - np.asarray(pval.pattern_dict[key]) if config.ABSOLUTE_FLAG is True else -np.asarray(pval.pattern_dict[key])
                    )

        for key in list(pval.pattern_dict.keys()):
            max_value = max(rho[key]) 
            max_gain_db = gain[0]
            max_list.append(max_gain_db)
            max_gain_db_str = 'Peak Gain: {:.2f} dBi'.format(max_gain_db)
            max_gain_db_slist.append(max_gain_db_str)
            fig = plt.figure(figsize=(imagesize, imagesize))
            plot_title = (
                ((name[0] + '\n') if show_name else '') + 'Frequency: ' + str(band[0]) + ' MHz. ' + max_gain_db_str
            )
            fig.suptitle(plot_title)
            ax = plt.subplot(111, polar=True, projection='polar')
            ax.set_rlim(min(min(rho[key]),config.TICK_START), max(max(rho[key]), config.TICK_STOP) + rlim_shift)
            # set where the zero location is
            ax.set_theta_zero_location('N')
            # set the angle to be increasing clockwise or counterclockwise
            ax.set_theta_direction(-1)
            ax.tick_params(axis='y', which='major', labelrotation=-gain_ticks_position)
            # set ticks position
            ax.set_rlabel_position(gain_ticks_position)

            # long/right antenna is always red, and is always in second file
            temp0 = np.full(361, max_value-3)
            temp1 = rho[key][360:720]
            temp2 = rho[key][0:360]
            buf1 = [0]*360
            buf2 = [0]*360

            # a hack for C250 planet files where the angle is rotated by 90
            # degree
            if key == 'horizontal' and config.C250_FLAG is True:
                rotation_offset = config.C250_ROTATION_OFFSET
                for l in range(0, 360):
                    buf2[(l + rotation_offset) % 360] = temp2[l]
                    if self.single_file_flag is False:
                        buf1[(l + rotation_offset) % 360] = temp1[l]
                temp1 = buf1
                temp2 = buf2

            if key == 'vertical' and config.MSIV_FLAG is True:
                rotation_offset = config.MSIV_ROTATION_OFFSET
                for l in range(0, 360):
                    buf2[(l + rotation_offset) % 360] = temp2[l]
                    if self.single_file_flag is False:
                        buf1[(l + rotation_offset) % 360] = temp1[l]
                temp1 = buf1
                temp2 = buf2

            if options.rotation_offset > 0:
                rotation_offset = options.rotation_offset
                for l in range(0, 360):
                    buf2[(l + rotation_offset) % 360] = temp2[l]
                    if self.single_file_flag is False:
                        buf1[(l + rotation_offset) % 360] = temp1[l]
                temp1 = buf1
                temp2 = buf2

            if show_3db is True:
                plt.polar(
                    theta,
                    temp0,
                    label= 'max -3dB',
                    color= 'gray',
                    ls='--',
                    lw=1
                )
            if self.single_file_flag is True:
                temp2 = np.insert(temp2,360,temp2[0]) # Add first as last to draw 359-0
                plt.polar(
                    theta,
                    temp2,
                    label=key, #'Antenna 1',
                    color= 'blue' if key == 'horizontal' else 'red',
                    ls='-',
                    lw=line_width
                )
            else:
                temp1 = np.insert(temp1,360,temp1[0]) # Add first as last to draw 359-0
                temp2 = np.insert(temp2,360,temp2[0]) # Add first as last to draw 359-0
                plt.polar(
                    theta,
                    temp2,
                    label= key + ' 1', #'Antenna 1',
                    color='blue',
                    ls='-',
                    lw=line_width
                )
                plt.polar(
                    theta,
                    temp1,
                    label= key + ' 2', #'Antenna 2',
                    color='red',
                    ls='--',
                    lw=line_width
                )
                # short/left is always blue

            # not working well with python 2.7
            if options.show_legend is True:
                plt.legend(loc='lower left', borderaxespad=-1.5)
            tick_range = np.arange(
                np.floor(tick_start),
                np.ceil(tick_stop)+0.1,
                np.floor(tick_spacing)
            )

            ax.set_yticks(tick_range)
            # counter is used to label every other ticks
            counter = 0
            # only show every other ticks
            tick_label = []
            units = 'dBi' if config.ABSOLUTE_FLAG is True else 'dB'
            for x in tick_range:
                if counter % 2 == 1:
                    tick_label.append(' %1.1f %s' % (x,units))
                    counter += 1
                else:
                    if tick_spacing == 1:
                        tick_label.append(' %1.1f %s' % (x,units))
                    else:
                        tick_label.append('')
                    counter += 1

            # show full ticks
            tick_label_full = []
            for x in tick_range:
                tick_label_full.append(' %1.1f %s' % (x,units))
            ax.set_yticklabels(tick_label_full)
            if save_file:
                file_name_body = os.path.splitext(os.path.basename(file_path))[0]
                file_path_save = dir_path[0] + file_format + '/'
                if not os.path.exists(file_path_save):
                    os.makedirs(file_path_save)

                output_name = (
                    dir_path[0] + file_format + '/' + file_name_prefix
                    + file_name_body + '_' + key + '.' + file_format
                )
                plt.savefig(output_name, format=file_format)
                print(
                    '{} file saved at {}'.format(file_format, output_name)
                )

            if options.show_fig:
                plt.draw()

        if options.show_fig:
            plt.show()
        plt.close(fig)

def main():
    pyap = Pyap()
    pyap.wrapper(sys.argv)


if __name__=='__main__':
    sys.exit(main()) # pragma: no cover
