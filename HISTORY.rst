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
* Added SIMULATE_FLAG param to add simulated pattern 60/08 as antenna 2.
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

.. _pafx2msi: https://github.com/Strang00/pafx2msi