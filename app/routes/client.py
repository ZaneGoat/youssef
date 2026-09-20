from flask import Blueprint, render_template, abort, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Terrain, Reservation
from app.forms import ReservationForm, EditProfileForm
from datetime import datetime

bp = Blueprint('client', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    terrains = Terrain.query.all()
    return render_template('client/index.html', title='Home', terrains=terrains)

@bp.route('/terrain/<int:id>')
def terrain_detail(id):
    terrain = Terrain.query.get_or_404(id)
    return render_template('client/terrain_detail.html', title=terrain.name, terrain=terrain)

@bp.route('/reserve/<int:id>', methods=['GET', 'POST'])
@login_required
def reserve(id):
    terrain = Terrain.query.get_or_404(id)
    form = ReservationForm()
    if form.validate_on_submit():
        # Basic check for time validity
        if form.start_time.data >= form.end_time.data:
            flash('End time must be after start time.')
            return render_template('client/reserve.html', title='Reserve', form=form, terrain=terrain)
        
        # Check for overlapping reservations
        existing_res = Reservation.query.filter(
            Reservation.terrain_id == id,
            Reservation.date == form.date.data,
            Reservation.status != 'cancelled'
        ).all()
        
        for res in existing_res:
            if (form.start_time.data < res.end_time and form.end_time.data > res.start_time):
                flash('This time slot is already booked.')
                return render_template('client/reserve.html', title='Reserve', form=form, terrain=terrain)

        # Calculate total price (hourly)
        duration = datetime.combine(datetime.today(), form.end_time.data) - datetime.combine(datetime.today(), form.start_time.data)
        hours = duration.total_seconds() / 3600
        total_price = hours * terrain.hourly_rate

        reservation = Reservation(user_id=current_user.id, terrain_id=id,
                                  date=form.date.data, start_time=form.start_time.data,
                                  end_time=form.end_time.data, total_price=total_price)
        db.session.add(reservation)
        db.session.commit()
        flash('Your reservation request has been submitted!')
        return redirect(url_for('client.my_reservations'))
    return render_template('client/reserve.html', title='Reserve', form=form, terrain=terrain)

@bp.route('/my-reservations')
@login_required
def my_reservations():
    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.timestamp.desc()).all()
    return render_template('client/my_reservations.html', title='My Reservations', reservations=reservations)

@bp.route('/reservation/cancel/<int:id>', methods=['POST'])
@login_required
def cancel_reservation(id):
    reservation = Reservation.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if reservation.status == 'pending':
        reservation.status = 'cancelled'
        db.session.commit()
        flash('Reservation cancelled.')
    else:
        flash('Cannot cancel a confirmed or already cancelled reservation.')
    return redirect(url_for('client.my_reservations'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('client.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('client/profile.html', title='Profile', form=form)
