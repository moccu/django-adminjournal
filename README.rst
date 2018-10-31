django-adminjournal
===================

.. image:: https://img.shields.io/pypi/v/django-adminjournal.svg
   :target: https://pypi.org/project/django-adminjournal/
   :alt: Latest Version

.. image:: https://codecov.io/gh/moccu/django-adminjournal/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/moccu/django-adminjournal
   :alt: Coverage Status

.. image:: https://readthedocs.org/projects/django-adminjournal/badge/?version=latest
   :target: https://django-adminjournal.readthedocs.io/en/stable/?badge=latest
   :alt: Documentation Status

.. image:: https://travis-ci.org/moccu/django-adminjournal.svg?branch=master
   :target: https://travis-ci.org/moccu/django-adminjournal


This library added extended capabilities to log access to Django ModelAdmins.


Features
--------

* Log additions, changes, deletions of models via the Django admin
* Log read access to change lists and model instances (unsaved change views)
* Log calls to actions in changelists of ModelAdmins


Requirements
------------

django-adminjournal supports Python 3 only and requires at least Django 1.11.
The package uses Django's JSONField. Therefore, PostgreSQL database backend is required.


Prepare for development
-----------------------

A Python 3.6 interpreter is required in addition to pipenv.

.. code-block:: shell

    $ pipenv install --python 3.6 --dev
    $ pipenv shell
    $ pip install -e .


Now you're ready to run the tests:

.. code-block:: shell

    $ pipenv run py.test


Resources
---------

* `Documentation <https://django-adminjournal.readthedocs.io>`_
* `Bug Tracker <https://github.com/moccu/django-adminjournal/issues>`_
* `Code <https://github.com/moccu/django-adminjournal/>`_
