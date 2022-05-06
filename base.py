import sqlalchemy

engine = sqlalchemy.create_engine('postgresql://postgres:140596@localhost:5432/Vkinder')
engine
connection = engine.connect()
sel = connection.execute("""
SELECT * FROM sets;
""").fetchall()
print(sel)