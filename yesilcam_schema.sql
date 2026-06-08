CREATE DATABASE IF NOT EXISTS yesilcam;
USE yesilcam;

DROP TABLE IF EXISTS Recommendations;
DROP TABLE IF EXISTS Subscriptions;
DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS Watchlists;
DROP TABLE IF EXISTS WatchHistory;
DROP TABLE IF EXISTS MovieActors;
DROP TABLE IF EXISTS MovieGenres;
DROP TABLE IF EXISTS Movies;
DROP TABLE IF EXISTS Actors;
DROP TABLE IF EXISTS Genres;
DROP TABLE IF EXISTS Directors;
DROP TABLE IF EXISTS Users;

-- ============================================================
--  TABLES
-- ============================================================

CREATE TABLE Directors (
    director_id INT          PRIMARY KEY,
    full_name   VARCHAR(100) NOT NULL,
    birth_year  YEAR,
    nationality VARCHAR(50)  DEFAULT 'Turkish',
    bio         TEXT
);

CREATE TABLE Genres (
    genre_id   INT         PRIMARY KEY,
    genre_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Actors (
    actor_id    INT          PRIMARY KEY,
    full_name   VARCHAR(100) NOT NULL,
    birth_year  YEAR,
    birth_place VARCHAR(100),
    bio         TEXT
);

CREATE TABLE Users (
    user_id   INT          PRIMARY KEY,
    username  VARCHAR(50)  NOT NULL UNIQUE,
    email     VARCHAR(100) NOT NULL UNIQUE,
    password  VARCHAR(100) NOT NULL,
    full_name VARCHAR(100),
    join_date DATE         NOT NULL
);

CREATE TABLE Movies (
    movie_id     INT          PRIMARY KEY,
    title        VARCHAR(200) NOT NULL UNIQUE,
    release_year YEAR         NOT NULL,
    duration_min SMALLINT,
    language     VARCHAR(30)  DEFAULT 'Turkish',
    director_id  INT,
    synopsis     TEXT,
    avg_rating   DECIMAL(3,1),
    view_count   INT          DEFAULT 0,
    CONSTRAINT chk_year CHECK (release_year BETWEEN 1900 AND 2100),
    FOREIGN KEY (director_id) REFERENCES Directors(director_id)
);

CREATE TABLE MovieGenres (
    movie_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

CREATE TABLE MovieActors (
    movie_id       INT          NOT NULL,
    actor_id       INT          NOT NULL,
    character_name VARCHAR(100),
    is_lead        BOOLEAN      DEFAULT FALSE,
    PRIMARY KEY (movie_id, actor_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id),
    FOREIGN KEY (actor_id) REFERENCES Actors(actor_id)
);

CREATE TABLE WatchHistory (
    history_id         INT     PRIMARY KEY,
    user_id            INT     NOT NULL,
    movie_id           INT     NOT NULL,
    watched_at         DATE    NOT NULL,
    watch_pct          TINYINT DEFAULT 100,
    watch_duration_min SMALLINT,
    FOREIGN KEY (user_id)  REFERENCES Users(user_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
);

CREATE TABLE Watchlists (
    watchlist_id INT  PRIMARY KEY,
    user_id      INT  NOT NULL,
    movie_id     INT  NOT NULL,
    added_at     DATE NOT NULL,
    FOREIGN KEY (user_id)  REFERENCES Users(user_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
);

CREATE TABLE Reviews (
    review_id  INT     PRIMARY KEY,
    user_id    INT     NOT NULL,
    movie_id   INT     NOT NULL,
    rating     TINYINT NOT NULL,
    comment    TEXT,
    created_at DATE    NOT NULL,
    CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5),
    UNIQUE KEY uq_user_movie (user_id, movie_id),
    FOREIGN KEY (user_id)  REFERENCES Users(user_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
);

CREATE TABLE Subscriptions (
    sub_id     INT         PRIMARY KEY,
    user_id    INT         NOT NULL UNIQUE,
    plan       VARCHAR(20) DEFAULT 'free',
    start_date DATE        NOT NULL,
    end_date   DATE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Recommendations (
    rec_id     INT          PRIMARY KEY,
    user_id    INT          NOT NULL,
    movie_id   INT          NOT NULL,
    reason     VARCHAR(150),
    created_at DATE         NOT NULL,
    UNIQUE KEY uq_rec (user_id, movie_id),
    FOREIGN KEY (user_id)  REFERENCES Users(user_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
);

-- ============================================================
--  INSERT DATA
-- ============================================================

-- Directors
INSERT INTO Directors (director_id, full_name, birth_year, nationality, bio) VALUES
(1,  'Atıf Yılmaz',      1925, 'Turkish', 'Known for female-centered films. Directed Selvi Boylum Al Yazmalı, Mine, and Adı Vasfiye.'),
(2,  'Lütfi Ö. Akad',    1916, 'Turkish', 'Founding master of Turkish cinema. Directed the migration trilogy: Gelin, Düğün, Diyet.'),
(3,  'Metin Erksan',     1929, 'Turkish', 'Won the Golden Bear at Berlin 1964 for Susuz Yaz. Pioneer of Turkish art cinema.'),
(4,  'Halit Refiğ',      1934, 'Turkish', 'Pioneer of the National Cinema movement. Directed Gurbet Kuşları and Haremde Dört Kadın.'),
(5,  'Yılmaz Güney',     1937, 'Turkish', 'Won the Cannes Palme d''Or in 1982 for Yol. Defining figure of Turkish social realist cinema.'),
(6,  'Ertem Eğilmez',    1929, 'Turkish', 'Shaped Yeşilçam comedy with the Hababam Sınıfı series, Davaro, and Züğürt Ağa.'),
(7,  'Şerif Gören',      1944, 'Turkish', 'Directed Sürü and Yol under Yılmaz Güney''s supervision. Key social realist director.'),
(8,  'Zeki Ökten',       1941, 'Turkish', 'Directed Düşman from Güney''s screenplay. Important figure of social realist cinema.'),
(9,  'Osman Seden',      1921, 'Turkish', 'Prolific director of melodramas and action films. Directed over 100 films.'),
(10, 'Memduh Ün',        1920, 'Turkish', 'Veteran director known for romantic dramas and social films of early Yeşilçam.'),
(11, 'Tunç Başaran',     1948, 'Turkish', 'Directed humanist social films. Known for Hakkari''de Bir Mevsim.'),
(12, 'Ali Özgentürk',    1945, 'Turkish', 'Directed At and Hazal. Brought Anatolian realism to the big screen.'),
(13, 'Bilge Olgaç',      1940, 'Turkish', 'One of the few female directors of Yeşilçam. Directed Gönül Yarası and Berdel.'),
(14, 'Yücel Çakmaklı',   1937, 'Turkish', 'Representative of the National Cinema movement. Directed Birleşen Yollar.'),
(15, 'Orhan Aksoy',      1932, 'Turkish', 'Prolific Yeşilçam director. Directed Kızılırmak Karakoyun and many popular melodramas.');

-- Genres
INSERT INTO Genres (genre_id, genre_name) VALUES
(1,  'Drama'),
(2,  'Comedy'),
(3,  'Melodrama'),
(4,  'Action'),
(5,  'Romance'),
(6,  'Social Realism'),
(7,  'Adventure'),
(8,  'Musical'),
(9,  'Historical'),
(10, 'Thriller'),
(11, 'Family'),
(12, 'Rural');

-- Actors
INSERT INTO Actors (actor_id, full_name, birth_year, birth_place, bio) VALUES
(1,  'Türkan Şoray',     1945, 'İstanbul', 'The Sultan of Turkish cinema. Most iconic actress of the Yeşilçam era.'),
(2,  'Fatma Girik',      1942, 'İstanbul', 'Known as Erkek Fatma. Played strong, independent female roles.'),
(3,  'Yılmaz Güney',     1937, 'Adana',    'The Ugly King. Powerful actor and director of social realist cinema.'),
(4,  'Hülya Koçyiğit',   1947, 'İstanbul', 'Lead actress of the National Cinema movement. Multiple Golden Orange winner.'),
(5,  'Tarık Akan',       1949, 'Balıkesir','Handsome dramatic star of Yeşilçam. Starred in Yol.'),
(6,  'Kemal Sunal',      1944, 'İstanbul', 'Most beloved comedy actor of Turkish cinema. Immortalized the Şaban character.'),
(7,  'Münir Özkul',      1925, 'İstanbul', 'Veteran actor of drama and comedy. Played Bacaksız in Hababam Sınıfı.'),
(8,  'Adile Naşit',      1930, 'İstanbul', 'Beloved comedy actress known for warm mother and neighbor roles.'),
(9,  'Kadir İnanır',     1949, 'Trabzon',  'The Black Prince of Turkish cinema. Starred in Selvi Boylum Al Yazmalı.'),
(10, 'Ayhan Işık',       1929, 'İstanbul', 'Popular romantic star of 1950s and 1960s Yeşilçam melodramas.'),
(11, 'Belgin Doruk',     1936, 'İstanbul', 'The Princess of Turkish cinema. Iconic early Yeşilçam actress.'),
(12, 'Sadri Alışık',     1925, 'İstanbul', 'Legendary actor equally gifted in comedy and drama.'),
(13, 'Çolpan İlhan',     1928, 'İstanbul', 'Elegant and refined actress known for sophisticated dramatic roles.'),
(14, 'Göksel Arsoy',     1936, 'İstanbul', 'Popular action and melodrama star of the 1960s and 1970s.'),
(15, 'İzzet Günay',      1930, 'Bursa',    'Deep-voiced charismatic actor with a long and varied career.'),
(16, 'Ediz Hun',         1940, 'İstanbul', 'Romantic leading man of cinema and television.'),
(17, 'Filiz Akın',       1943, 'İstanbul', 'One of the most loved Yeşilçam stars. Starred in Hazal.'),
(18, 'Orhan Günşıray',   1934, 'İstanbul', 'Reliable character actor often cast as the villain.'),
(19, 'Şener Şen',        1941, 'Çorum',    'One of the greatest Turkish comedy actors. Iconic in Züğürt Ağa and Davaro.'),
(20, 'Müjde Ar',         1955, 'İstanbul', 'Star of Atıf Yılmaz''s female-focused films: Mine and Adı Vasfiye.'),
(21, 'Cüneyt Arkın',     1937, 'Çorum',    'The action legend of Turkish cinema. Appeared in over 300 films.'),
(22, 'Fikret Hakan',     1934, 'İstanbul', 'Serious and charismatic actor known for strong leading roles.'),
(23, 'Perihan Savaş',    1955, 'İstanbul', 'Recognized for powerful dramatic performances.'),
(24, 'Hülya Avşar',      1963, 'Edirne',   'Rose to fame through acting and music in the 1980s.');

-- Users
INSERT INTO Users (user_id, username, email, password, full_name, join_date) VALUES
(1,  'elif_y',  'elif@mail.com',  'pass123', 'Elif Yıldırım',  '2025-01-10'),
(2,  'oyku_a',   'oyku@mail.com',   'pass123', 'Öykünur Akyüz',     '2025-01-15'),
(3,  'ulduz_o',   'ulduz@mail.com',   'pass123', 'Ulduz Özel',    '2025-02-01'),
(4,  'selin_a',  'selin@mail.com',  'pass123', 'Selin Arslan',  '2025-02-10'),
(5,  'can_b',    'can@mail.com',    'pass123', 'Can Bozkurt',   '2025-03-01'),
(6,  'zeynep_a', 'zeynep@mail.com', 'pass123', 'Zeynep Arslan', '2025-03-05'),
(7,  'berk_t',   'berk@mail.com',   'pass123', 'Berk Tekin',    '2025-03-10'),
(8,  'nisa_k',   'nisa@mail.com',   'pass123', 'Nisa Kaya',     '2025-03-12'),
(9,  'omer_y',   'omer@mail.com',   'pass123', 'Ömer Yıldız',   '2025-03-15'),
(10, 'lale_d',   'lale@mail.com',   'pass123', 'Lale Demir',    '2025-03-20'),
(11, 'tarik_b',  'tarik@mail.com',  'pass123', 'Tarık Bal',     '2025-04-01'),
(12, 'sinem_o',  'sinem@mail.com',  'pass123', 'Sinem Öz',      '2025-04-05'),
(13, 'emre_c',   'emre@mail.com',   'pass123', 'Emre Can',      '2025-04-10'),
(14, 'ipek_s',   'ipek@mail.com',   'pass123', 'İpek Sarı',     '2025-04-15'),
(15, 'ali_g',    'ali@mail.com',    'pass123', 'Ali Güven',     '2025-04-20');

-- Movies
INSERT INTO Movies (movie_id, title, release_year, duration_min, language, director_id, synopsis, avg_rating, view_count) VALUES
-- Metin Erksan
(1,  'Susuz Yaz',                      1963,  90, 'Turkish', 3,  'Two brothers fight over water rights in an Aegean village. Won the Golden Bear at Berlin 1964.',            4.1, 4200),
(2,  'Sevmek Zamanı',                  1965,  90, 'Turkish', 3,  'A philosophical love story questioning existential themes. One of Erksan''s most personal films.',           4.1, 3900),
(3,  'Hudutların Kanunu',              1966,  95, 'Turkish', 3,  'A gritty drama about smugglers and the harsh law of the Eastern Anatolian frontier.',                        4.0, 3600),
(4,  'Kuyucaklı Yusuf',               1955,  85, 'Turkish', 3,  'Based on Sabahattin Ali''s novel about an orphan boy and his tragic fate in an Anatolian town.',             3.8, 2700),
(5,  'Acı Hayat',                      1962,  95, 'Turkish', 3,  'A melancholic masterpiece about poverty, inequality and broken dreams in Istanbul.',                         4.0, 3900),
-- Yılmaz Güney
(6,  'Umut',                           1970,  95, 'Turkish', 5,  'A poor cart driver in Adana loses his horse and falls into desperation chasing superstitions for wealth.',   4.3, 5800),
(7,  'Ağıt',                           1971,  90, 'Turkish', 5,  'A poetry-like film following a fugitive through the mountains. Güney as director and lead actor.',            4.0, 3400),
(8,  'Arkadaş',                        1974,  97, 'Turkish', 5,  'Two old friends reunite and discover how differently their lives and values have evolved.',                    4.1, 3700),
(9,  'Yol',                            1982, 114, 'Turkish', 7,  'Five convicts on week-long leave each face a different human tragedy. Cannes Palme d''Or 1982.',              4.6, 9100),
(10, 'Sürü',                           1978, 115, 'Turkish', 7,  'A nomadic tribe travels from Eastern Anatolia to Ankara with their flock in a powerful social epic.',         4.4, 6800),
(11, 'Düşman',                         1979, 110, 'Turkish', 8,  'A man migrates to Istanbul and faces unemployment and poverty in the city slums. Written by Güney.',          4.2, 5100),
(12, 'Kibar Feyzo',                    1978,  95, 'Turkish', 5,  'A satire on feudal order in Eastern Anatolia. Feyzo tries to win the woman he loves from the local agha.',  4.3, 7200),
-- Lütfi Ö. Akad
(13, 'Gelin',                          1973,  95, 'Turkish', 2,  'First of the migration trilogy. A bride struggles against a patriarchal family after moving to Istanbul.',   4.2, 4700),
(14, 'Düğün',                          1973,  90, 'Turkish', 2,  'Second of the trilogy. A family wedding is the backdrop for tensions between old and new values.',            4.0, 3900),
(15, 'Diyet',                          1974,  88, 'Turkish', 2,  'Third of the trilogy. Explores urban poverty and the erosion of rural family bonds.',                        4.0, 3700),
(16, 'Vesikalı Yarim',                 1968,  95, 'Turkish', 2,  'A licensed woman falls in love with a young man who wants to save her. Türkan Şoray stars.',                 4.4, 7400),
(17, 'Ana',                            1967,  85, 'Turkish', 2,  'A powerful portrayal of a mother''s selfless sacrifice for her children in a struggling family.',             4.0, 3200),
-- Atıf Yılmaz
(18, 'Selvi Boylum Al Yazmalım',       1977,  90, 'Turkish', 1,  'A woman torn between her loyal husband and a charming truck driver. Türkan Şoray at her finest.',            4.3, 6300),
(19, 'Mine',                           1982, 100, 'Turkish', 1,  'A young married woman questions her identity and desires in a small town. Starring Müjde Ar.',               4.1, 4300),
(20, 'Adı Vasfiye',                    1985,  95, 'Turkish', 1,  'A mysterious woman described by multiple men who each remember her differently. Starring Müjde Ar.',         4.0, 3900),
(21, 'Bir Yudum Sevgi',                1984,  98, 'Turkish', 1,  'Atıf Yılmaz''s courageous look at female desire and societal pressure in 1980s Turkey.',                    3.9, 3400),
(22, 'Ah Güzel İstanbul',              1966,  88, 'Turkish', 1,  'A nostalgic romantic film capturing the unique atmosphere of 1960s Istanbul with Türkan Şoray.',              3.9, 4100),
(23, 'Şoför Nebahat',                  1960,  92, 'Turkish', 1,  'A woman becomes a taxi driver and fights to survive in a male-dominated world. A feminist classic.',          3.9, 3800),
(24, 'Berdel',                         1990, 102, 'Turkish', 13, 'Two girls are exchanged as brides in the berdel tradition. Directed by Bilge Olgaç.',                       4.1, 3200),
-- Ertem Eğilmez
(25, 'Hababam Sınıfı',                 1975,  95, 'Turkish', 6,  'The most beloved school comedy in Turkish cinema, based on Rıfat İlgaz''s famous novel.',                  4.4, 9500),
(26, 'Hababam Sınıfı Sınıfta Kaldı', 1975,  90, 'Turkish', 6,  'Second Hababam film. The same beloved characters return with new mischief and laughs.',                       4.2, 8100),
(27, 'Hababam Sınıfı Uyanıyor',       1976,  90, 'Turkish', 6,  'Third Hababam film. The students face new teachers and fresh chaos at school.',                              4.2, 7800),
(28, 'Hababam Sınıfı Tatilde',         1977,  92, 'Turkish', 6,  'Fourth Hababam film. The gang goes on holiday and the comedy continues outside the classroom.',               4.1, 7200),
(29, 'Davaro',                         1981,  95, 'Turkish', 6,  'A village simpleton comes to Istanbul. Kemal Sunal and Şener Şen shine together.',                           4.3, 8100),
(30, 'Züğürt Ağa',                     1985, 100, 'Turkish', 6,  'A once-powerful village ağa loses everything and struggles to adapt to city life. Şener Şen stars.',         4.3, 7600),
(31, 'Neşeli Günler',                  1978, 100, 'Turkish', 6,  'A cheerful ensemble comedy about neighbours and daily life that became a Yeşilçam staple.',                  3.8, 4800),
(32, 'Ah Nerede',                      1975,  88, 'Turkish', 6,  'Kemal Sunal plays a naive young man trying to find his place in the big city.',                              3.9, 5300),
(33, 'Banker Bilo',                    1980,  92, 'Turkish', 6,  'Kemal Sunal satirizes greed and financial schemes in this sharp and funny comedy.',                          4.0, 6100),
(34, 'Canım Kardeşim',                 1973,  85, 'Turkish', 6,  'A warm comedy about the bond and rivalry between two brothers.',                                              3.7, 4100),
(37, 'Tosun Paşa',                     1976,  90, 'Turkish', 6,  'Kemal Sunal plays a double role as a mild-mannered man and his intimidating lookalike.',                     4.0, 6500),
(38, 'Namuslu',                        1984,  92, 'Turkish', 6,  'Kemal Sunal plays an honest man pressured by those around him to compromise his principles.',                 3.9, 5900),
(39, 'Çiçek Abbas',                    1982,  90, 'Turkish', 6,  'A loveable village boy comes to the city and navigates urban life with innocence and humour.',                3.9, 5500),
(40, 'İnek Şaban',                     1982,  88, 'Turkish', 6,  'Kemal Sunal reprises his famous Şaban character in this standalone village comedy.',                          3.8, 5200),
-- Halit Refiğ
(43, 'Haremde Dört Kadın',             1965,  95, 'Turkish', 4,  'A historical drama set in the Ottoman harem examining the lives and power struggles of four women.',          4.0, 3100),
-- Osman Seden
(48, 'Şaban Oğlu Şaban',               1977,  90, 'Turkish', 9,  'Kemal Sunal as a simple village man navigating life with more heart than brains.',                            3.9, 6200),
(50, 'Tatlı Dillim',                   1972,  85, 'Turkish', 9,  'Türkan Şoray in a light romantic musical comedy set against a lively Istanbul backdrop.',                     3.7, 3600),
(51, 'Kızılırmak Karakoyun',           1967,  95, 'Turkish', 15, 'Türkan Şoray and Ayhan Işık in a sweeping romantic drama set along the Kızılırmak river.',                  4.0, 4200),
-- Memduh Ün
(52, 'Kırık Plak',                     1959,  90, 'Turkish', 10, 'A touching romantic drama starring Ayhan Işık and Belgin Doruk as young lovers in Istanbul.',                  3.8, 2400),
(53, 'Yalnızlar Rıhtımı',              1959,  90, 'Turkish', 10, 'A melancholic story of lonely dockworkers searching for meaning and connection in Istanbul.',                 3.7, 2100),
-- Yücel Çakmaklı
(55, 'Birleşen Yollar',                1970,  90, 'Turkish', 14, 'One of the first National Cinema films. A drama about values, identity and modern life.',                    3.8, 2600),
(56, 'Memleketim',                     1974,  92, 'Turkish', 14, 'A heartfelt film about love of homeland and the tension between tradition and modernity.',                    3.8, 2400),
-- Tunç Başaran
(57, 'Hakkari''de Bir Mevsim',        1983, 105, 'Turkish', 11, 'A city-raised teacher assigned to a remote mountain village has his entire worldview transformed.',           4.2, 3800),
-- Bilge Olgaç
(58, 'Gönül Yarası',                   1977,  88, 'Turkish', 13, 'A tender melodrama about love and heartbreak told with Bilge Olgaç''s characteristic sensitivity.',          3.9, 2700),
-- Orhan Aksoy
(59, 'Vurun Kahpeye',                  1973,  95, 'Turkish', 15, 'A patriotic teacher fights for her village during the Turkish War of Independence. A historical classic.',   3.8, 2900);

-- MovieGenres
INSERT INTO MovieGenres (movie_id, genre_id) VALUES
(1,1),(1,6),(2,1),(2,5),(3,1),(3,6),(4,1),(4,3),(5,1),(5,3),
(6,1),(6,6),(7,1),(7,12),(8,1),(9,1),(9,6),(10,1),(10,6),(11,1),(11,6),(12,1),(12,2),
(13,1),(13,6),(14,1),(14,6),(15,1),(15,6),(16,1),(16,3),(17,1),(17,3),
(18,1),(18,3),(18,5),(19,1),(19,3),(20,1),(20,3),(21,1),(22,3),(22,5),(22,8),(23,1),(23,6),(24,1),(24,12),
(25,2),(25,11),(26,2),(27,2),(28,2),(28,7),(29,2),(29,12),(30,2),(30,1),(31,2),(31,11),
(32,2),(33,2),(34,2),(34,11),(37,2),(38,2),(39,2),(39,12),(40,2),(40,12),
(43,1),(43,9),
(48,2),(48,12),(50,3),(50,5),(50,8),(51,3),(51,5),
(52,1),(52,5),(53,1),(53,3),
(55,1),(56,1),(57,1),(57,12),(58,1),(58,3),(59,1),(59,9);

-- MovieActors
INSERT INTO MovieActors (movie_id, actor_id, character_name, is_lead) VALUES
(1,3,'Osman',TRUE),(1,22,'Hasan',FALSE),
(2,14,'Haluk',TRUE),(2,13,'Meral',TRUE),
(3,22,'Mehmet',TRUE),(3,17,'Ayşe',FALSE),
(4,10,'Yusuf',TRUE),(4,11,'Muazzez',TRUE),
(5,1,'Süheyla',TRUE),(5,10,'Ali',FALSE),
(6,3,'Cabbar',TRUE),
(7,3,'Zeynel',TRUE),
(8,3,'Azem',TRUE),(8,5,'Memo',TRUE),
(9,5,'Seyit Ali',TRUE),
(10,22,'Seyit',TRUE),(10,4,'Berivan',TRUE),
(11,22,'Fikret',TRUE),
(12,3,'Feyzo',TRUE),(12,4,'Gülo',TRUE),
(13,4,'Meryem',TRUE),(13,15,'İlyas',TRUE),
(14,4,'Fatma',TRUE),(15,4,'Hacer',TRUE),
(16,1,'Sabahat',TRUE),(16,9,'Halil',TRUE),
(17,1,'Ana',TRUE),
(18,1,'Asya',TRUE),(18,9,'İlyas',TRUE),
(19,20,'Mine',TRUE),(20,1,'Vasfiye',TRUE),(20,20,'Friend',FALSE),
(21,20,'Ayşe',TRUE),(22,1,'Nermin',TRUE),(22,9,'Orhan',TRUE),
(23,2,'Nebahat',TRUE),(24,23,'Girl',TRUE),
(25,6,'Şaban',TRUE),(25,7,'Headmaster',FALSE),(25,8,'Mother',FALSE),
(26,6,'Şaban',TRUE),(26,7,'Headmaster',FALSE),
(27,6,'Şaban',TRUE),(27,7,'Headmaster',FALSE),
(28,6,'Şaban',TRUE),(28,7,'Headmaster',FALSE),
(29,6,'Memo',TRUE),(29,19,'Davaro',TRUE),
(30,19,'İhsan Ağa',TRUE),
(31,6,'Hasan',TRUE),(31,8,'Fatma',FALSE),
(32,6,'Şaban',TRUE),(33,6,'Bilo',TRUE),(33,7,'Partner',FALSE),
(34,6,'Brother',TRUE),(37,6,'Tosun',TRUE),(38,6,'Şaban',TRUE),(39,6,'Abbas',TRUE),(39,8,'Mother',FALSE),
(40,6,'Şaban',TRUE),
(43,1,'Haseki',TRUE),
(48,6,'Şaban',TRUE),(48,8,'Mother',FALSE),
(50,1,'Leyla',TRUE),(51,1,'Ayşe',TRUE),(51,10,'Man',TRUE),
(52,10,'Bülent',TRUE),(52,11,'Nermin',TRUE),
(53,12,'Dockworker',TRUE),
(55,16,'Young Man',TRUE),(56,14,'Hero',TRUE),
(57,22,'Teacher',TRUE),(58,1,'Woman',TRUE),(59,17,'Aliye',TRUE);

-- WatchHistory
INSERT INTO WatchHistory (history_id, user_id, movie_id, watched_at, watch_pct, watch_duration_min) VALUES
(1,1,25,'2025-03-01',100,95),(2,1,9,'2025-03-05',100,114),(3,1,12,'2025-03-10',100,95),
(4,1,18,'2025-03-14',100,90),(5,1,6,'2025-03-18',80,76),
(6,2,18,'2025-03-02',100,90),(7,2,22,'2025-03-07',85,75),(8,2,25,'2025-03-13',100,95),
(9,2,16,'2025-03-16',100,95),(10,2,9,'2025-03-20',100,114),
(11,3,1,'2025-03-03',100,90),(12,3,6,'2025-03-08',100,95),(13,3,11,'2025-03-12',70,77),
(14,3,10,'2025-03-17',100,115),
(15,4,30,'2025-03-04',100,100),(16,4,29,'2025-03-09',100,95),(17,4,25,'2025-03-15',100,95),
(18,4,37,'2025-03-19',100,90),
(19,5,9,'2025-03-06',100,114),(20,5,24,'2025-03-11',100,102),
(21,6,16,'2025-04-01',100,95),(22,6,9,'2025-04-03',100,114),(23,6,29,'2025-04-05',100,95),
(24,6,10,'2025-04-07',100,115),(25,6,25,'2025-04-10',100,95),
(26,7,25,'2025-04-02',100,95),(27,7,29,'2025-04-04',100,95),(28,7,30,'2025-04-06',100,100),
(29,7,26,'2025-04-08',100,90),(31,7,9,'2025-04-13',100,114),(34,8,10,'2025-04-05',100,115),
(35,8,16,'2025-04-07',90,86),(36,8,19,'2025-04-09',100,100),
(37,9,29,'2025-04-02',100,95),(38,9,30,'2025-04-04',100,100),(39,9,33,'2025-04-06',100,92),
(41,9,37,'2025-04-10',100,90),(42,10,16,'2025-04-01',100,95),(43,10,19,'2025-04-03',100,100),
(44,10,21,'2025-04-05',100,98),(45,10,18,'2025-04-07',100,90),(46,10,24,'2025-04-09',100,102),
(47,11,10,'2025-04-02',100,115),(48,11,11,'2025-04-04',100,110),(49,11,8,'2025-04-06',100,97),
(50,11,9,'2025-04-08',100,114),(51,11,12,'2025-04-10',100,95),
(52,12,25,'2025-04-01',100,95),(53,12,26,'2025-04-03',100,90),(54,12,27,'2025-04-05',100,90),
(55,12,28,'2025-04-07',100,92),(56,12,39,'2025-04-09',100,90),(58,13,1,'2025-04-02',100,90),
(59,13,2,'2025-04-04',100,90),(60,13,3,'2025-04-06',100,95),(61,13,10,'2025-04-08',100,115),
(63,14,18,'2025-04-01',100,90),(64,14,16,'2025-04-03',100,95),(65,14,19,'2025-04-05',100,100),
(66,14,20,'2025-04-07',100,95),(67,14,50,'2025-04-09',100,85);

-- Watchlists
INSERT INTO Watchlists (watchlist_id, user_id, movie_id, added_at) VALUES
(1,1,18,'2025-03-02'),(2,1,30,'2025-03-03'),(3,1,16,'2025-03-04'),
(4,2,9,'2025-03-02'),(5,2,6,'2025-03-05'),(6,2,12,'2025-03-08'),
(7,3,25,'2025-03-04'),(8,3,10,'2025-03-06'),(9,3,13,'2025-03-09'),
(10,4,1,'2025-03-05'),(11,4,11,'2025-03-07'),
(13,5,18,'2025-03-03'),(14,5,8,'2025-03-09'),(15,5,57,'2025-03-12'),
(16,6,10,'2025-04-02'),(17,6,12,'2025-04-03'),
(19,7,16,'2025-04-01'),(20,7,1,'2025-04-03'),(21,7,10,'2025-04-06'),
(22,8,9,'2025-04-02'),(23,8,29,'2025-04-04'),(24,8,30,'2025-04-06'),
(25,9,25,'2025-04-01'),(26,9,26,'2025-04-03'),(27,9,27,'2025-04-05'),
(28,10,9,'2025-04-02'),(29,10,10,'2025-04-04'),
(31,11,16,'2025-04-01'),(32,11,19,'2025-04-03'),(33,11,1,'2025-04-05'),
(34,12,29,'2025-04-02'),(35,12,30,'2025-04-04'),
(37,13,18,'2025-04-01'),
(39,14,9,'2025-04-02'),(40,14,10,'2025-04-04'),
(41,15,16,'2025-04-01'),(42,15,19,'2025-04-03'),(43,15,9,'2025-04-05');

-- Reviews
INSERT INTO Reviews (review_id, user_id, movie_id, rating, comment, created_at) VALUES
(1,1,25,5,'Hababam Sınıfı is the peak of Turkish comedy. Kemal Sunal is a legend.','2025-03-02'),
(2,1,9,5,'Yol is a truly shattering film. The genius of Güney in every frame.','2025-03-06'),
(3,1,12,4,'Kibar Feyzo makes you laugh and think at the same time. A masterpiece.','2025-03-11'),
(4,1,18,5,'Selvi Boylum is the most emotional Turkish film I have ever watched.','2025-03-15'),
(5,2,18,5,'I cried watching Selvi Boylum Al Yazmalı. Türkan Şoray is priceless.','2025-03-03'),
(6,2,22,4,'Ah Güzel İstanbul is pure nostalgia. A love letter to the city.','2025-03-09'),
(7,2,16,5,'Vesikalı Yarim is a landmark of Turkish cinema. Unforgettable.','2025-03-16'),
(8,3,1,5,'Susuz Yaz deserved every international award it received.','2025-03-04'),
(9,3,6,4,'Umut is a quiet, devastating portrait of poverty. Güney at his best.','2025-03-09'),
(10,3,10,5,'Sürü is one of the greatest films ever made in Turkey.','2025-03-18'),
(11,4,30,5,'Züğürt Ağa is Şener Şen''s finest performance. Hilarious and heartbreaking.','2025-03-05'),
(12,4,29,4,'Davaro is pure joy. Kemal Sunal and Şener Şen are a perfect pair.','2025-03-10'),
(13,4,37,4,'Tosun Paşa never gets old. Kemal Sunal in a double role is brilliant.','2025-03-20'),
(14,5,9,5,'Watching Yol feels like a masterclass in cinema. Extraordinary.','2025-03-07'),
(15,5,24,4,'Berdel handles women''s issues with great power and honesty.','2025-03-12'),
(16,6,16,5,'Vesikalı Yarim is how you make a great film about a woman.','2025-04-02'),
(17,6,9,5,'Yol says something new every time you watch it. A towering work.','2025-04-04'),
(18,6,29,4,'Davaro - Kemal Sunal and Şener Şen''s chemistry is unbelievable.','2025-04-06'),
(19,7,25,5,'Hababam Sınıfı is a classic that every generation can enjoy.','2025-04-03'),
(20,7,30,5,'Züğürt Ağa - Şener Şen at the peak of his career.','2025-04-07'),
(21,7,29,4,'Davaro is one of the funniest Turkish films ever made.','2025-04-09'),
(23,8,13,5,'Gelin is the strongest film of Akad''s trilogy. Very moving.','2025-04-04'),
(24,8,10,5,'Sürü is one of the most important films in Turkish cinema.','2025-04-06'),
(25,9,30,5,'Züğürt Ağa is the peak of Turkish comedy.','2025-04-03'),
(26,9,29,5,'Davaro and Züğürt Ağa are Şener Şen''s two masterpieces.','2025-04-05'),
(27,9,33,4,'Banker Bilo - Kemal Sunal as a social critic. Very clever.','2025-04-07'),
(28,10,16,5,'Vesikalı Yarim shows how much Türkan Şoray could carry a film alone.','2025-04-02'),
(29,10,19,4,'Mine is a brave and original film. Atıf Yılmaz was ahead of his time.','2025-04-04'),
(30,10,18,5,'Selvi Boylum Al Yazmalı is the peak of romantic drama in Turkish cinema.','2025-04-06'),
(31,11,10,5,'Sürü is Güney''s screenwriting genius on full display.','2025-04-03'),
(32,11,11,4,'Düşman captures urban despair in a very realistic way.','2025-04-05'),
(33,11,9,5,'Yol is the greatest achievement of Turkish cinema.','2025-04-07'),
(34,12,25,5,'Hababam Sınıfı appeals to every age. A timeless classic.','2025-04-02'),
(35,12,26,4,'Hababam Sınıfı Sınıfta Kaldı is as fun as the original.','2025-04-04'),
(36,12,29,4,'Davaro - two masters of comedy working together perfectly.','2025-04-08'),
(37,13,1,4,'Susuz Yaz earned its international recognition. A unique Turkish work.','2025-04-03'),
(38,13,2,4,'Sevmek Zamanı is full of existential questions. Beautifully made.','2025-04-05'),
(39,13,10,5,'Sürü is the all-time greatest Turkish film in my view.','2025-04-09'),
(40,14,18,5,'Selvi Boylum Al Yazmalı - I listen to the soundtrack on repeat after watching.','2025-04-02'),
(41,14,16,5,'Vesikalı Yarim is the most important female story in Turkish cinema.','2025-04-04'),
(42,14,19,4,'Mine is courageous and original. Atıf Yılmaz was a pioneer.','2025-04-06'),
(43,14,20,4,'Adı Vasfiye has such a creative narrative technique.','2025-04-08'),
(44,15,30,5,'Züğürt Ağa is Şener Şen''s best performance.','2025-04-03'),
(45,15,29,4,'Davaro is a shared memory of a whole generation.','2025-04-05');

-- Update avg_rating from reviews
SET SQL_SAFE_UPDATES = 0;
UPDATE Movies SET avg_rating = 4.1 WHERE movie_id = 1;
UPDATE Movies SET avg_rating = 4.1 WHERE movie_id = 2;
UPDATE Movies SET avg_rating = 4.0 WHERE movie_id = 3;
UPDATE Movies SET avg_rating = 3.8 WHERE movie_id = 4;
UPDATE Movies SET avg_rating = 4.0 WHERE movie_id = 5;
UPDATE Movies SET avg_rating = 4.3 WHERE movie_id = 6;
UPDATE Movies SET avg_rating = 4.0 WHERE movie_id = 7;
UPDATE Movies SET avg_rating = 4.1 WHERE movie_id = 8;
UPDATE Movies SET avg_rating = 4.6 WHERE movie_id = 9;
UPDATE Movies SET avg_rating = 4.4 WHERE movie_id = 10;
UPDATE Movies SET avg_rating = 4.2 WHERE movie_id = 11;
UPDATE Movies SET avg_rating = 4.3 WHERE movie_id = 12;
UPDATE Movies SET avg_rating = 4.2 WHERE movie_id = 13;
UPDATE Movies SET avg_rating = 4.0 WHERE movie_id = 14;
UPDATE Movies SET avg_rating = 4.0 WHERE movie_id = 15;
UPDATE Movies SET avg_rating = 4.4 WHERE movie_id = 16;
UPDATE Movies SET avg_rating = 4.0 WHERE movie_id = 17;
UPDATE Movies SET avg_rating = 4.3 WHERE movie_id = 18;
UPDATE Movies SET avg_rating = 4.1 WHERE movie_id = 19;
UPDATE Movies SET avg_rating = 4.0 WHERE movie_id = 20;
UPDATE Movies SET avg_rating = 3.9 WHERE movie_id = 21;
UPDATE Movies SET avg_rating = 3.9 WHERE movie_id = 22;
UPDATE Movies SET avg_rating = 3.9 WHERE movie_id = 23;
UPDATE Movies SET avg_rating = 4.1 WHERE movie_id = 24;
UPDATE Movies SET avg_rating = 4.4 WHERE movie_id = 25;
UPDATE Movies SET avg_rating = 4.2 WHERE movie_id = 26;
UPDATE Movies SET avg_rating = 4.2 WHERE movie_id = 27;
UPDATE Movies SET avg_rating = 4.1 WHERE movie_id = 28;
UPDATE Movies SET avg_rating = 4.3 WHERE movie_id = 29;
UPDATE Movies SET avg_rating = 4.3 WHERE movie_id = 30;
UPDATE Movies SET avg_rating = 3.8 WHERE movie_id = 31;
UPDATE Movies SET avg_rating = 3.9 WHERE movie_id = 32;
UPDATE Movies SET avg_rating = 4.0 WHERE movie_id = 33;
UPDATE Movies SET avg_rating = 3.7 WHERE movie_id = 34;
UPDATE Movies SET avg_rating = 4.0 WHERE movie_id = 43;
UPDATE Movies SET avg_rating = 3.9 WHERE movie_id = 47;
UPDATE Movies SET avg_rating = 3.9 WHERE movie_id = 48;
UPDATE Movies SET avg_rating = 3.7 WHERE movie_id = 50;
UPDATE Movies SET avg_rating = 4.0 WHERE movie_id = 51;
UPDATE Movies SET avg_rating = 3.8 WHERE movie_id = 52;
UPDATE Movies SET avg_rating = 3.7 WHERE movie_id = 53;
UPDATE Movies SET avg_rating = 3.8 WHERE movie_id = 55;
UPDATE Movies SET avg_rating = 3.8 WHERE movie_id = 56;
UPDATE Movies SET avg_rating = 4.2 WHERE movie_id = 57;
UPDATE Movies SET avg_rating = 3.9 WHERE movie_id = 58;
UPDATE Movies SET avg_rating = 3.8 WHERE movie_id = 59;

-- Subscriptions
INSERT INTO Subscriptions (sub_id, user_id, plan, start_date, end_date) VALUES
(1,1,'premium','2025-01-10','2026-01-10'),(2,2,'premium','2025-01-15','2026-01-15'),
(3,3,'basic','2025-02-01','2026-02-01'),(4,4,'basic','2025-02-10','2026-02-10'),
(5,5,'free','2025-03-01',NULL),(6,6,'premium','2025-03-05','2026-03-05'),
(7,7,'basic','2025-03-10','2026-03-10'),(8,8,'free','2025-03-12',NULL),
(9,9,'free','2025-03-15',NULL),(10,10,'basic','2025-03-20','2026-03-20'),
(11,11,'premium','2025-04-01','2026-04-01'),(12,12,'free','2025-04-05',NULL),
(13,13,'basic','2025-04-10','2026-04-10'),(14,14,'premium','2025-04-15','2026-04-15'),
(15,15,'free','2025-04-20',NULL);

-- Recommendations
INSERT INTO Recommendations (rec_id, user_id, movie_id, reason, created_at) VALUES
(1,1,10,'You watched Yol - you will love Sürü','2025-03-06'),
(2,1,13,'Based on your interest in social realism','2025-03-10'),
(3,2,13,'You enjoyed Vesikalı Yarim - try Gelin','2025-03-17'),
(4,2,10,'Popular among drama fans','2025-03-20'),
(5,3,25,'Top comedy - highly rated by users like you','2025-03-13'),
(7,4,9,'Based on your high ratings for drama','2025-03-11'),
(8,4,16,'You liked Züğürt Ağa - try Vesikalı Yarim','2025-03-20'),
(9,5,30,'Most-watched comedy this month','2025-03-12'),
(10,5,16,'Highly rated among romance fans','2025-03-14'),
(11,6,12,'You watched Sürü and Düşman - try Kibar Feyzo','2025-04-08'),
(12,7,18,'Popular among users who watched Vesikalı Yarim','2025-04-12'),
(14,9,37,'You enjoyed Davaro - try Tosun Paşa','2025-04-09'),
(15,10,20,'You watched Mine - you will enjoy Adı Vasfiye','2025-04-10');

-- ============================================================
--  TRIGGERS
-- ============================================================

-- Trigger 1: After a new review is inserted, automatically recalculate
--             avg_rating on the Movies table.
DELIMITER $$
CREATE TRIGGER trg_after_review_insert
AFTER INSERT ON Reviews
FOR EACH ROW
BEGIN
    UPDATE Movies
    SET avg_rating = (
        SELECT ROUND(AVG(rating), 1)
        FROM Reviews
        WHERE movie_id = NEW.movie_id
    )
    WHERE movie_id = NEW.movie_id;
END$$

-- Trigger 2: After a review is deleted, recalculate avg_rating.
--             If no reviews remain, set avg_rating to NULL.
CREATE TRIGGER trg_after_review_delete
AFTER DELETE ON Reviews
FOR EACH ROW
BEGIN
    UPDATE Movies
    SET avg_rating = (
        SELECT ROUND(AVG(rating), 1)
        FROM Reviews
        WHERE movie_id = OLD.movie_id
    )
    WHERE movie_id = OLD.movie_id;
END$$

-- Trigger 3: After a new WatchHistory record is inserted,
--             automatically increment view_count on the Movies table.
CREATE TRIGGER trg_after_watchhistory_insert
AFTER INSERT ON WatchHistory
FOR EACH ROW
BEGIN
    UPDATE Movies
    SET view_count = view_count + 1
    WHERE movie_id = NEW.movie_id;
END$$
DELIMITER ;

-- ============================================================
--  REQUIRED QUERIES
-- ============================================================

-- Search movies by genre
SELECT m.title, m.release_year, m.avg_rating, d.full_name AS director
FROM Movies m
JOIN MovieGenres mg ON m.movie_id = mg.movie_id
JOIN Genres g       ON mg.genre_id = g.genre_id
LEFT JOIN Directors d ON m.director_id = d.director_id
WHERE g.genre_name = 'Drama'
ORDER BY m.avg_rating DESC;

-- Search movies by release year range
SELECT title, release_year, avg_rating, duration_min
FROM Movies
WHERE release_year BETWEEN 1975 AND 1985
ORDER BY release_year, avg_rating DESC;

-- Search movies by minimum rating
SELECT m.title, m.release_year, m.avg_rating,
       d.full_name AS director,
       GROUP_CONCAT(g.genre_name SEPARATOR ', ') AS genres
FROM Movies m
LEFT JOIN Directors d ON m.director_id = d.director_id
LEFT JOIN MovieGenres mg ON m.movie_id = mg.movie_id
LEFT JOIN Genres g ON mg.genre_id = g.genre_id
WHERE m.avg_rating >= 4.3
GROUP BY m.movie_id, m.title, m.release_year, m.avg_rating, d.full_name
ORDER BY m.avg_rating DESC;

--  Top 10 most-watched (trending) movies
SELECT title, release_year, view_count, avg_rating
FROM Movies
ORDER BY view_count DESC
LIMIT 10;

-- Top 10 highest-rated movies
SELECT m.title, m.release_year, m.avg_rating, d.full_name AS director,
       COUNT(r.review_id) AS review_count
FROM Movies m
LEFT JOIN Directors d ON m.director_id = d.director_id
LEFT JOIN Reviews r   ON m.movie_id = r.movie_id
GROUP BY m.movie_id, m.title, m.release_year, m.avg_rating, d.full_name
HAVING review_count > 0
ORDER BY m.avg_rating DESC, review_count DESC
LIMIT 10;

-- User watch history with movie details
SELECT u.username, m.title, wh.watched_at, wh.watch_pct,
       wh.watch_duration_min,
       m.duration_min AS total_duration_min
FROM WatchHistory wh
JOIN Users  u ON wh.user_id  = u.user_id
JOIN Movies m ON wh.movie_id = m.movie_id
WHERE u.username = 'elif_y'
ORDER BY wh.watched_at DESC;

-- Total movies watched and total/average time per user
SELECT u.username, u.full_name,
       COUNT(DISTINCT wh.movie_id)                      AS movies_watched,
       IFNULL(SUM(wh.watch_duration_min), 0)            AS total_minutes,
       ROUND(IFNULL(AVG(wh.watch_duration_min), 0), 1)  AS avg_session_min,
       MIN(wh.watched_at)                                AS first_watch,
       MAX(wh.watched_at)                                AS last_watch
FROM Users u
LEFT JOIN WatchHistory wh ON u.user_id = wh.user_id
GROUP BY u.user_id, u.username, u.full_name
ORDER BY total_minutes DESC;

-- Genre distribution across all movies
SELECT g.genre_name,
       COUNT(mg.movie_id) AS movie_count,
       ROUND(COUNT(mg.movie_id) * 100.0 / (SELECT COUNT(*) FROM Movies), 1) AS pct
FROM Genres g
LEFT JOIN MovieGenres mg ON g.genre_id = mg.genre_id
GROUP BY g.genre_id, g.genre_name
ORDER BY movie_count DESC;

--  Most active users by total watch time
SELECT u.username, u.full_name, s.plan,
       COUNT(wh.history_id)          AS sessions,
       SUM(wh.watch_duration_min)    AS total_min,
       ROUND(AVG(wh.watch_duration_min), 1) AS avg_min_per_session
FROM Users u
JOIN WatchHistory wh ON u.user_id = wh.user_id
LEFT JOIN Subscriptions s ON u.user_id = s.user_id
GROUP BY u.user_id, u.username, u.full_name, s.plan
ORDER BY total_min DESC;

-- Director performance summary
SELECT d.full_name AS director,
       COUNT(DISTINCT m.movie_id)       AS films_directed,
       ROUND(AVG(m.avg_rating), 2)      AS avg_film_rating,
       SUM(m.view_count)                AS total_views,
       MAX(m.avg_rating)                AS best_rated_score
FROM Directors d
JOIN Movies m ON d.director_id = m.director_id
GROUP BY d.director_id, d.full_name
ORDER BY avg_film_rating DESC;

-- Actors appearing in the most films
SELECT a.full_name AS actor,
       COUNT(ma.movie_id)              AS films,
       SUM(ma.is_lead)                 AS lead_roles,
       ROUND(AVG(m.avg_rating), 2)     AS avg_movie_rating
FROM Actors a
JOIN MovieActors ma ON a.actor_id = ma.actor_id
JOIN Movies m       ON ma.movie_id = m.movie_id
GROUP BY a.actor_id, a.full_name
ORDER BY films DESC
LIMIT 10;

-- Trending analysis — most watched in last 30 days
SELECT m.title, m.avg_rating,
       COUNT(wh.history_id) AS views_last_30_days
FROM Movies m
JOIN WatchHistory wh
    ON m.movie_id = wh.movie_id
    AND wh.watched_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY m.movie_id, m.title, m.avg_rating
ORDER BY views_last_30_days DESC
LIMIT 10;

-- Subscription plan distribution
SELECT plan,
       COUNT(*) AS user_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Subscriptions), 1) AS pct
FROM Subscriptions
GROUP BY plan
ORDER BY user_count DESC;



-- Reusable SQL View: complete movie catalogue summary with director and genres
CREATE OR REPLACE VIEW vw_movie_catalogue_summary AS
SELECT m.movie_id,
       m.title,
       m.release_year,
       m.avg_rating,
       m.view_count,
       d.full_name AS director,
       GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR ', ') AS genres
FROM Movies m
LEFT JOIN Directors d ON m.director_id = d.director_id
LEFT JOIN MovieGenres mg ON m.movie_id = mg.movie_id
LEFT JOIN Genres g ON mg.genre_id = g.genre_id
GROUP BY m.movie_id, m.title, m.release_year, m.avg_rating, m.view_count, d.full_name;

-- Example use of the SQL View
SELECT title, release_year, director, genres, avg_rating, view_count
FROM vw_movie_catalogue_summary
WHERE avg_rating >= 4.3
ORDER BY avg_rating DESC, view_count DESC;

-- Language filter
SELECT title, release_year, language, avg_rating
FROM Movies
WHERE language = 'Turkish'
ORDER BY avg_rating DESC;

-- Delete from
DELETE FROM Reviews
WHERE user_id = 5 AND movie_id = 30;

-- Insert and Curdate (updated)
INSERT INTO Reviews (review_id, user_id, movie_id, rating, comment, created_at)
VALUES (46, 5, 30, 5, 'Züğürt Ağa is unforgettable — Şener Şen is extraordinary.',
CURDATE());
