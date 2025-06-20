from model import app, db, Student, Teacher, Class, TeacherToClass, StudentToClass, Template, QuestionFile, AnswerFile, VisionPro, TeacherToTemplate, StudentToTemplate, TemplateToAnswerFile, TemplateToQuestionFile
from flask import jsonify, request, send_from_directory, session
from datetime import datetime, timedelta
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename
from functools import wraps
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

# 配置 Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'  # 使用文件系统存储会话
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)  # 会话有效期60分钟
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_sessions')  # 会话文件存储目录
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'

app.secret_key = "jerry"

# 初始化Flask-Session
Session(app)

# 确保会话存储目录存在
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# 修复：使用全局CORS配置，不依赖于request对象
CORS(app, supports_credentials=True)

# 添加请求后处理器来处理CORS头部
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, If-Modified-Since')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
    return response

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify(code=401, message="Please login first")
        # 更新会话过期时间
        session.modified = True
        return f(*args, **kwargs)
    return decorated_function

# 教师权限验证装饰器
def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_teacher'):
            return jsonify(code=403, message="Teacher permission required")
        return f(*args, **kwargs)
    return decorated_function

# 文件存储目录设置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
QUESTION_FOLDER = os.path.join(UPLOAD_FOLDER, 'questions')
ANSWER_FOLDER = os.path.join(UPLOAD_FOLDER, 'answers')

# 确保上传目录存在
os.makedirs(QUESTION_FOLDER, exist_ok=True)
os.makedirs(ANSWER_FOLDER, exist_ok=True)

# 文件工具函数
def save_file(file, is_question=True):
    """保存上传的文件到服务器，返回文件名和路径"""
    if not file:
        return None, None
    
    # 安全处理文件名并添加唯一标识
    original_filename = secure_filename(file.filename)
    unique_id = uuid.uuid4().hex
    filename = f"{unique_id}_{original_filename}"
    
    # 选择存储目录
    folder = QUESTION_FOLDER if is_question else ANSWER_FOLDER
    filepath = os.path.join(folder, filename)
    
    try:
        file.save(filepath)
        return original_filename, filepath
    except Exception as e:
        print(f"Error saving file: {e}")
        return None, None

def get_file(filepath):
    """获取文件进行下载"""
    if not os.path.exists(filepath):
        return None
    
    directory, filename = os.path.split(filepath)
    try:
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        print(f"Error retrieving file: {e}")
        return None

def delete_file(filepath):
    """删除存储的文件"""
    if not filepath or not os.path.exists(filepath):
        return False
    
    try:
        os.remove(filepath)
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

@app.route("/")
def index():
    return send_from_directory('/var/www/jerrykongzzz.top', 'homepage.html')

# 学生登录
@app.route("/student/login", methods=["POST"])
def student_login():
    data = request.get_json()
    account = data.get("account")
    password = data.get("password")

    if not all([account, password]):
        return jsonify(code=400, message="missing parameters")

    student = Student.query.filter_by(account=account).first()
    if not student:
        return jsonify(code=400, message="student not found")
    
    if not check_password_hash(student.password, password):
        return jsonify(code=400, message="password incorrect")
    
    # 设置会话数据
    session.permanent = True
    session['user_id'] = student.sid
    session['teacher_name'] = student.name
    session['is_teacher'] = False
    
    # 获取学生的班级信息
    classes = student.classes
    class_list = []
    for cls in classes:
        class_info = {
            "id": cls.cid,
            "name": cls.name,
            "studentNum": cls.studentNum
        }
        class_list.append(class_info)
    
    return jsonify(code=200, message="login successfully", 
                  student_id=student.sid, 
                  student_name=student.name,
                  classes=class_list)

# 老师登录
@app.route("/teacher/login", methods=["POST"])
def teacher_login():
    data = request.get_json()
    account = data.get("account")
    password = data.get("password")

    if not all([account, password]):
        return jsonify(code=400, message="missing parameters")

    teacher = Teacher.query.filter_by(account=account).first()
    if not teacher:
        return jsonify(code=400, message="teacher not found")
    
    if not check_password_hash(teacher.password, password):
        return jsonify(code=400, message="password incorrect")
    
    # 设置会话数据
    session.permanent = True
    session['user_id'] = teacher.tid
    session['teacher_name'] = teacher.name
    session['is_teacher'] = True
    
    return jsonify(
        code=200, 
        message="login successfully", 
        id=teacher.tid,
        name=teacher.name
    )

