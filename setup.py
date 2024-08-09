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

list_of_locations = [''] + ['Aachen', 'Aalen', 'Aarhus', 'Aix-en-Provence', 'Albstadt', 'Amiens', 'Amsterdam', 'Annecy', 'Antwerp', 'Augsburg', 'Avranches', 'Bad Homburg', 'Bad Neustadt an der Saale', 'Barberà del Vallès', 'Barcelona', 'Beijing', 'Berlin', 'Bertrange', 'Bielefeld', 'Biot', 'Bobigny', 'Bonn', 'Bordeaux', 'Bornheim', 'Botucatu', 'Boulogne-Billancourt', 'Breda', 'Bremen', 'Bretten', 'Breuil-le-Sec', 'Brognard', 'Brussels', 'Buchloe', 'Buchs', 'Böblingen', 'Bühl', 'Cannes', 'Cassis', 'Cayenne', 'Cesson-Sévigné', 'Cham', 'Charenton-le-Pont', "Charmes-sur-l'Herbasse", 'Clamart', 'Clermont-Ferrand', 'Clichy', 'Colmar', 'Cologne', 'Colombes', 'Copenhagen', 'Courbevoie', 'Crailsheim', 'Créteil', 'Dettingen an der Iller', 'Dijon', 'Dingolfing', 'Dortmund', 'Dresden', 'Dudelange', 'Dusseldorf', 'Düsseldorf', 'Eggenstein-Leopoldshafen', 'Eindhoven', 'Eisenach', 'Elchingen', 'Emsbüren', 'Esch-sur-Alzette', 'Eschborn', 'Essen', 'Fleury-Mérogis', 'Fontenay-sous-Bois', 'France', 'Frankfurt', 'Frankfurt am Main', 'Freiburg im Breisgau', 'Freising',
                            'French Guiana', 'Friville-Escarbotin', 'Fulda', 'Garching', 'Gennevilliers', 'Gerlingen', 'Germany', 'Giengen', 'Girona', 'Gonesse', 'Grenoble', 'Grenzach-Wyhlen', 'Guyancourt', 'Gütersloh', 'Halle (Saale)', 'Hamburg', 'Hanover', 'Hauts-de-Seine', 'Heidenheim', 'Heilbronn', 'Heringsdorf', 'Holzgerlingen', 'Isigny-sur-Mer', 'Issy-les-Moulineaux', 'Italy', 'Japan', 'Jena', 'Karlsruhe', 'Kempten', 'Kiel', 'Korbach', 'Kreuzlingen', 'Kufstein', 'Kusterdingen', 'La Balme-les-Grottes', 'Langgöns', 'Laval', 'Le Kremlin-Bicêtre', 'Le Pré-Saint-Gervais', 'Leiden', 'Leinfelden-Echterdingen', 'Leipzig', 'Les Herbiers', 'Leutkirch im Allgäu', 'Levallois-Perret', 'Lille', 'Limbach-Oberfrohna', 'Limoges', 'Lisbon', 'Lohr a. Main', 'London', 'Ludwigshafen', 'Lussemburgo', 'Luxembourg', 'Lyngby', 'Lyon', 'Madrid', 'Magstadt', 'Mainz', 'Mannheim', 'Marchamalo', 'Marcoussis', 'Marsaz', 'Marseille', 'Martigues', 'Massy', 'Matoury', 'Melsungen', 'Metz', 'Metzingen', 'Mexico', 'Milan', 'Mogliano Veneto', 'Monaco', 'Mondeville', 'Monheim am Rhein', 
                            'Montrouge', 'Munich', 'Murrhardt', 'Möglingen', 'Münster', 'Nanterre', 'Nantes', 'Neuilly-sur-Seine', 'Nice', 'Nidderau', 'Nogent-sur-Marne', 'Nogent-sur-Seine', 'Nuremberg', 'Oberkochen', 'Odense', 'Orleans', 'Pantin', 'Paris', 'Parma', 'Pau', 'Plochingen', 'Poissy', 'Prague', 'Puch bei Hallein', 'Pulnoy', 'Puteaux', 'Radeberg', 'Radolfzell am Bodensee', 'Ramillies', 'Ravensburg', 'Regensburg', 'Rennes', 'Reutlingen', 'Roissy-en-France', 'Rome', 'Rungis', 'Saarbrücken', 'Saint-Etienne', 'Saint-Laurent-Blangy', 'Saint-Maur-des-Fossés', 'Saint-Ouen-sur-Seine', 'Salzburg', 'Salzgitter', 'Schwalbach am Taunus', 'Schwarzheide', 'Sihlbrugg', 'Singapore', 'Sosnowiec', 'Stockport', 'Strasbourg', 'Stuttgart', 'Suresnes', 'Szczecin', 'Teltow', 'Thailand', 'Toulouse', 'Traunreut', 'Trieste', 'Uhingen', 'Ulm', 'União das freguesias de Carnaxide e Queijas', 'Unterföhring', 'Vanves', 'Verberie', 'Verona', 'Vert-le-Grand', 'Vienna', "Villeneuve-d'Ascq", 'Vimercate', 'Vitry-sur-Seine', 'Walldorf', 'Wambrechies', 'Warsaw', 'Weil am Rhein', 'Wiener Neudorf', 'Würzburg', 'Zaventem', 'Zürich', 's-Hertogenbosch', 'Évry-Courcouronnes', 'Świebodzin']

