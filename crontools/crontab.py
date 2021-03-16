import calendar
import dataclasses as dc
import datetime as dt
import heapq
import itertools as it
import operator as op
import tzlocal
from typing import Any, ClassVar, Dict, Generic, Iterator, Iterable, Optional, Type, TypeVar, Tuple


def unique(iterable: Iterable[Any]) -> Iterator[Any]:
    """
    Returns iterator over all values skipping consecutive duplicates (similar to unix 'uniq' utility).

    :param iterable: iterable object to iterate over
    :return: iterator
    """

    it = iter(iterable)

    prev = None
    for val in it:
        if val == prev:
            continue
        prev = val
        yield val


@dc.dataclass(frozen=True)
class Range:
    """
    Crontab expression range.

    :param begin: interval begin
    :param end: interval end
    :param step: interval step
    """

    title: ClassVar[str]
    min_value: ClassVar[int]
    max_value: ClassVar[int]
    aliases: ClassVar[Optional[Dict[str, int]]]

    begin: Optional[int] = None
    end: Optional[int] = None
    step: Optional[int] = None

    @classmethod
    def __init_subclass__(cls, title: str, min_value: int, max_value: int, aliases: Optional[Dict[str, int]] = None):
        cls.title = title
        cls.min_value = min_value
        cls.max_value = max_value
        cls.aliases = aliases

    def __iter__(self) -> Iterator[int]:
        return self.iter()

    def __str__(self) -> str:
        if self.begin is None:
            result = "*"
        else:
            result = f"{self.begin}"

        if self.end is not None:
            result = f"{result}-{self.end}"

        if self.step is not None:
            result = f"{result}/{self.step}"

        return result

    @classmethod
    def fromstr(cls, string: str) -> 'Range':
        """
        Parses crontab expression range.

        :param string: crontab expression range string
        :return: range
        """

        begin, end, step = None, None, None
        string = string.strip()

        interval, *maybe_step = string.split('/', maxsplit=1)
        if maybe_step:
            maybe_step = maybe_step[0]
            step = cls._parse_number(maybe_step)

        if interval == '*':
            return cls(None, None, step)

        begin, *maybe_end = interval.split('-', maxsplit=1)
        begin = cls.aliases.get(begin, begin) if cls.aliases else begin
        begin = cls._parse_number(begin)
        if maybe_end:
            maybe_end = maybe_end[0]
            maybe_end = cls.aliases.get(maybe_end, maybe_end) if cls.aliases else maybe_end

            end = cls._parse_number(maybe_end)
            if begin > end:
                raise ValueError(f"{cls.title} range is empty")

        return cls(begin, end, step)

    @classmethod
    def _parse_number(cls, value: str):
        try:
            value = int(value)
        except ValueError:
            raise ValueError(f"{cls.title} value must be of type int, got: {value}")

        if not (cls.min_value <= value <= cls.max_value):
            raise ValueError(f"{cls.title} value must be of range [{cls.min_value}, {cls.max_value}], got: {value}")

        return value

    @property
    def is_default(self) -> bool:
        """
        Is range has default value (asterisk value).
        """

        return self.begin is None

    def iter(self, start_from: Optional[int] = None) -> Iterator[int]:
        """
        Returns iterator over range values starting from `start_from`.

        :param start_from: range value to iterate from
        :return: range values iterator
        """

        if self.is_default:
            begin = self.min_value
            end = self.max_value
        else:
            begin = self.begin
            end = self.begin if self.end is None else self.end

        step = 1 if self.step is None else self.step

        if start_from is not None:
            begin = max(begin, start_from)

        return iter(range(begin, end + 1, step))


@dc.dataclass(frozen=True)
class SecondsRange(Range, title='second', min_value=0, max_value=59):
    """
    Crontab expression second range.
    """


@dc.dataclass(frozen=True)
class MinuteRange(Range, title='minute', min_value=0, max_value=59):
    """
    Crontab expression minute range.
    """


@dc.dataclass(frozen=True)
class HourRange(Range, title='hour', min_value=0, max_value=23):
    """
    Crontab expression hour range.
    """


@dc.dataclass(frozen=True)
class MonthdayRange(Range, title='day', min_value=1, max_value=31):
    """
    Crontab expression day range.
    """


@dc.dataclass(frozen=True)
class MonthRange(
    Range, title='month', min_value=1, max_value=12, aliases={
        'JAN':  1, 'FEB':  2, 'MAR':  3,
        'APR':  4, 'MAY':  5, 'JUN':  6,
        'JUL':  7, 'AUG':  8, 'SEP':  9,
        'OCT': 10, 'NOV': 11, 'DEC': 12,

        'jan':  1, 'feb':  2, 'mar':  3,
        'apr':  4, 'may':  5, 'jun':  6,
        'jul':  7, 'aug':  8, 'sep':  9,
        'oct': 10, 'nov': 11, 'dec': 12,
    },
):
    """
    Crontab expression month range.
    """