# 用户登出
@app.route("/user/logout", methods=["DELETE"])
def user_logout():
    session.clear()
    return jsonify(code=200, message="logout successfully")


# 获取教师信息
@app.route('/api/teacher/info', methods=['POST'])
@login_required
@teacher_required
def get_teacher_info():
    data = request.get_json()
    teacher = db.session.get(Teacher, data.get('teacher_id'))
    if not teacher:
        return jsonify(code=404, message="Teacher not found")
    
    return jsonify(
        code=200,
        data={
            'name': teacher.name,
            'teacher_id': teacher.tid,
            'email': teacher.email,
            'birth': teacher.birth,
            'gender': teacher.gender,
            'phone': teacher.phone
        }
    )

# 更新教师信息
@app.route('/api/teacher/update', methods=['POST'])
@login_required
@teacher_required
def update_teacher_info():
    data = request.get_json()
    teacher = db.session.get(Teacher, data.get('user_id'))
    if not teacher:
        return jsonify(code=404, message="Teacher not found")
    
    try:
        teacher.name = data.get('name', teacher.name)
        teacher.email = data.get('email', teacher.email)
        teacher.school = data.get('school', teacher.school)
        db.session.commit()
        
        # 更新会话中的用户名
        session['teacher_name'] = teacher.name
        
        return jsonify(code=200, message="Profile updated successfully")
    except Exception as e:
        db.session.rollback()
        return jsonify(code=500, message="Failed to update profile")

# 获取教师班级
@app.route("/teacher/classes", methods=['POST'])
@login_required
@teacher_required
def get_teacher_classes():
    data = request.get_json()
    teacher_id = data.get("teacher_id")
    teacher = db.session.get(Teacher, teacher_id)
    if not teacher:
        return jsonify(code=404, message="Teacher not found")
    
    TC = TeacherToClass.query.filter_by(tid=teacher_id).all()
    classes = []
    for tc in TC:
        class_obj = db.session.get(Class, tc.cid)
        if class_obj:
            classes.append({
                "class_id": class_obj.cid,
                "class_name": class_obj.name,
                "student_count": class_obj.studentNum,
            })
    
    return jsonify(code=200, data=classes)

# 获取教师模板
@app.route("/api/teacher/templates", methods=["POST"])
@login_required
@teacher_required
def get_teacher_templates():
    data = request.get_json()
    teacher_id = data.get("teacher_id")
    teacher = db.session.get(Teacher, teacher_id)
    if not teacher:
        return jsonify(code=404, message="Teacher not found")
    
    teacher_templates = TeacherToTemplate.query.filter_by(tid=teacher_id).all()
    list = []
    for teacher_template in teacher_templates:
        template_obj = db.session.get(Template, teacher_template.temid)
        student_templates = StudentToTemplate.query.filter_by(temid=teacher_template.temid).all()
        submitted_num = 0
        num = 0
        for student_template in student_templates:
            if student_template.isSubmitted:
                submitted_num += 1
            num += 1
        list.append({
            "template_id": template_obj.temid,
            "template_name": template_obj.name,
            "start_time": template_obj.startTime,
            "end_time": template_obj.endTime,
            "submitted_num": submitted_num,
            "total_num": num
        })
    
    return jsonify(code=200, data=list)

