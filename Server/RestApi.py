from io import BytesIO
from operator import le
import re
from flask import render_template, Flask, jsonify, request, send_file
from werkzeug.utils import secure_filename
import json
import os
import sys
import numpy as np
import pandas as pd
import base64
import shutil
from datetime import date
from datetime import datetime
import face_recognition
import gspread
from gspread import Cell
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image
from googleapiclient import discovery
import firebase_admin
from firebase_admin import credentials, initialize_app, firestore, auth
import requests
import time
from flask_cors import CORS
from datetime import datetime


scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
        ]

google_sheet_credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "attendance-401315-8d4c70e8b930.json", scopes)
google_file = gspread.authorize(google_sheet_credentials)
gc = gspread.service_account(filename='attendance-401315-8d4c70e8b930.json')

attendance_sheet_id = "1lusBMa4HwoKbBezyfADTyB7adgeq1HNJU9FbKWZIvhs"
app = Flask(__name__)


cred = credentials.Certificate(
     "tutorial-5464c-firebase-adminsdk-a7xcz-4a38da703f.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/new-employee', methods=['POST'])
def new_employee():
    try:
        data = request.get_json()
        name = data['name']
        id = data['id']
        department = data['department']
        image_data = data['image']
        if image_data.startswith('data:image/png;base64,'):
            image_data = image_data[len('data:image/png;base64,'):]

        # Decode base64 image data
        image_binary = base64.b64decode(image_data)

        # Save the received image data to a file
        image_filename = os.path.join(UPLOAD_FOLDER, f'{name}_{id}.png')
        with open(image_filename, 'wb') as image_file:
            image_file.write(image_binary)
        obj={
            'Emp_id':id,
            'Emp_name':name,
            'Department':department,
            'BitStream':[image_data]
        }
        print(obj)
        data=[obj]
        for record in data:
            add=db.collection(u'Hack').document(record['Emp_name'])
            add.set(record)

        # You can perform additional processing or database operations here
        # For now, just send a success response
        return jsonify({'success': True, 'message': 'Employee registered successfully'})
        
        # # Decode base64 image data
        # image_binary = base64.b64decode(image_data)

        # # Save the received image data to a file
        # image_filename = os.path.join(UPLOAD_FOLDER, f'{name}_{id}.png')
        # with open(image_filename, 'wb') as image_file:
        #     image_file.write(image_binary)

        # # You can perform additional processing or database operations here
        # # For now, just send a success response
        # return jsonify({'success': True, 'message': 'Employee registered successfully'})
    except Exception as e:
        print(f'Error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

def get_image_from_firebase(emp_name):
    # Use Firebase SDK to get image for the given emp_name
    # Return the path to the downloaded image
    pass





@app.route('/check-server', methods=['GET'])
def check_server():
    return 'hii', 200

@app.route('/send-snapshot', methods=['POST'])
def handleSnapClick():
    # Receive the snapshot image data from the request as JSON
    request_data = request.json
    
    # Extract the 'image' value from the JSON
    image_data = request_data.get('image', '')

    # Print the received image data for debugging
    # print(image_data)
    
    # Process the image data (you can save it or perform other actions)
    # For now, let's just return a response
    return 'Snapshot received and processed!', 200

# @app.route('/add-manual-entry', methods=["GET"])
# def add_manual_entry():
#         # Extracting data from the request's query parameters
#         enrollment = request.args.get("enrollment", 1234)
#         name = request.args.get("name", "het")
#         mobile = request.args.get("mobile", 123)
#         email = request.args.get("email", "abc")

#         # Access the Google Sheet by name or ID
#         # attendance_sheet = google_file.open(attendance_sheet_id)
#         attendance_sheet2 = gc.open_by_url('https://docs.google.com/spreadsheets/d/1lusBMa4HwoKbBezyfADTyB7adgeq1HNJU9FbKWZIvhs/edit#gid=0')
#         # Find the next empty row to append the data
#         # next_empty_row = len(attendance_sheet.get_all_values()) + 1
#         attendance_sheet = attendance_sheet2.get_worksheet(0)

#         next_empty_row = 1
#         # Append data to the Google Sheet
#         attendance_sheet.update_cell(next_empty_row, 1, enrollment)
#         attendance_sheet.update_cell(next_empty_row, 2, name)
#         attendance_sheet.update_cell(next_empty_row, 3, mobile)
#         attendance_sheet.update_cell(next_empty_row, 4, email)

#         return jsonify({"message": "Manual Entry Added!"}), 200

# @app.route('/add-manual-entry', methods=["POST"])
def add_manual_entry(docker_response,state):
    # Extracting docker compare face response
    # data = request.get_json()
    # docker_response = data.get("result", [])
    arr=[]
    for item in docker_response.get("result", []):
        subjects = item.get("subjects", [])
        str2=""
        for subject in subjects:
            similarity = subject.get("similarity", 0)
            Emp_id = subject.get("subject")

            


            # Check the similarity threshold and proceed
            if similarity > 0.99:
                # Fetch employee details from Firebase based on emp_id
                # emp_data = db.collection("Hack").document(Emp_id).get().to_dict()
                emp_data_query = db.collection("Hack").where('Emp_id', '==', Emp_id).get()

                emp_data = None
                for doc in emp_data_query:
                    if doc.exists:
                        emp_data = doc.to_dict()
                        break  # Assuming 'Emp_id' is unique, we break after getting the first matching document.

                if not emp_data:
                    print(f"Failed to fetch data for emp_id: {Emp_id}")
                else:
                    # Now you can work with emp_data which will be a dictionary containing the employee details.
                    # print(emp_data)
                    pass
                
                # Assuming the Firebase data structure is similar to the sample you provided, 
                # if not adjust the keys below
                name = emp_data.get("Emp_name", "")
                department = emp_data.get("Department", "")
                # You might want to extract other details if they exist.
                print(name, department)
                # Append these details to Google Sheet
                attendance_sheet2 = gc.open_by_url('https://docs.google.com/spreadsheets/d/1lusBMa4HwoKbBezyfADTyB7adgeq1HNJU9FbKWZIvhs/edit#gid=0')
                attendance_sheet = attendance_sheet2.get_worksheet(0)

                # Finding the next empty row. Adjust this logic if your sheet contains headers.
                next_empty_row = len(attendance_sheet.get_all_values()) + 1
                current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Appending data to the Google Sheet
                attendance_sheet.update_cell(next_empty_row, 1, Emp_id)
                attendance_sheet.update_cell(next_empty_row, 2, name)
                attendance_sheet.update_cell(next_empty_row, 3, department)
                attendance_sheet.update_cell(next_empty_row, 4,state)
                attendance_sheet.update_cell(next_empty_row, 5, current_timestamp)
                arr.append(Emp_id)
                print(arr)


                log = {
                    'Status': state,
                    'timestamp': current_timestamp,
                }

                obj = {
                    'Emp_id': Emp_id,
                    'Emp_name': name,
                    'Department': department,
                }

                print(obj)  
                data=[obj]

                for record in data:
                    employee_ref = db.collection(u'eae').document(record['Emp_id'])

                    # Check if the employee document exists
                    doc = employee_ref.get()

                    if not doc.exists:
                        # If the employee doesn't exist, set the initial employee details
                        employee_ref.set({
                            'Emp_id': record['Emp_id'],
                            'Emp_name': record['Emp_name'],
                            'Department': record['Department'],
                        })

                    # Add the new log to the 'logs' subcollection
                    employee_ref.collection('logs').add(log)


                # log = {
                #     'Status': state,
                #     'timestamp': current_timestamp,
                # }
                # obj={
                #     'Emp_id':Emp_id,
                #     'Emp_name':name,
                #     'Department':department,
                #     'log':log,
                # }

                # print(obj)
                # data=[obj]
                # for record in data:
                #     add=db.collection(u'eae').document(record['Emp_id'])
                #     add.set(record)
                
                # Add other details if you need to
                str2+="Attendance Marked for Employee: "
                for i in arr:
                    str2+=" "
                    str2+=i
            else:   
                str2+="Not an Employee, DO register. Please"
                # return jsonify(str)

                
    return str2







def get_faculties(school_id, role, uid):
    try:
        faculties = db.collection(role).where(
            "school_id", "==", school_id).stream()
        # faculties = db.collection(role).where('__name__','==',uid).get()

        all_faculties = []
        for doc in faculties:
            if (doc.id != uid):
                curr = doc.to_dict()
                curr["id"] = doc.id
                all_faculties.append(curr)
        return all_faculties
    except:
        return None


# Remove dir or files


def remove_file_or_dir(path: str) -> None:
    """ Remove a file or directory """
    try:
        shutil.rmtree(path)
    except NotADirectoryError:
        os.remove(path)


def face_unlock(encoding, image):
    image = face_recognition.load_image_file(image)
    image_encoding = face_recognition.face_encodings(image)[0]
    result = face_recognition.compare_faces([encoding], image_encoding)
    return result


def face_data_upload(list_encodings, image):
    image = face_recognition.load_image_file(image)
    image_encoding = face_recognition.face_encodings(image)[0]
    result = face_recognition.compare_faces(list_encodings, image_encoding)
    can_upload = True not in result
    return can_upload


def image_face_recognition(list_encodings, list_names, image):
    image = face_recognition.load_image_file(image)
    image_encoding = face_recognition.face_encodings(image)
    known_faces = []
    for face in image_encoding:
        result = face_recognition.compare_faces(list_encodings, face)
        if True in result:
            match = list_names[result.index(True)]
            known_faces.append(match)
    known_faces = list(set(known_faces))
    print(known_faces)
    return known_faces


@app.route('/add-faculty', methods=["POST"])
def add_faculty():
    uid = request.form.get('uid')
    role = request.form.get('role')

    curr_faculty = db.collection(role).where(
        'uid', '==', uid).get()[0].to_dict()

    enrollment = curr_faculty["enrollment"]

    # im = Image.open(BytesIO(base64.b64decode(curr_faculty["byteArray"])))
    # im.save("./Tmp_Faces/"+enrollment+".png", "PNG")

    # image = face_recognition.load_image_file("./Tmp_Faces/"+enrollment+".png")
    # face_encoding = face_recognition.face_encodings(image)[0]

    school_id = curr_faculty["school_id"]
    email = curr_faculty["email"]
    name = curr_faculty["name"]
    mobile = curr_faculty["mobile"]

    all_faculties = get_faculties(school_id, role, uid)

    # encodings = []

    # if len(all_faculties) > 0:
    #     for faculty in all_faculties:
    #         x = np.array(faculty["face_encoding"])
    #         curr_encoding = x.astype(np.float64)
    #         encodings.append(curr_encoding)

    #     if not face_data_upload(encodings, "./Tmp_Faces/"+enrollment+".png"):
    #         remove_file_or_dir("./Tmp_Faces/"+enrollment+".png")
    #         db.collection(role).document(uid).delete()
    #         auth.delete_user(uid)
    #         return jsonify({"message": "Person Already Exists!"})

    # face_encoding_strlist = []
    # for i in face_encoding:
    #     face_encoding_strlist.append(str(i))

    # data = {
    #     "enrollment" : enrollment,
    #     "name" : name,
    #     "face_encoding":face_encoding_strlist,
    #     "mobile":mobile
    # }

    # remove_file_or_dir("./Tmp_Faces/"+enrollment+".png")

    attendance_sheet_name = "attendance_" + role + "_" + school_id

    sheet = None

    try:
        sheet = google_file.open(attendance_sheet_name)
    except:
        sheet = google_file.create(attendance_sheet_name)
        sheet.share('margav9535@gmail.com',
                    perm_type='user', role='writer')

    sheet = sheet.sheet1
    sheet.update_cell(1, 1, "Enrollment No.")
    sheet.update_cell(1, 2, "Name")
    sheet.update_cell(1, 3, "Mobile")
    sheet.update_cell(1, 4, "Email")

    get_all_sheet_data = sheet.get_all_values()

    no_of_rows = 1

    if len(get_all_sheet_data) > 0:
        no_of_rows = len(get_all_sheet_data)

    sheet.update_cell(no_of_rows + 1, 1, enrollment)
    sheet.update_cell(no_of_rows + 1, 2, name)
    sheet.update_cell(no_of_rows + 1, 3, mobile)
    sheet.update_cell(no_of_rows + 1, 4, email)

    # try:
    #     db.collection(role).document(uid).update({
    #         "face_encoding": face_encoding_strlist
    #     })
    return jsonify({"message": "Faculty Registered!"}), 200
    # except:
    #     return jsonify({"message": "Error occurred to store data!"})


def take_attendance_(sheet, get_all_sheet_data, time, known_faces):
    attendances = []
    sheet_enrollments = []

    curr_col = str(date.today()) + "(" + time + ")"

    for i in range(1, len(get_all_sheet_data)):
        sheet_enrollments.append(get_all_sheet_data[i][0])

    if get_all_sheet_data[0][-1] == curr_col:
        for i in range(1, len(get_all_sheet_data)):
            attendances.append(get_all_sheet_data[i][-1])
        index = 0
        for e in sheet_enrollments:
            if e in known_faces.split(','):
                attendances[index] = 'P'
            index += 1
    else:
        for e in sheet_enrollments:
            if e in known_faces.split(','):
                attendances.append('P')
            else:
                attendances.append("")

    attendances.insert(0, curr_col)

    no_of_rows = 1
    no_of_cols = 3

    if len(get_all_sheet_data) > 0:
        no_of_cols = len(get_all_sheet_data[0])

    if get_all_sheet_data[0][-1] == curr_col:
        for i in range(0, len(attendances)):
            sheet.update_cell(i + 1, no_of_cols, attendances[i])
    else:
        for i in range(0, len(attendances)):
            sheet.update_cell(i + 1, no_of_cols + 1, attendances[i])



@app.route("/take-faculty-attendance", methods=["POST"])
def take_faculty_attendance():
    role = request.form.get('role')
    school_id = request.form.get('school_id')
    time = request.form.get('type')
    known_faces = request.form.get('known_face')

    attendance_sheet_name = "CCC_Attendance"

    sheet = None

    try:
        sheet = google_file.open(attendance_sheet_name)
    except:
        return jsonify({"message": "Data doesn't exists!"})

    sheet = sheet.sheet1

    get_all_sheet_data = sheet.get_all_values()

    take_attendance_(sheet, get_all_sheet_data, time, known_faces)

    return jsonify({"message": "Done"})


@app.route("/take-attendance", methods=["POST"])
def take_attendance():
    school_id = request.form.get('school_id')
    role = request.form.get('role')
    uid = request.form.get('uid')
    time = request.form.get('type')  # indicates entry / exit

    curr_att = db.collection("attendance").document(uid).get().to_dict()
    # print(curr_att)

    # return "ok"

    im = Image.open(BytesIO(base64.b64decode(curr_att["byteArray"])))
    im.save("./Tmp_Faces/group.png", "PNG")

    all_faculties = get_faculties(school_id, role, "")

    encodings = []
    names = []
    enrollments = []
    mobilenos = []

    for faculty in all_faculties:
        x = np.array(faculty["face_encoding"])
        curr_encoding = x.astype(np.float64)
        encodings.append(curr_encoding)
        names.append(faculty["name"])
        mobilenos.append(faculty["mobile"])
        enrollments.append(faculty["enrollment"])

    # return jsonify({"enrollment":enrollments,"face_encodings":encodings})

    known_faces = image_face_recognition(
        encodings, enrollments, "./Tmp_Faces/group.png")

    remove_file_or_dir("./Tmp_Faces/group.png")
    db.collection("attendance").document(uid).delete()

    if len(known_faces) == 0:
        return jsonify({"present_faculties": "No one present!"})

    attendance_sheet_name = "CCC_Attendance"

    sheet = None

    try:
        sheet = google_file.open(attendance_sheet_name)
        sheet = sheet.attendance
    except:
        return jsonify({"message": "Data doesn't exists!"})

    sheet = sheet.sheet1

    get_all_sheet_data = sheet.get_all_values()

    take_attendance_(sheet, get_all_sheet_data, time, known_faces)

    return jsonify({"present_faculties": known_faces})


@app.route("/generate-report", methods=["POST"])
def generate_report():
    uid = request.form.get("uid")
    role = request.form.get("role")
    school_id = request.form.get("school_id")
    email = request.form.get("email")

    # db_col = db.collection("schools").document(school_id).collection(role).stream()
    # curr_user = db.collection(role).where('uid','==',uid).get()[0].to_dict()

    # if curr_user is None:
    #     return jsonify({"message":"Unauthorized access!"})

    attendance_sheet_name = "CCC_Attendance"

    sheet = None

    try:
        sheet = google_file.open(attendance_sheet_name)
        sheet = sheet.attendance
        sheet.share(email, perm_type='user', role='writer')
        return jsonify({"message": "Successful"})
    except:
        return jsonify({"message": "Data not found!"})


@app.route('/face-unlock', methods=["POST"])
def face__unlock():
    file = request.files['image']
    school_id = request.form.get('school_id')
    role = request.form.get('role')

    file.save('./Tmp_Faces/' + secure_filename("group.jpg"))

    all_faculties = get_faculties(school_id, role)

    encodings = []
    names = []
    for faculty in all_faculties:
        x = np.array(faculty["face_encoding"])
        curr_encoding = x.astype(np.float64)
        encodings.append(curr_encoding)
        names.append((faculty["id"], faculty["name"]))

    known_faces = image_face_recognition(
        encodings, names, "./Tmp_Faces/group.jpg")

    remove_file_or_dir("./Tmp_Faces/group.jpg")


@app.route('/')
def hello():
    return "Connected"


@app.route('/log-request', methods=["POST"])
def logLoginRequestsInfo():
    # This data shall be logged in spreadsheet:
    # Name of User, Role of User, time of request to server, time of response from server, duration, location

    data = json.loads(request.data)

    name = data["name"]
    role = data["role"]
    requestTime = data["requesttime"]
    responseTime = data["responsetime"]
    duration = data["duration"]
    location = data["location"]
    faceStatus = data["facestatus"]
    faceDesc = data["desc"]

    attendance_sheet_name = "Attendance"

    sheet = None

    #try:
    sheet = google_file.open_by_key(attendance_sheet_id)
    #except:
    #    sheet = google_file.create(attendance_sheet_name)
    #    sheet.share('margav9535@gmail.com',
    #                perm_type='user', role='writer')
    #    sheet.share('hms02@ganpatuniversity.ac.in',
    #                perm_type='user', role='writer')
    #    sheetid = sheet.id
        # change_owner(sheetid, "hms02@ganpatuniversity.ac.in")

    try:
        worksheet = sheet.sheet1

        worksheet.update_cell(1, 1, "Name")
        worksheet.update_cell(1, 2, "Role")
        worksheet.update_cell(1, 3, "Request Time")
        worksheet.update_cell(1, 4, "Response Time")
        worksheet.update_cell(1, 5, "Duration")
        worksheet.update_cell(1, 6, "Location")
        worksheet.update_cell(1, 7, "Face Status")
        worksheet.update_cell(1, 8, ".gitattributesDescription")

        get_all_sheet_data = worksheet.get_all_values()

        no_of_rows = 1
        no_of_cols = 1

        if len(get_all_sheet_data) > 0:
            no_of_rows = len(get_all_sheet_data)

        worksheet.update_cell(no_of_rows + 1, 1, name)
        worksheet.update_cell(no_of_rows + 1, 2, role)
        worksheet.update_cell(no_of_rows + 1, 3, requestTime)
        worksheet.update_cell(no_of_rows + 1, 4, responseTime)
        worksheet.update_cell(no_of_rows + 1, 5, duration)
        worksheet.update_cell(no_of_rows + 1, 6, location)
        worksheet.update_cell(no_of_rows + 1, 7, faceStatus)
        worksheet.update_cell(no_of_rows + 1, 8, faceDesc)

        return jsonify({"message": "Done"})
    except Exception as ex:
        return jsonify({"Error": str(ex)})


# @app.route('/getEntryExitStatus', methods=["POST"])
# def getEntryExitStatusReuest():
#    data = json.loads(request.data)
#    userID = data["user_id"]
#    date = data["date"]
#    EntryExitStatus = getEntryExitStatus(userID,date)
#    return jsonify({"data": EntryExitStatus})
def getEntryExitStatus(sheet, user_id, date):
    dateCell = sheet.findall(date)
    isExit = False
    if dateCell:
        if type(dateCell) == Cell:
            dateCell = [dateCell]
        for cells in dateCell:
            row = cells.row
            row_values = sheet.row_values(row)
            if user_id in row_values:
                isExit = True
                break
    checkEntryExitStatus = "Entry" if isExit == False else "Exit"
    return checkEntryExitStatus


rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"


def sign_in_with_email_and_password(email: str, password: str, return_secure_token: bool = True):
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": return_secure_token
    })

    r = requests.post(rest_api_url,
                      params={"key": "AIzaSyC_hCmXK2hfOMy9cLiwltciTRo0V0lfnGs"},
                      data=payload)

    return r.json()


