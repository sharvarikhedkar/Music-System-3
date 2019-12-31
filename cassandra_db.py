from cassandra.cluster import Cluster
cluster = Cluster(['172.17.0.2'])
session = cluster.connect()
session.execute("CREATE KEYSPACE IF NOT EXISTS music WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };")
session.execute("use music");
session.execute('''Create COLUMNFAMILY users(
      user_name VARCHAR,
      hashed_password VARCHAR,
      display_name VARCHAR,
      email_id VARCHAR,
      home_url VARCHAR,
      createdDate VARCHAR,
      modifiedDate VARCHAR,
      PRIMARY KEY (user_name)
);

''')
session.execute(''' Create COLUMNFAMILY musicData(
      Id INT,
      track_title VARCHAR,
      album_title VARCHAR,
      track_artist VARCHAR,
      track_length VARCHAR, 
      media_url VARCHAR,
      album_url VARCHAR,
      playlist_title VARCHAR,
      user_name VARCHAR,
      description VARCHAR,  
      track_id VARCHAR,
      playlist_id VARCHAR,
      createdDate VARCHAR,
      modifiedDate VARCHAR,
      PRIMARY KEY (id)
);
''')