# 创建新模板
@app.route("/api/template/create", methods=["POST"])
@login_required
@teacher_required
def create_template():
    """创建新的模板"""
    data = request.get_json()
    teacher_id = data.get("teacher_id")
    teacher = db.session.get(Teacher, teacher_id)
    if not teacher:
        return jsonify(code=404, message="Teacher not found")

    student_list = []
    student_ids = data.get("student_ids")
    for student_id in student_ids:
        student = db.session.get(Student, student_id)
        if not student:
            return jsonify(code=404, message="Student not found")
        student_list.append({
            "student_id": student.sid,
        })

    #自动帮我创建对应文件夹
    question_names = data.get("question_names")
    question_paths = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads', 'questions', data.get("name"))
    for student in student_list:
        answer_paths = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads', 'answers', data.get("name"), str(student.get("student_id")))
        os.makedirs(answer_paths, exist_ok=True)
    os.makedirs(question_paths, exist_ok=True)

    template = Template(
        name=data.get("name"),
        startTime=data.get("startTime"),
        endTime=data.get("endTime"),
        description=data.get("description")
    )
    db.session.add(template)
    db.session.commit()

    #找到刚刚添加的模板
    template_obj = Template.query.filter_by(name=data.get("name")).order_by(Template.temid.desc()).first()
    template_id = template_obj.temid

    for i in range(len(question_names)):
        question = QuestionFile(
            questionFileName=str(template_id) + question_names[i],
            questionFilePath=os.path.join(question_paths, question_names[i])
        )
        db.session.add(question)
    db.session.commit()

    for i in range(len(question_names)):
        for student in student_list:
            answer = AnswerFile(
                answerFileName=str(template_id) + str(student.get("student_id")) + question_names[i],
                answerFilePath=os.path.join(answer_paths, question_names[i])
            )
        db.session.add(answer)
    db.session.commit()


    for student in student_list:
        student_template = StudentToTemplate(
            sid=student.get("student_id"),
            temid=template_id,
            isSubmitted=False,
            totalTime=0,
            score=''
        )
        db.session.add(student_template)
    db.session.commit()

    teacher_template = TeacherToTemplate(
        tid=teacher_id,
        temid=template_id
    )
    db.session.add(teacher_template)
    db.session.commit()

    # 将问题和答案与模板关联
    for i in range(len(question_names)):
        question_file = db.session.get(QuestionFile, question_names[i])
        template_to_question_file = TemplateToQuestionFile(
            temid=template_id,
            qid=question_file.id
        )
        db.session.add(template_to_question_file)
        answer_file = db.session.get(AnswerFile, question_names[i])
        template_to_answer_file = TemplateToAnswerFile(
            temid=template_id,
            aid=answer_file.id
        )
        db.session.add(template_to_answer_file)
    db.session.commit()

    return jsonify(code=200, message="Template created successfully")

# 删除模板
@app.route("/api/template/delete", methods=["POST"])
@login_required
@teacher_required
def delete_template():
    """删除模板"""
    data = request.get_json()
    template_id = data.get("template_id")
    template = db.session.get(Template, template_id)
    if not template:
        return jsonify(code=404, message="Template not found")
    
    try:
        student_templates = StudentToTemplate.query.filter_by(temid=template_id).all()
        for student_template in student_templates:
            db.session.delete(student_template)
        teacher_templates = TeacherToTemplate.query.filter_by(temid=template_id).all()
        for teacher_template in teacher_templates:
            db.session.delete(teacher_template)
        question_files = QuestionFile.query.filter_by(template_id=template_id).all()
        for question_file in question_files:
            db.session.delete(question_file)
        answer_files = AnswerFile.query.filter_by(template_id=template_id).all()
        for answer_file in answer_files:
            db.session.delete(answer_file)
        TemplateToQuestionFile.query.filter_by(temid=template_id).delete()
        TemplateToAnswerFile.query.filter_by(temid=template_id).delete()
        db.session.delete(template)
        db.session.commit()
        return jsonify(code=200, message="Template deleted successfully")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code=500, message="error deleting template")

