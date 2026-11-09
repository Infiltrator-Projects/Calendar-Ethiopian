// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 1993-2026 Shannon Smith

/*
 * Ethiopian Amete Mihret arithmetic calendar.
 *
 * One Coptic-style 13-month chronology owns both date conversion and period
 * navigation. The sibling conversion module defines the leap cycle and epoch;
 * this adapter keeps year-era mapping consistent between all operations.
 * Common's checked/saturating arithmetic protects intermediate calculations,
 * while ICU supplies locale-specific formatting.
 */

#include "calendar-arithmetic.h"
#include "calendar-arithmetic-internal.h"

#include "julian-day.h"

static gboolean
arithmetic_mode_supported(CalendarCalendarMode mode)
{
    switch (mode)
    {
        case CALENDAR_CALENDAR_MODE_ETHIOPIAN:
            return TRUE;
        default:
            return FALSE;
    }
}

static gint64
signed_year_from_fields(CalendarCalendarMode mode,
                        const CalendarCalendarFields *fields)
{
    switch (mode)
    {

        case CALENDAR_CALENDAR_MODE_ETHIOPIAN:
            return calendar_arithmetic_coptic_signed_year_from_fields(
                mode, fields);

        default:
            return fields->year;
    }
}

static void
set_signed_year(CalendarCalendarMode mode,
                gint64 signed_year,
                CalendarCalendarFields *fields)
{
    switch (mode)
    {

        case CALENDAR_CALENDAR_MODE_ETHIOPIAN:
            calendar_arithmetic_coptic_set_signed_year(mode, signed_year, fields);
            break;

        default:
            fields->year = signed_year;
            fields->auxiliary = 0;
            break;
    }
}

static gint
periods_per_year(CalendarCalendarMode mode)
{
    switch (mode)
    {
        case CALENDAR_CALENDAR_MODE_ETHIOPIAN:
            return 13;
        default:
            return 12;
    }
}

static gint
month_length(CalendarCalendarMode mode,
             const CalendarCalendarFields *fields)
{
    const gint64 year = signed_year_from_fields(mode, fields);

    switch (mode)
    {

        case CALENDAR_CALENDAR_MODE_ETHIOPIAN:
            return calendar_arithmetic_coptic_month_length(
                year, fields->month);

        default:
            return 0;
    }
}

static gint64
fields_to_jdn(CalendarCalendarMode mode,
              const CalendarCalendarFields *fields)
{
    const gint64 year = signed_year_from_fields(mode, fields);

    switch (mode)
    {

        case CALENDAR_CALENDAR_MODE_ETHIOPIAN:
            return calendar_arithmetic_coptic_fields_to_jdn(
                mode, year, fields->month, fields->day);

        default:
            return CALENDAR_UNIX_EPOCH_JDN;
    }
}

gboolean
calendar_arithmetic_fields_from_jdn(
    CalendarCalendarMode mode,
    gint64 jdn,
    CalendarCalendarFields *fields)
{

    g_return_val_if_fail(fields != NULL, FALSE);
    *fields = (CalendarCalendarFields){ 0 };

    switch (mode)
    {

        case CALENDAR_CALENDAR_MODE_ETHIOPIAN:
            return calendar_arithmetic_coptic_fields_from_jdn(
                mode, jdn, fields);

        default:
            return FALSE;
    }
}

gint64
calendar_arithmetic_month_start(
    CalendarCalendarMode mode,
    gint64 jdn)
{
    CalendarCalendarFields fields;

    if (!arithmetic_mode_supported(mode) ||
        !calendar_arithmetic_fields_from_jdn(mode, jdn, &fields))
    {
        return G_MAXINT64;
    }

    fields.day = 1;
    return fields_to_jdn(mode, &fields);
}

gint64
calendar_arithmetic_add_months(
    CalendarCalendarMode mode,
    gint64 jdn,
    gint amount)
{
    CalendarCalendarFields fields;
    gint64 year;
    gint64 serial;
    gint period_count;
    gint target_month;

    if (!arithmetic_mode_supported(mode) ||
        !calendar_arithmetic_fields_from_jdn(mode, jdn, &fields))
    {
        return G_MAXINT64;
    }

    year = signed_year_from_fields(mode, &fields);
    period_count = periods_per_year(mode);
    serial = calendar_i64_add_saturating(
        calendar_i64_add_saturating(
            calendar_i64_multiply_saturating(year, period_count),
            fields.month - 1),
        amount);
    year = calendar_floor_divide(serial, period_count);
    target_month = (gint)calendar_positive_modulo(serial, period_count) + 1;

    set_signed_year(mode, year, &fields);
    fields.month = target_month;
    fields.day = MIN(fields.day, month_length(mode, &fields));
    return fields_to_jdn(mode, &fields);
}

gint64
calendar_arithmetic_add_years(
    CalendarCalendarMode mode,
    gint64 jdn,
    gint amount)
{
    CalendarCalendarFields fields;
    gint64 year;

    if (!arithmetic_mode_supported(mode) ||
        !calendar_arithmetic_fields_from_jdn(mode, jdn, &fields))
    {
        return G_MAXINT64;
    }

    year = calendar_i64_add_saturating(
        signed_year_from_fields(mode, &fields), amount);
    set_signed_year(mode, year, &fields);
    fields.day = MIN(fields.day, month_length(mode, &fields));
    return fields_to_jdn(mode, &fields);
}