list_of_category = [''] +['Actuarial', 'Admin', 'Agronomy & Biology', 'Asset Management', 'Audit', 'Chemistry & Processes', 'Civil Engineering & Structures', 'Communication, PR & Events', 'Construction', 'Corporate Finance', 'Corporate law', 'Customer service', 'Design & Creative', 'Economics', 'Education & Training', 'Electronics & Signal Processing', 'Energy, Materials & Mechanical engineering', 'Environment & Sustainable Development', 'Financial Services', 'Human Resources', 'IT Project, Data & Product Management', 'Industrial Design & Engineering', 'Infrastructures, Networks & Telecom', 'Journalism & Publishing', 'Logistics & Supply Chain', 'Management Control and Accounting', 'Management, Consulting & Strategy', 'Marketing & Webmarketing', 'Media', 'Paramedical & Care', 'Production & Operations', 'Programming', 'Purchasing', 'Quality & Maintenance', 'Sales & Business Development', 'Security & Politics', 'Social Law', 'Statistics, Data Analytics & Applied Maths', 'Tax law', 'Tourism, Hospitality & Food services', 'Web Design & Usability']

list_of_education = [''] +['BAC +5', 'nan', 'BAC +3', 'BAC +2', 'No Level Prerequired', 'BAC']

list_of_durations = [''] +['2 months', '3 months', '4 months', '6 months']