# 获取学生在特定模板下的详细答案情况
@app.route("/api/template/student/answers", methods=["POST"])
@login_required
@teacher_required
def get_student_template_answers():
    """获取特定学生在特定模板下的详细答案情况"""
    data = request.get_json()
    template_id = data.get("template_id")
    student_id = data.get("student_id")
    
    if not all([template_id, student_id]):
        return jsonify(code=400, message="Missing required parameters")
    
    # 检查模板和学生是否存在
    template = db.session.get(Template, template_id)
    if not template:
        return jsonify(code=404, message="Template not found")
        
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify(code=404, message="Student not found")
    
    # 检查学生是否被分配了该模板
    student_template = StudentToTemplate.query.filter_by(temid=template_id, sid=student_id).first()
    if not student_template:
        return jsonify(code=404, message="Student not assigned to this template")
    
    # 获取该模板的所有问题文件
    template_question_relations = TemplateToQuestionFile.query.filter_by(temid=template_id).all()
    question_data = []
    
    # 获取该模板的所有答案文件
    template_answer_relations = TemplateToAnswerFile.query.filter_by(temid=template_id).all()
    all_answer_files = []
    
    for relation in template_answer_relations:
        answer_file = db.session.get(AnswerFile, relation.aid)
        if answer_file:
            all_answer_files.append(answer_file)
    
    # 构建问题和答案数据
    for relation in template_question_relations:
        question_file = db.session.get(QuestionFile, relation.qid)
        if not question_file:
            continue
        
        # 使用问题文件名和学生ID的组合来匹配答案文件
        matching_answer = None
        for answer_file in all_answer_files:
            expected_file = f"{student_id}{question_file.questionFileName}"
            if answer_file.answerFileName == expected_file:
                matching_answer = answer_file
                break
        
        question_info = {
            "question_id": question_file.id,
            "question_name": question_file.questionFileName,
            "question_path": question_file.questionFilePath,
            "has_answer": matching_answer is not None
        }
        
        # 如果有匹配的答案文件，添加答案信息
        if matching_answer:
            question_info.update({
                "answer_id": matching_answer.id,
                "answer_name": matching_answer.answerFileName,
                "answer_path": matching_answer.answerFilePath
            })
        
        question_data.append(question_info)
    
    # 检查学生是否有答案文件
    has_any_answer = any(q["has_answer"] for q in question_data)
    
    # 返回学生信息和详细答案情况
    student_data = {
        "student_id": student.sid,
        "student_name": student.name,
        "account": student.account,
        "total_time": student_template.totalTime,
        "score": student_template.score,
        "is_submitted": student_template.isSubmitted or has_any_answer,  # 如果数据库标记已提交或有任何答案，则认为已提交
        "questions": question_data
    }
    
    return jsonify(
        code=200,
        message="Student answers retrieved successfully",
        data=student_data
    )


# 获取模板详情 - 只包含基本信息和学生列表，不包含详细答案
@app.route("/api/template/detail", methods=["POST"])
@login_required
@teacher_required
def get_template_detail():
    """获取模板详情及学生基本情况，不包含详细答案"""  
    data = request.get_json()
    template_id = data.get("template_id")
    template = db.session.get(Template, template_id)
    if not template:
        return jsonify(code=404, message="Template not found")
    
    # 获取模板基本信息
    template_info = {
        "template_id": template.temid,
        "template_name": template.name,
        "start_time": template.startTime,
        "end_time": template.endTime,
        "description": template.description
    }
    
    # 获取所有相关的问题文件
    questions_data = []
    template_question_relations = TemplateToQuestionFile.query.filter_by(temid=template_id).all()
    
    for relation in template_question_relations:
        question_file = db.session.get(QuestionFile, relation.qid)
        if question_file:
            questions_data.append({
                "question_id": question_file.id,
                "question_name": question_file.questionFileName,
                "question_path": question_file.questionFilePath
            })
    
    # 获取所有相关的学生及其基本提交情况（不包含详细答案）
    students_data = []
    student_templates = StudentToTemplate.query.filter_by(temid=template_id).all()
    
    for st in student_templates:
        student = db.session.get(Student, st.sid)
        if not student:
            continue
        
        student_data = {
            "student_id": student.sid,
            "student_name": student.name,
            "account": student.account,
            "total_time": st.totalTime,
            "score": st.score,
            "is_submitted": st.isSubmitted  # 使用数据库中的提交状态
        }
        
        students_data.append(student_data)
    
    return jsonify(
        code=200, 
        message="Template details retrieved successfully",
        data={
            "template": template_info,
            "questions": questions_data,
            "questions_count": len(questions_data),
            "students": students_data
        }
    )


# 用户注册
@app.route("/user/register", methods=["POST"])
def user_register():
    """
    "name": "Jerry",
    "account": "Jerry",
    "password": "Jerry",
    "ifTeacher": 0 or 1 (0: student, 1: teacher)
    """
    data = request.get_json()
    name = data.get("name")
    account = data.get("account")
    password = data.get("password")
    birth = data.get("birth")
    gender = data.get("gender")
    ifTeacher = data.get("ifTeacher")

    if not (all([name, account, password, birth, gender]) and ifTeacher in [0, 1]):
        return jsonify(code = 400, message = "missing parameters")
    
    # 检查账号和名称是否已被使用 (检查老师和学生表)
    student_account = Student.query.filter_by(account=account).first()
    teacher_account = Teacher.query.filter_by(account=account).first()
    
    if student_account or teacher_account:
        return jsonify(code = 400, message = "account already exists")
    
    student_name = Student.query.filter_by(name=name).first()
    teacher_name = Teacher.query.filter_by(name=name).first()
    
    if student_name or teacher_name:
        return jsonify(code = 400, message = "name already exists")

    try:
        if ifTeacher == 1:
            # 创建老师账号
            teacher = Teacher(name=name, account=account, password=password, birth=birth, gender=gender)
            db.session.add(teacher)
        else:
            # 创建学生账号
            student = Student(name=name, account=account, password=password, birth=birth, gender=gender)
            db.session.add(student)
            
        db.session.commit()
        return jsonify(code = 200, message = "user registered successfully")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code = 500, message = "error")

