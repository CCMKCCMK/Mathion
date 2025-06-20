from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import pymysql
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Jerrysql666@localhost:3306/visionpro'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'jerry'

db = SQLAlchemy(app)

class Student (db.Model):
    __tablename__ = 'student'
    sid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    account = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), unique=False, nullable=False)
    templates = db.relationship('StudentToTemplate', backref='student', lazy='dynamic')
    birth = db.Column(db.String(80), unique=False, nullable=False)
    gender = db.Column(db.String(80), unique=False, nullable=False)
    vp_id = db.Column(db.String(100), unique=True)
    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

class Teacher (db.Model):
    __tablename__ = 'teacher'
    tid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    account = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), unique=False, nullable=False)
    birth = db.Column(db.String(80), unique=False, nullable=False)
    gender = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=False, nullable=False)
    phone = db.Column(db.String(80), unique=False, nullable=False)
    templates = db.relationship('TeacherToTemplate', backref='teacher', lazy='dynamic')
    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

class Class (db.Model):
    __tablename__ = 'class'
    cid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    studentNum = db.Column(db.Integer, unique=False, nullable=False)

class TeacherToClass (db.Model):
    __tablename__ = 'teacher_class'
    id = db.Column(db.Integer, primary_key=True)
    tid = db.Column(db.Integer, db.ForeignKey('teacher.tid'))
    cid = db.Column(db.Integer, db.ForeignKey('class.cid'))

class StudentToClass (db.Model):
    __tablename__ = 'student_class'
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Integer, db.ForeignKey('student.sid'))
    cid = db.Column(db.Integer, db.ForeignKey('class.cid'))

class VisionPro (db.Model):
    __tablename__ = 'visionpro'
    vp_id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(80), unique=False, nullable=True)
    owner_id = db.Column(db.Integer, unique=True, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.tid'))
    curState = db.Column(db.String(80), unique=False, nullable=False)

class Template (db.Model):
    __tablename__ = 'template'
    temid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    startTime = db.Column(db.String(20), unique=False, nullable=True)
    endTime = db.Column(db.String(20), unique=False, nullable=True)
    description = db.Column(db.Text)
    question_files = db.relationship('TemplateToQuestionFile', backref='template', lazy=True)
    answer_files = db.relationship('TemplateToAnswerFile', backref='template', lazy=True)
    
class TeacherToTemplate (db.Model):
    __tablename__ = 'teacher_template'
    id = db.Column(db.Integer, primary_key=True)
    tid = db.Column(db.Integer, db.ForeignKey('teacher.tid'))
    temid = db.Column(db.Integer, db.ForeignKey('template.temid'))

class StudentToTemplate (db.Model):
    __tablename__ = 'student_template'
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Integer, db.ForeignKey('student.sid'))
    temid = db.Column(db.Integer, db.ForeignKey('template.temid'))
    isSubmitted = db.Column(db.Boolean, default=False)
    totalTime = db.Column(db.Integer, unique=False, nullable=True) # in minutes
    score = db.Column(db.String(20), unique=False, nullable=True)

class QuestionFile(db.Model):
    __tablename__ = 'question_file' 
    id = db.Column(db.Integer, primary_key=True)
    questionFileName = db.Column(db.String(255), unique=True, nullable=False)
    questionFilePath = db.Column(db.String(255), unique=True, nullable=False)  # Path to stored file
    upload_date = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    templateToQuestionFile = db.relationship('TemplateToQuestionFile', backref='question_file', lazy=True)

class AnswerFile(db.Model):
    __tablename__ = 'answer_file'
    id = db.Column(db.Integer, primary_key=True)
    answerFileName = db.Column(db.String(255), unique=True, nullable=False)
    answerFilePath = db.Column(db.String(255), unique=True, nullable=False)  # Path to stored file
    upload_date = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    templateToAnswerFile = db.relationship('TemplateToAnswerFile', backref='answer_file', lazy=True)

class TemplateToAnswerFile(db.Model):
    __tablename__ = 'template_to_answer_file'
    id = db.Column(db.Integer, primary_key=True)
    temid = db.Column(db.Integer, db.ForeignKey('template.temid'))
    aid = db.Column(db.Integer, db.ForeignKey('answer_file.id'))

