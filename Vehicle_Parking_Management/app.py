from flask import Flask
from werkzeug.security import generate_password_hash

from extensions import db
from models import User, ParkingSlot

from routes.auth import auth_bp
from routes.parking import parking_bp


def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = "vehicle-parking-secret-key-change-this"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize SQLAlchemy
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(parking_bp)

    # Initialize database
    with app.app_context():

        db.create_all()

        # --------------------------------------------------
        # Create default parking slots
        # --------------------------------------------------

        if ParkingSlot.query.count() == 0:

            for i in range(1, 21):

                slot = ParkingSlot(
                    slot_number=f"A{i:02d}",
                    status="Available"
                )

                db.session.add(slot)

            db.session.commit()

        # --------------------------------------------------
        # Create default Admin user
        # --------------------------------------------------

        admin = User.query.filter_by(
            email="admin@gmail.com"
        ).first()

        if admin is None:

            admin = User(
                name="Admin",
                email="admin@gmail.com",
                password=generate_password_hash("a")
            )

            db.session.add(admin)
            db.session.commit()

            print("Default Admin user created.")
            print("Email: admin@gmail.com")
            print("Password: a")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)