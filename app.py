from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
import psycopg2

app = Flask(__name__)
app.secret_key = 'sk'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:vamsi@localhost:5432/library'
db = SQLAlchemy(app)
conn = psycopg2.connect(
    host='localhost', dbname='library', user='postgres', password='vamsi', port=5432
)

class User(db.Model):
    """Model for user accounts."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    type_of_acc = db.Column(db.String(20), nullable=False)

    def __init__(self, username, password, type_of_acc):
        self.username = username
        self.password = password
        self.type_of_acc = type_of_acc

@app.route('/')
def index():
    """Home page route."""
    return render_template('welcome.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        type_of_acc = request.form["type_of_acc"]

        new_user = User(username, password, type_of_acc)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    """User login route."""
    if request.method == 'POST':
        if 'username' not in request.form or 'password' not in request.form:
            return "Form data missing", 400

        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            session['type_of_acc'] = user.type_of_acc
            if user.type_of_acc == 'librarian':
                return redirect(url_for('dashboard'))
            elif user.type_of_acc == 'student':
                return redirect(url_for('std_dashboard'))
        elif user:
            return "Incorrect password"
        else:
            return "User not found"

    return render_template('login.html')

@app.route("/dashboard")
def dashboard():
    """Librarian dashboard route."""
    cur = conn.cursor()
    query = "SELECT book_id, book_name, availability FROM books"
    cur.execute(query)
    list_books = cur.fetchall()
    cur.close()
    return render_template("index.html", list_books=list_books)

@app.route("/add_book", methods=['POST'])
def add_book():
    """Route to add a book."""
    cur = conn.cursor()
    try:
        if request.method == "POST":
            book_id = request.form['id']
            book_name = request.form['Bookname']
            availability = request.form['availability']
            cur.execute(
                "INSERT INTO books (book_id, book_name, availability) VALUES (%s, %s, %s)",
                (book_id, book_name, availability)
            )
            conn.commit()
            flash("Added Successfully")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {str(e)}")
    finally:
        cur.close()
    return redirect(url_for('dashboard'))

@app.route('/modify/<int:book_id>', methods=['POST', 'GET'])
def modify(book_id):
    """Route to modify a book."""
    cur = conn.cursor()
    if request.method == 'POST':
        book_name = request.form['Bookname']
        availability = request.form['availability']
        cur.execute(
            "UPDATE books SET book_name=%s, availability=%s WHERE book_id=%s",
            (book_name, availability, book_id)
        )
        conn.commit()
        flash('Book modified successfully')
        return redirect(url_for('dashboard'))
    else:
        cur.execute("SELECT book_id, book_name, availability FROM books WHERE book_id = %s", (book_id,))
        book = cur.fetchone()
        cur.close()
        
        book_data = {
            'id': book[0],
            'book_name': book[1],
            'availability': book[2]
        }
        return render_template('modify.html', book=book_data)

@app.route('/remove/<int:book_id>', methods=['POST', 'GET'])
def remove(book_id):
    """Route to remove a book."""
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
        conn.commit()
        flash("Removed successfully")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {str(e)}")
    finally:
        cur.close()
    return redirect(url_for('dashboard'))

@app.route("/logout")
def logout():
    """User logout route."""
    session.pop('username', None)
    flash("Logged out successfully")
    return redirect(url_for('login'))

@app.route('/std_dashboard')    
def std_dashboard():
    """Student dashboard route."""
    cur = conn.cursor()
    query = "SELECT book_id, book_name, availability FROM books"
    cur.execute(query)
    list_books = cur.fetchall()
    cur.close()
    return render_template('std_dash.html', list_books=list_books)

@app.route('/return_book/<int:book_id>', methods=['POST', 'GET'])
def return_books(book_id):
    """Route to return a borrowed book."""
    cur = conn.cursor()
    cur.execute('SELECT availability FROM books WHERE book_id = %s', (book_id,))
    data = cur.fetchone()
    
    if data and data[0] == 0:
        try:
            cur.execute("UPDATE books SET availability = %s WHERE book_id = %s", (1, book_id))
            conn.commit()
            flash('Success in returning the book')
        except Exception as e:
            conn.rollback()
            flash(f"An error occurred: {str(e)}")
    else:
        flash("Cannot return the book because it is already available")
    cur.close()
    return redirect(url_for('std_dashboard'))

@app.route('/borrow_book/<int:book_id>', methods=['POST', 'GET'])
def borrow_books(book_id):
    """Route to borrow a book."""
    cur = conn.cursor()
    cur.execute('SELECT availability FROM books WHERE book_id = %s', (book_id,))
    data = cur.fetchone()
    
    if data and data[0] == 1:
        try:
            cur.execute("UPDATE books SET availability = %s WHERE book_id = %s", (0, book_id))
            conn.commit()
            flash('Success in borrowing the book')
        except Exception as e:
            conn.rollback()
            flash(f"An error occurred: {str(e)}")
    else:
        flash("Cannot borrow the book because it is not available")
    cur.close()
    return redirect(url_for('std_dashboard'))


app.run(debug=True)