# 班级创建
@app.route("/class/create", methods=["POST"])
@login_required
@teacher_required
def class_create():
    """
    "name": "Year1_Class1",
    "studentNum": 100,
    "teacherName": "Jerry"
    """
    # 判断是否是老师
    data = request.get_json()
    teacher_id = data.get("teacher_id")
    if not teacher_id:
        return jsonify(code=400, message="not login as teacher")
    
    name = data.get("name")
    studentNum = data.get("studentNum")
    
    if not all([name, studentNum]):
        return jsonify(code = 400, message = "missing parameters")

    # 创建新班级
    class_obj = Class(
        name = name,
        studentNum = studentNum
    )
    
    try:
        db.session.add(class_obj)
        db.session.commit()
        
        # 关联老师与班级
        teacher_to_class = TeacherToClass(
            tid = teacher_id,
            cid = class_obj.cid
        )
        
        db.session.add(teacher_to_class)
        db.session.commit()
        return jsonify(code = 200, message = "class created successfully", class_id = class_obj.cid)
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code = 500, message = "error")

# 班级基础信息修改
@app.route("/class/info/update", methods=["POST"])
@login_required
@teacher_required
def class_info_update():
    """
    "classId": 2,
    "name": "Year2_Class2",
    "studentNum": 30
    """
    # 判断是否是老师
    data = request.get_json()
    teacher_id = data.get("teacher_id")
    if not teacher_id:
        return jsonify(code=400, message="not login as teacher")
        
    classId = data.get("classId")
    name = data.get("name")
    studentNum = data.get("studentNum")

    if not classId:
        return jsonify(code = 400, message = "missing parameters")

    class_obj = db.session.get(Class, classId)
    if not class_obj:
        return jsonify(code = 400, message = "class not found")
    
    # 检查是否是该班级的老师
    teacher_class = TeacherToClass.query.filter_by(tid=teacher_id, cid=classId).first()
    if not teacher_class:
        return jsonify(code = 400, message = "not the teacher of this class")

    if name:
        class_obj.name = name
    if studentNum:
        class_obj.studentNum = studentNum
        
    try:
        db.session.commit()
        return jsonify(code = 200, message = "class updated successfully")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code = 500, message = "error")

# 班级删除
@app.route("/class/delete", methods=["POST"])
@login_required
@teacher_required
def class_delete():
    """
    "classId": 2
    """
    # 判断是否是老师
    data = request.get_json()
    teacher_id = data.get("teacher_id")
    if not teacher_id:
        return jsonify(code=400, message="not login as teacher")
        
    classId = data.get("classId")

    if not classId:
        return jsonify(code = 400, message = "missing parameters")

    class_obj = db.session.get(Class, classId)
    if not class_obj:
        return jsonify(code = 400, message = "class not found")
    
    # 检查是否是该班级的老师
    teacher_class = TeacherToClass.query.filter_by(tid=teacher_id, cid=classId).first()
    if not teacher_class:
        return jsonify(code = 400, message = "not the teacher of this class")
    
    # 检查班级是否有关联的模板
    templates = Template.query.filter_by(cid=classId).all()
    if templates:
        return jsonify(code = 400, message = "class has templates, cannot be deleted")
        
    try:
        # 删除班级的所有学生关联
        StudentToClass.query.filter_by(cid=classId).delete()
        
        # 删除班级的所有老师关联
        TeacherToClass.query.filter_by(cid=classId).delete()
        
        # 删除班级
        db.session.delete(class_obj)
        db.session.commit()
        return jsonify(code = 200, message = "class deleted successfully")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code = 500, message = "error")

