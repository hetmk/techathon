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
    "{your-credentials}", scopes)
google_file = gspread.authorize(google_sheet_credentials)
gc = gspread.service_account(filename='{your-credentials}')

attendance_sheet_id = "{your-credentials}"
app = Flask(__name__)


cred = credentials.Certificate(
     "{your-credentials}")
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
                attendance_sheet2 = gc.open_by_url('{your-credentials}')
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


                str2+="Attendance Marked for Employee: "
                for i in arr:
                    str2+=" "
                    str2+=i
            else:   
                str2+="Not an Employee, DO register. Please"
                # return jsonify(str)

                
    return str2


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




@app.route('/')
def hello():
    return "Connected"



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
    headers = {'Content-Type': 'application/json', 'x-api-key': "{compareface-api-key}"}
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
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=None)

