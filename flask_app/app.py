from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify # Pour la connexion serveur client
from werkzeug.security import generate_password_hash, check_password_hash # Pour le hachage de mdp
import sqlite3


app = Flask(__name__)
app.secret_key = "5e3131acc05d3c14bc1863c863d566b857f91a32559aa835b9023209993cee78"
# Bien sur il pour le déploiement il faut faire un appel à une variable d'environnement pour ne pas divulger la secret key.

# Fonction qui retourne le nom utilisateur dans la session
def is_logged_in():
    return "user_name" in session


# fonction pour envoyer une requête en se connectant à la base de donnéelse:
# Sauvegarde tout changement     
def execute_query(query, params=()):
    with sqlite3.connect('SQL_data/cours_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params) # Execute la requêtte
        conn.commit() # Envoie les changement à la base de données

        ## Erreur sqlite3.IntegrityError


# Fonction pour obtenir la connexion à la base de donnée
def get_db_connection():
    with  sqlite3.connect('SQL_data/cours_data.db') as conn:
        conn.row_factory = sqlite3.Row # ça transforme les lignes en dictionnaires
        return conn


# Action pour ce logout/quitter la session
@app.route("/logout")
def logout():
    session.pop("user_name", None)
    session.pop("user_id", None)

    return render_template("index.html")


# Chemin vers la page de connexion/inscritption
@app.route('/', methods = ["GET", "POST"])
def index():

    if request.method == "POST": # Si l'utilisateur envoie des données

        username = request.form.get("username")
        password = request.form.get("password")

        # Savoir si le compte est bien dans la base de données
        cursor = get_db_connection().cursor()
        
        try: # Try si la base ne contient aucun utilisateur

            cursor.execute("SELECT password, user_id FROM user WHERE user_name = ?", (username,))
            user_data = cursor.fetchone() # Obtention du mot de passe haché et de l'user_id
            
            # Si l'utilisateur est trouvé dans la bdd
            if user_data and user_data['password'] and check_password_hash(user_data[0], password):
                session["user_name"] = username
                session["user_id"] = user_data['user_id']
                return redirect(url_for("accueil"))

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")

        return render_template("index.html",
                               show_alert = True,
                               message = "Utilisateur non trouvé...")

    return render_template('index.html') # Affichage de la page principale du login


# Fonction pour ajouter un utilisateur dans la base de donnée
@app.route("/signup", methods = ["POST"])
def signup():

    username = request.form.get("username")
    password = request.form.get("password")

    if username and password:
    
        try: 
            # Hashage du password
            password = generate_password_hash(password)
            execute_query("INSERT INTO user (user_name, password) VALUES (?, ?)", (username, password))
            return redirect(url_for("index"))
        
        except sqlite3.IntegrityError: # Erruer lorsque l'utilisateur est déjà dans la base de données
            return redirect(url_for("index"))
    
    return render_template('index.html') # Affichage de la page principale du login



# Action pour afficher les cours en fonctions de l'onglet selectionné
def get_courses(category):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Obtention de tout les cours sauf ceux personnel d'un id différent de l'owner
    if category == "tous":
        cur.execute("""
        SELECT n.course_id,
               n.name
        FROM   Names            AS n
        JOIN   Category_cours   AS c  ON c.course_id = n.course_id
        LEFT   JOIN Cours_User  AS cu ON cu.course_id = n.course_id
        WHERE  (
                  c.category NOT IN ('personnel', 'partagé')      -- cours publics
               )
               OR
               (
                  c.category IN ('personnel', 'partagé')          -- cours privés
                  AND cu.user_id = ?                              -- même propriétaire
               )
        ORDER BY n.name COLLATE NOCASE
    """, (session["user_id"],))

    # Obtention des cours de appartenant à l'utilisateur connecté
    elif category == "personnel":
        cur.execute("""
        select n.course_id, n.name from Names as n 
        JOIN Cours_User as cu ON cu.course_id = n.course_id
        WHERE cu.user_id = ?""", (session["user_id"],))
    
    # Obtention des cours de la catégorie Partagé et initiaux
    else:
        cur.execute("SELECT n.course_id, n.name FROM Names as n JOIN Category_cours as c WHERE c.course_id = n.course_id and c.category = ?", (category,))  # Obtention des cours par rapport à la catégorie souhaité

    rows = cur.fetchall()
    courses = [dict(row) for row in rows]
    conn.close()
    
    return courses


# Chemin pour obtenir les nom des cours et leur id
@app.route('/get_courses', methods=['GET'])
def get_courses_api():
    if not is_logged_in():
        return redirect(url_for("index")) # Retour vers

    category = request.args.get("category", "initiaux")  # Default to "initiaux"
    courses = get_courses(category)
    return jsonify(courses)


# Chemin vers la page d'accueil
@app.route('/accueil') # Définition du chemin d'url vers la page index.html
def accueil():
    if not is_logged_in():
        return redirect(url_for("index")) # Retour vers
    return render_template('accueil.html') # Affichage de la page principale index.html


# Route to list all courses with their names
@app.route('/cours') # Définition du chemin d'url vers la page cours.html
def cours():
    if not is_logged_in():
        return redirect(url_for("index")) # Retour vers

    courses = get_courses("tous")

    if courses:
        # Affichage de la page des cours avec le résultat des cours de la base de données
        return render_template('cours.html', courses=courses)
    else:
        return "Cours non trouvé... :/"

# Chemin pour ajouter du vocabulaire dans la bdd
@app.route('/add_vocabulaire', methods=['POST'])
def add_vocabulaire():
    data = request.get_json()
    vocabulaire = data.get('vocabulaire')
    traduction = data.get('traduction')
    description = data.get('description', '')
    course_id = data.get('course_id', 0) # Par défault cours id 0

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO Cours (course_id, vocabulaire, traduction, description) VALUES (?, ?, ?, ?)",
        (course_id, vocabulaire, traduction, description)
    )
    conn.commit()
    conn.close()

    print(f"Ajout de {vocabulaire}, {traduction}")

    # On retourne les infos pour les afficher directement dans le tableau
    return jsonify({
        "vocabulaire": vocabulaire,
        "traduction": traduction,
        "description": description
    })

