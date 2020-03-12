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
	    (1, "reviewer", ""),
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


.. |pypi| image:: https://img.shields.io/pypi/v/edc-sites.svg
    :target: https://pypi.python.org/pypi/edc-sites
    
.. |travis| image:: https://travis-ci.com/clinicedc/edc-sites.svg?branch=develop
    :target: https://travis-ci.com/clinicedc/edc-sites
    
.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-sites/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/clinicedc/edc-sites

.. |downloads| image:: https://pepy.tech/badge/edc-sites
   :target: https://pepy.tech/project/edc-sites
