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


Examples:

    python pyap -g -n TEST_ ./python_antenna_pattern/data/LTE-L_1960MHz_P1.txt  
    python pyap -g -3 -f png -n TEST_ ./python_antenna_pattern/data/AMB4520R8v06_05T.msi

Usage::

    usage: pyap [-h] [-v] [-s] [-g] [-3] [--show-name] [-r ROTATION_OFFSET]
                [-f {pdf,eps,png}] [-n FILE_NAME_PREFIX] [--fontsize FONTSIZE]
                [--size IMAGE_SIZE_X100PX]
                target_pattern_file


Credits
-------

Respect to Tsung-Yi Chen, original author of python-antenna-pattern v0.1.0.

Package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
