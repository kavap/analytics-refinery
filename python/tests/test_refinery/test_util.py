from unittest import TestCase
from datetime import datetime, timedelta
from refinery.util import HiveUtils, HivePartition, HdfsUtils, sh
import os


class TestReinferyUtil(TestCase):
    def test_sh(self):
        command = ['/bin/echo', 'test-list']
        output = sh(command)
        self.assertEqual(output, 'test-list')

        command = '/bin/echo test-string'
        output = sh(command)
        self.assertEqual(output, 'test-string')

    def test_sh_pipe(self):
        command = '/bin/echo hi_there | /usr/bin/env sed -e \'s@_there@_you@\''
        output = sh(command)
        self.assertEqual(output, 'hi_you')

class TestHivePartition(TestCase):
    def setUp(self):
        self.partition_desc = 'datacenter=eqiad/year=2017/month=11/day=2/hour=16'
        self.hive_partition = HivePartition(self.partition_desc)

    def test_init_from_hive_desc(self):
        should_be = [
            ('datacenter', 'eqiad'),
            ('year', '2017'),
            ('month', '11'),
            ('day', '2'),
            ('hour', '16')
        ]
        self.assertEqual(self.hive_partition.items(), should_be)

    def test_init_from_hive_spec(self):
        partition_spec = HiveUtils.partition_spec_from_partition_desc(self.partition_desc)
        hive_partition = HivePartition(partition_spec)
        should_be = [
            ('datacenter', 'eqiad'),
            ('year', '2017'),
            ('month', '11'),
            ('day', '2'),
            ('hour', '16')
        ]
        self.assertEqual(hive_partition.items(), should_be)

    def test_init_from_hive_path(self):
        hive_path = '/path/to/data/datacenter=eqiad/year=2017/month=11/day=2/hour=16'
        hive_partition = HivePartition(hive_path)
        should_be = [
            ('datacenter', 'eqiad'),
            ('year', '2017'),
            ('month', '11'),
            ('day', '2'),
            ('hour', '16')
        ]
        self.assertEqual(hive_partition.items(), should_be)

    def test_init_from_camus_path(self):
        camus_path     = '/path/to/eqiad_data/hourly/2017/11/02/16'
        hive_partition = HivePartition(camus_path)

        should_be = [
            ('year', '2017'),
            ('month', '11'),
            ('day', '2'),
            ('hour', '16')
        ]
        self.assertEqual(hive_partition.items(), should_be)

    def test_datetime(self):
        d = self.hive_partition.datetime()
        should_be = datetime(2017,11,2,16)
        self.assertEqual(d, should_be)

    def test_list(self):
        self.assertEqual(self.partition_desc.split('/'), self.hive_partition.list())

    def test_desc(self):
        self.assertEqual(self.hive_partition.desc(), self.partition_desc)

    def test_spec(self):
        should_be = 'datacenter=\'eqiad\',year=2017,month=11,day=2,hour=16'
        self.assertEqual(self.hive_partition.spec(), should_be)

    def test_path(self):
        self.assertEqual(self.hive_partition.path(), self.partition_desc)

    def test_camus_path(self):
        should_be = '/path/to/data/hourly/eqiad/2017/11/02/16'
        self.assertEqual(self.hive_partition.camus_path('/path/to/data/hourly'), should_be)

    def test_glob(self):
        should_be = '*/*/*/*/*'
        self.assertEqual(self.hive_partition.glob(), should_be)


