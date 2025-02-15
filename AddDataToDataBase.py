import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


cred = credentials.Certificate("")
firebase_admin.initialize_app(cred,{
    'databaseURL':""
})

ref=db.reference('Students')

data={
    "6637":
        {
            "Name":"Mohammed Maaz",
            "major":"AIML",
            "Ending_year":"2025",
            "Total_Attendance":60,
            "Year":4,
            "last_recorded":"2024-9-3 00:54:34"
        },
"6638":
        {
            "Name":"John Wick",
            "major":"AIML",
            "Ending_year":"2025",
            "Total_Attendance":8,
            "Year":4,
            "last_recorded":"2024-9-3 00:54:34"
        }
}

for key,value in data.items():
    ref.child(key).set(value)