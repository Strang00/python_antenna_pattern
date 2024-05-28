======================
python-antenna-pattern
======================


Generate antenna radiation pattern in polar coordinates using python


* Free software: Apache Software License 2.0
* Documentation: https://python-antenna-pattern.readthedocs.io.


Features
--------

Simple cli to 
 * generate pdf, eps or ptarget_pattern_fileng file from a planet file
 * convert individual file or convert entire folder of files


Examples::

   python pyap -g -n TEST_ ./python_antenna_pattern/data/LTE-L_1960MHz_P1.txt  
   python pyap -g -3 -f png -n TEST_ ./python_antenna_pattern/data/AMB4520R8v06_05T.msi


Usage::

   pyap [-h] [-v] [-s] [-g] [-3] [--show-name] [-r ROTATION_OFFSET]
        [-f {pdf,eps,png}] [-n FILE_NAME_PREFIX] [--fontsize FONTSIZE]
        [--size IMAGE_SIZE_X100PX]
        target_pattern_file

   positional arguments:
      target_pattern_file   Use specified file, list of files, or a directory
                              containing planet files to plot antenna pattern

   options:
      -h, --help            show this help message and exit
      -v, --verbose         Show all logs when running the commands. (default:
                              False)
      -s, --show-fig        Show figure. This will pause after each figure is
                              generated. (default: False)
      -g, --show-legend     Show legend (default: False)
      -3, --show-3db        Show half-power line (max - 3dB) (default: False)
      --show-name           Add NAME attribute to caption (default: False)
      -r ROTATION_OFFSET, --rotation-offset ROTATION_OFFSET
                              Rotational offset when plotting the polar pattern
                              (default: 0)
      -f {pdf,eps,png}, --filetype {pdf,eps,png}
                              File type of the output figure, either pdf or eps or
                              png (default: pdf)
      -n FILE_NAME_PREFIX, --file-name-prefix FILE_NAME_PREFIX
                              Prefix of the generated filename (default: PYAP_)
      --fontsize FONTSIZE   Font size in the legend and the title (default: 12)
      --size IMAGE_SIZE_X100PX
                              Image size in 100px units (default: 8)


Credits
-------

Respect to Tsung-Yi Chen, original author of python-antenna-pattern v0.1.0.

Package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
