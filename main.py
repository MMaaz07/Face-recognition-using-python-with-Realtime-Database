import os
from copyreg import pickle
import pickle
import cvzone

import cv2
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("xxxxx.json") #Online Firebase Database API json file name here
firebase_admin.initialize_app(cred,{
    'databaseURL':"",
    'storageBucket':""
})

bucket=storage.bucket()


#print(cv2.__version__)
#import cv2

cap=cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

imgBackground = cv2.imread('Resources/background.png')

#importing the mode images into a list
folderModePath='Resources/Modes'
modePathList=os.listdir(folderModePath)
imgModeList=[]
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
#print(len(imgModeList))

#load the encoding file
file=open('EncodeFile.p','rb')
encodeListKnownWithIds=pickle.load(file)
file.close()
encodeListKnown,studentIds=encodeListKnownWithIds
#print(studentIds)
print("Encode File Loaded")

modeType=0
count=0
id=-1
imgStudent=[]


if imgBackground is None:
    print("Error: Could not load the background image. Check the file path.")
    exit()

#Load the encoding file
#print("Loading Encode File......")
file=open('EncodeFile.p','rb')
encodeListKnownWithIds=pickle.load(file)
file.close()
encodeListKnown,studentIds= encodeListKnownWithIds
#print(studentIds)




while True:
    success, img=cap.read()




    imgS=cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrFrame= face_recognition.face_locations(imgS)
    encodeCurrFrame=face_recognition.face_encodings(imgS,faceCurrFrame)

    imgBackground[162:162+480,55:55+640]=img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    if faceCurrFrame:
        for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches",matches)
            # print("faceDis",faceDis)

            matchIndex = np.argmin(faceDis)
            # print("faceDis",matchIndex)

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                if count == 0:
                    cvzone.putTextRect(imgBackground,"Loading",(275,400))
                    cv2.imshow("Face Attendance",imgBackground)
                    cv2.waitKey(1)
                    count = 1
                    modeType = 1

        if count != 0:
            if count == 1:
                # Get the fata
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                # Get the Image from the Storage
                blob = bucket.get_blob(f'Images/{id}.jpeg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # Update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_recorded'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondElapsed)
                if secondElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['Total_Attendance'] += 1
                    ref.child('Total_Attendance').set(studentInfo['Total_Attendance'])
                    ref.child('last_recorded').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    count = 0

            if modeType != 3:
                if 10 < count < 20:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if count <= 10:
                    cv2.putText(imgBackground, str(studentInfo['Total_Attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['Ending_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['Year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['Name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['Name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    # imgBackground[175:175+468,909:909+468]=imgStudent

                count += 1

            if count >= 20:
                count = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType=0
        count=0

        # print("known Face Detected")
        # print(studentIds[matchIndex])



    #cv2.imshow("webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)