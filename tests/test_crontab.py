import datetime as dt

import freezegun
import pytest

from crontools.crontab import Crontab
from crontools.crontab import SecondsField, MinuteField, HourField, MonthdayField, MonthField, WeekdayField, YearField
from crontools.crontab import SecondsRange, MinuteRange, HourRange, MonthdayRange, MonthRange, WeekdayRange, YearRange


@pytest.mark.parametrize(
    'expr, minute_field, hour_field, monthday_field, month_field, weekday_field, second_field, year_field, '
    'seconds_ext, years_ext',
    [
        (
            '* * * * *',
            MinuteField((MinuteRange(None, None, None),)),
            HourField((HourRange(None, None, None),)),
            MonthdayField((MonthdayRange(None, None, None),)),
            MonthField((MonthRange(None, None, None),)),
            WeekdayField((WeekdayRange(None, None, None),)),
            SecondsField((SecondsRange(0, None, None),)),
            YearField((YearRange(2020, 2099, None),)),
            False,
            False,
        ),
        (
            '30 * * * * *',
            MinuteField((MinuteRange(None, None, None),)),
            HourField((HourRange(None, None, None),)),
            MonthdayField((MonthdayRange(None, None, None),)),
            MonthField((MonthRange(None, None, None),)),
            WeekdayField((WeekdayRange(None, None, None),)),
            SecondsField((SecondsRange(30, None, None),)),
            YearField((YearRange(2020, 2099, None),)),
            True,
            False,
        ),
        (
            '* * * * * 2000',
            MinuteField((MinuteRange(None, None, None),)),
            HourField((HourRange(None, None, None),)),
            MonthdayField((MonthdayRange(None, None, None),)),
            MonthField((MonthRange(None, None, None),)),
            WeekdayField((WeekdayRange(None, None, None),)),
            SecondsField((SecondsRange(0, None, None),)),
            YearField((YearRange(2000, None, None),)),
            False,
            True,
        ),

        (
            '0 0-23 */2 1,2-3,4-12/2 0,1,2',
            MinuteField((MinuteRange(0, None, None),)),
            HourField((HourRange(0, 23, None),)),
            MonthdayField((MonthdayRange(None, None, 2),)),
            MonthField((MonthRange(1, None, None), MonthRange(2, 3, None), MonthRange(4, 12, 2))),
            WeekdayField((WeekdayRange(1, None, None), WeekdayRange(2, None, None), WeekdayRange(7, None, None))),
            SecondsField((SecondsRange(0, None, None),)),
            YearField((YearRange(2020, 2099, None),)),
            False,
            False,
        ),
        (
            '* * * JAN-DEC/2 SUN,TUE-fri',
            MinuteField((MinuteRange(None, None, None),)),
            HourField((HourRange(None, None, None),)),
            MonthdayField((MonthdayRange(None, None, None),)),
            MonthField((MonthRange(1, 12, 2),)),
            WeekdayField((WeekdayRange(2, 5, None), WeekdayRange(7, None, None))),
            SecondsField((SecondsRange(0, None, None),)),
            YearField((YearRange(2020, 2099, None),)),
            False,
            False,
        ),
    ],
)
@freezegun.freeze_time('2020-01-01 00:00:00.000Z+00:00')
def test_cron_parser(
        expr, minute_field, hour_field, monthday_field, month_field, weekday_field, second_field, year_field,
        seconds_ext, years_ext,
):
    cron = Crontab.parse(expr, seconds_ext=seconds_ext, years_ext=years_ext)

    assert cron.second_field == second_field
    assert cron.minute_field == minute_field
    assert cron.hour_field == hour_field
    assert cron.monthday_field == monthday_field
    assert cron.month_field == month_field
    assert cron.weekday_field == weekday_field
    assert cron.year_field == year_field


@pytest.mark.parametrize(
    'expr, exc, message',
    [
        (
            'a * * * *',
            ValueError,
            "minute value must be of type int",
        ),
        (
            '* 1-! * * *',
            ValueError,
            "hour value must be of type int",
        ),
        (
            '* * 1-12/. * *',
            ValueError,
            "day value must be of type int",
        ),
        (
            '*/* * * * *',
            ValueError,
            "minute value must be of type int",
        ),
        (
            '*// * * * *',
            ValueError,
            "minute value must be of type int",
        ),
        (
            '1-- * * * *',
            ValueError,
            "minute value must be of type int",
        ),
        (
            '1,, * * * *',
            ValueError,
            "minute value must be of type int",
        ),
        (
            '* 2-1 * * *',
            ValueError,
            "hour range is empty",
        ),
        (
            '60 * * * *',
            ValueError,
            r"minute value must be of range \[0, 59\]",
        ),
        (
            '* 24 * * *',
            ValueError,
            r"hour value must be of range \[0, 23\]",
        ),
        (
            '* * 32 * *',
            ValueError,
            r"day value must be of range \[1, 31\]",
        ),
        (
            '* * * 13 *',
            ValueError,
            r"month value must be of range \[1, 12\]",
        ),
        (
            '* * * * 8',
            ValueError,
            r"weekday value must be of range \[1, 7\]",
        ),
        (
            '* * 0 * *',
            ValueError,
            r"day value must be of range \[1, 31\]",
        ),
        (
            '* * * 0 *',
            ValueError,
            r"month value must be of range \[1, 12\]",
        ),
        (
            '* * * *',
            ValueError,
            r"crontab expression must be of 5 fields",
        ),
    ],
)
@freezegun.freeze_time('2020-01-01 00:00:00.000Z+00:00')
def test_cron_parser_errors(expr, exc, message):
    with pytest.raises(exc, match=message):
        Crontab.parse(expr)


