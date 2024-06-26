=======
History
=======

0.1.0 (2020-08-07)
------------------

* First release on PyPI.


1.0.0 (2024-05-28)
------------------

* New multiplatform release with bugfixes and improvements.
* Added support for MS Windows (unsupported enums replaced).
* Added PNG output filtype and input MSI example.
* Added type of pattern horizontal or vertical to the legend.
* Vertical pattern drawn in red as used in HUAWEI datasheets.
* Config params reviewed, cleaned unused, updated used.
* Implemented NAME reading and added option --show-name to draw it.
* Implemented GAIN units reading and conversion dBd to dBi used in MSI.
* Bugfixed broken usage of C250_FLAG for single file source.
* Added LINE_WIDTH for pattern line width instead of unused LW.
* Added MSIV_FLAG and MSIV_ROTATION_OFFSET to rotate vertical pattern only.
* Added ABSOLUTE_FLAG to draw relative chart with peak 0dB instead of dBi.
* Added TICK_POSITION to control dB ticks position and rotation angle.
* Added option --size and changed --fontsize usage, updated defaults.
* Added option --show-3db to draw half-power level, updated legend position.


1.0.1 (2024-05-30)
------------------

* Added beam width measurement, printed to console when --show-3db used.
* Added SIMULATE_FLAG param to add simulated pattern 59/07 as antenna 2.
* Added SIMULATE_TILT param to define tilt for simulated antenna pattern.
* Added SIMULATE_SAVE param for saving simulation results to MSI file.
* Added COLOR_* params for configuring colors without changes in code.


1.0.2 (2024-06-04)
------------------

* Added --merge option to merge multiple files to one pattern with min loss.
* Added MERGE_SAVE param to save merged file when --merge option used.
* Bugfix GAIN write to have .2f format (floating points sometimes kidding).
* Extend tilt read from rare optional header ELECTRIC_TILT and from filename.


1.0.3 (2024-06-11)
------------------

* Fixed frequency reading for float value rare case (but still used as int).
* Added comments with TODO and refernce link to simulate method: `sin(x)/x`.
* Added ELECTRIC_TILT field to saved MSI files.
* Added reference to pafx2msi_ and vice versa.


1.0.4 (2024-06-25)
------------------
* Fixed config params C250_FLAG and C250_ROTATION_OFFSET to HOR_ROTATION_OFFSET.
* Fixed config params MSIV_FLAG and MSIV_ROTATION_OFFSET to VER_ROTATION_OFFSET.
* New options -rh and -rv rotates data on loading and allows to resave rotated.
* Fixed command line option -r to -rh and -rv for separate hor and ver rotation.
* Fixed command line option -g to -l (--show-legend), -s to -i (--show-image).
* Fixed command line option -n to -p (--file-prefix), -f to -t (--file-type).
* Added command line option -f for --font-size, -z for --size, -n for --name.
* Added command line option -o SAVE_SUFFIX to resave pattern file with rotation.
* Added command line option -c to combine HORIZONTAL and VERTICAL on one image.
* Added command line option -s TILT to simulate pattern instead of SIMULATE* params.
* Added command line option -w to disable drawing watermark with version on image.
* Added ability to process unlimited number of files by passed mask in -c mode.
* Added tool name and version to COMMENT in saved pattern and as image watermark.
* Removed SIMULATE_FLAG and SIMULATE_TILT config params (use option -s).


.. _pafx2msi: https://github.com/Strang00/pafx2msi