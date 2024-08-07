# *************** IMPORTS ***************
from dotenv import load_dotenv
import logging
import os
import streamlit as st

logging.basicConfig(level=logging.INFO, # Set the logging level
format='%(asctime)s [%(levelname)s] - %(message)s',
datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__name__)
LOGGER.info("Init Global Variable")

# ********* load .env content
load_dotenv()

# ********* set token for openai and datastax
api_key = st.secrets["api"]
# ********* set token for openai and datastax
OPENAI_API_KEY = api_key["openai_api_key"]
ASTRADB_API_ENDPOINT= api_key["ASTRADB_API_ENDPOINT"]
ASTRADB_NAMESPACE_NAME= api_key["ASTRADB_NAMESPACE_NAME"]
ASTRADB_COLLECTION_NAME= api_key["ASTRADB_COLLECTION_NAME"]
ASTRADB_TOKEN_KEY= api_key["ASTRADB_TOKEN_KEY"]

# ********* Global Variables
OUTPUT_CV_EXTRACT = {
    "summary": {
        "name": "CV owner name",
        "location": "city, country",
        "phone": "string of phone number",
        "email": "email",
        "summary": "work summary of the CV owner"
    },
    "work_experience":[
        {
        "company_name": "company name cv owner worked",
        "job_title": "string of job position",
        "date": "start and end of MONTH and YEAR",
        "description": ["an array of work experience description"]
        }
    ],
    "education":[
        {
        "school_name": "school name, college name",
        "date": "start and end of MONTH and YEAR",
        "degree_major": "degree major of especially in university",
        "score": "final score or evaluate point in university",
        "description": ["an array of education description"]
        }
    ],
    "project": [
        {
        "project_name": "the project name",
        "date": "start and end of MONTH and YEAR",
        "description": ["an array of project description"]
        }
    ],
    "skills": []

}
        
REQUIRED_FIELDS = {
    'summary': ['description'],
    'work_experience': [
        'company_name', 
        'job_title', 
        'date', 
        'description'
        ],
    'education': [
        'school_name', 
        'date', 
        'degree_major', 
        'description'
        ],
    'project': [
        'project_name', 
        'date', 
        'description'
        ],
    'skills': []
}

PAYLOAD_TYPE = {
    "summary": {
        "name": str,
        "location": str,
        "phone": str,
        "email": str,
        "description": str
    },
    "work_experience":{
        "company_name": str,
        "job_title": str,
        "date": str,
        "description": list
        },
    "education":{
        "school_name": str,
        "date": str,
        "degree_major": str,
        "description": list
        },
    "project":{
        "project_name": str,
        "date": str,
        "description": list
        },
    "skills": []
}

EXPECTED_KEYS = {
    'question',
    'answer'
}

