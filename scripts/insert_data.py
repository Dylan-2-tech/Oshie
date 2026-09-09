import sqlite3
import numpy as np
import json

# fonction d'ajout de données dans une la table (vocab, trad, desc)

def add_data(cursor, vocab, trad, desc):
    
    # Ajout de la carte
    requette = f"Insert into Cours Value({vocab}, {trad}, {desc});"
    cursor.execute(requette)



# optention des données à partir du json
data = {}
with open("../cours/cours1.json", "r") as file:
    
    data = json.load(file)

    file.close()

# obtention du contenu
card_list: list = []
# Check si c'est une liste et si c'est dans le json
if "content" in data and isinstance(data["content"], list):
    card_list = data["content"]

print(card_list)


con = sqlite3.connect('../SQL_data/cours/politesse/data.db')
cursor = con.cursor()

for elem in card_list:
    for vocab, trad in elem.keys():
        add_data(cursor, vocab, trad, "")


# Insere des données
result = cursor.execute("""select * from Cours;""")

listeLigne = result.fetchall()

con.close()

npListeLigne = np.array(listeLigne)

print("Contenue de du cours:\n")
print(npListeLigne[0: 10])


