import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage


cred = credentials.Certificate("xxx.json") #Online Firebase Database API json file name here
firebase_admin.initialize_app(cred,{
    'databaseURL':"",
    'storageBucket':""
})


#Importing the mode images into a list
folderPath='Images'

PathList=os.listdir(folderPath)
print(PathList)
imgList=[]
studentIds=[]
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    studentIds.append(os.path.splitext(path)[0])

    fileName=f'{folderPath}/{path}'
    bucket=storage.bucket()
    blob=bucket.blob(fileName)
    blob.upload_from_filename(fileName)


    #print(path)
    #print(os.path.splitext(path)[0])
print(studentIds)



def findEncodigs(ImagesList):
    encodeList=[]
    for img in ImagesList:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode=face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList
#Load the encoding file
#print("Encoding started......")
encodeListKnown=findEncodigs(imgList)
encodeListKnownWithIds=[encodeListKnown,studentIds]
#print(encodeListKnown)
#print("encoding Complete")
encodeListKnown,studentIds=encodeListKnownWithIds



file=open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownWithIds,file)
file.close()
#print("File Saved")