@pytest.mark.parametrize(
    'expr, seconds_ext, year_ext',
    [
        (
            '* * * * *',
            False,
            False,
        ),
        (
            '*/2 * * * * * *',
            True,
            True,
        ),
        (
            '1 1 1 1 1 1 1990',
            True,
            True,
        ),
        (
            '0-59 0-23 1-31 1-12 1-7',
            False,
            False,
        ),
        (
            '1-15/2,20-30/2 1-5/2,10-15/2 5-5/2,6-7/2 3-8/2 4-5/3',
            False,
            False,
        ),
        (
            '0-59 0-59 0-23 1-31 1-12 1-7 1970-2099',
            True,
            True,
        ),
    ],
)
@freezegun.freeze_time('2020-01-01 00:00:00.000Z+00:00')
def test_cron_str(expr, seconds_ext, year_ext):
    cron = Crontab.parse(expr, seconds_ext=seconds_ext, years_ext=year_ext)
    assert str(cron) == expr


@pytest.mark.parametrize(
    'expr, Field, result, start_from',
    [
        (
            '*/10',
            MinuteField,
            [0, 10, 20, 30, 40, 50],
            None,
        ),
        (
            '1,2,5,10-20/2,13,40,40',
            MinuteField,
            [1, 2, 5, 10, 12, 13, 14, 16, 18, 20, 40],
            None,
        ),
        (
            '8-23',
            HourField,
            [20, 21, 22, 23],
            20,
        ),
        (
            '*',
            MonthdayField,
            [1, 2, 3, 4, 5, 6, 7],
            None,
        ),
        (
            'TUE-FRI',
            WeekdayField,
            [2, 3, 4, 5],
            None,
        ),
        (
            'JAN-DEC',
            MonthField,
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            None,
        ),
        (
            '2020',
            YearField,
            [2020],
            None,
        ),
    ],
)
@freezegun.freeze_time('2020-01-01 00:00:00.000Z+00:00')
def test_cron_field_iterator(expr, Field, result, start_from):
    field = Field.fromstr(expr)

    for actual, expected in zip(field.iter(start_from), result):
        assert actual == expected


