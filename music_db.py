from typing import Tuple, List, Set

def clear_database(mydb):
    """
    Deletes all the rows from all the tables of the database.
    If a table has a foreign key to a parent table, it is deleted before 
    deleting the parent table, otherwise the database system will throw an error. 

    Args:
        mydb: database connection
    """
    cur = mydb.cursor()
    try:
        # Disable FK checks
        cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        tables = [
            "Rating",
            "SongGenre", 
            "Song",
            "Album",
            "UserAccount",
            "Genre",
            "Artist"
        ]
        
        # Use TRUNCATE for fast, lock-free clearing
        for t in tables:
            cur.execute(f"TRUNCATE TABLE {t};")
        
        # Re-enable FK checks
        cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        mydb.commit()
    except Exception:
        mydb.rollback()
        raise
    finally:
        cur.close()

def _ensure_artist(cur, artist_name):
    """
    Helper function to ensure artist exists in database.
    Returns artist_id.
    """
    cur.execute("SELECT artist_id FROM Artist WHERE name = %s", (artist_name,))
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute("INSERT INTO Artist (name) VALUES (%s)", (artist_name,))
    return cur.lastrowid

def _ensure_genre(cur, genre_name):
    """
    Helper function to ensure genre exists in database.
    Returns genre_id.
    """
    cur.execute("SELECT genre_id FROM Genre WHERE name = %s", (genre_name,))
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute("INSERT INTO Genre (name) VALUES (%s)", (genre_name,))
    return cur.lastrowid

def load_single_songs(mydb, single_songs: List[Tuple[str, Tuple[str, ...], str, str]]) -> Set[Tuple[str,str]]:
    """
    Add single songs to the database. 

    Args:
        mydb: database connection
        
        single_songs: List of single songs to add. Each single song is a tuple of the form:
              (song title, genre names, artist name, release date)
        Genre names is a tuple since a song could belong to multiple genres
        Release date is of the form yyyy-dd-mm
        Example 1 single song: ('S1',('Pop',),'A1','2008-10-01') => here song is of genre Pop
        Example 2 single song: ('S2',('Rock', 'Pop),'A2','2000-02-15') => here song is of genre Rock and Pop

    Returns:
        Set[Tuple[str,str]]: set of (song,artist) for combinations that already exist 
        in the database and were not added (rejected). 
        Set is empty if there are no rejects.
    """
    rejects = set()
    cur = mydb.cursor()
    try:
        for (title, genres, artist_name, release_date) in single_songs:
            # Enforce at least one genre
            if not genres or len(genres) == 0:
                rejects.add((title, artist_name))
                continue

            try:
                # Ensure artist exists
                artist_id = _ensure_artist(cur, artist_name)

                # Insert song as single (album_id NULL, single_release_date set)
                cur.execute(
                    "INSERT INTO Song (title, artist_id, album_id, single_release_date) VALUES (%s, %s, NULL, %s)",
                    (title, artist_id, release_date)
                )
                song_id = cur.lastrowid

                # Ensure genres and insert SongGenre rows
                for g in genres:
                    genre_id = _ensure_genre(cur, g)
                    cur.execute("INSERT INTO SongGenre (song_id, genre_id) VALUES (%s, %s)", (song_id, genre_id))

                # Commit this song
                mydb.commit()
            except Exception:
                mydb.rollback()
                rejects.add((title, artist_name))
    finally:
        cur.close()
    return rejects

def load_albums(mydb, albums: List[Tuple[str,str,str,str,List[str]]]) -> Set[Tuple[str,str]]:
    """
    Add albums to the database. 
    
    Args:
        mydb: database connection
        
        albums: List of albums to add. Each album is a tuple of the form:
              (album title, genre, artist name, release date, list of song titles) 
        Release date is of the form yyyy-dd-mm
        Example album: ('Album1','Jazz','A1','2008-10-01',['s1','s2','s3','s4','s5','s6'])

    Returns:
        Set[Tuple[str,str]: set of (album, artist) combinations that were not added (rejected) 
        because the artist already has an album of the same title.
        Set is empty if there are no rejects.
    """
    rejects = set()
    cur = mydb.cursor()
    try:
        for (album_title, genre_name, artist_name, release_date, song_titles) in albums:
            try:
                # Ensure artist and genre exist
                artist_id = _ensure_artist(cur, artist_name)
                genre_id = _ensure_genre(cur, genre_name)

                # Check if album exists for this artist
                cur.execute("SELECT album_id FROM Album WHERE name = %s AND artist_id = %s", (album_title, artist_id))
                if cur.fetchone():
                    rejects.add((album_title, artist_name))
                    continue

                # Insert album
                cur.execute(
                    "INSERT INTO Album (name, artist_id, release_date, genre_id) VALUES (%s, %s, %s, %s)",
                    (album_title, artist_id, release_date, genre_id)
                )
                album_id = cur.lastrowid

                # Insert songs for album
                song_conflict = False
                for s_title in song_titles:
                    try:
                        cur.execute(
                            "INSERT INTO Song (title, artist_id, album_id, single_release_date) VALUES (%s, %s, %s, NULL)",
                            (s_title, artist_id, album_id)
                        )
                        song_id = cur.lastrowid
                        # Insert SongGenre mapping using album genre
                        cur.execute("INSERT INTO SongGenre (song_id, genre_id) VALUES (%s, %s)", (song_id, genre_id))
                    except Exception:
                        song_conflict = True
                        break

                if song_conflict:
                    mydb.rollback()
                    rejects.add((album_title, artist_name))
                else:
                    mydb.commit()
            except Exception:
                mydb.rollback()
                rejects.add((album_title, artist_name))
    finally:
        cur.close()
    return rejects