# 班级添加学生
@app.route("/class/student/add", methods=["POST"])
@login_required
@teacher_required
def class_add_student():
    """
    "classId": 2,
    "studentId": 3
    """
    # 判断是否是老师
    data = request.get_json()
    teacher_id = data.get("teacher_id")
    if not teacher_id:
        return jsonify(code=400, message="not login as teacher")
        
    classId = data.get("classId")
    studentId = data.get("studentId")

    if not all([classId, studentId]):
        return jsonify(code = 400, message = "missing parameters")

    # 检查班级是否存在
    class_obj = db.session.get(Class, classId)
    if not class_obj:
        return jsonify(code = 400, message = "class not found")
    
    # 检查是否是该班级的老师
    teacher_class = TeacherToClass.query.filter_by(tid=teacher_id, cid=classId).first()
    if not teacher_class:
        return jsonify(code = 400, message = "not the teacher of this class")
        
    # 检查学生是否存在
    student = db.session.get(Student, studentId)
    if not student:
        return jsonify(code = 400, message = "student not found")
    
    # 检查学生是否已在班级中
    student_class = StudentToClass.query.filter_by(sid=studentId, cid=classId).first()
    if student_class:
        return jsonify(code = 400, message = "student already in this class")
    
    # 添加学生到班级
    student_to_class = StudentToClass(
        sid = studentId,
        cid = classId
    )
    
    # 更新班级学生数量
    class_obj.studentNum += 1
    
    try:
        db.session.add(student_to_class)
        db.session.commit()
        return jsonify(code = 200, message = "student added to class successfully")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code = 500, message = "error")

# 模板文件上传
@app.route("/api/template/<int:template_id>/file/upload", methods=["POST"])
def template_file_upload(template_id):
    """上传问题或答案文件到模板"""
    # 检查请求中是否包含文件
    if 'question_file' not in request.files and 'answer_file' not in request.files:
        return jsonify(code=400, message="missing files")
    
    question_file = request.files.get('question_file')
    answer_file = request.files.get('answer_file')
    
    template = db.session.get(Template, template_id)
    if not template:
        return jsonify(code=404, message="Template not found")
    
    file_ids = []
    
    # 处理问题文件
    if question_file and question_file.filename != '':
        question_filename, question_filepath = save_file(question_file, is_question=True)
        if question_filename and question_filepath:
            question_file_record = QuestionFile(
                template_id=template_id,
                questionFileName=question_filename,
                questionFilePath=question_filepath
            )
            try:
                db.session.add(question_file_record)
                db.session.commit()
                file_ids.append(question_file_record.fid)
            except Exception as e:
                print(e)
                db.session.rollback()
                return jsonify(code=500, message="database error")
    
    # 处理答案文件
    if answer_file and answer_file.filename != '':
        answer_filename, answer_filepath = save_file(answer_file, is_question=False)
        if answer_filename and answer_filepath:
            answer_file_record = AnswerFile(
                template_id=template_id,
                answerFileName=answer_filename,
                answerFilePath=answer_filepath
            )
            try:
                db.session.add(answer_file_record)
                db.session.commit()
                file_ids.append(answer_file_record.fid)
            except Exception as e:
                print(e)
                db.session.rollback()
                return jsonify(code=500, message="database error")
    
    if file_ids:
        return jsonify(code=200, message="file uploaded successfully", file_ids=file_ids)
    else:
        return jsonify(code=400, message="no valid files provided")

# 下载问题文件
@app.route("/api/template/file/question/<int:file_id>", methods=["GET"])
def template_file_download_question(file_id):
    """下载问题文件"""
    file_record = db.session.get(QuestionFile, file_id)
    if not file_record:
        return jsonify(code=404, message="Question file not found")
    
    if not file_record.questionFilePath:
        return jsonify(code=404, message="question file not found")
    
    file_response = get_file(file_record.questionFilePath)
    if file_response:
        return file_response
    else:
        return jsonify(code=404, message="file not found or inaccessible")

# 下载答案文件
@app.route("/api/template/file/answer/<int:file_id>", methods=["GET"])
def template_file_download_answer(file_id):
    """下载答案文件"""
    file_record = db.session.get(AnswerFile, file_id)
    if not file_record:
        return jsonify(code=404, message="Answer file not found")
    
    if not file_record.answerFilePath:
        return jsonify(code=404, message="answer file not found")
    
    file_response = get_file(file_record.answerFilePath)
    if file_response:
        return file_response
    else:
        return jsonify(code=404, message="file not found or inaccessible")

