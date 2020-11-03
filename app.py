import pathlib
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
from flask import request, redirect



app = Flask(__name__)
current_dir = pathlib.Path(__file__).parent.absolute()
db_path = current_dir
db_uri = 'sqlite:///{}/{}'.format(db_path, "data.db")
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state_name = db.Column(db.String(80), unique=True, nullable=False)
    state_abbr = db.Column(db.String(2), unique=True, nullable=False)
    total_ecv = db.Column(db.Integer, nullable=False)
    red = db.Column(db.Integer)
    blue = db.Column(db.Integer)

    def __repr__(self):
        return '<State %r>' % self.state_name


@app.route('/map.svg')
def map():
    FL = 2
    results = Results.query.all()
    results_dict = {}
    for x in results:
        results_dict[x.state_abbr] = {"state_name":x.state_name, "total_ecv":x.total_ecv, "red":x.red, "blue":x.blue}

    total_red = (Results.query.with_entities(func.sum(Results.red)).all())[0][0]
    total_blue = Results.query.with_entities(func.sum(Results.blue)).all()[0][0]

    total_red = "{0:0=3d}".format(total_red)
    total_blue = "{0:0=3d}".format(total_blue)

    return render_template('map.svg', result=results_dict, total_red=total_red, total_blue=total_blue)

@app.route('/')
def frontend():
    return render_template('map.html')

@app.route('/backend')
def backend():
    results = Results.query.all()
    return render_template('backend.html', results=results)

@app.route('/update', methods = ['POST'])
def update():
    form = request.form

    form_results = {}

    for entry in form:

        entrystring = entry.split("-")

        state = entrystring[1]
        color = entrystring[0]
        vote = request.form[entry]

        if state not in form_results:
            form_results[state] = {}

        form_results[state][color] = vote

        update_row = Results.query.filter_by(state_abbr=state).first()

        if color == "red":
            update_row.red = int(vote)

        if color == "blue":
            update_row.blue = int(vote)

        print(color + " " + state + " " + vote)

        db.session.commit()



    return form_results