# -*- coding: utf-8 -*-
from django.utils.translation import gettext as _

import django_filters
from django.contrib.auth.models import User

from core import models

class ChildFieldFilter(django_filters.FilterSet):
    class Meta:
        model = models.Child
        fields = ["first_name"]

    @property
    def qs(self):
        children = super().qs
        user = getattr(self.request, 'user', None)
        # User.objects.filter()
        return models.Child.objects.filter(care_givers__username = user)

class TagFilter(django_filters.FilterSet):
    tag = django_filters.ModelChoiceFilter(
        label=_("Tag"),
        field_name="tags__name",
        distinct=True,
        queryset=models.Tag.objects.all().order_by("name"),
    )


class BMIFilter(TagFilter, ChildFieldFilter):
    class Meta:
        model = models.BMI
        fields = ["child"]


class DiaperChangeFilter(TagFilter):
    class Meta:
        model = models.DiaperChange
        fields = ["child", "wet", "solid", "color"]


class FeedingFilter(TagFilter):
    class Meta:
        model = models.Feeding
        fields = ["child", "type", "method"]


class HeadCircumferenceFilter(TagFilter):
    class Meta:
        model = models.HeadCircumference
        fields = ["child"]


class HeightFilter(TagFilter):
    class Meta:
        model = models.Height
        fields = ["child"]


class NoteFilter(TagFilter):
    class Meta:
        model = models.Note
        fields = ["child"]


class PumpingFilter(django_filters.FilterSet):
    class Meta:
        model = models.Pumping
        fields = ["child"]


class SleepFilter(TagFilter):
    class Meta:
        model = models.Sleep
        fields = ["child"]


class TemperatureFilter(TagFilter):
    class Meta:
        model = models.Temperature
        fields = ["child"]


class TummyTimeFilter(TagFilter):
    class Meta:
        model = models.TummyTime
        fields = ["child"]


class WeightFilter(TagFilter):
    class Meta:
        model = models.Weight
        fields = ["child"]