class TemplateToQuestionFile(db.Model):
    __tablename__ = 'template_to_question_file'
    id = db.Column(db.Integer, primary_key=True)
    temid = db.Column(db.Integer, db.ForeignKey('template.temid'))
    qid = db.Column(db.Integer, db.ForeignKey('question_file.id'))

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Insert student data
        student1 = Student(name='David', account='david', birth='2010-01-01', gender='Male')
        student1.set_password('123')
        student2 = Student(name='Emily', account='emily', birth='2010-01-01', gender='Female')
        student2.set_password('456')
        student3 = Student(name='Michael', account='michael', birth='2010-01-01', gender='Male')
        student3.set_password('789')
        student4 = Student(name='Sarah', account='sarah', birth='2010-01-01', gender='Female')
        student4.set_password('abc')
        student5 = Student(name='John', account='john', birth='2010-01-01', gender='Male')
        student5.set_password('def')
        student6 = Student(name='Alice', account='alice', birth='2010-01-01', gender='Female')
        student6.set_password('ghi')
        student7 = Student(name='Bob', account='bob', birth='2010-01-01', gender='Male')
        student7.set_password('jkl')
        student8 = Student(name='Charlie', account='charlie', birth='2010-01-01', gender='Male')
        student8.set_password('mno')
        student9 = Student(name='David', account='david1', birth='2010-01-01', gender='Male')
        student9.set_password('pqr')
        student10 = Student(name='Eve', account='eve', birth='2010-01-01', gender='Female')
        student10.set_password('stu')
        student11 = Student(name='Frank', account='frank', birth='2010-01-01', gender='Male')
        student11.set_password('uvw')
        student12 = Student(name='Grace', account='grace', birth='2010-01-01', gender='Female')
        student12.set_password('xyz')
        student13 = Student(name='Henry', account='henry', birth='2010-01-01', gender='Male')
        student13.set_password('123')
        student14 = Student(name='Ivy', account='ivy', birth='2010-01-01', gender='Female')
        student14.set_password('456')
        student15 = Student(name='Jack', account='jack', birth='2010-01-01', gender='Male')
        student15.set_password('789')
        
        db.session.add_all([student1, student2, student3, student4, student5, student6, student7, student8, student9, student10, student11, student12, student13, student14, student15])
        db.session.commit()

        # Insert teacher data
        teacher1 = Teacher(name='Jerry', account='jerry', birth='2010-01-01', gender='Male', email='jerry@gmail.com', phone='1234567890')
        teacher1.set_password('0826')
        teacher2 = Teacher(name='Esther', account='esther', birth='2010-01-01', gender='Female', email='esther@gmail.com', phone='1234567890')
        teacher2.set_password('0207')
        teacher3 = Teacher(name='Charlie', account='charlie', birth='2010-01-01', gender='Male', email='charlie@gmail.com', phone='1234567890')
        teacher3.set_password('0710')
        teacher4 = Teacher(name='Test01', account='test01', birth='2010-01-01', gender='Male', email='test01@gmail.com', phone='1234567890')
        teacher4.set_password('test01')
        db.session.add_all([teacher1, teacher2, teacher3, teacher4])
        db.session.commit()

        # Insert class data
        classes = [
            Class(name='Year1_Class1', studentNum=2),
            Class(name='Year2_Class2', studentNum=3),
            Class(name='Year3_Class3', studentNum=4),
            Class(name='Year4_Class4', studentNum=5),
            Class(name='Year5_Class5', studentNum=6),
            ]
        db.session.add_all(classes)
        db.session.commit()

        # Insert student_class data
        student_to_class_records = [
            StudentToClass(sid=student1.sid, cid=classes[0].cid),
            StudentToClass(sid=student2.sid, cid=classes[0].cid),
            StudentToClass(sid=student3.sid, cid=classes[1].cid),
            StudentToClass(sid=student4.sid, cid=classes[1].cid),
            StudentToClass(sid=student5.sid, cid=classes[1].cid),
            StudentToClass(sid=student6.sid, cid=classes[2].cid),
            StudentToClass(sid=student7.sid, cid=classes[2].cid),
            StudentToClass(sid=student8.sid, cid=classes[2].cid),
            StudentToClass(sid=student9.sid, cid=classes[3].cid),
            StudentToClass(sid=student10.sid, cid=classes[3].cid),
            StudentToClass(sid=student11.sid, cid=classes[3].cid),
            StudentToClass(sid=student12.sid, cid=classes[4].cid),
            StudentToClass(sid=student13.sid, cid=classes[4].cid),
            StudentToClass(sid=student14.sid, cid=classes[4].cid),
            StudentToClass(sid=student15.sid, cid=classes[4].cid),
        ]
        db.session.add_all(student_to_class_records)
        db.session.commit()

        teacher_to_class_records = [
            TeacherToClass(tid=teacher1.tid, cid=classes[0].cid),
            TeacherToClass(tid=teacher1.tid, cid=classes[1].cid),
            TeacherToClass(tid=teacher1.tid, cid=classes[2].cid),
            TeacherToClass(tid=teacher2.tid, cid=classes[3].cid),
            TeacherToClass(tid=teacher2.tid, cid=classes[4].cid),
            TeacherToClass(tid=teacher3.tid, cid=classes[4].cid),
            TeacherToClass(tid=teacher4.tid, cid=classes[4].cid),
        ]
        db.session.add_all(teacher_to_class_records)
        db.session.commit()


        # Insert question file data
        os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads', 'questions', 'template1'), exist_ok=True)
        question_file1 = QuestionFile(questionFileName='11.jpg', questionFilePath='./uploads/questions/template1/1.jpg')
        question_file2 = QuestionFile(questionFileName='12.jpg', questionFilePath='./uploads/questions/template1/2.jpg')
        question_file3 = QuestionFile(questionFileName='13.jpg', questionFilePath='./uploads/questions/template1/3.jpg')
        question_file4 = QuestionFile(questionFileName='14.jpg', questionFilePath='./uploads/questions/template1/4.jpg')
        os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads', 'questions', 'template2'), exist_ok=True)
        question_file5 = QuestionFile(questionFileName='21.jpg', questionFilePath='./uploads/questions/template2/1.jpg')
        question_file6 = QuestionFile(questionFileName='22.jpg', questionFilePath='./uploads/questions/template2/2.jpg')
        question_file7 = QuestionFile(questionFileName='23.jpg', questionFilePath='./uploads/questions/template2/3.jpg')
        question_file8 = QuestionFile(questionFileName='24.jpg', questionFilePath='./uploads/questions/template2/4.jpg')
        os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads', 'questions', 'template3'), exist_ok=True)
        question_file9 = QuestionFile(questionFileName='31.jpg', questionFilePath='./uploads/questions/template3/1.jpg')
        question_file10 = QuestionFile(questionFileName='32.jpg', questionFilePath='./uploads/questions/template3/2.jpg')
        question_file11 = QuestionFile(questionFileName='33.jpg', questionFilePath='./uploads/questions/template3/3.jpg')
        question_file12 = QuestionFile(questionFileName='34.jpg', questionFilePath='./uploads/questions/template3/4.jpg')
        os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads', 'questions', 'template4'), exist_ok=True)
        question_file13 = QuestionFile(questionFileName='41.jpg', questionFilePath='./uploads/questions/template4/1.jpg')
        question_file14 = QuestionFile(questionFileName='42.jpg', questionFilePath='./uploads/questions/template4/2.jpg')
        question_file15 = QuestionFile(questionFileName='43.jpg', questionFilePath='./uploads/questions/template4/3.jpg')
        question_file16 = QuestionFile(questionFileName='44.jpg', questionFilePath='./uploads/questions/template4/4.jpg')
        db.session.add_all([question_file1, question_file2, question_file3, question_file4, question_file5, question_file6, question_file7, question_file8, question_file9, question_file10, question_file11, question_file12, question_file13, question_file14, question_file15, question_file16])
        db.session.commit()

        # Insert answer file data
        os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads', 'answers', 'template1'), exist_ok=True)
        answer_file11 = AnswerFile(answerFileName='111.jpg', answerFilePath='./uploads/answers/template1/1/1.jpg')
        answer_file12 = AnswerFile(answerFileName='112.jpg', answerFilePath='./uploads/answers/template1/1/2.jpg')
        answer_file13 = AnswerFile(answerFileName='113.jpg', answerFilePath='./uploads/answers/template1/1/3.jpg')
        answer_file14 = AnswerFile(answerFileName='114.jpg', answerFilePath='./uploads/answers/template1/1/4.jpg')
        answer_file51 = AnswerFile(answerFileName='151.jpg', answerFilePath='./uploads/answers/template1/5/1.jpg')
        answer_file52 = AnswerFile(answerFileName='152.jpg', answerFilePath='./uploads/answers/template1/5/2.jpg')
        answer_file53 = AnswerFile(answerFileName='153.jpg', answerFilePath='./uploads/answers/template1/5/3.jpg')
        answer_file54 = AnswerFile(answerFileName='154.jpg', answerFilePath='./uploads/answers/template1/5/4.jpg')
        answer_file91 = AnswerFile(answerFileName='191.jpg', answerFilePath='./uploads/answers/template1/9/1.jpg')
        answer_file92 = AnswerFile(answerFileName='192.jpg', answerFilePath='./uploads/answers/template1/9/2.jpg')
        answer_file93 = AnswerFile(answerFileName='193.jpg', answerFilePath='./uploads/answers/template1/9/3.jpg')
        answer_file94 = AnswerFile(answerFileName='194.jpg', answerFilePath='./uploads/answers/template1/9/4.jpg')
        answer_file131 = AnswerFile(answerFileName='1131.jpg', answerFilePath='./uploads/answers/template1/13/1.jpg')
        answer_file132 = AnswerFile(answerFileName='1132.jpg', answerFilePath='./uploads/answers/template1/13/2.jpg')
        answer_file133 = AnswerFile(answerFileName='1133.jpg', answerFilePath='./uploads/answers/template1/13/3.jpg')
        answer_file134 = AnswerFile(answerFileName='1134.jpg', answerFilePath='./uploads/answers/template1/13/4.jpg')

        os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads', 'answers', 'template2'), exist_ok=True)
        answer_file21 = AnswerFile(answerFileName='221.jpg', answerFilePath='./uploads/answers/template2/2/1.jpg')
        answer_file22 = AnswerFile(answerFileName='222.jpg', answerFilePath='./uploads/answers/template2/2/2.jpg')
        answer_file23 = AnswerFile(answerFileName='223.jpg', answerFilePath='./uploads/answers/template2/2/3.jpg')
        answer_file24 = AnswerFile(answerFileName='224.jpg', answerFilePath='./uploads/answers/template2/2/4.jpg')
        answer_file61 = AnswerFile(answerFileName='261.jpg', answerFilePath='./uploads/answers/template2/6/1.jpg')
        answer_file62 = AnswerFile(answerFileName='262.jpg', answerFilePath='./uploads/answers/template2/6/2.jpg')
        answer_file63 = AnswerFile(answerFileName='263.jpg', answerFilePath='./uploads/answers/template2/6/3.jpg')
        answer_file64 = AnswerFile(answerFileName='264.jpg', answerFilePath='./uploads/answers/template2/6/4.jpg')
        answer_file101 = AnswerFile(answerFileName='2101.jpg', answerFilePath='./uploads/answers/template2/10/1.jpg')
        answer_file102 = AnswerFile(answerFileName='2102.jpg', answerFilePath='./uploads/answers/template2/10/2.jpg')
        answer_file103 = AnswerFile(answerFileName='2103.jpg', answerFilePath='./uploads/answers/template2/10/3.jpg')
        answer_file104 = AnswerFile(answerFileName='2104.jpg', answerFilePath='./uploads/answers/template2/10/4.jpg')
        answer_file141 = AnswerFile(answerFileName='2141.jpg', answerFilePath='./uploads/answers/template2/14/1.jpg')
        answer_file142 = AnswerFile(answerFileName='2142.jpg', answerFilePath='./uploads/answers/template2/14/2.jpg')
        answer_file143 = AnswerFile(answerFileName='2143.jpg', answerFilePath='./uploads/answers/template2/14/3.jpg')
        answer_file144 = AnswerFile(answerFileName='2144.jpg', answerFilePath='./uploads/answers/template2/14/4.jpg')

        os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads', 'answers', 'template3'), exist_ok=True)
        answer_file31 = AnswerFile(answerFileName='331.jpg', answerFilePath='./uploads/answers/template3/3/1.jpg')
        answer_file32 = AnswerFile(answerFileName='332.jpg', answerFilePath='./uploads/answers/template3/3/2.jpg')
        answer_file33 = AnswerFile(answerFileName='333.jpg', answerFilePath='./uploads/answers/template3/3/3.jpg')
        answer_file34 = AnswerFile(answerFileName='334.jpg', answerFilePath='./uploads/answers/template3/3/4.jpg')
        answer_file71 = AnswerFile(answerFileName='371.jpg', answerFilePath='./uploads/answers/template3/7/1.jpg')
        answer_file72 = AnswerFile(answerFileName='372.jpg', answerFilePath='./uploads/answers/template3/7/2.jpg')
        answer_file73 = AnswerFile(answerFileName='373.jpg', answerFilePath='./uploads/answers/template3/7/3.jpg')
        answer_file74 = AnswerFile(answerFileName='374.jpg', answerFilePath='./uploads/answers/template3/7/4.jpg')
        answer_file111 = AnswerFile(answerFileName='3111.jpg', answerFilePath='./uploads/answers/template3/11/1.jpg')
        answer_file112 = AnswerFile(answerFileName='3112.jpg', answerFilePath='./uploads/answers/template3/11/2.jpg')
        answer_file113 = AnswerFile(answerFileName='3113.jpg', answerFilePath='./uploads/answers/template3/11/3.jpg')
        answer_file114 = AnswerFile(answerFileName='3114.jpg', answerFilePath='./uploads/answers/template3/11/4.jpg')
        answer_file151 = AnswerFile(answerFileName='3151.jpg', answerFilePath='./uploads/answers/template3/15/1.jpg')
        answer_file152 = AnswerFile(answerFileName='3152.jpg', answerFilePath='./uploads/answers/template3/15/2.jpg')
        answer_file153 = AnswerFile(answerFileName='3153.jpg', answerFilePath='./uploads/answers/template3/15/3.jpg')
        answer_file154 = AnswerFile(answerFileName='3154.jpg', answerFilePath='./uploads/answers/template3/15/4.jpg')
        os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads', 'answers', 'template4'), exist_ok=True)
        answer_file41 = AnswerFile(answerFileName='441.jpg', answerFilePath='./uploads/answers/template4/4/1.jpg')
        answer_file42 = AnswerFile(answerFileName='442.jpg', answerFilePath='./uploads/answers/template4/4/2.jpg')
        answer_file43 = AnswerFile(answerFileName='443.jpg', answerFilePath='./uploads/answers/template4/4/3.jpg')
        answer_file44 = AnswerFile(answerFileName='444.jpg', answerFilePath='./uploads/answers/template4/4/4.jpg')
        answer_file81 = AnswerFile(answerFileName='481.jpg', answerFilePath='./uploads/answers/template4/8/1.jpg')
        answer_file82 = AnswerFile(answerFileName='482.jpg', answerFilePath='./uploads/answers/template4/8/2.jpg')
        answer_file83 = AnswerFile(answerFileName='483.jpg', answerFilePath='./uploads/answers/template4/8/3.jpg')
        answer_file84 = AnswerFile(answerFileName='484.jpg', answerFilePath='./uploads/answers/template4/8/4.jpg')
        answer_file121 = AnswerFile(answerFileName='4121.jpg', answerFilePath='./uploads/answers/template4/12/1.jpg')
        answer_file122 = AnswerFile(answerFileName='4122.jpg', answerFilePath='./uploads/answers/template4/12/2.jpg')
        answer_file123 = AnswerFile(answerFileName='4123.jpg', answerFilePath='./uploads/answers/template4/12/3.jpg')
        answer_file124 = AnswerFile(answerFileName='4124.jpg', answerFilePath='./uploads/answers/template4/12/4.jpg')
        db.session.add_all([answer_file11, answer_file12, answer_file13, answer_file14, answer_file51, answer_file52, answer_file53, answer_file54, answer_file91, answer_file92, answer_file93, answer_file94, answer_file131, answer_file132, answer_file133, answer_file134, answer_file21, answer_file22, answer_file23, answer_file24, answer_file61, answer_file62, answer_file63, answer_file64, answer_file101, answer_file102, answer_file103, answer_file104, answer_file141, answer_file142, answer_file143, answer_file144, answer_file31, answer_file32, answer_file33, answer_file34, answer_file71, answer_file72, answer_file73, answer_file74, answer_file111, answer_file112, answer_file113, answer_file114, answer_file151, answer_file152, answer_file153, answer_file154, answer_file41, answer_file42, answer_file43, answer_file44, answer_file81, answer_file82, answer_file83, answer_file84, answer_file121, answer_file122, answer_file123, answer_file124])
        db.session.commit()

        # Insert template data
        template1 = Template(
                         startTime='2025-01-01 00:00:00',
                         endTime='2025-03-15 23:59:59',
                         name='Template 1',
                         description='This is a test template1')
        template2 = Template(
                         startTime='2025-01-01 00:00:00',
                         endTime='2025-12-31 23:59:59',
                         name='Template 2',
                         description='This is a test template2')
        template3 = Template(
                         startTime='2025-05-01 00:00:00',
                         endTime='2025-12-31 23:59:59',
                         name='Template 3',
                         description='This is a test template3')
        template4 = Template(
                         startTime='2025-05-01 00:00:00',
                         endTime='2025-12-31 23:59:59',
                         name='Template 4',
                         description='This is a test template4')
        db.session.add_all([template1, template2, template3, template4])
        db.session.commit()

        # Insert template_to_question_file data
        template_to_question_file_records = [
            TemplateToQuestionFile(temid=template1.temid, qid=question_file1.id),
            TemplateToQuestionFile(temid=template1.temid, qid=question_file2.id),
            TemplateToQuestionFile(temid=template1.temid, qid=question_file3.id),
            TemplateToQuestionFile(temid=template1.temid, qid=question_file4.id),
            TemplateToQuestionFile(temid=template2.temid, qid=question_file5.id),
            TemplateToQuestionFile(temid=template2.temid, qid=question_file6.id),
            TemplateToQuestionFile(temid=template2.temid, qid=question_file7.id),
            TemplateToQuestionFile(temid=template2.temid, qid=question_file8.id),
            TemplateToQuestionFile(temid=template3.temid, qid=question_file9.id),
            TemplateToQuestionFile(temid=template3.temid, qid=question_file10.id),
            TemplateToQuestionFile(temid=template3.temid, qid=question_file11.id),
            TemplateToQuestionFile(temid=template3.temid, qid=question_file12.id),
            TemplateToQuestionFile(temid=template4.temid, qid=question_file13.id),
            TemplateToQuestionFile(temid=template4.temid, qid=question_file14.id),
            TemplateToQuestionFile(temid=template4.temid, qid=question_file15.id),
            TemplateToQuestionFile(temid=template4.temid, qid=question_file16.id),
        ]
        db.session.add_all(template_to_question_file_records)
        db.session.commit()

        # Insert template_to_answer_file data
        template_to_answer_file_records = [
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file11.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file12.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file13.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file14.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file51.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file52.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file53.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file54.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file91.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file92.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file93.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file94.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file131.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file132.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file133.id),
            TemplateToAnswerFile(temid=template1.temid, aid=answer_file134.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file21.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file22.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file23.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file24.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file61.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file62.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file63.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file64.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file101.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file102.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file103.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file104.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file141.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file142.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file143.id),
            TemplateToAnswerFile(temid=template2.temid, aid=answer_file144.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file31.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file32.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file33.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file34.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file71.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file72.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file73.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file74.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file111.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file112.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file113.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file114.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file151.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file152.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file153.id),
            TemplateToAnswerFile(temid=template3.temid, aid=answer_file154.id),
            TemplateToAnswerFile(temid=template4.temid, aid=answer_file41.id),
            TemplateToAnswerFile(temid=template4.temid, aid=answer_file42.id),
            TemplateToAnswerFile(temid=template4.temid, aid=answer_file43.id),
            TemplateToAnswerFile(temid=template4.temid, aid=answer_file44.id),
            TemplateToAnswerFile(temid=template4.temid, aid=answer_file81.id),
            TemplateToAnswerFile(temid=template4.temid, aid=answer_file82.id),
            TemplateToAnswerFile(temid=template4.temid, aid=answer_file83.id),
            TemplateToAnswerFile(temid=template4.temid, aid=answer_file84.id),
            TemplateToAnswerFile(temid=template4.temid, aid=answer_file121.id),
            TemplateToAnswerFile(temid=template4.temid, aid=answer_file122.id),
            TemplateToAnswerFile(temid=template4.temid, aid=answer_file123.id),
            TemplateToAnswerFile(temid=template4.temid, aid=answer_file124.id),
            
        ]
        db.session.add_all(template_to_answer_file_records)
        db.session.commit()

        teacher_to_template_records = [
            TeacherToTemplate(tid=teacher1.tid, temid=template1.temid),
            TeacherToTemplate(tid=teacher1.tid, temid=template2.temid),
            TeacherToTemplate(tid=teacher1.tid, temid=template3.temid),
            TeacherToTemplate(tid=teacher1.tid, temid=template4.temid),
            TeacherToTemplate(tid=teacher2.tid, temid=template1.temid),
            TeacherToTemplate(tid=teacher2.tid, temid=template2.temid),
            TeacherToTemplate(tid=teacher2.tid, temid=template3.temid),
            TeacherToTemplate(tid=teacher2.tid, temid=template4.temid),
            TeacherToTemplate(tid=teacher3.tid, temid=template1.temid),
            TeacherToTemplate(tid=teacher3.tid, temid=template2.temid),
            TeacherToTemplate(tid=teacher3.tid, temid=template3.temid),
            TeacherToTemplate(tid=teacher4.tid, temid=template4.temid),
        ]
        db.session.add_all(teacher_to_template_records)
        db.session.commit()

        student_to_template_records = [
            StudentToTemplate(sid=student1.sid, temid=template1.temid, isSubmitted=True, totalTime=125, score='100'),
            StudentToTemplate(sid=student2.sid, temid=template2.temid, isSubmitted=False, totalTime=34, score=''),
            StudentToTemplate(sid=student3.sid, temid=template3.temid, isSubmitted=False, totalTime=1, score=''),
            StudentToTemplate(sid=student4.sid, temid=template4.temid, isSubmitted=False, totalTime=0, score=''),
            StudentToTemplate(sid=student5.sid, temid=template1.temid, isSubmitted=True, totalTime=125, score='100'),
            StudentToTemplate(sid=student6.sid, temid=template2.temid, isSubmitted=False, totalTime=34, score=''),
            StudentToTemplate(sid=student7.sid, temid=template3.temid, isSubmitted=False, totalTime=1, score=''),
            StudentToTemplate(sid=student8.sid, temid=template4.temid, isSubmitted=False, totalTime=0, score=''),
            StudentToTemplate(sid=student9.sid, temid=template1.temid, isSubmitted=True, totalTime=125, score='100'),   
            StudentToTemplate(sid=student10.sid, temid=template2.temid, isSubmitted=False, totalTime=34, score=''),
            StudentToTemplate(sid=student11.sid, temid=template3.temid, isSubmitted=False, totalTime=1, score=''),
            StudentToTemplate(sid=student12.sid, temid=template4.temid, isSubmitted=False, totalTime=0, score=''),
            StudentToTemplate(sid=student13.sid, temid=template1.temid, isSubmitted=True, totalTime=125, score='100'),
            StudentToTemplate(sid=student14.sid, temid=template2.temid, isSubmitted=False, totalTime=34, score=''),
            StudentToTemplate(sid=student15.sid, temid=template3.temid, isSubmitted=False, totalTime=1, score=''),
            
        ]
        db.session.add_all(student_to_template_records)
        db.session.commit()

        # Insert visionpro data
        visionpro1 = VisionPro(vp_id=1, owner_name=student1.name, owner_id=student1.sid, teacher_id=teacher1.tid, curState='Assigned')
        visionpro2 = VisionPro(vp_id=2, teacher_id=teacher1.tid, curState='Not Assigned')
        visionpro3 = VisionPro(vp_id=3, teacher_id=teacher1.tid, curState='Not Assigned')
        visionpro4 = VisionPro(vp_id=4, owner_name=student2.name, owner_id=student2.sid, teacher_id=teacher1.tid, curState='Assigned')
        visionpro5 = VisionPro(vp_id=5, teacher_id=teacher1.tid, curState='Not Assigned')
        visionpro6 = VisionPro(vp_id=6, teacher_id=teacher2.tid, curState='Not Assigned')
        visionpro7 = VisionPro(vp_id=7, teacher_id=teacher2.tid, curState='Not Assigned')
        visionpro8 = VisionPro(vp_id=8, teacher_id=teacher2.tid, curState='Not Assigned')
        visionpro9 = VisionPro(vp_id=9, teacher_id=teacher2.tid, curState='Not Assigned')
        visionpro10 = VisionPro(vp_id=10, teacher_id=teacher2.tid, curState='Not Assigned')
        db.session.add_all([visionpro1, visionpro2, visionpro3, visionpro4, visionpro5, visionpro6, visionpro7, visionpro8, visionpro9, visionpro10])
        db.session.commit()

        print('Data inserted successfully!')