predefined_cvs = {
    "ADE CV": {
        "summary": {
            "email": "ade.n.dewantoro@student.uns.ac.id",
            "location": "Surakarta, Indonesia",
            "name": "Ade Nugroho Dewantoro (Mr)",
            "phone": "+6287855090955",
            "summary": "An quick learner and enthusiastic Mechanical Engineer with experience in practical, analysis and research. Experienced in numerical studies and developing a new way of learning in engineering field, that combine Finite Element Method and Experiential Learning. Currently study meshless Radial Basis Function method and domain decomposition to simulate a natural convection in the annular surface."
        },
        "work_experience": [
            {
                "company_name": "LPPKS",
                "date": "06/2019 — 12/2019",
                "description": [
                    "Communicated with department of education, assessor, and LPPKS",
                    "Prepared assessment instrument for the event",
                    "Ensured every event that assigned ran according to the standard established by the Ministry of Education Republic Indonesia",
                    "Assigned to different regions: Riau, Aceh Jaya, Pelembang, Sumba Island, Bojonegoro, and Surakarta"
                ],
                "job_title": "Freelance Staff"
            }
        ],
        "education": [
            {
                "date": "09/2015 — 07/2019",
                "degree_major": "Bachelor of Education in Mechanical Engineering from Departement of Vocational Education, with major in Automotive Engineering and Energy Conversion",
                "description": [],
                "school_name": "Sebelas Maret University, Indonesia",
                "score": "4-year scholarship (Bidik Misi) from Ministry of Research, Technology and Higer Education, Republic Indonesia"
            },
            {
                "date": "09/2020 — Present",
                "degree_major": "Master's degree in Mechanical Engineering from Postgraduate Departement, with major in Energy Conversion",
                "description": [],
                "school_name": "Sebelas Maret University, Indonesia",
                "score": "2-year scholarship from Sebelas Maret University"
            }
        ],
        "project": [
            {
                "date": "2017",
                "description": "Analyzed the comparative variation of the composition of palm waste and coconut shells to find the highest calorific value as an indicator of new energy that can achieve SDGS 2030. Responsible for preparing the sample with the variation composition.",
                "project_name": "Refuse Derifed Fuel Project 2017"
            },
            {
                "date": "2019",
                "description": "Focused on providing a new way of learning in engineering field by combining Experiential Learning and Finite Element Method. Established a new learning options for turbine engineering courses.",
                "project_name": "Final Year Project 2019"
            },
            {
                "date": "2020",
                "description": "Research for modeling natural convection in the annular pipe using Radial Basis Function. Project is in progress.",
                "project_name": "Master Project 2020"
            }
        ],
        "skills": [
            "Solidworks: Able to create 2D and 3D design",
            "Ansys: Able to simulate an airfoil for wind turbine use using the finite element method",
            "Matlab: Able to make an algorithm and coding a program to simulate simple engineering problems using matlab software"
        ]
    },
    "Joseph CV": {
        "summary": {
            "email": "josephdiva2@gmail.com",
            "location": "",
            "name": "Josephine Diva",
            "phone": "089618587103",
            "summary": "My name is Josephine, and I am passionate about artificial intelligence (AI) and software development. With two years of experience in software development using Java, as well as nearly a year of experience with Python, I have been involved in various projects ranging from desktop applications to machine learning algorithm implementations. I believe that AI has great potential to change the world, and I am committed to continuously expanding my knowledge and skills in this field to create innovative and empowering technological solutions."
        },
        "work_experience": [
            {
                "company_name": "ID/X Partners x Rakamin Academy",
                "date": "Oct 2023 - Nov 2023",
                "description": [
                    "During the execution of the Project Based Internship program, I had the opportunity to gain insights into the role of a Data Engineer at ID/X Partners. I also learned how to solve problems and work on projects aligned with the activities of ID/X Partners."
                ],
                "job_title": "Data Engineer Intern"
            },
            {
                "company_name": "Bangkit Academy led by Google, Tokopedia, Gojek, & Traveloka",
                "date": "Feb 2023 - Jul 2023",
                "description": [
                    "Bangkit is offered as a Kampus Merdeka’s Studi Independen Bersertifikat program supported by the Ministry of Education, Culture, Research and Technology of the Republic of Indonesia. Throughout 2 (two) semesters, we are enrolling at minimum 9,000 university students across 3 learning paths to help them grow in-demand skills in tech and prepare them to take Google’s certification."
                ],
                "job_title": "Machine Learning Cohort"
            }
        ],
        "education": [
            {
                "date": "Aug 2020 - Dec 2024",
                "degree_major": "Bachelor's Degree in Informatics",
                "description": [],
                "school_name": "Sanata Dharma University",
                "score": ""
            }
        ],
        "project": [],
        "skills": [
            "Computer Vision",
            "Natural Language Processing (NLP)",
            "Convolutional Neural Networks (CNN)",
            "Golang Fundamental",
            "SQL Basic",
            "SQL Operation",
            "OLAP Data Modeling",
            "ETL & ELT",
            "Data Warehouse Scheduling",
            "Data Warehouse Management"
        ]
    }
}

LOGGER.info("Setup Done")

