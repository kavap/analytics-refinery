CREATE TABLE webrequest_sequence_stats(
    hostname            string  COMMENT 'Source node hostname',
    webrequest_source   string  COMMENT 'Source cluster',
    year                int,
    month               int,
    day                 int,
    hour                int,
    sequence_min        bigint  COMMENT 'Min sequence found for this hostname in this hour',
    sequence_max        bigint  COMMENT 'Max sequence found for this hostname in this hour',
    count_actual        bigint  COMMENT 'Actual number of records for this hostname in this hour',
    count_expected      bigint  COMMENT 'Max - Min + 1.  All is well if this == count_actual',
    count_different     bigint  COMMENT 'count_expected - count_actual',
    count_duplicate     bigint  COMMENT 'Number of duplicate sequences for this hostname in this hour',
    count_null_sequence bigint  COMMENT 'Sanity check for number of records where sequence is NULL.',
    percent_different   double  COMMENT 'Difference in percent between count_expected and count_actual.'
);
