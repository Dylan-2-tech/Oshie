import sqlite3
import numpy as np

con = sqlite3.connect('../SQL_data/cours/politesse/data.db')
cursor = con.cursor()

# Affiche les données
result = cursor.execute("""select * from Cours;""")

listeLigne = result.fetchall()

con.close()

npListeLigne = np.array(listeLigne)

print("Contenue de du cours:\n")
print(npListeLigne[0: 10])
