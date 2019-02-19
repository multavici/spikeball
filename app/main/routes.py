from datetime import datetime, timedelta
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, CreateEventForm, AddCoordinatesForm
from app.models import User, Event, Location
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route("/")
@bp.route("/home")
def home():
    next = request.args.get("next")
    return render_template("home.html", title="Home Page", next=next)


@bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    events_today = (
        Event.query.filter(Event.datetime >= today)
        .filter(Event.datetime < today + timedelta(days=1))
        .order_by(Event.datetime)
        .all()
    )
    events_this_week = (
        Event.query.filter(Event.datetime >= today + timedelta(days=1))
        .filter(Event.datetime < today + timedelta(days=7))
        .order_by(Event.datetime)
        .all()
    )
    events_later = (
        Event.query.filter(Event.datetime >= today + timedelta(days=7))
        .order_by(Event.datetime)
        .all()
    )
    events_past = (
        Event.query.filter(Event.datetime < today)
        .order_by(Event.datetime.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "index.html",
        title="Home Page",
        events_today=events_today,
        events_this_week=events_this_week,
        events_later=events_later,
        events_past=events_past,
    )


@bp.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username.lower()).first_or_404()
    events = (
        Event.query.filter_by(user_id=user.id)
        .filter(Event.datetime >= datetime.today() - timedelta(days=1))
        .order_by(Event.datetime)
        .all()
    )
    return render_template("user.html", user=user, events=events)


@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data.lower()
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved")
        return redirect(url_for("main.edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title="Edit Profile", form=form)


@bp.route("/create_event", methods=["GET", "POST"])
@login_required
def create_event():
    form = CreateEventForm()
    locations = Location.query.all()
    if form.validate_on_submit():
        date_time = datetime.combine(form.date.data, form.time.data)
        location_id, new_location = None, None
        for location in locations:
            if form.location.data == location.name:
                location_id = location.id
        if not location_id:
            new_location = Location(name=form.location.data)
            db.session.add(new_location)
            db.session.flush()
            location_id = new_location.id
        event = Event(
            user_id=current_user.id,
            location_id=location_id,
            datetime=date_time,
            info=form.info.data,
        )
        event.add_participant(current_user)
        db.session.add(event)
        db.session.commit()
        flash(
            "Your event is now added! {} at {}".format(
                event.datetime.strftime("%A %d %B, %H:%M"), event.location.name
            )
        )
        if new_location:
            return redirect(url_for("main.add_location", location_id=new_location.id))
        return redirect(url_for("main.index"))
    return render_template(
        "create_event.html", title="Create Event", form=form, locations=locations
    )


@bp.route("/join/<event_id>")
@login_required
def join_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        flash("Event with id {} not found".format(event_id))
        return redirect(url_for("main.index"))
    event.add_participant(current_user)
    db.session.commit()
    flash("You are now joining {}".format(event))
    return redirect(url_for("main.index"))


@bp.route("/leave/<event_id>")
@login_required
def leave_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        flash("Event with id {} not found".format(event_id))
        return redirect(url_for("main.index"))
    event.remove_participant(current_user)
    db.session.commit()
    flash("You have left {}".format(event))
    return redirect(url_for("main.index"))


@bp.route("/delete/<event_id>")
@login_required
def delete_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        flash("Event with id {} not found".format(event_id))
        return redirect(url_for("main.index"))
    if event.creator != current_user:
        flash("Only the creator of an event can delete it")
        return redirect(url_for("main.index"))
    print(event.participants)
    print(current_user)
    if event.participants != [current_user] and event.participants != []:
        flash(
            "Other people said they would join, please make sure they know the event is cancelled"
        )
    db.session.delete(event)
    db.session.commit()
    flash("Event has been deleted".format(event))
    return redirect(url_for("main.index"))


@bp.route("/add_location/<location_id>", methods=["GET", "POST"])
@login_required
def add_location(location_id):
    location = Location.query.filter_by(id=location_id).first()
    form = AddCoordinatesForm()
    if form.validate_on_submit():
        location.latitude = form.latitude.data
        location.longitude = form.longitude.data
        db.session.commit()
        flash("The location {} has been saved".format(location.name))
        return redirect(url_for("main.index"))
    return render_template("add_location.html", location=location, form=form)


@bp.route("/event_detail/<event_id>")
@login_required
def event_detail(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        flash("Event with id {} not found".format(event_id))
        return redirect(url_for("main.index"))
    return render_template("event_detail.html", event=event)


@bp.route("/events_today/")
@login_required
def events_today():
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    events_today = (
        Event.query.filter(Event.datetime >= today)
        .filter(Event.datetime < today + timedelta(days=1))
        .all()
    )
    if events_today is None:
        flash("No events today")
        return redirect(url_for("main.index"))
    return render_template("events_today.html", events_today=events_today)
