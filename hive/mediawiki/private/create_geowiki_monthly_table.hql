-- Creates table statement for geoeditors_monthly table.
--
-- Parameters:
--     <none>
--
-- Usage
--     hive -f create_geoeditors_monthly_table.hql   \
--          --database wmf
--

CREATE EXTERNAL TABLE `geoeditors_monthly` (
  `wiki_db`                         string      COMMENT 'The wiki database the editors worked in',
  `country_code`                    string      COMMENT 'The 2-letter ISO country code this group of editors geolocated to, including Unknown (--)',
  `users_are_anonymous`             boolean     COMMENT 'Whether or not this group of editors edited anonymously',
  `activity_level`                  string      COMMENT 'How many edits this group of editors performed, can be "at least 1", "at least 5", or "at least 100"',
  `distinct_editors`                bigint      COMMENT 'Number of editors meeting this activity level',
  `namespace_zero_distinct_editors` bigint      COMMENT 'Number of editors meeting this activity level with only namespace zero edits'
)
COMMENT
  'This table corresponds to the erosen_ tables in analytics-slave.eqiad.wmnet, db "staging".  Purging this data may be necessary but no decision has been made about it yet.'
PARTITIONED BY (
  `month` string COMMENT 'The month in YYYY-MM format'
)
STORED AS PARQUET
LOCATION
  'hdfs://analytics-hadoop/wmf/data/wmf/mediawiki_private/geoeditors_monthly'
;
