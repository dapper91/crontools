=========
crontools
=========

Features:

- crontab expression parser
- optional seconds field support
- optional year field support
- crontab fire time sequential iteration support

Installation
------------

You can install crontools with pip:

.. code-block:: console

    $ pip install crontools


Quickstart
----------

On the server side everything is also pretty straightforward:

.. code-block:: python

    import datetime as dt
    import crontools as ct

    tz = dt.timezone.utc
    now = dt.datetime.fromisoformat('2021-02-01 00:00:00+00:00')
    ct = ct.Crontab.parse(
        '30 30 12-16/2 1,2 JAN SAT,SUN *',
        seconds_ext=True,
        years_ext=True,
        tz=tz,
    )

    cron_iter = ct.iter(start_from=now)
    for n, fire_datetime in zip(range(1, 31), cron_iter):
        print("{n:2}: {dt}".format(n=n, dt=fire_datetime))

    output:

     1: 2022-01-01 12:30:30+00:00
     2: 2022-01-01 14:30:30+00:00
     3: 2022-01-01 16:30:30+00:00
     4: 2022-01-02 12:30:30+00:00
     5: 2022-01-02 14:30:30+00:00
     6: 2022-01-02 16:30:30+00:00
     7: 2022-01-08 12:30:30+00:00
     8: 2022-01-08 14:30:30+00:00
     9: 2022-01-08 16:30:30+00:00
    10: 2022-01-09 12:30:30+00:00
    11: 2022-01-09 14:30:30+00:00
    12: 2022-01-09 16:30:30+00:00
    13: 2022-01-15 12:30:30+00:00
    14: 2022-01-15 14:30:30+00:00
    15: 2022-01-15 16:30:30+00:00
    16: 2022-01-16 12:30:30+00:00
    17: 2022-01-16 14:30:30+00:00
    18: 2022-01-16 16:30:30+00:00
    19: 2022-01-22 12:30:30+00:00
    20: 2022-01-22 14:30:30+00:00
    21: 2022-01-22 16:30:30+00:00
    22: 2022-01-23 12:30:30+00:00
    23: 2022-01-23 14:30:30+00:00
    24: 2022-01-23 16:30:30+00:00
    25: 2023-01-01 12:30:30+00:00
    26: 2023-01-01 14:30:30+00:00
    27: 2023-01-01 16:30:30+00:00
    28: 2023-01-02 12:30:30+00:00
    29: 2023-01-02 14:30:30+00:00
    30: 2023-01-02 16:30:30+00:00
