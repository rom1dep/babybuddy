# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date

import altair as alt
import pandas as pd
from django.db.models.aggregates import Sum
from django.db.models.expressions import Window
from django.views.generic.detail import DetailView
from django_pandas.io import read_frame

from babybuddy.mixins import PermissionRequiredMixin
from core import models
from . import graphs


class BMIChangeChildReport(PermissionRequiredMixin, DetailView):
    """
    Graph of BMI change over time.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/bmi_change.html"

    def get_context_data(self, **kwargs):
        context = super(BMIChangeChildReport, self).get_context_data(**kwargs)
        child = context["object"]
        objects = models.BMI.objects.filter(child=child)
        if objects:
            context["html"], context["js"] = graphs.bmi_change(objects)
        return context


class ChildReportList(PermissionRequiredMixin, DetailView):
    """
    Listing of available reports for a child.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/report_list.html"


class DiaperChangeAmounts(PermissionRequiredMixin, DetailView):
    """
    Graph of diaper "amounts" - measurements of urine output.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/diaperchange_amounts.html"

    def get_context_data(self, **kwargs):
        context = super(DiaperChangeAmounts, self).get_context_data(**kwargs)
        child = context["object"]
        changes = models.DiaperChange.objects.filter(child=child, amount__gt=0)
        if changes and changes.count() > 0:
            context["html"], context["js"] = graphs.diaperchange_amounts(changes)
        return context


class DiaperChangeLifetimesChildReport(PermissionRequiredMixin, DetailView):
    """
    Graph of diaper "lifetimes" - time between diaper changes.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/diaperchange_lifetimes.html"

    def get_context_data(self, **kwargs):
        context = super(DiaperChangeLifetimesChildReport, self).get_context_data(
            **kwargs
        )
        child = context["object"]
        changes = models.DiaperChange.objects.filter(child=child)
        if changes and changes.count() > 1:
            context["html"], context["js"] = graphs.diaperchange_lifetimes(changes)
        return context


class DiaperChangeTypesChildReport(PermissionRequiredMixin, DetailView):
    """
    Graph of diaper changes by day and type.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/diaperchange_types.html"

    def get_context_data(self, **kwargs):
        context = super(DiaperChangeTypesChildReport, self).get_context_data(**kwargs)
        child = context["object"]
        changes = models.DiaperChange.objects.filter(child=child)
        if changes:
            context["html"], context["js"] = graphs.diaperchange_types(changes)
        return context


class FeedingAmountsChildReport(PermissionRequiredMixin, DetailView):
    """
    Graph of daily feeding amounts over time.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/feeding_amounts.html"

    def __init__(self):
        super(FeedingAmountsChildReport, self).__init__()
        self.html = ""
        self.js = ""

    def get_context_data(self, **kwargs):
        context = super(FeedingAmountsChildReport, self).get_context_data(**kwargs)
        child = context["object"]
        instances = models.Feeding.objects.filter(child=child)
        if instances:
            df = read_frame(instances.all(), fieldnames=['start', 'amount', 'method'])
            context['chart'] = alt.Chart(df).mark_bar().encode(
                x='start',
                y='amount',
                color='method'
            ).properties(width=1000).interactive()
        return context


class FeedingDurationChildReport(PermissionRequiredMixin, DetailView):
    """
    Graph of feeding durations over time.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/feeding_duration.html"

    def __init__(self):
        super(FeedingDurationChildReport, self).__init__()
        self.html = ""
        self.js = ""

    def get_context_data(self, **kwargs):
        context = super(FeedingDurationChildReport, self).get_context_data(**kwargs)
        child = context["object"]
        instances = models.Feeding.objects.filter(child=child)
        if instances:
            context["html"], context["js"] = graphs.feeding_duration(instances)
        return context


class FeedingTrendChildReport(PermissionRequiredMixin, DetailView):
    """
    Graph of feedings over time with target goal.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/feeding_trend.html"

    def __init__(self):
        super(FeedingTrendChildReport, self).__init__()
        self.html = ""
        self.js = ""

    def get_context_data(self, **kwargs):
        context = super(FeedingTrendChildReport, self).get_context_data(**kwargs)
        child = context["object"]
        instances = models.Feeding.objects \
            .filter(child=child, start__date=date.today()) \
            .annotate(served_amount=Window(
                expression=Sum("amount"),
                order_by="start"
            ))

        if instances:
            df = read_frame(instances.all(), fieldnames=['start', 'amount', 'type', 'served_amount'])
            bar = alt.Chart(df).mark_bar().encode(
                alt.X('start', title="Feeding Time"),
                y='amount',
                color='type'
            )
            bar_labels = bar.mark_text(dy=-5).encode(text='amount')
            line = alt.Chart(df).mark_line(color='green').encode(
                x='start',
                y='served_amount'
            )
            line_labels = line.mark_text(dy=-5).encode(text='served_amount')
            goal = alt.Chart(pd.DataFrame({
                'start': [datetime.combine(date.today(), datetime.min.time()),
                          datetime.combine(date.today(), datetime.max.time())],
                'goal': [0, child.feeding_target]
            })).mark_line(color='salmon', clip=True).encode(
                x='start',
                y='goal'
            )
            context["chart"] = (bar + bar_labels + line + line_labels + goal).interactive()
        return context