@dc.dataclass(frozen=True)
class WeekdayRange(
    Range, title='weekday', min_value=1, max_value=7, aliases={
        'MON': 1, 'TUE': 2, 'WED': 3,
        'THU': 4, 'FRI': 5, 'SAT': 6,
        'SUN': 7,

        'mon': 1, 'tue': 2, 'wed': 3,
        'thu': 4, 'fri': 5, 'sat': 6,
        'sun': 7, '0': 7,
    },
):
    """
    Crontab expression weekday range.
    """


@dc.dataclass(frozen=True)
class YearRange(Range, title='year', min_value=1970, max_value=2099):
    """
    Crontab expression year range.
    """


RangeType = TypeVar('RangeType', bound=Range)


@dc.dataclass(frozen=True)
class Field(Generic[RangeType]):
    """
    Crontab expression field.

    :param ranges: crontab expression range list
    """

    range_type: ClassVar[Type[Range]]

    ranges: Tuple[RangeType, ...]

    def __str__(self) -> str:
        return ",".join(map(str, self.ranges))

    def __iter__(self) -> Iterator[int]:
        return self.iter()

    def iter(self, start_from: Optional[int] = None) -> Iterator[int]:
        """
        Returns iterator over field values starting from `start_from`.

        :param start_from: value to iterate from
        :return: iterator over all field values
        """

        return unique(heapq.merge(*(rng.iter(start_from=start_from) for rng in self.ranges)))

    @classmethod
    def __init_subclass__(cls, range_type: Type[Range]):
        cls.range_type = range_type

    @classmethod
    def fromstr(cls, string: str) -> 'Field[RangeType]':
        """
        Parses crontab expression field.

        :param string: crontab expression field string
        :return: field
        """

        ranges = (cls.range_type.fromstr(item) for item in string.split(','))

        return cls(ranges=tuple(sorted(ranges, key=lambda rng: rng.begin)))

    @property
    def is_default(self) -> bool:
        """
        Is field has only default values (asterisk values).
        """

        return all(map(op.attrgetter('is_default'), self.ranges))


class MinuteField(Field[MinuteRange], range_type=MinuteRange): pass  # noqa: E701
class HourField(Field[HourRange], range_type=HourRange): pass  # noqa: E701
class MonthdayField(Field[MonthdayRange], range_type=MonthdayRange): pass  # noqa: E701
class MonthField(Field[MonthRange], range_type=MonthRange): pass  # noqa: E701
class WeekdayField(Field[WeekdayRange], range_type=WeekdayRange): pass  # noqa: E701
class SecondsField(Field[SecondsRange], range_type=SecondsRange): pass  # noqa: E701
class YearField(Field[YearRange], range_type=YearRange): pass  # noqa: E701


class DayField:
    """
    Hybrid field providing interface to iterate over
    crontab week days and month days of the current month sequentially.
    """

    def __init__(self, monthday_field: Field[MonthdayRange], weekday_field:  Field[WeekdayRange], tz: dt.timezone):
        self._monthday_field = monthday_field
        self._weekday_field = weekday_field
        self._tz = tz

    def __iter__(self) -> Iterator[int]:
        return self.iter()

    def iter(self, year: Optional[int] = None, month: Optional[int] = None, start_from: Optional[int] = None) -> Iterator[int]:
        """
        Returns iterator over month days and week days values of a particular month and year starting from `start_from`.

        :param year: iterator year
        :param month: iterator month
        :param start_from: value to iterate from
        :return: iterator over all days
        """

        now = dt.datetime.now(tz=self._tz)
        year = now.year if year is None else year
        month = now.month if month is None else month

        if self._weekday_field.is_default:
            day_iter = self._monthday_iter(year, month)
        elif self._monthday_field.is_default:
            day_iter = self._weekday_iter(year, month)
        else:
            day_iter = heapq.merge(self._monthday_iter(year, month), self._weekday_iter(year, month))

        if start_from is not None:
            day_iter = it.dropwhile(lambda value: value < start_from, day_iter)

        return unique(day_iter)

    def _monthday_iter(self, year: int, month: int) -> Iterator[int]:
        for day in self._monthday_field:
            if day > calendar.monthrange(year, month)[1]:
                continue

            yield day

    def _weekday_iter(self, year: int, month: int, start_day: int = 1) -> Iterator[int]:
        curr_day = start_day
        curr_weekday = calendar.weekday(year, month, curr_day) + 1
        weekday_iter = self._weekday_field.iter(start_from=curr_weekday)

        for _ in range(6):
            for weekday in weekday_iter:
                curr_day += (weekday - curr_weekday)
                curr_weekday += (weekday - curr_weekday)
                if curr_day > calendar.monthrange(year, month)[1]:
                    return

                yield curr_day

            curr_day += (8 - curr_weekday)
            curr_weekday = 1
            if curr_day > calendar.monthrange(year, month)[1]:
                return

            weekday_iter = self._weekday_field.iter()


