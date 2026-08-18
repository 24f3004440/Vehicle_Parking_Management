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

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
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

    def __repr__(self):
        return f"<ParkingSlot {self.slot_number}>"