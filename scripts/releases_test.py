#!/usr/bin/env python3


from textwrap import dedent
from unittest import mock

from releases import get_releases

GIT_TAGS = dedent(
    """
    2017-06-26T22:31:52+02:00|0.1
    2017-07-09T11:37:55+02:00|0.2
    2017-07-17T22:08:58+02:00|0.2.1
    2017-12-11T21:16:02+01:00|0.2.2
    2017-12-12T23:55:09+01:00|0.2.3
    2017-12-14T23:08:49+01:00|0.2.4
    2017-12-16T16:15:42+01:00|0.2.5
    2017-12-16T16:40:52+01:00|0.2.6
    2017-12-26T21:29:05+01:00|0.3
    2017-12-27T23:36:54+01:00|0.3.1
    2017-12-27T23:44:11+01:00|0.3.2
    2018-01-07T22:27:43+01:00|0.3.3
    2018-01-07T22:52:04+01:00|0.3.4
    2018-01-07T23:08:10+01:00|0.3.5
    2018-02-18T14:48:53+01:00|0.4
    2018-02-24T15:37:50+01:00|0.5
    2018-02-24T18:08:07+01:00|0.5.1
    2018-02-26T21:39:41+01:00|0.5.2
    2018-02-27T23:10:45+01:00|0.5.3
    2018-02-28T19:29:47+01:00|0.5.4
    2018-03-04T15:16:57+01:00|0.6
    2018-03-06T21:56:21+01:00|0.6.1
    2018-03-21T21:05:15+01:00|0.7
    2018-04-02T20:04:53+02:00|0.8
    2018-04-17T21:31:49+02:00|0.9
    2018-04-17T23:20:48+02:00|0.9.1
    2018-04-23T19:44:48+02:00|0.10
    2018-05-06T16:24:23+02:00|0.11
    2018-05-09T23:46:23+02:00|0.12
    2018-05-19T11:43:36+02:00|0.13
    2018-06-02T18:11:24+02:00|0.14
    2018-06-06T22:03:42+02:00|0.14.1
    2018-06-16T15:04:57+02:00|0.14.2
    2018-06-24T16:00:40+02:00|0.15
    2018-07-22T22:44:16+02:00|0.16
    2018-08-19T19:05:22+02:00|0.16.1
    2018-08-21T19:03:14+02:00|0.16.2
    2018-08-21T20:34:15+02:00|0.16.3
    2018-10-07T11:53:35+02:00|0.17
    2019-01-22T12:05:12+01:00|0.18
    2019-01-29T14:25:50+01:00|0.18.1
    2019-02-13T09:28:23+01:00|0.18.2
    2019-03-21T10:41:32+01:00|0.18.3
    2019-05-16T12:30:38+02:00|0.19.0
    2019-05-02T14:26:46+02:00|0.19.0-rc1
    2019-05-10T10:05:26+02:00|0.19.0-rc2
    2019-06-28T10:25:35+02:00|0.19.1
    2019-10-04T10:42:33+02:00|0.20.0
    2019-09-24T15:28:11+02:00|0.20.0-rc1
    2019-10-28T10:54:39+01:00|0.20.1
    2020-04-24T10:11:25+02:00|0.21
    2020-04-09T09:57:16+02:00|0.21-rc1
    2020-04-22T11:10:55+02:00|0.21-rc2
    2020-06-11T10:44:20+02:00|0.21.1
    2020-07-27T11:21:40+02:00|0.21.2
    2020-09-09T07:48:14+02:00|1.0
    2020-08-23T15:21:29+02:00|1.0-rc1
    2020-10-31T12:43:37+01:00|1.0.1
    2021-03-10T10:25:28+01:00|1.1
    2021-02-24T08:18:56+01:00|1.1-rc1
    2021-03-01T19:21:36+01:00|1.1-rc2
    2021-04-13T10:27:07+02:00|1.1.1
    2021-05-19T15:30:51+02:00|1.1.2
    2021-08-01T22:04:02+02:00|1.1.3
    2021-08-02T20:47:50+02:00|1.1.4
    2021-12-27T20:56:03+01:00|1.2.0
    2021-12-08T20:15:55+01:00|1.2.0-rc1
    2021-12-21T09:12:57+00:00|1.2.0-rc2
    2021-11-05T09:24:36+00:00|1.2.0-testing
    2021-11-05T09:31:10+00:00|1.2.0-testing2
    2021-11-05T09:43:30+00:00|1.2.0-testing3
    2021-11-05T12:00:26+00:00|1.2.0-testing4
    2022-01-06T17:35:53+01:00|1.2.1
    2022-02-04T12:49:11+01:00|1.2.2
    2022-03-18T10:57:16+01:00|1.2.3
    2022-04-23T13:40:06+02:00|1.2.4
    2022-05-07T13:48:31+02:00|1.2.5
    2022-07-04T17:03:19+02:00|1.2.6
    2022-07-05T15:43:08+02:00|1.2.6-1
    2022-07-14T12:53:53+02:00|1.2.7
    2022-09-12T10:51:44+02:00|1.2.8
    2022-11-25T17:59:23+01:00|1.2.9
    2023-01-20T09:40:58+01:00|1.3.0-rc1
    2023-01-23T10:41:22+01:00|1.3.0-rc2
    2023-01-23T14:24:46+01:00|1.3.0-rc3
    """
)