def authenticate_user(email, password):
    try:
        # Sign in the user with their email and password
        user = sign_in_with_email_and_password(email, password)
        return user
    except Exception as E:
        print(E)
        return None


@app.route('/log-attendance', methods=["POST"])
def logAllAttendanceInfo():
    # This data shall be logged in spreadsheet:
    # date_time_of_attendance, user_id, username, user_role, email,
    # mobile_no, attendance location with accuracy, school location,
    # distance of attendance location from school location, school id,
    # Status of Attendance (Approved by System, Pending),
    # Status_Entry_Exit (Enter to school, exit from school)

    dataList = []

    start_time = time.time()
    data = json.loads(request.data)

    if data['newFace'] == "True":
        user = authenticate_user(data['email'], data['pwd'])
        if user is not None:
            userRecords = auth.get_user(user['localId'])
            database = firestore.client()
            faculty_query = database.collection('faculty').where('email', '==', userRecords.email)
            faculty_docs = faculty_query.get()
            if len(faculty_docs) == 0:
                principal_query = database.collection('principal').where('email', '==', userRecords.email)
                principal_docs = principal_query.get()

                if len(principal_docs) == 0:
                    return jsonify({"Error": "User not found"})

                doc = principal_docs[0]

            else:
                doc = faculty_docs[0]

            userData = doc.to_dict()
            dataList = [
                str(data["date"]),
                str(data["time"]),
                str(userData["enrollment"]),
                str(userData["name"]),
                str(data["user_role"]),
                str(userData["email"]),
                str(userData["mobile"]),
                str(data["locationwithaccuracy"]),
                str("Longitude: " + userData["schoolLatitude"]) + " | Latitude: " + str(userData["schoolLongitude"]),
                str(userData["school_id"]),
                str(data["attendance_status"])
            ]

            # Sign the User out of Firebase
            auth.current_user = None
        else:
            return jsonify({"Error": "User not Found!"})
    else:
        dataList = [
            str(data["date"]),
            str(data["time"]),
            str(data["user_id"]),
            str(data["username"]),
            str(data["user_role"]),
            str(data["email"]),
            str(data["mobile_no"]),
            str(data["locationwithaccuracy"]),
            str(data["school_location"]),
            str(data["school_id"]),
            str(data["attendance_status"])
        ]

    attendance_sheet_name = "CCC_Attendance"
    # Specify the sheet ID of the worksheet you want to fetch
    


    sheet = None

    #try:
    sheet = google_file.open_by_key(attendance_sheet_id)
    
    worksheet = sheet.worksheet("attendance")
    headerList = ["Date", "Time", "User ID", "Username", "User Role", "Email", "Mobile No", "Location | Accuracy",
                      "School Location", "School ID", "Attendance Status", "Entry/Exit Status"]
        ##        worksheet.update_cell(1, 1, "Date")
        ##        worksheet.update_cell(1, 2, "Time")
        ##        worksheet.update_cell(1, 3, "User ID")
        ##        worksheet.update_cell(1, 4, "Username")
        ##        worksheet.update_cell(1, 5, "User Role")
        ##        worksheet.update_cell(1, 6, "Email")
        ##        worksheet.update_cell(1, 7, "Mobile No")
        ##        worksheet.update_cell(1, 8, "Location | Accuracy")
        ##        worksheet.update_cell(1, 9, "School Location")
        ##        worksheet.update_cell(1, 10, "School ID")
        ##        worksheet.update_cell(1, 11, "Attendance Status")
        ##        worksheet.update_cell(1, 12, "Entry/Exit Status")

    worksheet.update('A1:L1', [headerList])
    #except Exception as ex:
        #return jsonify({"Error": str(ex)})
        # sheetid = sheet.id
        # change_owner(sheetid, "hms02@ganpatuniversity.ac.in")

    # worksheet = sheet.sheet2
    #worksheet = sheet.worksheet("attendance")
    #try:

    no_of_rows = len(worksheet.get_all_values()) + 1
    strRange = 'A' + str(no_of_rows) + ':L' + str(no_of_rows)
        # print("strRange=",strRange)
    dataList.append(str(getEntryExitStatus(worksheet, dataList[2], dataList[0])))
    worksheet.update(strRange, [dataList])
        ##        worksheet.update_cell(no_of_rows+1, 1, date)
        ##        worksheet.update_cell(no_of_rows+1, 2, time)
        ##        worksheet.update_cell(no_of_rows+1, 3, userID)
        ##        worksheet.update_cell(no_of_rows+1, 4, username)
        ##        worksheet.update_cell(no_of_rows+1, 5, userRole)
        ##        worksheet.update_cell(no_of_rows+1, 6, email)
        ##        worksheet.update_cell(no_of_rows+1, 7, mobileNo)
        ##        worksheet.update_cell(no_of_rows+1, 8, locationWithAccuracy)
        ##        worksheet.update_cell(no_of_rows+1, 9, schoolLocation)
        ##        worksheet.update_cell(no_of_rows+1, 10, schoolID)
        ##        worksheet.update_cell(no_of_rows+1, 11, attendanceStatus)
        ##        worksheet.update_cell(no_of_rows+1, 12, entryExitStatus)
    end_time = time.time()
    return jsonify({"message": "Done", "strRange": "" + strRange,
                        "Execution Time": "Time:" + str((end_time - start_time)) + " seconds"})

    #except Exception as ex:
        #return jsonify({"Error": str(ex)})


