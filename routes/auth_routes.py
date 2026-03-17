from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            login_user(user)
            flash("Login realizado com sucesso.", "success")
            return redirect("/dashboard")

        flash("Email ou senha inválidos.", "danger")

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        empresa = request.form["empresa"]
        email = request.form["email"]
        senha = request.form["senha"]

        usuario_existente = User.query.filter_by(email=email).first()
        if usuario_existente:
            flash("Este email já está cadastrado.", "warning")
            return redirect(url_for("auth.register"))

        senha_hash = generate_password_hash(senha)

        novo_user = User(
            empresa=empresa,
            email=email,
            senha=senha_hash
        )

        db.session.add(novo_user)
        db.session.commit()

        flash("Conta criada com sucesso. Faça login para continuar.", "success")
        return redirect("/login")

    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Você saiu da conta.", "info")
    return redirect("/login")