@dc.dataclass(frozen=True)
class Crontab:
    """
    Crontab.

    :param minute_field: minute field
    :param hour_field: hour field
    :param monthday_field: month day field
    :param month_field: month field
    :param weekday_field: week day field
    :param second_field: second field
    :param year_field: year field
    :param seconds_ext: use seconds extension
    :param years_ext: use year extension
    :param tz: timezone to use
    """

    minute_field: Field[MinuteRange]
    hour_field:  Field[HourRange]
    monthday_field:  Field[MonthdayRange]
    month_field:  Field[MonthRange]
    weekday_field:  Field[WeekdayRange]

    second_field: Field[SecondsRange]
    year_field: Field[YearRange]

    seconds_ext: bool = False
    years_ext: bool = False
    tz: dt.timezone = dt.timezone.utc

    @property
    def day_field(self) -> DayField:
        """
        Hybrid day field property.
        """

        return DayField(self.monthday_field, self.weekday_field, self.tz)

    def __str__(self) -> str:
        return " ".join(
            str(field) for field in (
                self.second_field if self.seconds_ext else None,
                self.minute_field,
                self.hour_field,
                self.monthday_field,
                self.month_field,
                self.weekday_field,
                self.year_field if self.years_ext else None,
            ) if field is not None
        )

    @classmethod
    def parse(
            cls,
            expr: str,
            seconds_ext: bool = False,
            years_ext: bool = False,
            tz: dt.timezone = tzlocal.get_localzone(),
            now: Optional[dt.datetime] = None,
    ) -> 'Crontab':
        """
        Parses Crontab expression.

        :param expr: crontab expression
        :param seconds_ext: use seconds extension
        :param years_ext: use years extension
        :param tz: timezone to use
        :param now: now datetime
        :return: `Crontab` instance
        """

        fields_number = 5 + seconds_ext + years_ext
        fields = expr.split()
        if len(fields) != fields_number:
            raise ValueError(f"crontab expression must be of {fields_number} fields")

        fields_iter = iter(fields)
        now = now or dt.datetime.now(tz=tz)

        return cls(
            second_field=SecondsField.fromstr(next(fields_iter)) if seconds_ext else SecondsField.fromstr('0'),
            minute_field=MinuteField.fromstr(next(fields_iter)),
            hour_field=HourField.fromstr(next(fields_iter)),
            monthday_field=MonthdayField.fromstr(next(fields_iter)),
            month_field=MonthField.fromstr(next(fields_iter)),
            weekday_field=WeekdayField.fromstr(next(fields_iter)),
            year_field=YearField.fromstr(next(fields_iter)) if years_ext else YearField.fromstr(f'{now.year}-2099'),
            seconds_ext=seconds_ext,
            years_ext=years_ext,
            tz=tz,
        )

    def __iter__(self) -> Iterator[dt.datetime]:
        for year in self.year_field:
            for month in self.month_field:
                for day in self.day_field.iter(year, month):
                    for hour in self.hour_field:
                        for minute in self.minute_field:
                            for second in self.second_field:
                                yield dt.datetime(
                                    year=year, month=month, day=day, hour=hour, minute=minute, second=second, tzinfo=self.tz,
                                )

    def iter(self, start_from: dt.datetime) -> Iterator[dt.datetime]:
        """
        Returns iterator over cron fire times starting from `start_from`.

        :param start_from: datetime to iterate from
        :return: datetime iterator
        """

        first_run = True
        year_iter = self.year_field.iter(start_from=start_from.year)

        for year in year_iter:
            if first_run and year == start_from.year:
                month_iter = self.month_field.iter(start_from=start_from.month)
            else:
                first_run = False
                month_iter = self.month_field.iter()

            for month in month_iter:
                if first_run and month == start_from.month:
                    day_iter = self.day_field.iter(year, month, start_from=start_from.day)
                else:
                    first_run = False
                    day_iter = self.day_field.iter(year, month)

                for day in day_iter:
                    if first_run and day == start_from.day:
                        hour_iter = self.hour_field.iter(start_from=start_from.hour)
                    else:
                        first_run = False
                        hour_iter = self.hour_field.iter()

                    for hour in hour_iter:
                        if first_run and hour == start_from.hour:
                            minute_iter = self.minute_field.iter(start_from=start_from.minute)
                        else:
                            first_run = False
                            minute_iter = self.minute_field.iter()

                        for minute in minute_iter:
                            if first_run and minute == start_from.minute:
                                second_iter = self.second_field.iter(start_from=start_from.second)
                            else:
                                first_run = False
                                second_iter = self.second_field.iter()

                            for second in second_iter:
                                if first_run and second == start_from.second:
                                    if start_from.microsecond:
                                        continue

                                yield dt.datetime(
                                    year=year, month=month, day=day, hour=hour, minute=minute, second=second, tzinfo=self.tz,
                                )

                            first_run = False
                        first_run = False
                    first_run = False
                first_run = False
            first_run = False

    def next_fire_time(self, now: dt.datetime) -> Optional[dt.datetime]:
        """
        Returns next cron fire time based on a current datetime

        :param now: current datetime
        :return: next fire datetime
        """

        return next(self.iter(start_from=now), None)