@app.route('/get-all-attendance-data', methods=["POST"])
def get_attendance_data():
    attendance_sheet_name = "CCC_Attendance"

    sheet = None

    stringData = ""
    try:
        sheet = google_file.open(attendance_sheet_name)
        sheet = sheet.worksheet("attendance")
        data = json.loads(request.data)
        # return data
        user_id = data["user_id"]
        dateTimeStr = data["date"]

        # datetime_obj = datetime.strptime(dateTimeStr, '%d-%m-%Y %I:%M:%S %p')
        # date = datetime_obj.strftime('%d-%m-%Y') # Output: 14-03-2023

        stringData = stringData + "user_id:" + user_id + ", date:" + dateTimeStr
        # return jsonify({"data": stringData})
        # userIDCell = sheet.findall(user_id)
        dateCell = sheet.findall(dateTimeStr)

        # status_value = row_values[-1] # Assuming the "status" column is the last column in the row.

        # stringData = stringData + "Get Attendance Data: user_id="+ user_id+ "cell="+ str(userIDCell

        # Get all the rows in the sheet
        # rows = sheet.get_all_values()

        # cells = sheet.findall(user_id) + sheet.findall(date)
        values_header_list = sheet.row_values(1)

        matching_rows = []
        if dateCell:
            if type(dateCell) == Cell:
                dateCell = [dateCell]
            for cells in dateCell:
                row = cells.row
                row_values = sheet.row_values(row)
                if user_id == row_values[2]:
                    matching_rows.append(row_values)

        # If any matching rows were found, return them
        if len(matching_rows) > 0:
            allValues = {'data': []}
            j = 0
            for row in matching_rows:
                column_values = {}
                for i in range(0, len(values_header_list)):
                    column_values[values_header_list[i]] = row[i]
                allValues["data"].append(column_values)
            return json.dumps(allValues)

        return jsonify({'data': ""})

    except Exception as inst:
        return jsonify({"message": "Data not found! Exception:" + str(inst.args) + ", error =" + str(
            inst) + ", str=" + stringData})


