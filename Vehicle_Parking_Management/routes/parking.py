from functools import wraps

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    flash
)

from extensions import db
from models import ParkingSlot


parking_bp = Blueprint(
    "parking",
    __name__
)


def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login to continue.",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        return function(*args, **kwargs)

    return decorated_function


@parking_bp.route("/")
def index():

    if "user_id" in session:
        return redirect(
            url_for("parking.dashboard")
        )

    return redirect(
        url_for("auth.login")
    )


@parking_bp.route("/dashboard")
@login_required
def dashboard():

    slots = ParkingSlot.query.order_by(
        ParkingSlot.id
    ).all()

    total = len(slots)

    available = sum(
        1
        for slot in slots
        if slot.status == "Available"
    )

    occupied = sum(
        1
        for slot in slots
        if slot.status == "Occupied"
    )

    return render_template(
        "dashboard.html",
        slots=slots,
        total=total,
        available=available,
        occupied=occupied
    )


@parking_bp.route(
    "/park/<int:slot_id>",
    methods=["POST"]
)
@login_required
def park_vehicle(slot_id):

    slot = db.session.get(
        ParkingSlot,
        slot_id
    )

    if not slot:

        flash(
            "Parking slot not found.",
            "danger"
        )

        return redirect(
            url_for("parking.dashboard")
        )

    if slot.status == "Occupied":

        flash(
            "This parking slot is already occupied.",
            "warning"
        )

        return redirect(
            url_for("parking.dashboard")
        )

    slot.status = "Occupied"

    db.session.commit()

    flash(
        f"Vehicle parked in slot {slot.slot_number}.",
        "success"
    )

    return redirect(
        url_for("parking.dashboard")
    )


@parking_bp.route(
    "/release/<int:slot_id>",
    methods=["POST"]
)
@login_required
def release_vehicle(slot_id):

    slot = db.session.get(
        ParkingSlot,
        slot_id
    )

    if not slot:

        flash(
            "Parking slot not found.",
            "danger"
        )

        return redirect(
            url_for("parking.dashboard")
        )

    slot.status = "Available"

    db.session.commit()

    flash(
        f"Slot {slot.slot_number} is now available.",
        "success"
    )

    return redirect(
        url_for("parking.dashboard")
    )