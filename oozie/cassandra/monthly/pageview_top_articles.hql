-- Parameters:
--     destination_directory -- HDFS path to write output files
--     source_table          -- Fully qualified table name to compute from.
--     separator             -- Separator for values
--     year                  -- year of partition to compute from.
--     month                 -- month of partition to compute from.
--     day                   -- day of partition to compute from.
--
-- Usage:
--     hive -f pageview_top_articles.hql                          \
--         -d destination_directory=/tmp/pageview_top_articles    \
--         -d source_table=wmf.pageview_hourly                    \
--         -d separator=\t                                        \
--         -d year=2015                                           \
--         -d month=5                                             \
--         -d day=1                                               \
--


SET hive.exec.compress.output=true;
SET mapreduce.output.fileoutputformat.compress.codec=org.apache.hadoop.io.compress.GzipCodec;


WITH ranked AS (
    SELECT
        project,
        page_title,
        access,
        year,
        month,
        views,
        rank() OVER (PARTITION BY project, access, year, month ORDER BY views DESC) as rank,
        row_number() OVER (PARTITION BY project, access, year, month ORDER BY views DESC) as rn
    FROM (
        SELECT
            project,
            reflect("org.json.simple.JSONObject", "escape", regexp_replace(page_title, '${separator}', '')) AS page_title,
            COALESCE(regexp_replace(access_method, ' ', '-'), 'all-access') AS access,
            LPAD(year, 4, "0") as year,
            LPAD(month, 2, "0") as month,
            SUM(view_count) as views
        FROM ${source_table}
        WHERE
            year = ${year}
            AND month = ${month}
            AND agent_type = 'user'
        GROUP BY project, regexp_replace(page_title, '${separator}', ''), access_method, year, month
        GROUPING SETS (
            (project, regexp_replace(page_title, '${separator}', ''), access_method, year, month),
            (project, regexp_replace(page_title, '${separator}', ''), year, month)
        )
    ) raw
),
max_rank AS (
    SELECT
        project,
        access,
        year,
        month,
        rank as max_rank
    FROM ranked
    WHERE
        rn = 1001
    GROUP BY
        project,
        access,
        year,
        month,
        rank
)
INSERT OVERWRITE DIRECTORY "${destination_directory}"
-- Since "ROW FORMAT DELIMITED DELIMITED FIELDS TERMINATED BY ' '" only
-- works for exports to local directories (see HIVE-5672), we have to
-- prepare the lines by hand through concatenation :-(
SELECT
    CONCAT_WS("${separator}",
        ranked.project,
        ranked.access,
        ranked.year,
        ranked.month,
        'all-days',
        CONCAT('[',
            CONCAT_WS(',', collect_set(
                CONCAT('{"article":"', ranked.page_title,
                    '","views":', CAST(ranked.views AS STRING),
                    ',"rank":', CAST(ranked.rank AS STRING), '}'))
            ),']')
    )
FROM ranked
LEFT JOIN max_rank ON (
    ranked.project = max_rank.project
    AND ranked.access = max_rank.access
    AND ranked.year = max_rank.year
    AND ranked.month = max_rank.month
)
WHERE ranked.rank < COALESCE(max_rank.max_rank, 1001)
GROUP BY
    ranked.project,
    ranked.access,
    ranked.year,
    ranked.month
;