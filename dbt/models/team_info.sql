{{ config(materialized='table') }}

SELECT DISTINCT
    home_team_id AS team_id,
    -- DISTINCT: 중복 제거 (경기마다 같은 팀이 반복 등장하므로)
    home_team_name AS team_name,
    home_city AS city,
    home_stadium AS stadium,
    home_founded AS founded
FROM {{ source('docker_test_db', 'game_result') }}
WHERE home_team_name IS NOT NULL
-- 팀명이 없는 행 제외