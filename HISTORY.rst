=======
History
=======

0.1.0 (2020-08-07)
------------------

* First release on PyPI.


1.0.0 (2024-05-28)
------------------

* New multiplatform release with bugfixes and improvements.
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