# Chemin pour supprimer du vocabulaire dans la bdd
@app.route("/delete_vocabulaire", methods=["POST"])
def delete_vocabulaire():
    data = request.get_json()
    items = data.get("items", [])

    if not items:
        return jsonify({"status": "no items provided"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    for item in items:
        course_id = item.get("course_id")
        vocabulaire = item.get("vocabulaire")
        if course_id and vocabulaire:
            print(f"Suppression : course_id={course_id}, vocabulaire={vocabulaire}")
            cur.execute(
                "DELETE FROM Cours WHERE course_id = ? AND vocabulaire = ?",
                (course_id, vocabulaire)
            )

    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"}), 200

# Chemin pour supprimer un cours
@app.route("/delete_cours", methods=["POST"])
def delete_cours():

    data = request.get_json()
    course_id = data.get('course_id')
    
    print(f"Suppression du cours {course_id}")

    # Suppression du cours dans names
    execute_query("DELETE FROM Names WHERE course_id = ?", (course_id,))

    # Suppression du cours dans Category_cours
    execute_query("DELETE FROM Category_cours WHERE course_id = ?", (course_id,))

    # Suppression du contenu du cours
    execute_query("DELETE FROM Cours WHERE course_id = ?", (course_id,))

    # Suppression dans la table cours user
    execute_query("DELETE FROM Cours_user WHERE course_id = ?", (course_id,))
    
    return "", 200

# Chemin pour créer son propre cours
@app.route("/create_cours", methods=["POST"])
def create_cours():
    
    data = request.get_json()  # Get JSON data from the request
    course_name = data.get('text')
     
    execute_query("INSERT INTO Names (name) VALUES (?)", (course_name,))
    
    # Obtention du course_id du nouveau cours
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT course_id FROM Names WHERE name = ?", (course_name,))
    course_id = cur.fetchone()['course_id']
    
    # Ajout de la category personnel du cours
    execute_query("INSERT INTO Category_cours (course_id, category) VALUES (?, ?)", (course_id, "personnel"))

    # Ajout du cours à l'utilisateur créant le cours
    execute_query("INSERT INTO Cours_user (user_id, course_id) VALUES (?, ?)",
                  (session["user_id"], course_id))

    return f"Cours {course_name} créé avec succés", 200

# Chemin pour Partager son propre cours
@app.route("/share_cours", methods=["POST"])
def share_cours():
    
    data = request.get_json()
    course_id = data.get('course_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Querry pour update la category en partagé
    cur.execute("""
        UPDATE Category_cours
        SET    category = ?
        WHERE  course_id = ?
    """, ("partage", course_id))
    
    conn.commit()
    conn.close()

    return "", 200

# Chemin pour rendre privé son propre cours (Vérouiller)
@app.route("/unshare_cours", methods=["POST"])
def unshare_cours():
    
    data = request.get_json()
    course_id = data.get('course_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Querry pour update la category en partagé
    cur.execute("""
        UPDATE Category_cours
        SET    category = ?
        WHERE  course_id = ?
    """, ("personnel", course_id))
    
    conn.commit()
    conn.close()

    return "", 200


# Fonction pour obtenir le contenu du cours reconnu par son id
def get_cours_content(course_id):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT course_id, vocabulaire, traduction, description FROM Cours WHERE course_id = ?', (course_id,))
    course_content = cur.fetchall()
    
    conn.close()
    
    return course_content

# Définition du chemin vers la page cours/0-...
@app.route('/cours/<int:course_id>')
def display_cours(course_id):
    if not is_logged_in():
        return redirect(url_for("index")) # Retour vers

    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch course name
    cur.execute('SELECT name FROM Names WHERE course_id = ?', (course_id,))
    course_name = cur.fetchone()

    # Obtenir le type du cours
    cur.execute('SELECT category FROM Category_cours WHERE course_id = ?', (course_id,))
    category = cur.fetchone()
    
    # Obtenir l'id de l'utilisateur créateur du cours
    cur.execute("""
        SELECT cu.user_id FROM cours_user as cu 
        where cu.course_id = ?""", (course_id,))

    owner = cur.fetchone()
    if not owner:
        owner_id = None
    else:
        owner_id = owner['user_id']

    course_content = get_cours_content(course_id)

    # Obtention de la liste de vocabulaire correspondant à l'id du cours
    if course_name and course_content: # Se le cours contient du vocabulaire
        return render_template('display_cours.html', course_name=course_name['name'], course_content=course_content, cours_category=category['category'], owner_id=owner_id)
        
    else: # Sinon affichage de la page avec le moyen d'ajouter du contenu
        return render_template('display_cours.html', course_name=course_name['name'], cours_category=category['category'], owner_id=owner_id)


if __name__ == '__main__':
    app.run(debug=True)

