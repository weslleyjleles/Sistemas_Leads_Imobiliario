from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from database import db
from models.lead import Lead

dashboard_bp = Blueprint("dashboard", __name__)

STATUS_OPTIONS = ["novo", "contato", "proposta", "fechado"]

@dashboard_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        mensagem = request.form["mensagem"]

        lead = Lead(
            nome=nome,
            telefone=telefone,
            mensagem=mensagem,
            status="novo",
            empresa_id=current_user.id
        )

        db.session.add(lead)
        db.session.commit()

        flash("Lead salvo com sucesso.", "success")
        return redirect(url_for("dashboard.dashboard"))

    busca = request.args.get("busca", "").strip()
    status_filtro = request.args.get("status", "").strip()

    query = Lead.query.filter_by(empresa_id=current_user.id)

    if busca:
        query = query.filter(Lead.nome.ilike(f"%{busca}%"))

    if status_filtro:
        query = query.filter(Lead.status == status_filtro)

    leads = query.order_by(Lead.id.desc()).all()

    leads_por_dia = (
        db.session.query(
            func.date(Lead.criado_em).label("dia"),
            func.count(Lead.id).label("total")
        )
        .filter(Lead.empresa_id == current_user.id)
        .group_by(func.date(Lead.criado_em))
        .order_by(func.date(Lead.criado_em))
        .all()
    )

    chart_labels = [str(item.dia) for item in leads_por_dia]
    chart_values = [item.total for item in leads_por_dia]

    status_counts = {
        "novo": Lead.query.filter_by(empresa_id=current_user.id, status="novo").count(),
        "contato": Lead.query.filter_by(empresa_id=current_user.id, status="contato").count(),
        "proposta": Lead.query.filter_by(empresa_id=current_user.id, status="proposta").count(),
        "fechado": Lead.query.filter_by(empresa_id=current_user.id, status="fechado").count(),
    }

    kanban_leads = {
        "novo": Lead.query.filter_by(empresa_id=current_user.id, status="novo").order_by(Lead.id.desc()).all(),
        "contato": Lead.query.filter_by(empresa_id=current_user.id, status="contato").order_by(Lead.id.desc()).all(),
        "proposta": Lead.query.filter_by(empresa_id=current_user.id, status="proposta").order_by(Lead.id.desc()).all(),
        "fechado": Lead.query.filter_by(empresa_id=current_user.id, status="fechado").order_by(Lead.id.desc()).all(),
    }

    return render_template(
        "dashboard.html",
        leads=leads,
        user=current_user,
        busca=busca,
        status_filtro=status_filtro,
        chart_labels=chart_labels,
        chart_values=chart_values,
        status_counts=status_counts,
        status_options=STATUS_OPTIONS,
        kanban_leads=kanban_leads
    )


@dashboard_bp.route("/lead/<int:lead_id>/editar", methods=["GET", "POST"])
@login_required
def editar_lead(lead_id):
    lead = Lead.query.filter_by(id=lead_id, empresa_id=current_user.id).first_or_404()

    if request.method == "POST":
        lead.nome = request.form["nome"]
        lead.telefone = request.form["telefone"]
        lead.mensagem = request.form["mensagem"]
        lead.status = request.form["status"]

        db.session.commit()
        flash("Lead atualizado com sucesso.", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("edit_lead.html", lead=lead, status_options=STATUS_OPTIONS)


@dashboard_bp.route("/lead/<int:lead_id>/status", methods=["POST"])
@login_required
def atualizar_status(lead_id):
    lead = Lead.query.filter_by(id=lead_id, empresa_id=current_user.id).first_or_404()

    novo_status = request.form["status"]

    if novo_status in STATUS_OPTIONS:
        lead.status = novo_status
        db.session.commit()
        flash("Status do lead atualizado.", "info")

    return redirect(url_for("dashboard.dashboard"))


@dashboard_bp.route("/lead/<int:lead_id>/kanban-status", methods=["POST"])
@login_required
def atualizar_status_kanban(lead_id):
    lead = Lead.query.filter_by(id=lead_id, empresa_id=current_user.id).first_or_404()

    data = request.get_json()
    novo_status = data.get("status")

    if novo_status in STATUS_OPTIONS:
        lead.status = novo_status
        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"success": False}), 400


@dashboard_bp.route("/lead/<int:lead_id>/excluir", methods=["POST"])
@login_required
def excluir_lead(lead_id):
    lead = Lead.query.filter_by(id=lead_id, empresa_id=current_user.id).first_or_404()

    db.session.delete(lead)
    db.session.commit()

    flash("Lead excluído com sucesso.", "info")
    return redirect(url_for("dashboard.dashboard"))