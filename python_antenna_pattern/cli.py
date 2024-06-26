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
  from python_antenna_pattern.core import __project__
  from python_antenna_pattern.core import __version__
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
            '-i',
            '--show-image',
            action='store_true',
            dest='show_fig',
            default=False,
            help='show image and pause after each figure is generated'
        )
        self.arg_parser.add_argument(
            '-l',
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
            '-m',
            '--merge',
            action='store_true',
            dest='merge',
            default=False,
            help='merge multiple sources to one pattern'
        )
        self.arg_parser.add_argument(
            '-c',
            '--combine',
            action='store_true',
            dest='combine_hv',
            default=False,
            help='combine horizontal and vertical patterns on chart'
        )
        self.arg_parser.add_argument(
            '-w',
            '--hide-watermark',
            action='store_true',
            dest='watermark_hide',
            default=False,
            help='hide watermark with version'
        )
        self.arg_parser.add_argument(
            '-n',
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
            '-t',
            '--file-type',
            choices=['pdf', 'eps', 'png'],
            dest='file_type',
            default='pdf',
            help='file type of the output figure, pdf or eps or png'
        )
        self.arg_parser.add_argument(
            '-p',
            '--file-prefix',
            type=str,
            dest='file_prefix',
            default=None,
            help='prefix of the generated filename'
        )
        self.arg_parser.add_argument(
            '-rh',
            '--rotation-horizontal',
            type=int,
            dest='rotation_h',
            default=0,
            help='horizontal rotational offset'
        )
        self.arg_parser.add_argument(
            '-rv',
            '--rotation-vertical',
            type=int,
            dest='rotation_v',
            default=0,
            help='vertical rotational offset'
        )
        self.arg_parser.add_argument(
            '-o',
            '--output',
            type=str,
            dest='save_suffix',
            default=None,
            help='resave pattern with passed suffix'
        )
        self.arg_parser.add_argument(
            '-f',
            '--font-size',
            type=int,
            dest='font_size',
            default=12,
            help='font size for texts on the chart'
        )
        self.arg_parser.add_argument(
            '-s',
            '--simulate',
            type=int,
            dest='simulate_tilt',
            default=None,
            help='simulate diagramm pattern using TILT'
        )
        self.arg_parser.add_argument(
            '-z',
            '--size',
            type=int,
            dest='image_size',
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
        if (args.combine_hv is False or args.merge is True):
            self.plot_pattern(args)
        else:
            src_files = list(glob.glob(args.pattern))
            if len(src_files) == 0:
                print(
                    'Files not found: {}'.format(args.pattern),
                    file=sys.stderr
                )
                sys.exit(os.EX_NOTFOUND)
            for file in src_files:
                args.pattern = file
                self.plot_pattern(args)

                
    # TODO: use optparse to add options rather than using config.py
    def plot_pattern(self, options, save_file=True):

        fontsize = options.font_size
        simulate = not (options.simulate_tilt is None)
        imagesize = options.image_size
        file_name_prefix = options.file_prefix
        if (file_name_prefix is None): file_name_prefix = ''
        file_format = options.file_type
        show_name = options.show_name
        show_3db = options.show_3db
        merge_src = options.merge
        plt.rc('font', size=fontsize)
        if not os.path.isfile(options.pattern):
            src_files = list(glob.glob(options.pattern))
            if len(src_files) == 0:
                print(
                    'Files not found: {}'.format(options.pattern),
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


        degree = np.arange(0, 360, 1)
        theta = degree*2*np.pi/360
        p_list = []
        dir_path = []
        band = []
        name = []
        gain = []
        file_path = ''

        # TODO: syncup cli args and these configs. or at least be able to pass
        # the config file
        clipping = config.MAX_GAIN_CLIPPING
        tick_start = config.TICK_START
        tick_stop = config.TICK_STOP
        tick_spacing = config.TICK_SPACING
        line_width = config.LINE_WIDTH
        rlim_shift = config.RLIM_SHIFT
        gain_ticks_position = config.TICK_POSITION # good with 45 also

        if merge_src is False is False and len(src_files) > 2:
            print(
                'PYAP currently does not support more than a pair of files at once',
                file=sys.stderr
            )
            sys.exit(70) # os.EX_SOFTWARE available only on UNIX platforms.

        if merge_src is False and options.combine_hv is True and len(src_files) > 1:
            print(
                'PYAP currently does not support more than one file at combine mode plot',
                file=sys.stderr
            )
            sys.exit(70) # os.EX_SOFTWARE available only on UNIX platforms.

        for file_path_original in src_files:
            file_path = file_path_original.replace('\\', '/')

            if (merge_src is True and len(p_list) >= 1):
                print('merging {}'.format(file_path))
                antenna_pattern2 = AntennaPattern()
                antenna_pattern2.parse_data(file_path)
                p_list[-1].merge_from(antenna_pattern2)
                band[-1] = p_list[-1].frequency
                gain[-1] = p_list[-1].max_gain_db
                name[-1] = p_list[-1].name
                continue
                
            antenna_pattern = AntennaPattern()
            # parse the antenna gains by cut or by antenna
            antenna_pattern.parse_data(file_path) # config.PARSE_BY
            if options.rotation_h != 0 or options.rotation_v != 0:
                antenna_pattern.offset_data(options.rotation_h, options.rotation_v)
                
            split_name = file_path.rsplit('/')
            file_name = split_name[-1]
            print('processing {}'.format(file_name))
            # temp now is a dictionary of the two antenna pattern in a file
            p_list.append(antenna_pattern)

            #b = parse_freq_band(file_name)
            band.append(antenna_pattern.frequency)
            gain.append(antenna_pattern.max_gain_db)
            name.append(antenna_pattern.name)
            # all but last element in the list
            dir_path.append('/'.join(split_name[0:-1]) + '/')

            if not (options.save_suffix is None):
                file_name_save = (dir_path[0] + file_name_prefix
                + os.path.splitext(os.path.basename(file_path))[0]
                + options.save_suffix + ".msi")
                antenna_pattern.save_data(file_name_save)

            #Simulate pattern ~59/7 with passed tilt
            if simulate:
                band.append(antenna_pattern.frequency)
                name.append(antenna_pattern.name)
                gain.append(antenna_pattern.max_gain_db)
                tilt = int(options.simulate_tilt)
                antenna_pattern = AntennaPattern()
                antenna_pattern.simulate_data(gain[-1], band[-1], tilt)
                if options.rotation_h != 0 or options.rotation_v != 0:
                    antenna_pattern.offset_data(options.rotation_h, options.rotation_v)
                print('simulatig source')
                p_list.append(antenna_pattern)
                file_name_prefix += "simulated_" + format(tilt,'02d') + 'T_'
                if config.SIMULATE_SAVE is True:
                    file_name_save = (dir_path[0] + file_name_prefix 
                    + os.path.splitext(os.path.basename(file_path))[0]
                    + ".msi")
                    antenna_pattern.save_data(file_name_save)

        if (merge_src is True and len(p_list) >= 1):
            file_name_prefix += "merged_" + format(len(src_files),'02d') + 'P_'
            if config.MERGE_SAVE is True:
                file_name_save = (dir_path[0] + file_name_prefix 
                + os.path.splitext(os.path.basename(file_path))[0]
                + ".msi")
                antenna_pattern.save_data(file_name_save)

        if len(p_list) < 2:
            self.single_file_flag = True

        if len(band) > 1:
            print('Frequency band list: {}'.format(band), file=sys.stderr)
            if band[0] != band[1]:
                print(
                    'Frequency band not match: {}'.format(band),
                    file=sys.stderr
                )
                sys.exit(70) # os.EX_SOFTWARE available only on UNIX platforms.

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
            # the vertical antenna pattern for the first file, is in rho[key][0:360]
            # and the antenna pattern for the second file is in rho[key][360:720],
            # and so on. Number of antenna to consider
            for key in list(pval.pattern_dict.keys()):
                key_array = pval.max_gain_db - np.asarray(pval.pattern_dict[key]) if config.ABSOLUTE_FLAG is True else -np.asarray(pval.pattern_dict[key])

                # in C250 planet files the angle is rotated by 90
                if key == 'horizontal' and config.HOR_ROTATION_OFFSET != 0:
                    rotation_offset = config.HOR_ROTATION_OFFSET
                    rotation_temp = list(key_array)
                    for l in range(0, 360):
                        key_array[(l + rotation_offset + 360) % 360] = rotation_temp[l]

                # in most mobile antenna vendors specs vertical peak drawn to look at 90 degrees
                if key == 'vertical' and config.VER_ROTATION_OFFSET != 0:
                    rotation_offset = config.VER_ROTATION_OFFSET
                    rotation_temp = list(key_array)
                    for l in range(0, 360):
                        key_array[(l + rotation_offset + 360) % 360] = rotation_temp[l]

                key_write = key if options.combine_hv is False else ''
                if key_write not in rho:
                    rho[key_write] = []
                rho[key_write] = np.append(
                    rho[key_write],
                    key_array
                )

        for key in list(rho.keys()):
            if options.combine_hv is True:
                name1 = 'horizontal'
                name2 = 'vertical'
                key_suffix = ''
            elif self.single_file_flag is True:
                name1 = key
                name2 = ''
                key_suffix = '_' + key
            elif simulate is True:
                name1 = key
                name2 = 'simulated'
                key_suffix = '_' + key
            else:
                name1 = key + ' 1'
                name2 = key + ' 2'
                key_suffix = ' ' + key

            max_value = max(rho[key]) 
            max_gain_db = gain[0]
            max_list.append(max_gain_db)
            max_gain_db_str = 'Peak Gain: {:.2f} dBi'.format(max_gain_db)
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
            if options.watermark_hide is False:
                ax.text(1.1, -0.1, f'Generated by {__project__} v{__version__}', transform=ax.transAxes, 
                    fontsize=fontsize, color='gray', alpha=0.2,
                    ha='right', va='top')
            
            # in two-file mode long/right antenna is always red, and is always in second file
            # in one-file mode horisontal/vertical are in blue/red colors
            temp0 = np.full(360, max_value-3)           
            temp1 = rho[key][0:360]
            temp2 = rho[key][360:720]
            buf1 = [0]*360
            buf2 = [0]*360

            # Measure beam width on level max-3dB
            if show_3db is True:
                width1 = np.full(4, -1) # width, left border, value with 0, right border
                width2 = np.full(4, -1) # width, left border, value with 0, right border
                prev_value1 = 0.0
                prev_value2 = 0.0
                peak_value1 = 30.0
                peak_value2 = 30.0
                for l in range(0, 360):
                    curr_value1 = -temp1[l] - (max_gain_db if config.ABSOLUTE_FLAG is True else 0)
                    if (prev_value1 > 3 and curr_value1 <=3):
                        width1[1] = l
                    if (prev_value1 > curr_value1 and curr_value1 < 3 and curr_value1 < peak_value1):
                        width1[2] = l
                        peak_value1 = curr_value1
                    if (prev_value1 < 3 and curr_value1 >=3):
                        width1[3] = l
                    prev_value1 = curr_value1
                    if (self.single_file_flag is False or options.combine_hv is True):
                        curr_value2 = -temp2[l] - (max_gain_db if config.ABSOLUTE_FLAG is True else 0)
                        if (prev_value2 >= 3 and curr_value2 <=3):
                            width2[1] = l
                        if (prev_value2 > curr_value2 and curr_value2 < 3 and curr_value2 < peak_value2):
                            width2[2] = l
                            peak_value2 = curr_value2
                        if (prev_value2 <= 3 and curr_value2 >=3):
                            width2[3] = l
                        prev_value2 = curr_value2
                if width1[1] >= 0:
                    width1[0] = (width1[3] - width1[1] + 360) %360
                    print(f'{name1} width: {width1[0]:.2f}')
                    print(f'{name1} peak : {width1[2]:.2f}')
                if peak_value1 > 0:
                    print(f'{name1} max  : {peak_value1:.2f} above zero')
                if (self.single_file_flag is False or options.combine_hv is True):
                    if width2[1] >= 0:
                        width2[0] = (width2[3] - width2[1] + 360) %360
                        print(f'{name2} width: {width2[0]:.2f}')
                        print(f'{name2} peak : {width2[2]:.2f}')
                    if peak_value2 > 0:
                        print(f'{name2} max  : {peak_value2:.2f} above zero')

            # Add first as last to draw 359-0
            thet0 = np.insert(theta,360,theta[0])    
            temp1 = np.insert(temp1,360,temp1[0])
            if self.single_file_flag is False or options.combine_hv is True:
                temp2 = np.insert(temp2,360,temp2[0])

            if show_3db is True:
                temp0 = np.insert(temp0,360,temp0[0])
                plt.polar(
                    thet0,
                    temp0,
                    label= 'max -3dB',
                    color= config.COLOR_3DB,
                    ls= '--',
                    lw= 1
                )                               
            if (options.combine_hv is True):
                plt.polar(
                    thet0,
                    temp1,
                    label= name1,
                    color= config.COLOR_HOR,
                    ls= '-',
                    lw= line_width
                )
                plt.polar(
                    thet0,
                    temp2,
                    label= name2,
                    color= config.COLOR_VER,
                    ls= '-',
                    lw= line_width
                )
            
            elif self.single_file_flag is True:
                plt.polar(
                    thet0,
                    temp1,
                    label= name1,
                    color= config.COLOR_HOR if key == 'horizontal' else config.COLOR_VER,
                    ls= '-',
                    lw= line_width
                )
            else:
                plt.polar(
                    thet0,
                    temp1,
                    label= name1,
                    color= config.COLOR_2A1,
                    ls= '-',
                    lw= line_width
                )
                plt.polar(
                    thet0,
                    temp2,
                    label= name2,
                    color= config.COLOR_2A2,
                    ls= '--',
                    lw= line_width
                )
                # short/left is always blue

            # not working well with python 2.7
            if options.show_legend is True:
                plt.legend(loc='lower left', borderaxespad=-2.0)
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
                file_path_save = dir_path[0] + file_format + '/'
                if not os.path.exists(file_path_save):
                    os.makedirs(file_path_save)
                file_name_body = os.path.splitext(os.path.basename(file_path))[0] + key_suffix
                file_name_save = file_path_save + file_name_prefix + file_name_body + '.' + file_format
                plt.savefig(file_name_save, format=file_format)
                print( '{} file saved at {}'.format(file_format, file_name_save) )

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
