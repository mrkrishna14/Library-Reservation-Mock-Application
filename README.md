# Library Reservation System

A Flask-based web application for managing library room reservations. This system allows users to register, login, search for available rooms, make reservations, and manage their bookings.

## Features

- **User Authentication**: Secure user registration and login system with password hashing
- **Room Search**: Search for available rooms by library and time slot
- **Reservation Management**: Make, view, and cancel room reservations
- **Database Integration**: SQLite database for persistent data storage
- **Responsive UI**: Clean and intuitive web interface

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with bcrypt password hashing
- **Forms**: Flask-WTF with WTForms validation
- **Frontend**: HTML templates with CSS styling

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Library-Reservation-Mock-Application
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
cd "Library Reservation"
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. **Register**: Create a new account with a username and password
2. **Login**: Access your account with your credentials
3. **Search**: Select a library and time slot to see available rooms
4. **Reserve**: Choose an available room and confirm your reservation
5. **Manage**: View your current reservations or cancel them if needed

## Project Structure

```
Library Reservation/
├── app.py                 # Main Flask application
├── database.db           # SQLite database (excluded from git)
├── reserve.db            # Reservation database (excluded from git)
├── static/               # CSS and static files
│   └── dashcss.css
├── templates/            # HTML templates
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard2.html
│   ├── reserve.html
│   ├── avrooms.html
│   ├── finalize.html
│   ├── view.html
│   ├── cancel.html
│   └── error.html
└── Examples/             # Example files and documentation
```

## Security Features

- Password hashing using bcrypt
- Session management with Flask-Login
- Input validation and sanitization
- SQL injection prevention with parameterized queries

## Development Notes

- Debug mode is enabled for development (set `debug=False` for production)
- Database files are excluded from version control
- All user inputs are properly validated and sanitized

## Future Enhancements

- Email notifications for reservations
- Admin panel for library management
- Advanced scheduling with recurring reservations
- Mobile-responsive design improvements
- Integration with library management systems

## License

This project is created for educational purposes as part of a computer science portfolio.
