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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# api_key = st.secrets["api"]
# ********* set token for openai and datastax
# OPENAI_API_KEY = os.getenv("openai_api_key")
ASTRADB_API_ENDPOINT= os.getenv("ASTRADB_API_ENDPOINT")
ASTRADB_NAMESPACE_NAME= os.getenv("ASTRADB_NAMESPACE_NAME")
ASTRADB_COLLECTION_NAME= os.getenv("ASTRADB_COLLECTION_NAME")
ASTRADB_TOKEN_KEY= os.getenv("ASTRADB_TOKEN_KEY")

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

list_of_locations = [''] + ['Paris', 'Suresnes', 'Neuilly-sur-Seine', 'Paris, Nantes, Lille, Lyon',
                     'Paris, Boulogne-Billancourt', 'Prague', 'Frankfurt', 'Singapore',
                     'Crailsheim', 'Garching', 'Pulnoy', 'Berlin', 'Issy-les-Moulineaux',
                     'Oberkochen', 'Aalen', 'Luxembourg', 'Girona', 'Barberà del Vallès',
                     'Barcelona', 'Szczecin', 'Świebodzin', 'Sosnowiec', 'London', 'Cologne',
                     'Bordeaux', 'Toulouse', 'Munich', 'Vitry-sur-Seine',
                     'Lussemburgo , Luxembourg', 'Kreuzlingen', 'Clichy', 'Lyon', 'Heidenheim',
                     'Pantin', 'Hamburg', 'Berlin, Düsseldorf, Frankfurt, Hamburg, Munich, Stuttgart', 'Grenoble',
                     'Marcoussis', 'Vanves', 'Leipzig', 'Leinfelden-Echterdingen',
                     'Paris, Grenoble', 'Bremen', 'Saint-Maur-des-Fossés', 'Stuttgart', 'Bonn',
                     'Annecy', 'Frankfurt am Main', 'Gerlingen', 'Regensburg', 'Ludwigshafen',
                     "Marsaz, Charmes-sur-l'Herbasse", 'Vert-le-Grand', 'Eisenach', 'Mainz',
                     'Freising', 'Hamburg, Stuttgart, Berlin, Leipzig, Nuremberg, Frankfurt, Essen, Düsseldorf, Karlsruhe, Cologne, Mannheim, Hanover, Munich, Dortmund',
                     'Zaventem', 'Ramillies', 'Brognard',
                     'Düsseldorf, Stuttgart, Munich, Frankfurt, Cologne, Leipzig, Hamburg, Berlin',
                     'Hamburg, Frankfurt, Stuttgart, Munich, Berlin, Nuremberg, Cologne, Düsseldorf',
                     'Melsungen', 'Jena', 'Leiden', 's-Hertogenbosch',
                     'Paris, Lille, Nantes, Nice, Lyon, Strasbourg', 'Düsseldorf',
                     'Fontenay-sous-Bois', 'Berlin, Stuttgart, Frankfurt, Cologne', 'Aarhus',
                     'Saint-Etienne, Paris', 'Dudelange', 'Wiener Neudorf', 'Weil am Rhein',
                     'Guyancourt', 'Brussels', 'Luxembourg, Lussemburgo', 'Cannes', 'Nanterre',
                     'Milan', 'Cayenne', 'Évry-Courcouronnes', 'nan', 'Paris, Nantes', 'Puteaux',
                     'France', 'Murrhardt', 'Bühl', 'Kusterdingen', 'Karlsruhe', 'Les Herbiers',
                     'Aachen', 'Halle (Saale)', 'Nuremberg', 'Nuremberg, Munich',
                     'Berlin, Dresden, Leipzig', 'Frankfurt, Germany', 'Fleury-Mérogis',
                     'Puch bei Hallein', 'Vienna, Salzburg', 'Levallois-Perret',
                     'Boulogne-Billancourt', 'Montrouge', 'French Guiana', 'Biot',
                     'Cesson-Sévigné', 'Martigues', 'Gennevilliers', 'Limbach-Oberfrohna',
                     'Colombes', 'Emsbüren', 'Laval']

list_of_category = [''] +["Banking & Finance", "Molecular Biology", "Supply Chain", "Marketing & Communication",
                     "Event Planning", "Operations", "Praktikum/Werkstudent", "Research and Advisory", "Digital Media", 
                     "Logistics & Supply Chain", "Education", "Corporate Social Responsibility", "Lean Management", 
                     "Production & Operations", "Customer Service", "Content Marketing", "Social Impact", "IT Project", 
                     "Backoffice Operations", "Financial Services", "Training and Development", "Data & Product Management", "Customer service", 
                     "Industrial Design & Engineering", "Financial Analysis", "Sustainability", "Chemistry", "Finance & Risk Management", "Administrative", "Design & Creative", "Health and Safety", "Marketing & Category Management", 
                     "Risk & Compliance", "Fashion", "Media", "Regulatory Strategy", "Education & Training", "Media Production", "Data Analytics", "Management Control", "Civil Engineering & Structures", "Event Management", "Compliance", 
                     "Mechatronics", "Construction", "Maintenance", "Information Technology", "Legal Internship", "Electronics & Signal Processing", "Product Management", "Market Research", "Financial Markets", "Data Visualization", "Cloud Computing",
                     "Sustainable Finance", "Marketing & Webmarketing", "Agronomy & Biology", "AI / Machine Learning", "Logistics", "Internship", "Quality Assurance & Maintenance", "Corporate law", "Performance Marketing", "Software Testing", "Politics", 
                     "Supply Chain Management", "Economics", "Corporate Finance", "Digital Marketing", "Webmarketing", "Back Office Operations", "PR & Events", "Recruitment", "Legal", "Consulting & Strategy", "Electronics", "Human Resources", "Content Creation", 
                     "Business Development", "Sales & Business Development", "Events", "Industrial Design", "Communications", "Pricing", "Online Marketing", "Purchasing", "Product Development", "Regulatory Compliance", "Nutrition & Food Science", "Tax Administration", "Real Estate", "Publishing", "Sports Management", "Project Management", "Financial Audit", "Quality Assurance", 
                     "Management", "Production", "Brand Management", "IT Project Management", "Virtual Reality", "Research & Development", "Risk Management", "Infrastructure Development", "Maintenance & Mechatronics", "Environment", "Accounting", 
                     "Real Estate Management", "Technology", "Infrastructures", "Insurance", "Maintenance Engineering", "E-Commerce", "Environment & Sustainable Development", "Audit", "Automotive Technology", "Social Media Management", "Tax Law", "Communication", "Leadership Development", "Asset Management", "Sales Operations", "E-commerce", "Statistics", "International Relations", "Data Analytics & Applied Maths", "Admin", "Data Analysis", "Public Relations", "Materials & Mechanical engineering", "Engineering", "Business Intelligence", "Energy", "Journalism", "Programming", "Business Continuity", "Technology & Software", "Data Management", "Robotics", "Industrial Training Program", "Fashion Industry", "Sustainable Development", "Renewable Energy", "Sales", "Finance", "Consulting", "Materials & Mechanical Engineering", "Marketing"]

list_of_education = [''] +['BAC +5', 'nan', 'BAC +3', 'BAC +2', 'No Level Prerequired', 'BAC']

list_of_durations = [''] +['2 months', '3 months', '4 months', '6 months']

LOGGER.info("Setup Done")

