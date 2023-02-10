import configparser

# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
    CREATE TABLE staging_events
    (
        artist            text SORTKEY,
        auth              varchar(20),
        firstname         text,
        gender            char(1),
        iteminsession     smallint,
        lastname          text,
        length            numeric,
        level             varchar(20),
        location          text,
        method            varchar(20),
        page              varchar(20),
        registration      numeric,
        sessionid         smallint,  
        song              text,
        status            smallint,
        ts                bigint,
        userAgent         text,
        userId            smallint
    )
    DISTSTYLE ALL;
""")

staging_songs_table_create = ("""
    CREATE TABLE staging_songs
    (
        num_songs         smallint,
        artist_id         varchar(256),
        artist_latitude   numeric,
        artist_longitude  numeric,
        artist_location   text,
        artist_name       text SORTKEY,
        song_id           varchar(256),
        title             text,
        duration          numeric,
        year              int
    )
    DISTSTYLE ALL;
""")

user_table_create = ("""
    CREATE TABLE IF NOT EXISTS users (
        user_id          smallint PRIMARY KEY SORTKEY,
        first_name       text,
        last_name        text,
        gender           char(1),
        level            varchar (20)
    );
""")

song_table_create = ("""
    CREATE TABLE songs (
        song_id          varchar (256) PRIMARY KEY SORTKEY, 
        title            text, 
        artist_id        varchar (256), 
        year             smallint,
        duration         numeric
    );
""")

artist_table_create = ("""
    CREATE TABLE artists (
        artist_id        varchar(256) PRIMARY KEY SORTKEY, 
        name             text, 
        location         text, 
        latitude         numeric, 
        longitude        numeric
    );
""")

time_table_create = ("""
CREATE TABLE time
(
    start_time           timestamp NOT NULL PRIMARY KEY DISTKEY SORTKEY, 
    hour                 int NOT NULL, 
    day                  int NOT NULL, 
    week                 int NOT NULL, 
    month                int NOT NULL, 
    year                 int NOT NULL, 
    weekday              varchar(9) ENCODE BYTEDICT NOT NULL
)
    DISTSTYLE KEY;
""")

songplays_table_create = ("""
CREATE TABLE songplays
(
    songplay_id           int IDENTITY(0, 1) PRIMARY KEY, 
    start_time            timestamp NOT NULL DISTKEY SORTKEY, 
    user_id               int NOT NULL, 
    level                 varchar(8), 
    song_id               varchar(20) NOT NULL, 
    artist_id             varchar(20) NOT NULL, 
    session_id            int NOT NULL, 
    location              varchar(256) NOT NULL, 
    user_agent            varchar(256) NOT NULL
)
    DISTSTYLE KEY;
""")
                     

# STAGING TABLES

staging_events_copy = ("""
    COPY {} FROM {}
    IAM_ROLE '{}'
    JSON {};
""").format(
    'staging_events',
    config['S3']['LOG_DATA'],
    config['IAM_ROLE']['ARN'],
    config['S3']['LOG_JSONPATH']
)

staging_songs_copy = ("""
    COPY {} FROM {}
    IAM_ROLE '{}'
    JSON 'auto';
""").format(
    'staging_songs',
    config['S3']['SONG_DATA'],
    config['IAM_ROLE']['ARN']
)

# FINAL TABLES



user_table_insert = ("""
INSERT INTO users (user_id, first_name, last_name, gender, level)
SELECT DISTINCT 
    userId, 
    firstName, 
    lastName, 
    gender, 
    level
FROM staging_events
WHERE page = 'NextSong' AND userId IS NOT NULL
""")

song_table_insert = ("""
INSERT INTO songs (song_id, title, artist_id, year, duration)
SELECT DISTINCT 
    song_id,
    title,
    artist_id,
    year,
    duration
FROM staging_songs
WHERE song_id IS NOT NULL;
""")

artist_table_insert = ("""
INSERT INTO artists (artist_id, name, location, latitude, longitude)
SELECT DISTINCT
    artist_id, 
    artist_name as artist_name, 
    artist_location as location, 
    artist_latitude as latitude, 
    artist_longitude as longitude
FROM staging_songs
WHERE artist_id IS NOT NULL;
""")

time_table_insert = ("""
INSERT INTO 
    time (start_time, hour, day, week, month, year, weekday)
SELECT DISTINCT
    timestamp 'epoch' + (ts/1000) * INTERVAL '1 second' as start_time,
    EXTRACT(HOUR FROM start_time) as hour,
    EXTRACT(DAY FROM start_time) as day,
    EXTRACT(weeks FROM start_time) as week,
    EXTRACT(MONTH FROM start_time) as month,
    EXTRACT(YEAR FROM start_time) as year,
    to_char(start_time, 'Day') AS day_of_week
FROM staging_events;
""")

songplays_table_insert = ("""
INSERT INTO 
    songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
SELECT DISTINCT
    TIMESTAMP 'epoch' + (events.ts / 1000) * INTERVAL '1 second',
    events.userId as user_ID,
    events.level,
    songs.song_id as song_ID,
    songs.artist_id as artist_ID,
    events.sessionId as session_ID,
    events.location,
    events.userAgent as user_agent
FROM staging_events events
INNER JOIN staging_songs songs ON songs.title = events.song 
AND events.artist = songs.artist_name
WHERE events.page = 'NextSong';
""")

# ANALYTIC QUERIES

query_top10_available_songplaytime_per_artist = ("""
SELECT a.name, sum(s.duration) length_played_total
FROM songs s
JOIN artists a
ON s.artist_id = a.artist_id
GROUP BY a.name 
ORDER BY length_played_total DESC
limit 10
""")

query_artists_more_than_one_song = ("""
SELECT a.name, COUNT (s.title)
FROM songs s
JOIN artists a
ON a.artist_id = s.artist_id
GROUP BY a.name
HAVING COUNT (s.title)>1
ORDER BY a.name
""")

# QUERY LISTS

create_table_queries =[staging_events_table_create,staging_songs_table_create,user_table_create,song_table_create,artist_table_create,time_table_create,songplays_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy,staging_songs_copy]
insert_table_queries=[user_table_insert,song_table_insert,artist_table_insert,time_table_insert,songplays_table_insert]
analytical_queries=[query_top10_available_songplaytime_per_artist,query_artists_more_than_one_song]