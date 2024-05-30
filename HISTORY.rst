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