def change_owner(spreadsheet_id, writer):
    drive_service = discovery.build('drive', 'v3')

    permission = drive_service.permissions().create(
        fileId=spreadsheet_id,
        transferOwnership=True,
        body={
            'type': 'user',
            'role': 'owner',
            'emailAddress': writer,
        }
    ).execute()

    drive_service.files().update(
        fileId=spreadsheet_id,
        body={'permissionIds': [permission['id']]}
    ).execute()


def LivelynessDetection(encodedFaceImage: str):
    # Decode the base64 image
    image_data = base64.b64decode(encodedFaceImage)
        
    # Generate the file name with date and time format
    current_datetime = datetime.now()
    image_filename = current_datetime.strftime("image_%d-%m-%Y %H-%M-%S.jpg")
        
    # Specify the folder where you want to save the image
    save_folder = "received_images_client"
        
    # Create the full path for the image file
    image_path = os.path.join(save_folder, image_filename)
        
    # Save the image to the specified folder
    with open(image_path, "wb") as image_file:
        image_file.write(image_data)
    url = 'http://localhost:4000'
    headers = {'Content-Type': 'application/json'}
    data = {'image': encodedFaceImage}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        response_data = response.json()
        res = response_data['Face']
        # Response example: {Status,Label,Face,Score}
        print (res)
        return jsonify({'face': res})
    else:
        error_message = 'Unexpected code in LivelynessDetection: ' + str(response.status_code)
        return jsonify({'error': error_message})

