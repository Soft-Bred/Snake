from flask import Flask, request
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
CORS(app)
db = SQLAlchemy(app)


class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)


@app.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    rows = Leaderboard.query.order_by(Leaderboard.score.desc()).limit(10).all()
    result = { i: row.__dict__['score'] for i, row in enumerate(rows, 1) }
    return jsonify(result= result)


@app.route("/score/add", methods=["PUT"])
def score_add():
    data = request.get_json()
    score = data.get('score')

    if score is None:
        return jsonify(success=False, reason="Must provide score"), 400

    db.session.add(Leaderboard(score=score))
    db.session.commit()

    return jsonify(success=True)
