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

Designed a normalized relational schema modeling artists, albums, songs, genres, users, and ratings

Defined primary keys, foreign keys, and unique constraints to minimize redundancy and enforce data integrity

Modeled one-to-many relationships (artist → albums, artist → songs, user → ratings)

Modeled many-to-many relationships between songs and genres using a junction table

Distinguished album tracks from singles by allowing nullable album references and separate release dates

Enforced uniqueness of songs per artist while allowing shared song titles across different artists

Ensured albums are uniquely identified by the combination of album name and artist

Selected appropriate SQL data types and sizes to support realistic large-scale music platforms
