from datetime import datetime, timezone

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="user",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    bookings = db.relationship(
        "ParkingBooking",
        back_populates="user",
        lazy=True
    )

    def __repr__(self):
        return f"<User {self.email}>"


class ParkingSlot(db.Model):
    __tablename__ = "parking_slots"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    slot_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Available",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    bookings = db.relationship(
        "ParkingBooking",
        back_populates="parking_slot",
        lazy=True
    )

    def __repr__(self):
        return f"<ParkingSlot {self.slot_number}>"


class ParkingBooking(db.Model):
    __tablename__ = "parking_bookings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    parking_slot_id = db.Column(
        db.Integer,
        db.ForeignKey("parking_slots.id"),
        nullable=False
    )

    booking_time = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    exit_time = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    daily_rate = db.Column(
        db.Float,
        default=50.0,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Active",
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="bookings"
    )

    parking_slot = db.relationship(
        "ParkingSlot",
        back_populates="bookings"
    )

    def get_days_parked(self):
        """
        Return the number of billable days.

        A booking is charged for at least one day.
        """
        end_time = self.exit_time

        if end_time is None:
            end_time = datetime.now(timezone.utc)

        start_time = self.booking_time

        # Handle databases that may return a naive datetime
        if start_time.tzinfo is None:
            start_time = start_time.replace(
                tzinfo=timezone.utc
            )

        if end_time.tzinfo is None:
            end_time = end_time.replace(
                tzinfo=timezone.utc
            )

        duration = end_time - start_time

        seconds = duration.total_seconds()

        # Minimum billing period is one day
        days = max(
            1,
            int((seconds + 86399) // 86400)
        )

        return days

    def get_total_cost(self):
        return self.get_days_parked() * self.daily_rate

    def __repr__(self):
        return f"<ParkingBooking {self.id}>"