def test_get_releases():
    with mock.patch("subprocess.check_output") as check_output_mock:
        check_output_mock.return_value = GIT_TAGS

        assert get_releases() == [
            {"id": "1.2.9", "date": "2022-11-25T17:59:23+01:00"},
            {"id": "1.2.8", "date": "2022-09-12T10:51:44+02:00"},
            {"id": "1.2.7", "date": "2022-07-14T12:53:53+02:00"},
            {"id": "1.2.6-1", "date": "2022-07-05T15:43:08+02:00"},
            {"id": "1.2.6", "date": "2022-07-04T17:03:19+02:00"},
            {"id": "1.2.5", "date": "2022-05-07T13:48:31+02:00"},
            {"id": "1.2.4", "date": "2022-04-23T13:40:06+02:00"},
            {"id": "1.2.3", "date": "2022-03-18T10:57:16+01:00"},
            {"id": "1.2.2", "date": "2022-02-04T12:49:11+01:00"},
            {"id": "1.2.1", "date": "2022-01-06T17:35:53+01:00"},
            {"id": "1.2.0", "date": "2021-12-27T20:56:03+01:00"},
            {"id": "1.1.4", "date": "2021-08-02T20:47:50+02:00"},
            {"id": "1.1.3", "date": "2021-08-01T22:04:02+02:00"},
            {"id": "1.1.2", "date": "2021-05-19T15:30:51+02:00"},
            {"id": "1.1.1", "date": "2021-04-13T10:27:07+02:00"},
            {"id": "1.1", "date": "2021-03-10T10:25:28+01:00"},
            {"id": "1.0.1", "date": "2020-10-31T12:43:37+01:00"},
            {"id": "1.0", "date": "2020-09-09T07:48:14+02:00"},
            {"id": "0.21.2", "date": "2020-07-27T11:21:40+02:00"},
            {"id": "0.21.1", "date": "2020-06-11T10:44:20+02:00"},
            {"id": "0.21", "date": "2020-04-24T10:11:25+02:00"},
            {"id": "0.20.1", "date": "2019-10-28T10:54:39+01:00"},
            {"id": "0.20.0", "date": "2019-10-04T10:42:33+02:00"},
            {"id": "0.19.1", "date": "2019-06-28T10:25:35+02:00"},
            {"id": "0.19.0", "date": "2019-05-16T12:30:38+02:00"},
            {"id": "0.18.3", "date": "2019-03-21T10:41:32+01:00"},
            {"id": "0.18.2", "date": "2019-02-13T09:28:23+01:00"},
            {"id": "0.18.1", "date": "2019-01-29T14:25:50+01:00"},
            {"id": "0.18", "date": "2019-01-22T12:05:12+01:00"},
            {"id": "0.17", "date": "2018-10-07T11:53:35+02:00"},
            {"id": "0.16.3", "date": "2018-08-21T20:34:15+02:00"},
            {"id": "0.16.2", "date": "2018-08-21T19:03:14+02:00"},
            {"id": "0.16.1", "date": "2018-08-19T19:05:22+02:00"},
            {"id": "0.16", "date": "2018-07-22T22:44:16+02:00"},
            {"id": "0.15", "date": "2018-06-24T16:00:40+02:00"},
            {"id": "0.14.2", "date": "2018-06-16T15:04:57+02:00"},
            {"id": "0.14.1", "date": "2018-06-06T22:03:42+02:00"},
            {"id": "0.14", "date": "2018-06-02T18:11:24+02:00"},
            {"id": "0.13", "date": "2018-05-19T11:43:36+02:00"},
            {"id": "0.12", "date": "2018-05-09T23:46:23+02:00"},
            {"id": "0.11", "date": "2018-05-06T16:24:23+02:00"},
            {"id": "0.10", "date": "2018-04-23T19:44:48+02:00"},
            {"id": "0.9.1", "date": "2018-04-17T23:20:48+02:00"},
            {"id": "0.9", "date": "2018-04-17T21:31:49+02:00"},
            {"id": "0.8", "date": "2018-04-02T20:04:53+02:00"},
            {"id": "0.7", "date": "2018-03-21T21:05:15+01:00"},
            {"id": "0.6.1", "date": "2018-03-06T21:56:21+01:00"},
            {"id": "0.6", "date": "2018-03-04T15:16:57+01:00"},
            {"id": "0.5.4", "date": "2018-02-28T19:29:47+01:00"},
            {"id": "0.5.3", "date": "2018-02-27T23:10:45+01:00"},
            {"id": "0.5.2", "date": "2018-02-26T21:39:41+01:00"},
            {"id": "0.5.1", "date": "2018-02-24T18:08:07+01:00"},
            {"id": "0.5", "date": "2018-02-24T15:37:50+01:00"},
            {"id": "0.4", "date": "2018-02-18T14:48:53+01:00"},
            {"id": "0.3.5", "date": "2018-01-07T23:08:10+01:00"},
            {"id": "0.3.4", "date": "2018-01-07T22:52:04+01:00"},
            {"id": "0.3.3", "date": "2018-01-07T22:27:43+01:00"},
            {"id": "0.3.2", "date": "2017-12-27T23:44:11+01:00"},
            {"id": "0.3.1", "date": "2017-12-27T23:36:54+01:00"},
            {"id": "0.3", "date": "2017-12-26T21:29:05+01:00"},
            {"id": "0.2.6", "date": "2017-12-16T16:40:52+01:00"},
            {"id": "0.2.5", "date": "2017-12-16T16:15:42+01:00"},
            {"id": "0.2.4", "date": "2017-12-14T23:08:49+01:00"},
            {"id": "0.2.3", "date": "2017-12-12T23:55:09+01:00"},
            {"id": "0.2.2", "date": "2017-12-11T21:16:02+01:00"},
            {"id": "0.2.1", "date": "2017-07-17T22:08:58+02:00"},
            {"id": "0.2", "date": "2017-07-09T11:37:55+02:00"},
            {"id": "0.1", "date": "2017-06-26T22:31:52+02:00"},
        ]