def recognizeFace(encodedFaceImage:str):
    # decoded_image = base64.b64decode(encodedFaceImage)
    url = 'http://localhost:8000/api/v1/recognition/recognize'
    headers = {'Content-Type': 'application/json', 'x-api-key': "d17f1343-f11f-4e50-b435-97f2e1a53751"}
    data = {'file': encodedFaceImage}
    # data = {'file': decoded_image}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
        return jsonify(response_data)
    else:
        error_message = 'Unexpected code in recognizeFace: ' + str(response.status_code)
        return jsonify({'error': str(error_message)})


@app.route("/run-face-check", methods=["POST"])
def face_check():
    # data = json.loads(request.data)
    # encodedFaceImage = data["image"]
    request_data = request.json 
    image_data=request_data.get('image','')
    status=request_data.get('status','')
    encodedFaceImage = image_data
    # print(encodedFaceImage)
    try:
        start_time_livelyness = time.time()
        LivelynessDetectionResult = LivelynessDetection(encodedFaceImage)
        end_time_livelyness = time.time()
        duration_livelyness = end_time_livelyness - start_time_livelyness
        LivelynessData = json.loads(LivelynessDetectionResult.get_data(as_text=True))

        if LivelynessData["face"] == "Real Face":
            start_time_recognize = time.time()
            recognizeFaceResult = recognizeFace(encodedFaceImage)
            end_time_recognize = time.time()
            duration_recognize = end_time_recognize - start_time_recognize

            recognizeFaceResultDict = json.loads(recognizeFaceResult.get_data(as_text=True))

            recognizeFaceResultDict["livelyness_execution_time"] = duration_livelyness
            recognizeFaceResultDict["recognize_execution_time"] = duration_recognize
            e=add_manual_entry(recognizeFaceResultDict,status)
            print(recognizeFaceResultDict)
            
            
            return jsonify(e)
            
        else:
            return jsonify({'data': "Fake Face"})
    except Exception as ex:
        print(ex)
        return jsonify({'error': str(ex)})
    