# 获取模板所有文件
@app.route("/api/template/<int:template_id>/files", methods=["GET"])
def get_template_files(template_id):
    """获取模板的所有文件"""
    try:
        question_files = QuestionFile.query.filter_by(template_id=template_id).all()
        answer_files = AnswerFile.query.filter_by(template_id=template_id).all()
        
        result = []
        # 处理问题文件
        for file in question_files:
            result.append({
                "id": file.fid,
                "type": "question",
                "has_question": True,
                "question_filename": file.questionFileName,
                "has_answer": False,
                "answer_filename": None,
                "upload_date": file.upload_date.strftime('%Y-%m-%d %H:%M:%S') if file.upload_date else None
            })
        
        # 处理答案文件
        for file in answer_files:
            result.append({
                "id": file.fid,
                "type": "answer",
                "has_question": False,
                "question_filename": None,
                "has_answer": True,
                "answer_filename": file.answerFileName,
                "upload_date": file.upload_date.strftime('%Y-%m-%d %H:%M:%S') if file.upload_date else None
            })
        
        return jsonify(code=200, message="files retrieved successfully", files=result)
    except Exception as e:
        print(e)
        return jsonify(code=500, message="database error")

# 删除问题文件
@app.route("/api/template/file/question/<int:file_id>", methods=["DELETE"])
def template_question_file_delete(file_id):
    """删除问题文件记录和关联的物理文件"""
    try:
        file_record = db.session.get(QuestionFile, file_id)
        if not file_record:
            return jsonify(code=404, message="Question file not found")
        
        # 删除物理文件
        if file_record.questionFilePath:
            delete_file(file_record.questionFilePath)
        
        # 删除数据库记录
        db.session.delete(file_record)
        db.session.commit()
        
        return jsonify(code=200, message="question file deleted successfully")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code=500, message="error deleting file")

# 删除答案文件
@app.route("/api/template/file/answer/<int:file_id>", methods=["DELETE"])
def template_answer_file_delete(file_id):
    """删除答案文件记录和关联的物理文件"""
    try:
        file_record = db.session.get(AnswerFile, file_id)
        if not file_record:
            return jsonify(code=404, message="Answer file not found")
        
        # 删除物理文件
        if file_record.answerFilePath:
            delete_file(file_record.answerFilePath)
        
        # 删除数据库记录
        db.session.delete(file_record)
        db.session.commit()
        
        return jsonify(code=200, message="answer file deleted successfully")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code=500, message="error deleting file")

# 获取班级信息
@app.route("/class/info/<int:class_id>", methods=["POST"])
@login_required
@teacher_required
def get_class_info(class_id):
    """获取指定班级的信息"""
    data = request.get_json()
    teacher_id = data.get("teacher_id")
    
    # 获取班级信息
    class_obj = db.session.get(Class, class_id)
    if not class_obj:
        return jsonify(code=404, message="class not found")
    
    # 检查是否是该班级的老师
    teacher_class = TeacherToClass.query.filter_by(tid=teacher_id, cid=class_id).first()
    if not teacher_class:
        return jsonify(code=403, message="not authorized to view this class")
    
    # 获取班级学生数量
    student_count = StudentToClass.query.filter_by(cid=class_id).count()
    
    # 构建班级信息
    class_info = {
        "class_id": class_obj.cid,
        "class_name": class_obj.name,
        "student_count": student_count,
        "created_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # 假设没有创建时间字段，使用当前时间
        "last_active": datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 假设没有最后活动时间，使用当前时间
    }
    
    return jsonify(code=200, message="success", data=class_info)

# 获取班级学生列表
@app.route("/class/students/<int:class_id>", methods=["POST"])
@login_required
@teacher_required
def get_class_students(class_id):
    """获取指定班级中的所有学生"""
    data = request.get_json()
    teacher_id = data.get("teacher_id")
    
    # 检查班级是否存在
    class_obj = db.session.get(Class, class_id)
    if not class_obj:
        return jsonify(code=404, message="class not found")
    
    # 检查是否是该班级的老师
    teacher_class = TeacherToClass.query.filter_by(tid=teacher_id, cid=class_id).first()
    if not teacher_class:
        return jsonify(code=403, message="not authorized to view this class")
    
    # 获取班级中的所有学生
    student_classes = StudentToClass.query.filter_by(cid=class_id).all()
    student_ids = [sc.sid for sc in student_classes]
    students = Student.query.filter(Student.sid.in_(student_ids)).all()
    
    # 构建学生信息列表
    student_list = []
    for student in students:
        student_class = StudentToClass.query.filter_by(sid=student.sid, cid=class_id).first()
        join_date = datetime.now().strftime('%Y-%m-%d')  # 假设没有加入日期字段，使用当前日期
        
        student_list.append({
            "student_id": student.sid,
            "name": student.name,
            "account": student.account,
            "join_date": join_date,
            "status": "Active"  # 假设所有学生都是活跃状态
        })
    
    return jsonify(code=200, message="success", data=student_list)

