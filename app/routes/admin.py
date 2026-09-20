import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from flask import abort
from app import db
from app.models import Terrain, Reservation, User
from app.forms import TerrainForm, AdminEditUserForm

bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def get_terrain_images():
    image_dir = os.path.join(current_app.static_folder, 'images', 'terrains')
    images = []
    if os.path.exists(image_dir):
        for f in os.listdir(image_dir):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append((f, f))
    return images

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_reservations = Reservation.query.count()
    total_revenue = db.session.query(db.func.sum(Reservation.total_price)).filter(Reservation.status == 'confirmed').scalar() or 0
    available_terrains = Terrain.query.count()
    upcoming_reservations = Reservation.query.filter(Reservation.status == 'pending').order_by(Reservation.date.asc()).limit(5).all()
    return render_template('admin/dashboard.html', title='Admin Dashboard', 
                           total_reservations=total_reservations, 
                           total_revenue=total_revenue,
                           available_terrains=available_terrains,
                           upcoming_reservations=upcoming_reservations)

@bp.route('/terrains')
@login_required
@admin_required
def manage_terrains():
    terrains = Terrain.query.all()
    return render_template('admin/manage_terrains.html', title='Manage Terrains', terrains=terrains)

@bp.route('/terrain/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_terrain():
    form = TerrainForm()
    form.image_url.choices = get_terrain_images()
    if form.validate_on_submit():
        terrain = Terrain(name=form.name.data, terrain_type=form.terrain_type.data,
                          description=form.description.data, hourly_rate=form.hourly_rate.data,
                          image_url=form.image_url.data)
        db.session.add(terrain)
        db.session.commit()
        flash('Terrain added successfully!')
        return redirect(url_for('admin.manage_terrains'))
    return render_template('admin/terrain_form.html', title='Add Terrain', form=form)

@bp.route('/terrain/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_terrain(id):
    terrain = Terrain.query.get_or_404(id)
    form = TerrainForm(obj=terrain)
    form.image_url.choices = get_terrain_images()
    if form.validate_on_submit():
        terrain.name = form.name.data
        terrain.terrain_type = form.terrain_type.data
        terrain.description = form.description.data
        terrain.hourly_rate = form.hourly_rate.data
        terrain.image_url = form.image_url.data
        db.session.commit()
        flash('Terrain updated successfully!')
        return redirect(url_for('admin.manage_terrains'))
    return render_template('admin/terrain_form.html', title='Edit Terrain', form=form)

@bp.route('/terrain/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_terrain(id):
    terrain = Terrain.query.get_or_404(id)
    db.session.delete(terrain)
    db.session.commit()
    flash('Terrain deleted successfully!')
    return redirect(url_for('admin.manage_terrains'))

@bp.route('/reservations')
@login_required
@admin_required
def manage_reservations():
    reservations = Reservation.query.order_by(Reservation.timestamp.desc()).all()
    return render_template('admin/manage_reservations.html', title='Manage Reservations', reservations=reservations)

@bp.route('/reservation/confirm/<int:id>', methods=['POST'])
@login_required
@admin_required
def confirm_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    reservation.status = 'confirmed'
    db.session.commit()
    flash('Reservation confirmed!')
    return redirect(url_for('admin.manage_reservations'))

@bp.route('/reservation/cancel/<int:id>', methods=['POST'])
@login_required
@admin_required
def cancel_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    reservation.status = 'cancelled'
    db.session.commit()
    flash('Reservation cancelled!')
    return redirect(url_for('admin.manage_reservations'))

@bp.route('/clients')
@login_required
@admin_required
def manage_clients():
    clients = User.query.filter_by(role='client').all()
    return render_template('admin/manage_clients.html', title='Manage Clients', clients=clients)

@bp.route('/client/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_client(id):
    client = User.query.get_or_404(id)
    if client.is_admin():
        flash('Cannot delete an admin user.')
    else:
        db.session.delete(client)
        db.session.commit()
        flash('Client deleted successfully!')
    return redirect(url_for('admin.manage_clients'))

@bp.route('/client/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_client(id):
    user = User.query.get_or_404(id)
    form = AdminEditUserForm(user.id, user.username, user.email, obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('User information updated successfully!')
        return redirect(url_for('admin.manage_clients'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role
    return render_template('admin/edit_user.html', title='Edit User', form=form, user=user)