class HeadCircumferenceChangeChildReport(PermissionRequiredMixin, DetailView):
    """
    Graph of head circumference change over time.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/head_circumference_change.html"

    def get_context_data(self, **kwargs):
        context = super(HeadCircumferenceChangeChildReport, self).get_context_data(
            **kwargs
        )
        child = context["object"]
        objects = models.HeadCircumference.objects.filter(child=child)
        if objects:
            (
                context["html"],
                context["js"],
            ) = graphs.head_circumference_change(objects)
        return context


class HeightChangeChildReport(PermissionRequiredMixin, DetailView):
    """
    Graph of height change over time.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/height_change.html"

    def get_context_data(self, **kwargs):
        context = super(HeightChangeChildReport, self).get_context_data(**kwargs)
        child = context["object"]
        objects = models.Height.objects.filter(child=child)
        if objects:
            context["html"], context["js"] = graphs.height_change(objects)
        return context


class PumpingAmounts(PermissionRequiredMixin, DetailView):
    """
    Graph of pumping milk amounts collected.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/pumping_amounts.html"

    def get_context_data(self, **kwargs):
        context = super(PumpingAmounts, self).get_context_data(**kwargs)
        child = context["object"]
        changes = models.Pumping.objects.filter(child=child)
        if changes and changes.count() > 0:
            context["html"], context["js"] = graphs.pumping_amounts(changes)
        return context


class SleepPatternChildReport(PermissionRequiredMixin, DetailView):
    """
    Graph of sleep pattern comparing sleep to wake times by day.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/sleep_pattern.html"

    def __init__(self):
        super(SleepPatternChildReport, self).__init__()
        self.html = ""
        self.js = ""

    def get_context_data(self, **kwargs):
        context = super(SleepPatternChildReport, self).get_context_data(**kwargs)
        child = context["object"]
        instances = models.Sleep.objects.filter(child=child).order_by("start")
        if instances:
            context["html"], context["js"] = graphs.sleep_pattern(instances)
        return context


class SleepTotalsChildReport(PermissionRequiredMixin, DetailView):
    """
    Graph of total sleep by day.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/sleep_totals.html"

    def __init__(self):
        super(SleepTotalsChildReport, self).__init__()
        self.html = ""
        self.js = ""

    def get_context_data(self, **kwargs):
        context = super(SleepTotalsChildReport, self).get_context_data(**kwargs)
        child = context["object"]
        instances = models.Sleep.objects.filter(child=child).order_by("start")
        if instances:
            context["html"], context["js"] = graphs.sleep_totals(instances)
        return context


class TemperatureChangeChildReport(PermissionRequiredMixin, DetailView):
    """
    Graph of temperature change over time.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/temperature_change.html"

    def get_context_data(self, **kwargs):
        context = super(TemperatureChangeChildReport, self).get_context_data(**kwargs)
        child = context["object"]
        objects = models.Temperature.objects.filter(child=child)
        if objects:
            context["html"], context["js"] = graphs.temperature_change(objects)
        return context


class TummyTimeDurationChildReport(PermissionRequiredMixin, DetailView):
    """
    Graph of tummy time durations over time.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/tummytime_duration.html"

    def __init__(self):
        super(TummyTimeDurationChildReport, self).__init__()
        self.html = ""
        self.js = ""

    def get_context_data(self, **kwargs):
        context = super(TummyTimeDurationChildReport, self).get_context_data(**kwargs)
        child = context["object"]
        instances = models.TummyTime.objects.filter(child=child)
        if instances:
            context["html"], context["js"] = graphs.tummytime_duration(instances)
        return context


class WeightChangeChildReport(PermissionRequiredMixin, DetailView):
    """
    Graph of weight change over time.
    """

    model = models.Child
    permission_required = ("core.view_child",)
    template_name = "reports/weight_change.html"

    def get_context_data(self, **kwargs):
        context = super(WeightChangeChildReport, self).get_context_data(**kwargs)
        child = context["object"]
        objects = models.Weight.objects.filter(child=child)
        if objects:
            context["html"], context["js"] = graphs.weight_change(objects)
        return context
