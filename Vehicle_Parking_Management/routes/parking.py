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

from models import (
    ParkingSlot,
    ParkingBooking
)


parking_bp = Blueprint(
    "parking",
    __name__
)


DAILY_PARKING_RATE = 50.0


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

    # Get the current user's active bookings
    active_bookings = ParkingBooking.query.filter_by(
        user_id=session["user_id"],
        status="Active"
    ).all()

    # Calculate current amount owed
    current_total = sum(
        booking.get_total_cost()
        for booking in active_bookings
    )

    return render_template(
        "dashboard.html",
        slots=slots,
        total=total,
        available=available,
        occupied=occupied,
        active_bookings=active_bookings,
        current_total=current_total,
        daily_rate=DAILY_PARKING_RATE
    )


@parking_bp.route("/park/<int:slot_id>", methods=["POST"])
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

    # Prevent a user from having multiple active bookings
    existing_booking = ParkingBooking.query.filter_by(
        user_id=session["user_id"],
        status="Active"
    ).first()

    if existing_booking:

        flash(
            "You already have an active parking booking.",
            "warning"
        )

        return redirect(
            url_for("parking.dashboard")
        )

    booking = ParkingBooking(
        user_id=session["user_id"],
        parking_slot_id=slot.id,
        daily_rate=DAILY_PARKING_RATE,
        status="Active"
    )

    slot.status = "Occupied"

    db.session.add(booking)
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

    booking = ParkingBooking.query.filter_by(
        parking_slot_id=slot.id,
        user_id=session["user_id"],
        status="Active"
    ).first()

    if not booking:

        flash(
            "You do not have an active booking for this slot.",
            "danger"
        )

        return redirect(
            url_for("parking.dashboard")
        )

    booking.exit_time = db.func.now()
    booking.status = "Completed"

    slot.status = "Available"

    db.session.commit()

    total = booking.get_total_cost()

    flash(
        f"Parking completed. Total amount: ₹{total:.2f}",
        "success"
    )

    return redirect(
        url_for("parking.dashboard")
    )


@parking_bp.route("/my-bookings")
@login_required
def my_bookings():

    bookings = ParkingBooking.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        ParkingBooking.booking_time.desc()
    ).all()

    total_paid = sum(
        booking.get_total_cost()
        for booking in bookings
        if booking.status == "Completed"
    )

    active_total = sum(
        booking.get_total_cost()
        for booking in bookings
        if booking.status == "Active"
    )

    return render_template(
        "my_bookings.html",
        bookings=bookings,
        total_paid=total_paid,
        active_total=active_total,
        daily_rate=DAILY_PARKING_RATE
    )

