
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    # Admin user (barber)
    admin = User(
        name="Ronald's Groom Suite Admin",
        email='admin@groomsuite.com',
        password=generate_password_hash('admin123'),
        role='admin'
    )

    # Test groom client
    client = User(
        name='Marcus Johnson',
        email='marcus@email.com',
        password=generate_password_hash('client123'),
        role='client'
    )

    db.session.add(admin)
    db.session.add(client)
    db.session.commit()
    print('Users seeded successfully!')