@app.route('/get-data', methods=["POST"])
def get_data():
    ##    data = {
    ##        '1234': {'school_id': '4321', 'email': 'abc@gmail.com', 'phone': '1234567890', 'name': 'abc', 'role': 'faculty'},
    ##        '5678': {'school_id': '4321', 'email': 'xyz@gmail.com', 'phone': '0987654321', 'name': 'xyz', 'role': 'principal'},
    ##        '1357': {'school_id': '4321', 'email': 'abc@gmail.com', 'phone': None, 'name': 'abc', 'role': 'faculty'}
    ##    }
    attendance_sheet_name = "CCC_Attendance"

    sheet = None

    stringData = ""
    try:
        sheet = google_file.open(attendance_sheet_name)
        sheet = sheet.worksheet("users")
        data = json.loads(request.data)
        unique_id = data['unique_id']
        cell = sheet.find(unique_id)
        print("id=", unique_id, "cell=", cell)
        if cell is None:
            return jsonify({"message": "Data not found! id = " + unique_id + "cell=" + str(cell)})
        values_header_list = sheet.row_values(1)
        values_list = sheet.row_values(cell.row)
        stringData = stringData + "Cell Row =" + str(cell.row) + ", len(headerlist)=" + str(
            len(values_header_list)) + ", len(value)=" + str(len(values_list))

        allValues = {}
        for i in range(0, len(values_list)):
            allValues[values_header_list[i]] = values_list[i]
        return jsonify({"data": json.dumps(allValues)})
    except Exception as inst:
        return jsonify({"message": "Data not found! Exception:" + str(inst.args) + ", error =" + str(
            inst) + ", str=" + stringData})


##    data = json.loads(request.data)
##    unique_id = data['unique_id']
##
##    if unique_id in data.keys():
##        return jsonify({"data": data[unique_id]})
##    else:
##        return jsonify({"data": "No Value"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=None)

'''
data = "base64 data"
im = Image.open(BytesIO(base64.b64decode(data)))
im.save("./Tmp_Faces/"+enrollment+".jpg","JPG")
'''
