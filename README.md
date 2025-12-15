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
