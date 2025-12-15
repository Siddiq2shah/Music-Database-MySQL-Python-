## Files
- `music_db.pdf` — schema diagram (no SQL inside)
- `music_db.sql` — MySQL schema (CREATE TABLE statements)
- `music_db.py` — Python implementation for loading data and running queries

## Database Design Summary
Entities modeled:
- Artist, Album, Song, Genre, UserAccount, Rating
Relationships:
- Artist -> Album (1-to-many)
- Artist -> Song (1-to-many)
- Album -> Song (1-to-many, nullable for singles)
- Song <-> Genre (many-to-many via SongGenre)
- UserAccount -> Rating (1-to-many)
- Song -> Rating (1-to-many)

Key constraints enforced:
- Artist names unique
- Genre names unique
- Album unique per (album name, artist)
- Song unique per (artist, title)
- Rating value restricted to 1–5

**music_db.pdf — Database Schema Design**

Designed a normalized relational schema modeling artists, albums, songs, genres, users, and ratings

Defined primary keys, foreign keys, and unique constraints to minimize redundancy and enforce data integrity

Modeled one-to-many relationships (artist → albums, artist → songs, user → ratings)

Modeled many-to-many relationships between songs and genres using a junction table

Distinguished album tracks from singles by allowing nullable album references and separate release dates

Enforced uniqueness of songs per artist while allowing shared song titles across different artists

Ensured albums are uniquely identified by the combination of album name and artist

Selected appropriate SQL data types and sizes to support realistic large-scale music platforms


**music_db.sql — Database Implementation (MySQL)**

Implemented the full relational schema using MySQL CREATE TABLE statements

Declared primary keys, foreign keys, and cascading relationships to maintain referential integrity

Enforced uniqueness constraints for artists, albums, users, and artist-song combinations

Created junction tables to support many-to-many song-genre relationships

Defined constraints to support both album-based songs and standalone singles

Structured the database to support efficient querying for analytics and aggregation tasks


**music_db.py — Database Population & Query Logic**

Implemented database reset functionality to safely clear all tables before grading

Wrote data-loading functions to insert artists, albums, songs, genres, users, and ratings while preventing duplicates

Enforced business rules in code, including valid rating ranges and minimum genre membership for songs

Handled album and single song insertion logic with correct release date handling

Implemented analytical SQL queries to:

Identify prolific individual artists over a given year range

Find artists’ most recent single releases in a specified year

Compute top song genres by frequency

Identify artists who released both albums and singles

Retrieve the most-rated songs within a year range

Identify the most engaged users based on rating activity

Returned query results in the exact formats required by the autograder

Designed queries to be robust, efficient, and compatible with automated grading
