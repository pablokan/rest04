from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/rest04' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Teacher(db.Model): # tabla de la BD
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    courses = db.relationship('Course', backref='teacher', lazy=True)
    def __init__(self, name): # constructor para el POST
        self.name = name

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    def __init__(self, description, teacher_id):
      self.description = description
      self.teacher_id = teacher_id

db.create_all()

class TeacherSchema(ma.Schema):
  id = fields.Integer(dump_only=True)
  name = fields.String()
  courses = fields.Nested('CourseSchema', many=True)

class CourseSchema(ma.Schema):
  id = fields.Integer(dump_only=True)
  description = fields.String()
  teacher_id = fields.Integer(dump_only=True)
        
teacher_schema = TeacherSchema()
course_schema = CourseSchema()

@app.route('/teachers', methods=['Post'])
def add_teacher():
  name = request.json['name']
  new_teacher= Teacher(name)
  db.session.add(new_teacher)
  db.session.commit()
  return teacher_schema.jsonify(new_teacher)

@app.route('/courses', methods=['Post'])
def add_lonely_course():
  description = request.json['description']
  teacher_id = request.json['teacher_id']
  new_course= Course(description, teacher_id)
  db.session.add(new_course)
  db.session.commit()
  return course_schema.jsonify(new_course)

@app.route('/teachers', methods=['GET'])
def get_teachers():
  allTeachers = Teacher.query.all()
  dumpy = teacher_schema.dump(allTeachers, many=True)
  print("dumpy:", dumpy)
  print("retorna:", jsonify(dumpy))
  return jsonify(dumpy)

@app.route('/teachers/<id>', methods=['GET'])
def get_algo(id):
  return teacher_schema.dump(Teacher.query.get(id))

@app.route('/teachers/<id>', methods=['PUT'])
def upd_teacher(id):
  teacher = Teacher.query.get(id)
  name = request.json['name']
  teacher.name = name
  db.session.commit()
  return teacher_schema.jsonify(teacher)

@app.route('/courses', methods=['GET'])
def get_courses():
  return jsonify(course_schema.dump(Course.query.all(), many=True))

@app.route('/courses/<id>', methods=['DELETE'])
def del_course(id):
  course = Course.query.get(id)
  db.session.delete(course)
  db.session.commit()
  return course_schema.jsonify(course)

@app.route('/')
def index():
  cartel =  "<a href='teachers'><h1>GET</h1></a>"
  return cartel

if __name__ == "__main__":
    app.run(debug=True)
