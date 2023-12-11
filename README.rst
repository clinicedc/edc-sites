|pypi| |actions| |codecov| |downloads|

edc-sites
---------

Site definitions to work with Django's `Sites Framework`__ and django_multisite_.

Define a ``sites.py``. This is usually in a separate project module. For example, for project ``meta`` there is a module ``meta_sites`` that contains a ``sites.py``.

.. code-block:: python

    # sites.py
    from edc_sites.single_site import SingleSite

	fqdn = "example.clinicedc.org"

	all_sites = (
	    SingleSite(
	        10,
	        "hindu_mandal",
	        title="Hindu Mandal Hospital",
	        country="tanzania",
	        country_code="tz",
	        domain=f"hindu_mandal.tz.{fqdn}",
	    ),
	    SingleSite(
	        20,
	        "amana",
	        title="Amana Hospital",
	        country="tanzania",
	        country_code="tz",
	        domain=f"hindu_mandal.tz.{fqdn}",
	    ),
	)


Register a ``post_migrate`` signal in ``apps.py`` to update the django model ``Site`` and the
EDC model ``SiteProfile`` on the next migration:


.. code-block:: python

	# apps.py

	from .sites import all_sites, fqdn

	def post_migrate_update_sites(sender=None, **kwargs):
	    from edc_sites.add_or_update_django_sites import add_or_update_django_sites

	    sys.stdout.write(style.MIGRATE_HEADING("Updating sites:\n"))
	    add_or_update_django_sites(
	        apps=django_apps, sites=all_sites, fqdn=fqdn, verbose=True
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
            SingleSite(
                101,
                "hindu_mandal",
                title="Hindu Mandal Hospital",
                country="tanzania",
                country_code="tz",
                domain=f"hindu_mandal.tz.{fqdn}",
            ),
            SingleSite(
                102,
                "amana",
                title="Amana Hospital",
                country="tanzania",
                country_code="tz",
                domain=f"hindu_mandal.tz.{fqdn}",
            ),
        ),
        "uganda":(
            SingleSite(
                201,
                "kojja",
                country="uganda",
                country_code="ug",
                domain=f"kojja.ug.{fqdn}",
            ),
            SingleSite(
                202,
                "mbarara",
                country="uganda",
                country_code="ug",
                domain=f"mbarara.ug.{fqdn}",
            ),
        ),
    }


In a multisite, multi-country deployment, managing the SITE_ID is complicated. We use django_multisite_ which nicely reads
the SITE_ID from the url. django_multisite will extract `kojja` from https://kojja.ug.example.clinicedc.org to do a model lookup
to get the SITE_ID.

Viewing data from multiple sites using ``view_auditallsites``
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The mixins provided by``edc_sites`` limit the EDC to only present data linked to the current site.
To expand access beyond the current site, ``edc_sites`` provides a special permission codename;
``view_auditallsites``. If a user has this permission, they will be shown data from the current
site plus any additional sites granted in their user profile.

The permission codename ``view_auditallsites`` cannot be allocated to a user with add/edit/delete
permissions to ANY model in the system. That is, the permission codename ``view_auditallsites``
is reserved for VIEW ONLY access, e.g the AUDITOR_ROLE. The one exception is for ``edc_auth``
and``auth`` models accessible to users granted ACCOUNT_MANAGER_ROLE permissions.

In your code, you can check if a user has access to more than just the current site using function
``has_permissions_for_extra_sites``:

.. code-block:: python

    if has_permissions_for_extra_sites(request):
        queryset = self.appointment_model_cls.objects.all()
    else:
        queryset = self.appointment_model_cls.on_site

To get a list of sites that the user has access to in the current request, use function
``site_ids_with_permissions``.

.. code-block:: python

    site_ids = site_ids_with_permissions(request)



.. |pypi| image:: https://img.shields.io/pypi/v/edc-sites.svg
    :target: https://pypi.python.org/pypi/edc-sites

.. |actions| image:: https://github.com/clinicedc/edc-sites/workflows/build/badge.svg?branch=develop
  :target: https://github.com/clinicedc/edc-sites/actions?query=workflow:build

.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-sites/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/clinicedc/edc-sites

.. |downloads| image:: https://pepy.tech/badge/edc-sites
   :target: https://pepy.tech/project/edc-sites

.. _django_multisite: https://github.com/ecometrica/django-multisite.git

.. _sites_framework: https://docs.djangoproject.com/en/dev/ref/contrib/sites/
__ sites_framework_