@pytest.mark.parametrize(
    'expr, result, years_ext, seconds_ext',
    [
        (
            '0 0 1 1 *',
            [
                dt.datetime(year=2020, month=1, day=1, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2021, month=1, day=1, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
            ],
            False,
            False,
        ),
        (
            '0 0 * * TUE,FRI',
            [
                dt.datetime(year=2020, month=1, day=3,  hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=7,  hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=10, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=14, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
            ],
            False,
            False,
        ),
        (
            '0 0 10,3,2,1 * TUE,FRI',
            [
                dt.datetime(year=2020, month=1, day=1,  hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=2,  hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=3,  hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=7,  hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=10, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=14, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
            ],
            False,
            False,
        ),
        (
            '0 1-10/2,2 1 1 *',
            [
                dt.datetime(year=2020, month=1, day=1, hour=1, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=1, hour=2, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=1, hour=3, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=1, hour=5, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=1, hour=7, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=1, hour=9, minute=0, second=0, tzinfo=dt.timezone.utc),
            ],
            False,
            False,
        ),
        (
            '0 0 0 28-31 2,3 * 2020',
            [
                dt.datetime(year=2020, month=2,  day=28, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=2,  day=29, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=3,  day=28, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
            ],
            True,
            True,
        ),
        (
            '0 0 0 28-31 2,3 * 2021',
            [
                dt.datetime(year=2021, month=2, day=28, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2021, month=3, day=28, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
            ],
            True,
            True,
        ),
        (
            '0 0 0 1 1-5,2-4,3 * 2020,2021',
            [
                dt.datetime(year=2020, month=1,  day=1, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=2,  day=1, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=3,  day=1, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=4,  day=1, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=5,  day=1, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2021, month=1,  day=1, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
            ],
            True,
            True,
        ),
    ],
)
@freezegun.freeze_time('2020-01-01 00:00:00.000Z+00:00')
def test_cron_iterator(expr, result, years_ext, seconds_ext):
    cron = Crontab.parse(expr, years_ext=years_ext, seconds_ext=seconds_ext, tz=dt.timezone.utc)

    for actual, expected in zip(cron, result):
        assert actual == expected


@pytest.mark.parametrize(
    'expr, start_from, result, years_ext, seconds_ext',
    [
        (
            '* * * * * *',
            dt.datetime(year=2020, month=2,  day=28, hour=12, minute=30, second=0, microsecond=1, tzinfo=dt.timezone.utc),
            [
                dt.datetime(year=2020, month=2,  day=28, hour=12, minute=31, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=2,  day=28, hour=12, minute=32, second=0, tzinfo=dt.timezone.utc),
            ],
            True,
            False,
        ),
        (
            '* * * * * * *',
            dt.datetime(year=2020, month=1, day=1, hour=12, minute=30, second=0, microsecond=1, tzinfo=dt.timezone.utc),
            [
                dt.datetime(year=2020, month=1, day=1, hour=12, minute=30, second=1, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=1, hour=12, minute=30, second=2, tzinfo=dt.timezone.utc),
            ],
            True,
            True,
        ),
        (
            '0 * * * * * *',
            dt.datetime(year=2020, month=1, day=1, hour=12, minute=30, second=0, microsecond=1, tzinfo=dt.timezone.utc),
            [
                dt.datetime(year=2020, month=1, day=1, hour=12, minute=31, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=1, day=1, hour=12, minute=32, second=0, tzinfo=dt.timezone.utc),
            ],
            True,
            True,
        ),
        (
            '0 0 * * *',
            dt.datetime(year=2020, month=2, day=28, hour=0, minute=0, second=0, microsecond=1, tzinfo=dt.timezone.utc),
            [
                dt.datetime(year=2020, month=2, day=29, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2020, month=3, day=1, hour=0, minute=0, second=0, tzinfo=dt.timezone.utc),
            ],
            False,
            False,
        ),
        (
            '0 0 1-31 * *',
            dt.datetime(year=2020, month=1, day=1, tzinfo=dt.timezone.utc),
            [
                dt.datetime(year=2020, month=1, day=1, tzinfo=dt.timezone.utc) + dt.timedelta(days=day)
                for day in range(368)
            ],
            False,
            False,
        ),
        (
            '0 0 * * MON-SUN',
            dt.datetime(year=2020, month=1, day=1, tzinfo=dt.timezone.utc),
            [
                dt.datetime(year=2020, month=1, day=1, tzinfo=dt.timezone.utc) + dt.timedelta(days=day)
                for day in range(367*7)
            ],
            False,
            False,
        ),
    ],
)
@freezegun.freeze_time('2020-01-01 00:00:00.000Z+00:00')
def test_cron_iterator_start_from(expr, start_from, result, years_ext, seconds_ext):
    cron = Crontab.parse(expr, years_ext=years_ext, seconds_ext=seconds_ext, tz=dt.timezone.utc)

    for actual, expected in zip(cron.iter(start_from), result):
        assert actual == expected


@pytest.mark.parametrize(
    'expr, now, result, years_ext, seconds_ext',
    [
        (
            '* * * * *',
            dt.datetime(year=2021, month=3, day=13, hour=23, minute=14, second=0, microsecond=1, tzinfo=dt.timezone.utc),
            dt.datetime(year=2021, month=3, day=13, hour=23, minute=15, second=0, microsecond=0, tzinfo=dt.timezone.utc),
            False,
            False,
        ),
        (
            '* * * * * *',
            dt.datetime(year=2021, month=3, day=13, hour=23, minute=14, second=0, microsecond=1, tzinfo=dt.timezone.utc),
            dt.datetime(year=2021, month=3, day=13, hour=23, minute=14, second=1, microsecond=0, tzinfo=dt.timezone.utc),
            False,
            True,
        ),
        (
            '* * * * *',
            dt.datetime(year=2020, month=2, day=28, hour=23, minute=59, second=1, tzinfo=dt.timezone.utc),
            dt.datetime(year=2020, month=2, day=29, hour=0, minute=0, tzinfo=dt.timezone.utc),
            False,
            False,
        ),
        (
            '* * * * *',
            dt.datetime(year=2020, month=12, day=31, hour=23, minute=59, second=1, tzinfo=dt.timezone.utc),
            dt.datetime(year=2021, month=1,  day=1,  hour=0,  minute=0, tzinfo=dt.timezone.utc),
            False,
            False,
        ),
        (
            '1 42 13 12 3 * 2021',
            dt.datetime(year=2021, month=3, day=12, hour=13, minute=42, second=1, microsecond=1, tzinfo=dt.timezone.utc),
            None,
            True,
            True,
        ),
        (
                '0 0 * * MON',
                dt.datetime(year=2021, month=2, day=28, hour=0, minute=0, second=0, microsecond=0, tzinfo=dt.timezone.utc),
                dt.datetime(year=2021, month=3, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=dt.timezone.utc),
                False,
                False,
        ),
        (
                '0 0 * * WED,THU',
                dt.datetime(year=2021, month=3, day=31, hour=0, minute=0, second=0, microsecond=1, tzinfo=dt.timezone.utc),
                dt.datetime(year=2021, month=4, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=dt.timezone.utc),
                False,
                False,
        ),
    ],
)
@freezegun.freeze_time('2020-01-01 00:00:00.000Z+00:00')
def test_cron_next_fire_time(expr, now, result, years_ext, seconds_ext):
    cron = Crontab.parse(expr, years_ext=years_ext, seconds_ext=seconds_ext, tz=dt.timezone.utc)

    assert cron.next_fire_time(now) == result
