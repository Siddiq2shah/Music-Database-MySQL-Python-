DROP TABLE IF EXISTS Rating;
DROP TABLE IF EXISTS SongGenre;
DROP TABLE IF EXISTS Song;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS UserAccount;
DROP TABLE IF EXISTS Artist;

CREATE TABLE Artist (
    artist_id INT UNSIGNED AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    PRIMARY KEY (artist_id),
    UNIQUE KEY uk_artist_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Genre (
    genre_id INT UNSIGNED AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    PRIMARY KEY (genre_id),
    UNIQUE KEY uk_genre_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Album (
    album_id INT UNSIGNED AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    artist_id INT UNSIGNED NOT NULL,
    release_date DATE NOT NULL,
    genre_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (album_id),
    FOREIGN KEY (artist_id) REFERENCES Artist(artist_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE KEY uk_album_name_artist (name, artist_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Song (
    song_id INT UNSIGNED AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    artist_id INT UNSIGNED NOT NULL,
    album_id INT UNSIGNED NULL,
    single_release_date DATE NULL,
    PRIMARY KEY (song_id),
    FOREIGN KEY (artist_id) REFERENCES Artist(artist_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (album_id) REFERENCES Album(album_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE KEY uk_song_artist_title (artist_id, title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE UserAccount (
    user_id INT UNSIGNED AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    PRIMARY KEY (user_id),
    UNIQUE KEY uk_user_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Rating (
    rating_id INT UNSIGNED AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    song_id INT UNSIGNED NOT NULL,
    rating_value TINYINT UNSIGNED NOT NULL CHECK (rating_value BETWEEN 1 AND 5),
    rating_date DATE NOT NULL,
    PRIMARY KEY (rating_id),
    FOREIGN KEY (user_id) REFERENCES UserAccount(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (song_id) REFERENCES Song(song_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE SongGenre (
    song_id INT UNSIGNED NOT NULL,
    genre_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (song_id, genre_id),
    FOREIGN KEY (song_id) REFERENCES Song(song_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;