list_of_locations = [''] + [
    'Aachen', 'Aalen', 'Aarhus', 'Aix-en-Provence', 'Albstadt', 'Amiens', 'Amsterdam', 'Annecy', 
    'Antwerp', 'Augsburg', 'Avranches', 'Bad Homburg', 'Bad Neustadt an der Saale', 'Barberà del Vallès', 
    'Barcelona', 'Beijing', 'Berlin', 'Bertrange', 'Bielefeld', 'Biot', 'Bobigny', 'Bonn', 'Bordeaux', 
    'Bornheim', 'Botucatu', 'Boulogne-Billancourt', 'Breda', 'Bremen', 'Bretten', 'Breuil-le-Sec', 
    'Brognard', 'Brussels', 'Buchloe', 'Buchs', 'Böblingen', 'Bühl', 'Cannes', 'Cassis', 'Cayenne', 
    'Cesson-Sévigné', 'Cham', 'Charenton-le-Pont', "Charmes-sur-l'Herbasse", 'Clamart', 'Clermont-Ferrand', 
    'Clichy', 'Colmar', 'Cologne', 'Colombes', 'Copenhagen', 'Courbevoie', 'Crailsheim', 'Créteil', 
    'Dettingen an der Iller', 'Dijon', 'Dingolfing', 'Dortmund', 'Dresden', 'Dudelange', 'Dusseldorf', 
    'Düsseldorf', 'Eggenstein-Leopoldshafen', 'Eindhoven', 'Eisenach', 'Elchingen', 'Emsbüren', 
    'Esch-sur-Alzette', 'Eschborn', 'Essen', 'Fleury-Mérogis', 'Fontenay-sous-Bois', 'France', 
    'Frankfurt', 'Frankfurt am Main', 'Freiburg im Breisgau', 'Freising', 'French Guiana', 
    'Friville-Escarbotin', 'Fulda', 'Garching', 'Gennevilliers', 'Gerlingen', 'Germany', 'Giengen', 
    'Girona', 'Gonesse', 'Grenoble', 'Grenzach-Wyhlen', 'Guyancourt', 'Gütersloh', 'Halle (Saale)', 
    'Hamburg', 'Hanover', 'Hauts-de-Seine', 'Heidenheim', 'Heilbronn', 'Heringsdorf', 'Holzgerlingen', 
    'Isigny-sur-Mer', 'Issy-les-Moulineaux', 'Italy', 'Japan', 'Jena', 'Karlsruhe', 'Kempten', 'Kiel', 
    'Korbach', 'Kreuzlingen', 'Kufstein', 'Kusterdingen', 'La Balme-les-Grottes', 'Langgöns', 'Laval', 
    'Le Kremlin-Bicêtre', 'Le Pré-Saint-Gervais', 'Leiden', 'Leinfelden-Echterdingen', 'Leipzig', 
    'Les Herbiers', 'Leutkirch im Allgäu', 'Levallois-Perret', 'Lille', 'Limbach-Oberfrohna', 'Limoges', 
    'Lisbon', 'Lohr a. Main', 'London', 'Ludwigshafen', 'Lussemburgo', 'Luxembourg', 'Lyngby', 'Lyon', 
    'Madrid', 'Magstadt', 'Mainz', 'Mannheim', 'Marchamalo', 'Marcoussis', 'Marsaz', 'Marseille', 
    'Martigues', 'Massy', 'Matoury', 'Melsungen', 'Metz', 'Metzingen', 'Mexico', 'Milan', 'Mogliano Veneto', 
    'Monaco', 'Mondeville', 'Monheim am Rhein', 'Montrouge', 'Munich', 'Murrhardt', 'Möglingen', 'Münster', 
    'Nanterre', 'Nantes', 'Neuilly-sur-Seine', 'Nice', 'Nidderau', 'Nogent-sur-Marne', 'Nogent-sur-Seine', 
    'Nuremberg', 'Oberkochen', 'Odense', 'Orleans', 'Pantin', 'Paris', 'Parma', 'Pau', 'Plochingen', 'Poissy', 
    'Prague', 'Puch bei Hallein', 'Pulnoy', 'Puteaux', 'Radeberg', 'Radolfzell am Bodensee', 'Ramillies', 
    'Ravensburg', 'Regensburg', 'Rennes', 'Reutlingen', 'Roissy-en-France', 'Rome', 'Rungis', 'Saarbrücken', 
    'Saint-Etienne', 'Saint-Laurent-Blangy', 'Saint-Maur-des-Fossés', 'Saint-Ouen-sur-Seine', 'Salzburg', 
    'Salzgitter', 'Schwalbach am Taunus', 'Schwarzheide', 'Sihlbrugg', 'Singapore', 'Sosnowiec', 'Stockport', 
    'Strasbourg', 'Stuttgart', 'Suresnes', 'Szczecin', 'Teltow', 'Thailand', 'Toulouse', 'Traunreut', 
    'Trieste', 'Uhingen', 'Ulm', 'União das freguesias de Carnaxide e Queijas', 'Unterföhring', 'Vanves', 
    'Verberie', 'Verona', 'Vert-le-Grand', 'Vienna', "Villeneuve-d'Ascq", 'Vimercate', 'Vitry-sur-Seine', 
    'Walldorf', 'Wambrechies', 'Warsaw', 'Weil am Rhein', 'Wiener Neudorf', 'Würzburg', 'Zaventem', 'Zürich', 
    's-Hertogenbosch', 'Évry-Courcouronnes', 'Świebodzin'
    ]

list_of_category = [''] +[
    "Accounting", "Advertising", "Aerospace Engineering", "Agricultural Engineering", "Agriculture",
    "Air Traffic Controller", "Animal Science", "Anthropology", "Archaeology", "Architecture",
    "Art History", "Arts", "Astronomy", "Aviation", "Banking", "Biochemistry", "Biology", "Biomedical Engineering",
    "Biotechnology", "Botany", "Broadcasting", "Business", "Business Administration", "Chemical Engineering",
    "Chemistry", "Civil Engineering", "Communication", "Computer Engineering", "Computer Science",
    "Construction Management", "Creative Writing", "Criminal Justice", "Criminology", "Culinary Arts", "Dance",
    "Dentistry", "Design", "Drama", "Economics", "Education", "Electrical Engineering", "Engineering", "English",
    "Environmental Engineering", "Environmental Science", "Fashion Design", "Film", "Finance", "Fine Arts",
    "Food Science", "Forestry", "Geography", "Geology", "Graphic Design", "Health Science", "History", "Hospitality",
    "Human Resources", "Industrial Engineering", "Information Technology", "International Relations", "Journalism",
    "Landscape Architecture", "Law", "Linguistics", "Literature", "Management", "Marketing", "Mathematics", "Mechanical Engineering",
    "Media", "Medicine", "Microbiology", "Music", "Nursing", "Nutrition", "Occupational Therapy", "Oceanography",
    "Performing Arts", "Pharmaceutical Sciences", "Philosophy", "Photography", "Physical Therapy", "Physics",
    "Political Science", "Psychology", "Public Administration", "Public Health", "Public Relations", "Real Estate",
    "Recreation", "Religious Studies", "Robotics", "Social Work", "Sociology", "Software Engineering", "Sports Management",
    "Statistics", "Teaching", "Theology", "Tourism", "Urban Planning", "Veterinary Medicine", "Zoology"
]

list_of_education = [''] +['BAC', 'BAC +2', 'BAC +3', 'BAC +4', 'BAC +5', 'No Level Prerequired']

list_of_durations = [''] +['2 months', '3 months', '4 months', '6 months']

LOGGER.info("Setup Done")

