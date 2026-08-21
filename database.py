import sqlite3
from werkzeug.security import generate_password_hash

# Initialize DB
def init_db():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, name TEXT)''')
    try:
        c.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", 
                  ("admin@bookurticket.com", generate_password_hash("admin123"), "Admin"))
    except sqlite3.IntegrityError:
        pass
        
    try:
        c.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists
                 
    # Create movies table if it doesn't already exist (No Dropping!)
    c.execute('''CREATE TABLE IF NOT EXISTS movies
                 (id INTEGER PRIMARY KEY, title TEXT, synopsis TEXT, image_url TEXT, genre TEXT, language TEXT, is_top BOOLEAN, trailer_url TEXT)''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS showtimes
                 (id INTEGER PRIMARY KEY, movie_id INTEGER, time TEXT)''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY, showtime_id INTEGER, seats TEXT, user_email TEXT, amount REAL)''')
    try:
        c.execute("ALTER TABLE bookings ADD COLUMN amount REAL")
    except sqlite3.OperationalError:
        pass # Column already exists
                 
    c.execute('''CREATE TABLE IF NOT EXISTS favorites
                 (id INTEGER PRIMARY KEY, user_email TEXT, movie_id INTEGER, UNIQUE(user_email, movie_id))''')
    
    # Only seed default movies if the table is empty
    c.execute("SELECT COUNT(*) FROM movies")
    if c.fetchone()[0] == 0:
        movies = [
            # --- HINDI ---
            ("Jawan", "A high-octane action thriller detailing the journey of a man rectifying the wrongs in society.", "https://tse3.mm.bing.net/th/id/OIP.3m5hebQ5hjmc3A2lAV2jdQHaJQ?rs=1&pid=ImgDetMain&o=7&rm=3", "Action/Thriller", "Hindi", True, "https://www.youtube.com/watch?v=MWOlnZSnXJo"),
            ("Pathaan", "An Indian spy races against time to prevent a mercenary group from executing an attack.", "https://filmfare.wwmindia.com/content/2022/dec/pathaan21669878743.jpg", "Action/Spy", "Hindi", False, "https://www.youtube.com/watch?v=vqu4z34wENw"),
            ("Animal", "The complex relationship between a father and son leads to a cycle of violence.", "https://www.masala.com/wp-content/uploads/cloud/2023/09/22/image-17.png", "Action/Drama", "Hindi", True, "https://www.youtube.com/watch?v=S7i50IGdnNs"),
            ("Brahmastra", "Shiva, a DJ, learns that he has a strange connection to fire.", "https://www.newdvdreleasedates.com/images/posters/large/brahmastra-part-one-shiva-2022-06.jpg", "Fantasy/Action", "Hindi", False, "https://www.youtube.com/watch?v=BUjXzrgntcY"),
            ("Dangal", "Former wrestler Phogat struggles toward glory at the Commonwealth Games.", "https://3.bp.blogspot.com/-YqWHiUr3F5o/WF00T7t89zI/AAAAAAAATBU/oG4hDjVCco8QhdYNi7YbHsxlIIQ8DuEqQCLcB/s1600/Dangal-poster.jpg", "Sports/Biography", "Hindi", True, "https://www.youtube.com/watch?v=x_7YlGv9u1g"),
            ("Stree 2", "The town of Chanderi is haunted again by a headless ghost.", "https://m.media-amazon.com/images/M/MV5BMTA1NmUxYzItZmVmNy00YmQxLTk4Y2UtZjVkMWUwMWQ5N2IxXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg", "Horror/Comedy", "Hindi", True, "https://www.youtube.com/watch?v=VlvOgk5BHS4"), 
            ("12th Fail", "A true story of resilience of a man from Chambal who aspires to be an officer.", "https://m.media-amazon.com/images/M/MV5BNTE3OTIxZDYtNjA0NC00N2YxLTg1NGQtOTYxNmZkMDkwOWNjXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg", "Drama/Biography", "Hindi", True, "https://www.youtube.com/watch?v=KjbtuqENvVE"),
            ("Fighter", "Top IAF aviators come together in the face of imminent danger.", "https://upload.wikimedia.org/wikipedia/en/2/22/Flight_2021_film_poster.jpg", "Action", "Hindi", False, "https://www.youtube.com/watch?v=6amIq_mP4xM"), 
            
            # --- TELUGU ---
            ("Kalki 2898 AD", "A modern avatar of Vishnu descends to Earth to protect the world.", "https://preview.redd.it/kalki-2898-a-d-offical-poster-v0-qd7gl7vni0xc1.jpeg?auto=webp&s=e0e35ae2558735d624aacedf0534da0bdfd23731", "Sci-Fi/Action", "Telugu", True, "https://www.youtube.com/watch?v=vnXho7kmlPw"),
            ("Pushpa 2: The Rule", "The clash between Pushpraj and Bhanwar Singh continues.", "https://upload.wikimedia.org/wikipedia/en/1/11/Pushpa_2-_The_Rule.jpg", "Action/Drama", "Telugu", True, "https://www.youtube.com/watch?v=wboGYls1Bns"),
            ("RRR", "Story about two legendary revolutionaries journeying for their country.", "https://upload.wikimedia.org/wikipedia/en/d/d7/RRR_Poster.jpg", "Action/Drama", "Telugu", True, "https://www.youtube.com/watch?v=2_BkCz3OnlY"),
            ("Devara: Part 1", "An epic action saga set in a coastal land.", "https://m.media-amazon.com/images/M/MV5BYmI5NTljYWItMDhjMC00NDQwLWFhMjQtNWNjNDYzYzkwNGQ0XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg", "Action/Epic", "Telugu", False, "https://www.youtube.com/watch?v=NcCYq3bvlJM"),
            ("Hanu-Man", "An ordinary man gains the powers of Lord Hanuman to save his village.", "https://images.filmibeat.com/ph-big/2022/11/hanuman-2023_166902346040.jpg", "Superhero/Action", "Telugu", True, "https://www.youtube.com/watch?v=MKqJBhOgapM"),
            ("Salaar", "A gang leader tries to keep a promise to his dying friend.", "https://tse3.mm.bing.net/th/id/OIP.PGJDTDyRAWbBTcb-OYsrBwHaKt?rs=1&pid=ImgDetMain&o=7&rm=3", "Action/Crime", "Telugu", True, "https://www.youtube.com/watch?v=4GPvYMKtrtI"),
            ("Guntur Kaaram", "A commoner takes on the local goons to save his family.", "https://tse3.mm.bing.net/th/id/OIP.TmIos7B2HWfpJV6f-0IjjAHaLH?rs=1&pid=ImgDetMain&o=7&rm=3", "Action/Drama", "Telugu", False, "https://www.youtube.com/watch?v=q8M6Ybjr2Wc"), 

            # --- TAMIL ---
            ("The Greatest of All Time", "A field agent of the SATS retires and is pulled back into a mission.", "https://image.tmdb.org/t/p/original/i8qC0kVg6gbQMjKAvrnF8lt73EY.jpg", "Sci-Fi/Action", "Tamil", True, "https://www.youtube.com/watch?v=tb37SwBvRoQ"),
            ("Leo", "A mild-mannered cafe owner is caught in the drug cartel crosshairs.", "https://tse3.mm.bing.net/th/id/OIP.V9vbP9jHm4gsv82lt4wpUQHaLQ?rs=1&pid=ImgDetMain&o=7&rm=3", "Action/Thriller", "Tamil", True, "https://www.youtube.com/watch?v=Po3jStA673E"),
            ("Maharaja", "A quiet barber embarks on a quest for vengeance.", "https://tse4.mm.bing.net/th/id/OIP.A2xj-i29frQdjTGmPmEhWgHaJQ?rs=1&pid=ImgDetMain&o=7&rm=3", "Action/Crime", "Tamil", True, "https://www.youtube.com/watch?v=n3ttNeXKPHg"),
            ("Vikram", "A special agent investigates a series of murders.", "https://th.bing.com/th/id/R.fd577bc80d0437bb6ff37d34a5166f8e?rik=gdYKUW9RRB4dSQ&pid=ImgRaw&r=0", "Action/Thriller", "Tamil", True, "https://www.youtube.com/watch?v=VL34SYoMS_g"),
            ("Jailer", "A retired jailer goes on a manhunt to find his son.", "https://upload.wikimedia.org/wikipedia/en/c/cb/Jailer_2023_Tamil_film_poster.jpg", "Action/Comedy", "Tamil", False, "https://www.youtube.com/watch?v=Y5BeWdODPqo"), 

            # --- KANNADA ---
            ("K.G.F: Chapter 2", "In the Kolar Gold Fields, Rocky's name strikes fear.", "https://th.bing.com/th/id/R.166fcdaa5a984875e5be13a561fbf4ca?rik=8fB5YtytrPOHeQ&riu=http%3a%2f%2fwww.impawards.com%2fintl%2findia%2f2022%2fposters%2fkgf_chapter_two_ver2.jpg&ehk=zOcIyXGr3pKl1HdmMrXxjgKfWRvkWm8ZPbvSK%2bDTw9U%3d&risl=&pid=ImgRaw&r=0", "Action/Crime", "Kannada", True, "https://www.youtube.com/watch?v=jQsE85cI384"),
            ("Kantara", "A clash between a local forest officer and village folklore.", "https://tse3.mm.bing.net/th/id/OIP.8Iyvo9EuMFsnsVWKO5fpZQHaJQ?rs=1&pid=ImgDetMain&o=7&rm=3", "Action/Thriller", "Kannada", True, "https://www.youtube.com/watch?v=TMQUFhWm8C0"),
            ("777 Charlie", "Dharma is stuck in a rut with his negative lifestyle and is lonely.", "https://image.tmdb.org/t/p/original/7mMOmXAAkVSlQB8eG8hCSpsTV0G.jpg", "Adventure/Drama", "Kannada", True, "https://www.youtube.com/watch?v=Z3r7f9zw-mo"), 
            ("Vikrant Rona", "A legendary detective goes to a mysterious village.", "https://popcornreviewss.com/wp-content/uploads/2022/07/Vikrant-Rona-2022-Action-Adventure-Kannada-Movie-Review.jpg", "Action/Mystery", "Kannada", False, "https://www.youtube.com/watch?v=Ylte9v30UcY"), 

            # --- MALAYALAM ---
            ("Manjummel Boys", "A group of friends gets trapped in the Guna Caves.", "https://tse4.mm.bing.net/th/id/OIP.SLLhjs7luQTxENJuEQM3igHaK0?rs=1&pid=ImgDetMain&o=7&rm=3", "Survival/Drama", "Malayalam", True, "https://www.youtube.com/watch?v=rqBuKT_8dMY"), 
            ("Aavesham", "Three teenagers head to Bangalore for their studies.", "https://mir-s3-cdn-cf.behance.net/project_modules/1400/3760c0196052999.6618f555ef003.jpg", "Action/Comedy", "Malayalam", True, "https://www.youtube.com/watch?v=L0yEMl8PXnw"),
            ("Bramayugam", "A folklore horror story about a man in a mysterious mansion.", "https://tse4.mm.bing.net/th/id/OIP.IiIA0A6tZX3WL8cGRs9-UwHaLH?rs=1&pid=ImgDetMain&o=7&rm=3", "Horror/Thriller", "Malayalam", True, "https://www.youtube.com/watch?v=wRDfDx-nOPY"), 
            ("Lucifer", "A political Godfather dies and thieves take over.", "https://image.tmdb.org/t/p/original/2NEHMVAcVzAnBL24CtHUmnYuH4v.jpg", "Action/Crime", "Malayalam", False, "https://www.youtube.com/watch?v=x1-Ya0NZQso"), 

            # --- MARATHI ---
            ("Ved", "A story of unrequited love and second chances.", "https://tse4.mm.bing.net/th/id/OIP.gJLLq3ldUAFQrL78r4U_DwHaKs?rs=1&pid=ImgDetMain&o=7&rm=3", "Romance/Drama", "Marathi", True, "https://www.youtube.com/watch?v=Al2Gtph9ytI"),
            ("Sairat", "A lower-caste boy falls in love with an upper-caste girl.", "https://images.plex.tv/photo?size=medium-360&scale=2&url=https:%2F%2Fmetadata-static.plex.tv%2F3%2Fgracenote%2F34e8c9042c3247a73a85292423ae37a4.jpg", "Romance/Drama", "Marathi", False, "https://www.youtube.com/watch?v=iShPI_JF524"),
            ("Baipan Bhaari Deva", "Six estranged sisters meet to take part in a competition.", "https://tse4.mm.bing.net/th/id/OIP.Nqmk-DyXEbKPQqH6u930hQHaJQ?rs=1&pid=ImgDetMain&o=7&rm=3", "Drama/Comedy", "Marathi", True, "https://www.youtube.com/watch?v=KBpH0xpYdvc"), 

            # --- BENGALI ---
            ("Babli", "A heart-touching romantic drama.", "https://assets-in.bmscdn.com/iedb/movies/images/mobile/thumbnail/xlarge/babli-et00406175-1722924165.jpg", "Romance/Drama", "Bengali", True, "https://www.youtube.com/watch?v=x95D8umOU8Q"),
            ("Amazon Obhijaan", "An adventurer heads into the deep Amazon rainforest.", "https://th.bing.com/th/id/R.14f7ce70bdaa7c06f99543defab01308?rik=4o7hCGGAUXqm1w&riu=http%3a%2f%2fwww.impawards.com%2fintl%2findia%2f2017%2fposters%2famazon_obhijaan.jpg&ehk=4FJCgRA7W5NIywJsmwAzvZ1SEaxxy%2byFTpGsb%2fs4PFE%3d&risl=&pid=ImgRaw&r=0", "Adventure/Action", "Bengali", False, "https://www.youtube.com/watch?v=H1a9k7Mnpew"), 

            # --- PUNJABI ---
            ("Carry On Jatta 3", "Chaos ensues when a man lies to his family.", "https://images.plex.tv/photo?size=medium-360&scale=2&url=https:%2F%2Fmetadata-static.plex.tv%2Fe%2Fgracenote%2Fe2b81b379b9290667ab3f14b294ba7a1.jpg", "Comedy", "Punjabi", True, "https://www.youtube.com/watch?v=QJ67Pf8PLdk"),
            ("Mastaney", "An epic tale of five commoners fighting against invaders.", "https://tse4.mm.bing.net/th/id/OIP.FYseUp0He0vJVzKGCZBO2gHaLH?rs=1&pid=ImgDetMain&o=7&rm=3", "Action/History", "Punjabi", False, "https://www.youtube.com/watch?v=YMDfraipmA8")
        ]
        c.executemany("INSERT INTO movies (title, synopsis, image_url, genre, language, is_top, trailer_url) VALUES (?, ?, ?, ?, ?, ?, ?)", movies)
        
        # Initial Showtimes for default movies
        showtimes = []
        for m_id in range(1, len(movies) + 1):
            showtimes.append((m_id, "10:00"))
            showtimes.append((m_id, "14:30"))
            showtimes.append((m_id, "19:00"))
        c.executemany("INSERT INTO showtimes (movie_id, time) VALUES (?, ?)", showtimes)
        
    conn.commit()
    conn.close()

init_db()
