import requests
import csv
import matplotlib.pyplot as plt
import numpy as np

from config import *
from azure.storage.blob import BlobServiceClient # Azure Blob Storage
from datetime import datetime # Manipulare date si ore
import smtplib # Trimite emailuri prin protocolul SMTP
from email.mime.text import MIMEText # Creare mesaj email in format text
from email.mime.multipart import MIMEMultipart # Creare email cu mai multe parti (text, atasamente)

# Funcție pentru trimiterea emailului cu detalii despre pace si activitate
def test_trimite_email(pace,activitate):
    sender_email = SENDER_EMAIL # adresa email expeditor
    sender_password = SENDER_PASSWORD  # parola aplicatie pt autentificare
    recipient_email = RECIPIENT_EMAIL # adresa email destinatar

    subject = "Informatii activitate" # Subiect email
    # Corp email cu info despre pace si activitate
    body = (f"Felicitari pentru rezultatul obtinut, ai un pace sub 8 min/km. Keep it up! "
            f"\nPace: {pace:.1f} min/km, Activitate: {activitate}")

    msg = MIMEMultipart() # Creare obiect pt mesajul email, poate avea mai multe parti
    msg['From'] = sender_email # seteaza adresa expeditor
    msg['To'] = recipient_email # seteaza adresa destinatar
    msg['Subject'] = subject # seteaza subiect
    msg.attach(MIMEText(body, 'plain')) # ataseaza corp mesaj ca text simplu

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server: # conectare la server SMTP Gmail (Simple Mail Transfer Protocol)
            server.starttls() # activare criptare TLS pt securitate (Transport Layer Security)
            server.login(sender_email, sender_password) # autentificare pe server
            server.send_message(msg) # trimitere mesaj
            print(f"Email trimis cu succes către {recipient_email}!") # mesaj de succes trimitere
    except Exception as e:
        print(f"Eroare la trimiterea emailului: {e}") # mesaj de eroare

# Functie creare gauge chart pentru ritmul cardiac
def plot_gauge(heart_rate, activity_name):
    fig, ax = plt.subplots(figsize=(6, 4), subplot_kw={'projection': 'polar'}) # creaza grafic polar (semi-cerc)

    # Parametri gauge chart
    lower_limit = 0 # limita inferioara (0 BPM)
    upper_limit = 200 # limita superioara (200 BPM)
    theta = np.linspace(0, np.pi, 100)  # generare 100 puncte de la 0 la 180 grade pentru semi-cerc
    radii = [0.8 for _ in np.linspace(lower_limit, upper_limit, 100)]  # setare raza constanta, zona plină pentru gauge complet

    # Colorare zone (verde, galben, roșu)
    colors = ['green' if hr <= 100 else 'yellow' if hr <= 150 else 'red' for hr in np.linspace(lower_limit, upper_limit, 100)]

    # Colorare semi-cerc cu zone de culoare
    for r, c, t in zip(radii, colors, theta):
        ax.bar(t, r, color=c, width=0.05, bottom=0.1)

    # Indicator pt valoarea curenta ritm cardiac
    indicator_angle = (heart_rate - lower_limit) * np.pi / (upper_limit - lower_limit)  # calcul unghi pt valoare curenta
    ax.plot([indicator_angle, indicator_angle], [0, 1], color="black", linewidth=3, label=f"{heart_rate} BPM") # desenare linie indicator
    
    # Text pt valoarea ritmului cardiac
    #ax.text(0, 1.1, f"{heart_rate} BPM", ha="left", fontsize=12)

    # Etichete pentru limitele dintre zone (verde, galben, roșu)
    ax.text(np.pi * 0, 1.05, "0", ha="center", fontsize=12, color="black")  # 0 - incepere
    ax.text(np.pi * 0.5, 1.05, "100", ha="center", fontsize=12, color="black") # 100 BPM - limita verde
    ax.text(np.pi * 0.75, 1.05, "150", ha="center", fontsize=12, color="black") # 150 BPM - limita galben
    ax.text(np.pi * 1, 1.05, "200", ha="center", fontsize=12, color="black") # 200 BPM - limita rosu

    # Ajustari grafic
    ax.set_yticklabels([]) # indeparteaza etichete de pe axa Y
    ax.set_xticks([]) # indeparteaza etichete de pe axa X
    ax.set_ylim(0, 1) # seteaza limita pe axa radiala
    ax.set_xlim(0, np.pi)  # limiteaza unghiul graficului la 180 grade
    plt.title(f"Ritm Cardiac: {activity_name}", fontsize=14) # titlu grafic
    plt.legend(loc="upper left") # afisare legenda
    plt.show() # afisare grafic

