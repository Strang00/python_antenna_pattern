=======
History
=======

0.1.0 (2020-08-07)
------------------

* First release on PyPI.


1.0.0 (2024-05-28)
------------------

* New multiplatform release with bugfixes and improvements.
* Added support for MS Windows (replaced os.EX_SOFTWARE).
* Added PNG output filtype and -z alias for --fontsize.
* Fontsize used simulaneously for title and legend now.
* Legend contains type of pattern: horizontal or vertical.
* Vertical drawn red as used in HUAWEI datasheets usually.
* Config params reviewed, cleaned unused and used all defined.
* Implemented NAME reading, added to caption with -n option.
* Implemented NAME reading, added to caption with -n option.
* Implemented GAIN measure units read and conversion dBd to dBi (used in MSI).
* Bugfixed usage of C250_FLAG with single file source.
* Added MSIV_FLAG and MSIV_ROTATION_OFFSET to rotate vertical pattern only.
* Added ABSOLUTE_FLAG to draw relative chart (with peak 0dB instead of dBi).
