-- Creates table statement for hourly aggregated pageview table.
--
-- NOTE:  When choosing partition field types,
-- one should take into consideration Hive's
-- insistence on storing partition values
-- as strings.  See:
-- https://wikitech.wikimedia.org/wiki/File:Hive_partition_formats.png
-- and
-- http://bots.wmflabs.org/~wm-bot/logs/%23wikimedia-analytics/20140721.txt
--
-- Parameters:
--     <none>
--
-- Usage
--     hive -f create_pageview_hourly_table.hql --database wmf
--

CREATE EXTERNAL TABLE IF NOT EXISTS `pageview_hourly`(
    `project`           string  COMMENT 'Project name from requests hostname',
    `language_variant`  string  COMMENT 'Language variant from requests path (not set if present in project name)',
    `page_title`        string  COMMENT 'Page Title from requests path and query',
    `access_method`     string  COMMENT 'Method used to access the pages, can be desktop, mobile web, or mobile app',
    `zero_carrier`      string  COMMENT 'Zero carrier if pageviews are accessed through one, null otherwise',
    `agent_type`        string  COMMENT 'Agent accessing the pages, can be spider or user',
    `referer_class`     string  COMMENT 'Can be internal, external or unknown',
    `continent`         string  COMMENT 'Continent of the accessing agents (computed using maxmind GeoIP database)',
    `country_code`      string  COMMENT 'Country iso code of the accessing agents (computed using maxmind GeoIP database)',
    `country`           string  COMMENT 'Country (text) of the accessing agents (computed using maxmind GeoIP database)',
    `subdivision`       string  COMMENT 'Subdivision of the accessing agents (computed using maxmind GeoIP database)',
    `city`              string  COMMENT 'City iso code of the accessing agents (computed using maxmind GeoIP database)',
    `user_agent_map`    map<string, string>  COMMENT 'User-agent map with device_family, browser_family, browser_major, os_family, os_major, os_minor and wmf_app_version keys and associated values',
    `record_version`    string  COMMENT 'Keeps track of changes in the table content definition - https://wikitech.wikimedia.org/wiki/Analytics/Data/Pageview_hourly',
    `view_count`        bigint  COMMENT 'number of pageviews'
)
PARTITIONED BY (
    `year`              int     COMMENT 'Unpadded year of pageviews',
    `month`             int     COMMENT 'Unpadded month of pageviews',
    `day`               int     COMMENT 'Unpadded day of pageviews',
    `hour`              int     COMMENT 'Unpadded hour of pageviews'
)
STORED AS PARQUET
LOCATION '/wmf/data/wmf/pageview/hourly'
;