# Strava API Authentication
client_id = CLIENT_ID #ID client Strava
client_secret = CLIENT_SECRET # parola client Strava
authorization_code = AUTHORIZATION_CODE # cod unic de autorizare obtinut la cerere

# Strava Access Token - URL obtinere token de acces
token_url = 'https://www.strava.com/oauth/token'
token_params = {
    'client_id': client_id,
    'client_secret': client_secret,
    'code': authorization_code,
    'grant_type': 'authorization_code' #tipul de cerere pt obtinerea tokenului
}

# Obtine un nou access token printr-o cerere POST
response = requests.post(token_url, data=token_params)
token_data = response.json() # raspuns ca JSON

if 'access_token' in token_data:
    access_token = token_data['access_token'] # salvare token de acces
    print("Access token obținut cu succes:", access_token) # mesaj succes
else:
    print("Eroare la obținerea access token-ului:", token_data) # mesaj eroare
    exit() # oprire executie script in caz de eroare

# Strava Activities Request - URL pt obtinere activitati Strava
activities_url = 'https://www.strava.com/api/v3/athlete/activities'
headers = {
    'Authorization': f'Bearer {access_token}' # adauga token de acces in header pt autentificare
}

# Cerere pt obtinere activitati Strava
activities_response = requests.get(activities_url, headers=headers)

# Verificare daca cererea a avut succes
if activities_response.status_code == 200: # status 200 - succes
    activities = activities_response.json() # parcurge raspunsul JSON
    #print("Activități obținute:") # afisare in consola

    # Salvare activitati intr-un fisier CSV local
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # creare timestamp pt fisier (YYYYMMDD_HHMMSS)
    csv_path = rf'c:\Users\Asus\Documents\activitati_strava_{timestamp}.csv' # path pt fisier local

    # Initializare date pt vizualizare
    pace_list = [] # lista pace activitati
    activity_names = [] # lista nume activitati
    heart_rate = None # variabila pt ritm cardiac mediu

    # Scriere date în fisier CSV local
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Activitate', 'Distanta (m)', 'Pace (min/km)', 'Ritm cardiac mediu (bpm)'])
        for activity in activities:
            distance = activity['distance'] # distanta activitate
            pace = (activity['elapsed_time'] / 60) / (distance / 1000) if distance > 0 else None #c alcul pace
            pace_display = f"{pace:.2f} min/km" if pace else "N/A" # afisare pace
            heart_rate = activity.get('average_heartrate', 'N/A') # obtinere ritm cardiac mediu

            # Verificare pace sub 8 min/km și trimitere email
            if pace and pace < 8:
                test_trimite_email(pace, activity['name'])

            # Adaugare date activitati pentru grafice
            if distance > 0:
                pace_list.append(pace)
                activity_names.append(activity['name'])

            # Scriere date in fisier
            writer.writerow([activity['name'], distance, pace_display, heart_rate])
        print("Fișierul a fost salvat local cu succes")

    # Configurare pt Azure Blob Storage
    # String de conexiune pt Azure Blob Storage
    connection_string = AZURE_CONNECTION_STRING
    blob_service_client = BlobServiceClient.from_connection_string(connection_string) # creare client pt Azure Blob Storage
    container_name = 'strava-data' # nume container
    blob_client = blob_service_client.get_blob_client(
        container='strava-data', # specifica containerul
        blob=f'activitati_strava_{timestamp}.csv' # nume fisier blob
    )

    # Incarcare fisier CSV in Azure Blob Storage
    with open(csv_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True) # incarcare fisier in blob cu suprascriere fisier existent
        print(f"Datele au fost salvate în Azure Blob Storage ca activitati_strava_{timestamp}.csv") # mesaj succes

    # Creare si afisare grafic cu Matplotlib pt pace activitati
    plt.figure(figsize=(10, 6))
    plt.plot(activity_names, pace_list, marker='o', color='g', linestyle='-', linewidth=2)
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Activitate')
    plt.ylabel('Pace (min/km)')
    plt.title('Evoluția pace-ului pentru activități')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Adaugare gauge-uri pentru fiecare activitate, in functie de ritm cardiac
    for activity in activities:
        heart_rate = activity.get('average_heartrate', None)
        activity_name = activity['name']
        if heart_rate:
            plot_gauge(heart_rate, activity_name)

else:
    print("Eroare la obținerea activităților:", activities_response.json())  # mesaj eroare daca cererea nu reuseste