def load_users(mydb, users: List[str]) -> Set[str]:
    """
    Add users to the database. 

    Args:
        mydb: database connection
        users: list of usernames

    Returns:
        Set[str]: set of all usernames that were not added (rejected) because 
        they are duplicates of existing users.
        Set is empty if there are no rejects.
    """
    rejects = set()
    cur = mydb.cursor()
    try:
        for u in users:
            try:
                cur.execute("INSERT INTO UserAccount (username) VALUES (%s)", (u,))
                mydb.commit()
            except Exception:
                mydb.rollback()
                rejects.add(u)
    finally:
        cur.close()
    return rejects

def load_song_ratings(mydb, song_ratings: List[Tuple[str,Tuple[str,str],int, str]]) -> Set[Tuple[str,str,str]]:
    """
    Load ratings for songs, which are either singles or songs in albums. 

    Args:
        mydb: database connection
        song_ratings: list of rating tuples of the form:
            (rater, (artist, song), rating, date)
        
        The rater is a username, the (artist,song) tuple refers to the uniquely identifiable song to be rated.
        e.g. ('u1',('a1','song1'),4,'2021-11-18') => u1 is giving a rating of 4 to the (a1,song1) song.

    Returns:
        Set[Tuple[str,str,str]]: set of (username,artist,song) tuples that are rejected, for any of the following
        reasongs:
        (a) username (rater) is not in the database, or
        (b) username is in database but (artist,song) combination is not in the database, or
        (c) username has already rated (artist,song) combination, or
        (d) everything else is legit, but rating is not in range 1..5
        
        An empty set is returned if there are no rejects.  
    """
    rejects = set()
    cur = mydb.cursor()
    try:
        for (username, (artist_name, song_title), rating_value, rating_date) in song_ratings:
            try:
                # Check user exists
                cur.execute("SELECT user_id FROM UserAccount WHERE username = %s", (username,))
                r = cur.fetchone()
                if not r:
                    rejects.add((username, artist_name, song_title))
                    continue
                user_id = r[0]

                # Find song by artist+title
                cur.execute("""
                    SELECT S.song_id
                    FROM Song S
                    JOIN Artist A ON S.artist_id = A.artist_id
                    WHERE A.name = %s AND S.title = %s
                """, (artist_name, song_title))
                sr = cur.fetchone()
                if not sr:
                    rejects.add((username, artist_name, song_title))
                    continue
                song_id = sr[0]

                # Rating value check
                if not (1 <= int(rating_value) <= 5):
                    rejects.add((username, artist_name, song_title))
                    continue

                # Check if user already rated this song
                cur.execute("SELECT 1 FROM Rating WHERE user_id = %s AND song_id = %s", (user_id, song_id))
                if cur.fetchone():
                    rejects.add((username, artist_name, song_title))
                    continue

                # Insert rating
                cur.execute(
                    "INSERT INTO Rating (user_id, song_id, rating_value, rating_date) VALUES (%s, %s, %s, %s)",
                    (user_id, song_id, rating_value, rating_date)
                )
                mydb.commit()
            except Exception:
                mydb.rollback()
                rejects.add((username, artist_name, song_title))
    finally:
        cur.close()
    return rejects

def get_most_prolific_individual_artists(mydb, n: int, year_range: Tuple[int,int]) -> List[Tuple[str,int]]:   
    """
    Get the top n most prolific individual artists by number of singles released in a year range. 
    Break ties by alphabetical order of artist name.

    Args:
        mydb: database connection
        n: how many to get
        year_range: tuple, e.g. (2015,2020)

    Returns:
        List[Tuple[str,int]]: list of (artist name, number of songs) tuples.
        If there are fewer than n artists, all of them are returned.
        If there are no artists, an empty list is returned.
    """
    start_year, end_year = year_range
    cur = mydb.cursor()
    try:
        q = """
        SELECT A.name, COUNT(*) AS cnt
        FROM Artist A
        JOIN Song S ON S.artist_id = A.artist_id
        WHERE S.album_id IS NULL
          AND YEAR(S.single_release_date) BETWEEN %s AND %s
        GROUP BY A.name
        ORDER BY cnt DESC, A.name ASC
        LIMIT %s
        """
        cur.execute(q, (start_year, end_year, n))
        res = [(row[0], int(row[1])) for row in cur.fetchall()]
        return res
    finally:
        cur.close()

