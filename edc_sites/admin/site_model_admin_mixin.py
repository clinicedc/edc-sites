from __future__ import annotations

import collections

from django.contrib import admin
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.db.models import QuerySet

from ..models import SiteProfile
from ..site import sites
from .list_filters import SiteListFilter

__all__ = ["SiteModelAdminMixin"]


class SiteModeAdminMixinError(Exception):
    pass


class SiteModelAdminMixin:
    language_db_field_name = "language"

    limit_related_to_current_country: list[str] = None
    limit_related_to_current_site: list[str] = None

    @admin.display(description="Site", ordering="site__id")
    def site_code(self, obj=None):
        return obj.site.id

    @admin.display(description="Site", ordering="site__id")
    def site_name(self, obj=None):
        try:
            site_profile = SiteProfile.objects.get(site__id=obj.site.id)
        except ObjectDoesNotExist:
            return obj.site.name
        return f"{site_profile.site.id} {site_profile.description}"

    def get_list_filter(self, request):
        """Insert `SiteListFilter` before field name `created`.

        Remove site from the list if user does not have access
        to mulitple sites.
        """
        list_filter = super().get_list_filter(request)
        list_filter = [x for x in list_filter if x != "site" and x != SiteListFilter]
        if sites.user_may_view_other_sites(request):
            try:
                index = list_filter.index("created")
            except ValueError:
                index = len(list_filter)
            list_filter.insert(index, SiteListFilter)
        return tuple(list_filter)

    def get_list_display(self, request):
        """Insert `site` after the first column"""
        list_display = super().get_list_display(request)
        if sites.user_may_view_other_sites(request) and "site" not in list_display:
            list_display = (list_display[0],) + (self.site_code,) + list_display[1:]
        elif "site" in list_display:
            list_display = tuple(
                [x for x in list_display if x not in ["site", self.site_code]]
            )
            list_display = (list_display[0],) + (self.site_code,) + list_display[1:]
        return list_display

    def get_readonly_fields(self, request, obj=None) -> tuple[str, ...]:
        """Add site to readonly_fields."""
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        if "site" not in readonly_fields:
            return readonly_fields + ("site",)
        return readonly_fields

    def get_queryset(self, request) -> QuerySet:
        """Limit modeladmin queryset for the current site only"""
        qs = super().get_queryset(request)
        site_ids = [request.site.id] + sites.get_view_only_site_ids_for_user(request=request)
        try:
            qs = qs.select_related("site").filter(site_id__in=site_ids)
        except FieldError:
            raise SiteModeAdminMixinError(
                f"Model missing field `site`. Model `{self.model}`. Did you mean to use "
                f"the SiteModelAdminMixin? See `{self}`."
            )
        return qs

    def get_form(self, request, obj=None, change=False, **kwargs):
        """Add current_site attr to form instance"""
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.current_site = getattr(request, "site", None)
        form.current_locale = getattr(request, "LANGUAGE_CODE", None)
        return form

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """Use site id to select languages to show in choices."""
        if db_field.name == self.language_db_field_name:
            try:
                language_choices = sites.get_language_choices_tuple(request.site, other=True)
            except AttributeError as e:
                if "WSGIRequest" not in str(e):
                    raise
            else:
                if language_choices:
                    kwargs["choices"] = language_choices
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter a ForeignKey field`s queryset by the current site
        or country.

        Note, a queryset set by the ModelForm class will overwrite
        the field's queryset added here.
        """
        self.raise_on_dups_in_field_lists(
            self.limit_related_to_current_country,
            self.limit_related_to_current_site,
        )
        if db_field.name in (self.limit_related_to_current_country or []):
            self.raise_on_queryset_exists(db_field, kwargs)
            country = sites.get_current_country(request)
            model_cls = getattr(self.model, db_field.name).field.related_model
            kwargs["queryset"] = model_cls.objects.filter(siteprofile__country=country)
        elif db_field.name in (self.limit_related_to_current_site or []) and getattr(
            request, "site", None
        ):
            self.raise_on_queryset_exists(db_field, kwargs)
            model_cls = getattr(self.model, db_field.name).field.related_model
            kwargs["queryset"] = model_cls.objects.filter(id=request.site.id)
        elif db_field.name in (self.limit_related_to_current_site or []):
            self.raise_on_queryset_exists(db_field, kwargs)
            model_cls = getattr(self.model, db_field.name).field.related_model
            kwargs["queryset"] = model_cls.on_site.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Filter a ManyToMany field`s queryset by the current site.

        Note, a queryset set by the ModelForm class will overwrite
        the field's queryset added here.
        """
        self.raise_on_dups_in_field_lists(
            self.limit_related_to_current_country,
            self.limit_related_to_current_site,
        )
        if db_field.name in (self.limit_related_to_current_site or []):
            self.raise_on_queryset_exists(db_field, kwargs)
            model_cls = getattr(self.model, db_field.name).remote_field.model
            kwargs["queryset"] = model_cls.on_site.all()
        elif db_field.name in (self.limit_related_to_current_country or []):
            country = sites.get_current_country(request)
            model_cls = getattr(self.model, db_field.name).remote_field.model
            kwargs["queryset"] = model_cls.objects.filter(siteprofile__country=country)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def raise_on_queryset_exists(self, db_field, kwargs):
        """Raise an exception if the `queryset` key exists in the
        kwargs dict.

        If `queryset` exists, remove the field name from the class attr:
            limit_fk_field_to_...
            limit_m2m_field_to_...
        """
        if "queryset" in kwargs:
            raise SiteModeAdminMixinError(
                f"Key `queryset` unexpectedly exists. Got field `{db_field.name}` "
                f"from {self}."
                f". Did you manually set key `queryset` for field `{db_field.name}`?"
            )

    @staticmethod
    def raise_on_dups_in_field_lists(*field_lists: list[str]):
        orig = []
        for field_list in field_lists:
            orig.extend(field_list or [])
        if dups := [item for item, count in collections.Counter(orig).items() if count > 1]:
            raise SiteModeAdminMixinError(
                f"Related field appears in more than one list. Got {dups}."
            )
