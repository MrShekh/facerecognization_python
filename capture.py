import cv2
import requests

URL = "http://127.0.0.1:8000/api/mark-attendance"  # ✅ Correct API endpoint

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # ✅ Use correct backend

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not capture frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Camera Preview", frame)  

    if len(faces) > 0:  # ✅ Only send if face is detected
        _, img_encoded = cv2.imencode('.jpg', frame)
        response = requests.post(URL, files={"file": ("image.jpg", img_encoded.tobytes(), "image/jpeg")})
        
        if response.status_code == 200:
            print(response.json())  # ✅ Print API response

    if cv2.waitKey(1) & 0xFF == ord("q"):  # ✅ Press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()