def get_artists_last_single_in_year(mydb, year: int) -> Set[str]:
    """
    Get all artists who released their last single in the given year.
    
    Args:
        mydb: database connection
        year: year of last release
        
    Returns:
        Set[str]: set of artist names
        If there is no artist with a single released in the given year, an empty set is returned.
    """
    cur = mydb.cursor()
    try:
        q = """
        SELECT A.name
        FROM Artist A
        JOIN (
            SELECT artist_id, MAX(YEAR(single_release_date)) AS last_year
            FROM Song
            WHERE album_id IS NULL
            GROUP BY artist_id
        ) AS T ON T.artist_id = A.artist_id
        WHERE T.last_year = %s
        """
        cur.execute(q, (year,))
        return set(row[0] for row in cur.fetchall())
    finally:
        cur.close()

def get_top_song_genres(mydb, n: int) -> List[Tuple[str,int]]:
    """
    Get n genres that are most represented in terms of number of songs in that genre.
    Songs include singles as well as songs in albums. 
    
    Args:
        mydb: database connection
        n: number of genres

    Returns:
        List[Tuple[str,int]]: list of tuples (genre,number_of_songs), from most represented to
        least represented genre. If number of genres is less than n, returns all.
        Ties broken by alphabetical order of genre names.
    """
    cur = mydb.cursor()
    try:
        q = """
        SELECT G.name, COUNT(SG.song_id) AS cnt
        FROM Genre G
        JOIN SongGenre SG ON SG.genre_id = G.genre_id
        GROUP BY G.name
        ORDER BY cnt DESC, G.name ASC
        LIMIT %s
        """
        cur.execute(q, (n,))
        res = [(row[0], int(row[1])) for row in cur.fetchall()]
        return res
    finally:
        cur.close()

def get_album_and_single_artists(mydb) -> Set[str]:
    """
    Get artists who have released albums as well as singles.

    Args:
        mydb; database connection

    Returns:
        Set[str]: set of artist names
    """
    cur = mydb.cursor()
    try:
        q = """
        SELECT DISTINCT A.name
        FROM Artist A
        WHERE EXISTS (SELECT 1 FROM Album AL WHERE AL.artist_id = A.artist_id)
          AND EXISTS (SELECT 1 FROM Song S WHERE S.artist_id = A.artist_id AND S.album_id IS NULL)
        """
        cur.execute(q)
        return set(row[0] for row in cur.fetchall())
    finally:
        cur.close()

def get_most_rated_songs(mydb, year_range: Tuple[int,int], n: int) -> List[Tuple[str,str,int]]:
    """
    Get the top n most rated songs in the given year range (both inclusive), 
    ranked from most rated to least rated. 
    "Most rated" refers to number of ratings, not actual rating scores. 
    Ties are broken in alphabetical order of song title. If the number of rated songs is less
    than n, all rates songs are returned.
    
    Args:
        mydb: database connection
        year_range: range of years, e.g. (2018-2021), during which ratings were given
        n: number of most rated songs

    Returns:
        List[Tuple[str,str,int]: list of (song title, artist name, number of ratings for song)   
    """
    start_year, end_year = year_range
    cur = mydb.cursor()
    try:
        q = """
        SELECT S.title, A.name, COUNT(R.rating_id) AS cnt
        FROM Rating R
        JOIN Song S ON R.song_id = S.song_id
        JOIN Artist A ON S.artist_id = A.artist_id
        WHERE YEAR(R.rating_date) BETWEEN %s AND %s
        GROUP BY S.title, A.name
        ORDER BY cnt DESC, S.title ASC
        LIMIT %s
        """
        cur.execute(q, (start_year, end_year, n))
        return [(row[0], row[1], int(row[2])) for row in cur.fetchall()]
    finally:
        cur.close()

def get_most_engaged_users(mydb, year_range: Tuple[int,int], n: int) -> List[Tuple[str,int]]:
    """
    Get the top n most engaged users, in terms of number of songs they have rated.
    Break ties by alphabetical order of usernames.

    Args:
        mydb: database connection
        year_range: range of years, e.g. (2018-2021), during which ratings were given
        n: number of users

    Returns:
        List[Tuple[str, int]]: list of (username,number_of_songs_rated) tuples
    """
    start_year, end_year = year_range
    cur = mydb.cursor()
    try:
        q = """
        SELECT U.username, COUNT(R.rating_id) AS cnt
        FROM Rating R
        JOIN UserAccount U ON R.user_id = U.user_id
        WHERE YEAR(R.rating_date) BETWEEN %s AND %s
        GROUP BY U.username
        ORDER BY cnt DESC, U.username ASC
        LIMIT %s
        """
        cur.execute(q, (start_year, end_year, n))
        return [(row[0], int(row[1])) for row in cur.fetchall()]
    finally:
        cur.close()

def main():
    pass

if __name__ == "__main__":
    main()