# 从班级移除学生
@app.route("/class/remove_student", methods=["POST"])
@login_required
@teacher_required
def remove_student_from_class():
    """从班级中移除学生"""
    data = request.get_json()
    teacher_id = data.get("teacher_id")
    class_id = data.get("class_id")
    student_id = data.get("student_id")
    
    if not all([class_id, student_id]):
        return jsonify(code=400, message="missing parameters")
    
    # 检查班级是否存在
    class_obj = db.session.get(Class, class_id)
    if not class_obj:
        return jsonify(code=404, message="class not found")
    
    # 检查是否是该班级的老师
    teacher_class = TeacherToClass.query.filter_by(tid=teacher_id, cid=class_id).first()
    if not teacher_class:
        return jsonify(code=403, message="not authorized for this class")
    
    # 检查学生是否在班级中
    student_class = StudentToClass.query.filter_by(sid=student_id, cid=class_id).first()
    if not student_class:
        return jsonify(code=404, message="student not in this class")
    
    try:
        # 删除学生班级关联
        db.session.delete(student_class)
        
        # 更新班级学生数量
        if class_obj.studentNum > 0:
            class_obj.studentNum -= 1
            
        db.session.commit()
        return jsonify(code=200, message="student removed successfully")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code=500, message="error removing student")

# 获取老师所有Vision Pro设备信息
@app.route("/vp/info", methods=["POST"])
@login_required
@teacher_required
def get_vp_info():
    """获取老师所有Vision Pro设备信息"""
    data = request.get_json()
    teacher_id = data.get("teacher_id")

    # 获取老师所有Vision Pro设备信息
    vision_pros = VisionPro.query.filter_by(teacher_id=teacher_id).all()

    # 构建返回数据
    vp_list = []
    for vp in vision_pros:
        class_name = "Not Assigned"
        
        # Only check for class if the VP has an owner
        if vp.owner_id:
            # Get the first class association for this student
            sc = StudentToClass.query.filter_by(sid=vp.owner_id).first()
            if sc:
                class_obj = db.session.get(Class, sc.cid)
                if class_obj:
                    class_name = class_obj.name
        
        vp_list.append({
            "vp_id": vp.vp_id,
            "owner_name": vp.owner_name or "Not Assigned",
            "owner_id": vp.owner_id or None,
            "teacher_id": vp.teacher_id,
            "class": class_name,
            "curState": vp.curState
        })

    return jsonify(code=200, message="success", data=vp_list)

@app.route("/vp/add", methods=["POST"])
@login_required
@teacher_required
def add_vp():
    """添加新的Vision Pro设备"""
    data = request.get_json()
    vp_id = data.get("vp_id")
    owner_name = ''
    owner_id = ''
    teacher_id = session.get('user_id')
    curState = 'Not Assigned'
    
    if not (vp_id):
        return jsonify(code=400, message="missing parameters")
    
    # 检查Vision Pro是否已存在
    existing_vp = VisionPro.query.filter_by(vp_id=vp_id).first()
    if existing_vp:
        return jsonify(code=400, message="Vision Pro already exists")
    
    # 创建新的Vision Pro设备    
    new_vp = VisionPro(vp_id=vp_id, owner_name=owner_name, owner_id=owner_id, teacher_id=teacher_id, curState=curState)
    db.session.add(new_vp)
    db.session.commit()
    
    return jsonify(code=200, message="Vision Pro added successfully")
    
@app.route("/vp/delete", methods=["POST"])
@login_required
@teacher_required
def delete_vp():
    """删除Vision Pro设备"""
    data = request.get_json()
    vp_id = data.get("vp_id")
    
    if not vp_id:
        return jsonify(code=400, message="missing parameters")
    
    # 检查Vision Pro是否存在
    vp = VisionPro.query.filter_by(vp_id=vp_id).first()
    if not vp:
        return jsonify(code=404, message="Vision Pro not found")
    
    # 删除Vision Pro设备    
    db.session.delete(vp)
    db.session.commit()
    
    return jsonify(code=200, message="Vision Pro deleted successfully")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7001, debug=False)