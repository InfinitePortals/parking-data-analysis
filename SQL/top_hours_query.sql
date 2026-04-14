WITH hourly_averages AS (
    SELECT
        garage_name,
        CAST(strftime('%w', substr(collected_at_pacific, 1, 10)) AS INTEGER) AS weekday,
        CAST(substr(collected_at_pacific, 12, 2) AS INTEGER) AS str_hour,
        AVG(percent_full) AS avg_percent_full
    FROM SJSU_PARKING_DATA_RAW
    WHERE CAST(substr(collected_at_pacific, 12, 2) AS INTEGER) BETWEEN 7 AND 16
    GROUP BY
        garage_name,
        weekday,
        str_hour
),
ranked_hours AS (
    SELECT
        garage_name,
        weekday,
        str_hour,
        avg_percent_full,
        ROW_NUMBER() OVER (
            PARTITION BY garage_name, weekday
            ORDER BY avg_percent_full DESC
        ) AS rn
    FROM hourly_averages
)
SELECT
    garage_name,
    weekday,
    str_hour,
    avg_percent_full,
	rn
FROM ranked_hours
WHERE rn <= 5
ORDER BY
    garage_name,
    weekday,
    rn;