class TestHiveUtil(TestCase):
    def setUp(self):
        self.hive = HiveUtils()
        self.hive.tables = {
            'table1': {
                'metadata': {
                    'Location':      'hdfs://test.example.com:8020/path/to/table1',
                },
            },
            'table2': {
                'metadata': {
                    'Location':      'hdfs://test.example.com:8020/path/to/table2',
                },
            },
        }

        self.table_info = {
            'table1': {
                'location':             '/path/to/table1',
                'partitions_desc':      ['webrequest_source=text/year=2013/month=10/day=01/hour=01', 'webrequest_source=text/year=2013/month=10/day=01/hour=02'],
                'partitions_spec':      ['webrequest_source=\'text\',year=2013,month=10,day=01,hour=01', 'webrequest_source=\'text\',year=2013,month=10,day=01,hour=02'],
                'partitions_datetime':  [datetime(2013,10,01,01), datetime(2013,10,01,02)],
                'partitions_path':      ['/path/to/table1/webrequest_text/hourly/2013/10/01/01', '/path/to/table1/webrequest_text/hourly/2013/10/01/02'],
            },
            'table2': {
                'location':             '/path/to/table2',
                'partitions_desc':      ['webrequest_source=text/year=2013/month=10/day=01/hour=01', 'webrequest_source=text/year=2013/month=10/day=01/hour=02'],
                'partitions_spec':      ['webrequest_source=\'text\',year=2013,month=10,day=01,hour=01', 'webrequest_source=\'text\',year=2013,month=10,day=01,hour=02'],
                'partitions_datetime':  [datetime(2013,10,01,01), datetime(2013,10,01,02)],
                'partitions_path':      ['/path/to/table1/webrequest_source=text/year=2013/month=10/day=01/hour=01', '/path/to/table2/webrequest_source=text/year=2013/month=10/day=01/hour=02'],
            },
        }

    def test_reset(self):
        self.hive.reset()
        self.assertEqual(self.hive.tables, {})

    def test_table_exists(self):
        self.assertTrue(self.hive.table_exists('table1'))
        self.assertFalse(self.hive.table_exists('nonya'))

    def test_table_location(self):
        self.assertEquals(self.hive.table_location('table1'), self.hive.tables['table1']['metadata']['Location'])
        self.assertEquals(self.hive.table_location('table1', strip_nameservice=True), '/path/to/table1')

    def test_partition_spec_from_partition_desc(self):
        expect = self.table_info['table1']['partitions_spec'][0]

        spec   = HiveUtils.partition_spec_from_partition_desc(self.table_info['table1']['partitions_desc'][0])
        self.assertEqual(spec, expect)

    def test_partition_spec_from_path(self):
        expect = self.table_info['table1']['partitions_spec'][0]
        path   = self.table_info['table1']['partitions_path'][0]
        regex  = r'/webrequest_(?P<webrequest_source>[^/]+)/hourly/(?P<year>[^/]+)/(?P<month>[^/]+)/(?P<day>[^/]+)/(?P<hour>[^/]+)'

        spec = HiveUtils.partition_spec_from_path(path, regex)
        self.assertEqual(spec, expect)

    def test_partition_datetime_from_spec(self):
        expect = self.table_info['table1']['partitions_datetime'][0]
        spec   = self.table_info['table1']['partitions_spec'][0]
        regex  = r'webrequest_source=(?P<webrequest_source>[^/,]+)[/,]year=(?P<year>[^/,]+)[/,]month=(?P<month>[^/,]+)[/,]day=(?P<day>[^/]+)[/,]hour=(?P<hour>[^/,]+)'

        dt     = HiveUtils.partition_datetime_from_spec(spec, regex)
        self.assertEqual(dt, expect)

    def test_partition_datetime_from_path_raw(self):
        expect = self.table_info['table1']['partitions_datetime'][0]
        path   = self.table_info['table1']['partitions_path'][0]
        regex  = r'.*/hourly/(.+)$'
        format = '%Y/%m/%d/%H'

        dt     = HiveUtils.partition_datetime_from_path(path, regex, format)
        self.assertEqual(dt, expect)

    def test_partition_datetime_from_path_refined(self):
        expect = self.table_info['table2']['partitions_datetime'][0]
        path   = self.table_info['table2']['partitions_path'][0]
        regex  = r'.*/(year=.+)$'
        format ='year=%Y/month=%m/day=%d/hour=%H'

        dt     = HiveUtils.partition_datetime_from_path(path, regex, format)
        self.assertEqual(dt, expect)

    def test_drop_partitions_ddl(self):
        partition_ddls = ['PARTITION ({0})'.format(spec)
            for spec in self.table_info['table1']['partitions_spec']
        ]
        expect = '\n'.join(['ALTER TABLE {0} DROP IF EXISTS {1};'.format('table1', partition_ddl) for partition_ddl in partition_ddls])

        statement = self.hive.drop_partitions_ddl('table1', self.table_info['table1']['partitions_spec'])
        self.assertEqual(statement, expect)
