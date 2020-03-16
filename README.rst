|pypi| |travis| |codecov| |downloads|

.. _sites_framework: https://docs.djangoproject.com/en/2.1/ref/contrib/sites/
__ sites_framework_

edc-sites
---------

Site definitions to work with Django's `Sites Framework`__.

Define a ``sites.py``. This is usually in a separate project module. For example, for project ``meta`` there is a module ``meta_sites`` that contains a ``sites.py``.

.. code-block:: python

	# sites.py

	fqdn = "meta.clinicedc.org"

	meta_sites = (
	    (10, "hindu_mandal", "Hindu Mandal Hospital"),
	    (20, "amana", "Amana Hospital"),
	)


Register a ``post_migrate`` signal in ``apps.py`` to update the django model ``Site`` and the EDC model ``SiteProfile`` on the next migration:

.. code-block:: python
	
	# apps.py

	from .sites import meta_sites, fqdn

	def post_migrate_update_sites(sender=None, **kwargs):
	    from edc_sites.add_or_update_django_sites import add_or_update_django_sites

	    sys.stdout.write(style.MIGRATE_HEADING("Updating sites:\n"))
	    add_or_update_django_sites(
	        apps=django_apps, sites=meta_sites, fqdn=fqdn, verbose=True
	    )
	    sys.stdout.write("Done.\n")
	    sys.stdout.flush()


For another deployment, we have alot of sites spread out over a few countries. In this case we pass a dictionary and
separate the lists of sites by country.

For example:

.. code-block:: python

    fqdn = "inte.clinicedc.org"

    all_sites = {
        "tanzania":(
            (10, "hindu_mandal", "Hindu Mandal Hospital"),
            (20, "amana", "Amana Hospital"),
        ),
        "uganda":(
            (10, "kojja", "Kojja Clinic"),
            (20, "mbarara", "Mbarara Clinic"),
            (30, "kampala", "Kampala Clinic"),
        ),
    }


In a mult-isite, multi-country deployment, managing the SITE_ID is complicated.

One approach is to manipulate the ``DJANGO_SETTINGS_MODULE``.

The ``DJANGO_SETTINGS_MODULE`` is referred to by ``wsgi.py`` and can just as easily be referred to in settings itself.
For example, instead of explicitly setting the ``SITE_ID`` you can use ``edc_sites`` utility ``get_site_from_environment``.

What we would like to be able do is this:

.. code-block:: bash

    # defaults as a test environment or whatever manage.py points to.
    $ python manage.py runserver
    >>> from django.conf import settings
    >>> setting.SITE_ID
    >>> 100

    # which, with the new folder structure,  is the same as this
    $ python manage.py runserver --settings=inte_edc.settings.defaults

    >>> from django.conf import settings
    >>> setting.SITE_ID
    >>> 100

    # This loads for a specific site
    $ python manage.py runserver --settings=inte_edc.settings.uganda.kojja

    >>> from django.conf import settings
    >>> setting.SITE_ID
    >>> 170


Of course, having a custom settings file is easy, but managing these across multiple deployments can easily lead
to code duplication. So let's backup a bit. What do we need to setup?


1. change ``manage.py``

.. code-block:: python

    ...
    ...
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inte_edc.settings.defaults")
    ...
    ...


    or to be more helpful ...

.. code-block:: python

    def main():
    default = "inte_edc.settings.defaults"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inte_edc.settings.defaults")
    if os.environ.get("DJANGO_SETTINGS_MODULE") == default:
        sys.stderr.write(
            style.ERROR(
                f"DJANGO_SETTINGS_MODULE not set. Using `{default}`. "
                f"Assuming a test environment (manage.py).\n"
            )
        )
    try:
        from django.core.management import execute_from_command_line
    ...
    ...


2. change ``wsgi.py``

.. code-block:: python

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inte_edc.settings")

    becomes this

.. code-block:: python

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inte_edc.settings.defaults")


3. create a custom sites module that has a ``sites.py``. In this case ``inte_sites.sites``;

.. code-block:: python

    fqdn = "inte.clinicedc.org"

    all_sites = {
        "tanzania":(
            (10, "hindu_mandal", "Hindu Mandal Hospital"),
            (20, "amana", "Amana Hospital"),
        ),
        "uganda":(
            (10, "kojja", "Kojja Clinic"),
            (20, "mbarara", "Mbarara Clinic"),
            (30, "kampala", "Kampala Clinic"),
        ),
    }


4. move settings.py to a folder and put all settings stuff in a ``defaults.py``::

    inte-edc/
        inte_edc/
            settings/
                __init__.py
                defaults.py
                uganda/
                    __init__.py
                    kampala.py
                    kojja.py
                    mbarara.py
            __init__.py
            wsgi.py
        inte_sites/
            __init__.py
            apps.py
            sites.py
    manage.py


5. create dummy ``settings`` files for each site, for example;

.. code-block:: python

    # kojja.py
    from ..defaults import *  # noqa


4. update the settings ``defaults.py`` file. Replace ``SITE_ID=<site_id>`` ...

.. code-block:: python

    # defaults.py
    from edc_sites import get_site_from_environment

    ...

    # extract country and sitename from DJANGO_SETTINGS_MODULE environment variable
    EDC_SITES_MODULE_NAME = env.str("EDC_SITES_MODULE_NAME")
    COUNTRY, SITE_ID = get_site_from_environment(
        default_site_name="mbarara",
        default_country="uganda",
        app_name=APP_NAME,
        sites_module_name=EDC_SITES_MODULE_NAME,
    )

    ...

    we choose "mbarara" and "uganda" for our default site_name and country.


5. We use a ``.env`` file and set ``EDC_SITES_MODULE_NAME`` to ``inte_sites.sites``.

6. set the ``DJANGO_SETTINGS_MODULE`` for each environment the project is loaded in.

Unless we are testing, we'll expect the ``DJANGO_SETTINGS_MODULE`` to be set.
We'll set it to a value that includes the county and site name.
As you can see from the change to ``defaults.py`` above, we parse the value using ``get_site_from_environment``.


.. |pypi| image:: https://img.shields.io/pypi/v/edc-sites.svg
    :target: https://pypi.python.org/pypi/edc-sites
    
.. |travis| image:: https://travis-ci.com/clinicedc/edc-sites.svg?branch=develop
    :target: https://travis-ci.com/clinicedc/edc-sites
    
.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-sites/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/clinicedc/edc-sites

.. |downloads| image:: https://pepy.tech/badge/edc-sites
   :target: https://pepy.tech/project/edc-sites
