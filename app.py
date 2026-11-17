import os
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cle-locale")


def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
    )


def executer(sql, params=(), lire=False):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if lire:
                return cur.fetchall()
            conn.commit()
    finally:
        conn.close()


@app.route("/")
def accueil():
    return redirect(url_for("liste_produits"))


# ---------- CATEGORIES ----------
@app.route("/categories")
def liste_categories():
    categories = executer(
        "SELECT * FROM CATEGORIE_PRODUIT ORDER BY libelle", lire=True)
    return render_template("categories.html", categories=categories)


@app.route("/categories/ajouter", methods=["POST"])
def ajouter_categorie():
    executer("INSERT INTO CATEGORIE_PRODUIT (libelle) VALUES (%s)",
             (request.form["libelle"],))
    return redirect(url_for("liste_categories"))


@app.route("/categories/<int:id>/modifier", methods=["GET", "POST"])
def modifier_categorie(id):
    if request.method == "POST":
        executer("UPDATE CATEGORIE_PRODUIT SET libelle=%s WHERE id_categorie=%s",
                 (request.form["libelle"], id))
        return redirect(url_for("liste_categories"))
    categorie = executer(
        "SELECT * FROM CATEGORIE_PRODUIT WHERE id_categorie=%s", (id,), lire=True)[0]
    return render_template("modifier_categorie.html", categorie=categorie)


@app.route("/categories/<int:id>/supprimer", methods=["POST"])
def supprimer_categorie(id):
    try:
        executer("DELETE FROM CATEGORIE_PRODUIT WHERE id_categorie=%s", (id,))
    except pymysql.err.IntegrityError:
        flash("Impossible de supprimer : cette catégorie contient des produits.")
    return redirect(url_for("liste_categories"))


# ---------- PRODUITS ----------
@app.route("/produits")
def liste_produits():
    produits = executer(
        """SELECT p.id_produit, p.designation, p.prix_vente, c.libelle
           FROM PRODUIT p
           JOIN CATEGORIE_PRODUIT c ON p.id_categorie = c.id_categorie
           ORDER BY p.designation""", lire=True)
    return render_template("produits.html", produits=produits)


@app.route("/produits/ajouter", methods=["GET", "POST"])
def ajouter_produit():
    if request.method == "POST":
        executer(
            "INSERT INTO PRODUIT (designation, prix_vente, id_categorie) VALUES (%s, %s, %s)",
            (request.form["designation"], request.form["prix_vente"],
             request.form["id_categorie"]))
        return redirect(url_for("liste_produits"))
    categories = executer("SELECT * FROM CATEGORIE_PRODUIT ORDER BY libelle", lire=True)
    return render_template("produit_form.html", produit=None, categories=categories)


@app.route("/produits/<int:id>/modifier", methods=["GET", "POST"])
def modifier_produit(id):
    if request.method == "POST":
        executer(
            """UPDATE PRODUIT SET designation=%s, prix_vente=%s, id_categorie=%s
               WHERE id_produit=%s""",
            (request.form["designation"], request.form["prix_vente"],
             request.form["id_categorie"], id))
        return redirect(url_for("liste_produits"))
    produit = executer("SELECT * FROM PRODUIT WHERE id_produit=%s", (id,), lire=True)[0]
    categories = executer("SELECT * FROM CATEGORIE_PRODUIT ORDER BY libelle", lire=True)
    return render_template("produit_form.html", produit=produit, categories=categories)


@app.route("/produits/<int:id>/supprimer", methods=["POST"])
def supprimer_produit(id):
    executer("DELETE FROM PRODUIT WHERE id_produit=%s", (id,))
    return redirect(url_for("liste_produits"))


if __name__ == "__main__":
    app.run(debug=True)