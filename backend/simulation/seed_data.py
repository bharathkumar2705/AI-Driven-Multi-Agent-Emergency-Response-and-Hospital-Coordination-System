"""
Deterministic seed data for the city simulation.
Fixed positions ensure reproducible demos.
"""

# Hospital positions on 10x10 grid
HOSPITALS = [
    {
        "hospital_id": "H1", "name": "City General Hospital",
        "location": {"row": 1, "col": 4},
        "total_beds": 50, "available_beds": 30,
        "icu_total": 10, "icu_available": 6,
        "emergency_capacity": 15, "emergency_used": 3,
        "available_specialists": ["Cardiologist", "Neurologist", "General Surgeon"],
        "status": "OPERATIONAL"
    },
    {
        "hospital_id": "H2", "name": "North Memorial Medical",
        "location": {"row": 1, "col": 8},
        "total_beds": 40, "available_beds": 22,
        "icu_total": 8, "icu_available": 4,
        "emergency_capacity": 12, "emergency_used": 5,
        "available_specialists": ["Cardiologist", "Orthopedic", "Pediatrician"],
        "status": "OPERATIONAL"
    },
    {
        "hospital_id": "H3", "name": "Central Medical Center",
        "location": {"row": 5, "col": 2},
        "total_beds": 60, "available_beds": 40,
        "icu_total": 12, "icu_available": 8,
        "emergency_capacity": 20, "emergency_used": 2,
        "available_specialists": ["Neurologist", "Oncologist", "General Surgeon"],
        "status": "OPERATIONAL"
    },
    {
        "hospital_id": "H4", "name": "Eastern Regional Hospital",
        "location": {"row": 5, "col": 8},
        "total_beds": 35, "available_beds": 18,
        "icu_total": 6, "icu_available": 3,
        "emergency_capacity": 10, "emergency_used": 4,
        "available_specialists": ["Cardiologist", "Neurologist"],
        "status": "OPERATIONAL"
    },
    {
        "hospital_id": "H5", "name": "South General Hospital",
        "location": {"row": 8, "col": 3},
        "total_beds": 45, "available_beds": 28,
        "icu_total": 9, "icu_available": 5,
        "emergency_capacity": 14, "emergency_used": 1,
        "available_specialists": ["Cardiologist", "Orthopedic", "General Surgeon"],
        "status": "OPERATIONAL"
    },
    {
        "hospital_id": "H6", "name": "Westside Trauma Center",
        "location": {"row": 8, "col": 7},
        "total_beds": 30, "available_beds": 12,
        "icu_total": 5, "icu_available": 2,
        "emergency_capacity": 8, "emergency_used": 6,
        "available_specialists": ["General Surgeon", "Orthopedic"],
        "status": "OPERATIONAL"
    }
]

# Ambulance starting positions (depots)
AMBULANCES = [
    {"ambulance_id": "A1", "current_location": {"row": 0, "col": 0}, "capacity": 1, "priority": 3},
    {"ambulance_id": "A2", "current_location": {"row": 0, "col": 9}, "capacity": 1, "priority": 2},
    {"ambulance_id": "A3", "current_location": {"row": 4, "col": 5}, "capacity": 1, "priority": 1},
    {"ambulance_id": "A4", "current_location": {"row": 9, "col": 0}, "capacity": 1, "priority": 2},
    {"ambulance_id": "A5", "current_location": {"row": 9, "col": 9}, "capacity": 1, "priority": 1},
    {"ambulance_id": "A6", "current_location": {"row": 2, "col": 6}, "capacity": 1, "priority": 2},
    {"ambulance_id": "A7", "current_location": {"row": 7, "col": 2}, "capacity": 1, "priority": 1},
    {"ambulance_id": "A8", "current_location": {"row": 6, "col": 8}, "capacity": 1, "priority": 1},
]

# Doctors distributed across hospitals
DOCTORS = [
    {"doctor_id": "D01", "name": "Dr. Sarah Chen", "specialization": "Cardiologist", "hospital_id": "H1", "availability": True},
    {"doctor_id": "D02", "name": "Dr. James Miller", "specialization": "Neurologist", "hospital_id": "H1", "availability": True},
    {"doctor_id": "D03", "name": "Dr. Emily Park", "specialization": "General Surgeon", "hospital_id": "H1", "availability": True},
    {"doctor_id": "D04", "name": "Dr. Michael Brown", "specialization": "Cardiologist", "hospital_id": "H2", "availability": True},
    {"doctor_id": "D05", "name": "Dr. Lisa Johnson", "specialization": "Orthopedic", "hospital_id": "H2", "availability": True},
    {"doctor_id": "D06", "name": "Dr. Robert Davis", "specialization": "Pediatrician", "hospital_id": "H2", "availability": True},
    {"doctor_id": "D07", "name": "Dr. Anna Martinez", "specialization": "Neurologist", "hospital_id": "H3", "availability": True},
    {"doctor_id": "D08", "name": "Dr. Kevin Wilson", "specialization": "Oncologist", "hospital_id": "H3", "availability": True},
    {"doctor_id": "D09", "name": "Dr. Jennifer Lee", "specialization": "General Surgeon", "hospital_id": "H3", "availability": True},
    {"doctor_id": "D10", "name": "Dr. David Taylor", "specialization": "Cardiologist", "hospital_id": "H4", "availability": True},
    {"doctor_id": "D11", "name": "Dr. Susan White", "specialization": "Neurologist", "hospital_id": "H4", "availability": True},
    {"doctor_id": "D12", "name": "Dr. Thomas Anderson", "specialization": "Cardiologist", "hospital_id": "H5", "availability": True},
    {"doctor_id": "D13", "name": "Dr. Patricia Moore", "specialization": "Orthopedic", "hospital_id": "H5", "availability": True},
    {"doctor_id": "D14", "name": "Dr. Christopher Jackson", "specialization": "General Surgeon", "hospital_id": "H5", "availability": True},
    {"doctor_id": "D15", "name": "Dr. Margaret Harris", "specialization": "General Surgeon", "hospital_id": "H6", "availability": True},
    {"doctor_id": "D16", "name": "Dr. Daniel Thompson", "specialization": "Orthopedic", "hospital_id": "H6", "availability": True},
]

# Pre-defined scenario patients
SCENARIO_PATIENTS = {
    "scenario_1": [
        {
            "patient_id": "P001", "name": "John Smith",
            "location": {"row": 3, "col": 3},
            "emergency_type": "Cardiac Arrest",
            "severity": "CRITICAL",
            "required_specialist": "Cardiologist",
            "required_resources": ["ICU"],
            "status": "WAITING"
        }
    ],
    "scenario_2": [
        {
            "patient_id": "P001", "name": "John Smith",
            "location": {"row": 2, "col": 2},
            "emergency_type": "Cardiac Arrest",
            "severity": "CRITICAL",
            "required_specialist": "Cardiologist",
            "required_resources": ["ICU"],
            "status": "WAITING"
        },
        {
            "patient_id": "P002", "name": "Maria Garcia",
            "location": {"row": 7, "col": 7},
            "emergency_type": "Stroke",
            "severity": "HIGH",
            "required_specialist": "Neurologist",
            "required_resources": ["ICU"],
            "status": "WAITING"
        },
        {
            "patient_id": "P003", "name": "Robert Lee",
            "location": {"row": 5, "col": 5},
            "emergency_type": "Fracture",
            "severity": "MODERATE",
            "required_specialist": "Orthopedic",
            "required_resources": [],
            "status": "WAITING"
        }
    ],
    "scenario_3": [
        {
            "patient_id": "P001", "name": "Alice Johnson",
            "location": {"row": 4, "col": 4},
            "emergency_type": "Cardiac Arrest",
            "severity": "CRITICAL",
            "required_specialist": "Cardiologist",
            "required_resources": ["ICU"],
            "status": "WAITING"
        }
    ],
    "scenario_4": [
        {
            "patient_id": "P001", "name": "Bob Wilson",
            "location": {"row": 3, "col": 6},
            "emergency_type": "Trauma",
            "severity": "HIGH",
            "required_specialist": "General Surgeon",
            "required_resources": [],
            "status": "WAITING"
        }
    ],
    "scenario_5": [
        {
            "patient_id": "P001", "name": "Carol Davis",
            "location": {"row": 6, "col": 3},
            "emergency_type": "Stroke",
            "severity": "CRITICAL",
            "required_specialist": "Neurologist",
            "required_resources": ["ICU"],
            "status": "WAITING"
        }
    ],
    "scenario_6": [
        {
            "patient_id": "P001", "name": "David Brown",
            "location": {"row": 2, "col": 5},
            "emergency_type": "Cardiac Arrest",
            "severity": "CRITICAL",
            "required_specialist": "Cardiologist",
            "required_resources": ["ICU"],
            "status": "WAITING"
        },
        {
            "patient_id": "P002", "name": "Eve Taylor",
            "location": {"row": 2, "col": 4},
            "emergency_type": "Stroke",
            "severity": "HIGH",
            "required_specialist": "Neurologist",
            "required_resources": [],
            "status": "WAITING"
        }
    ],
    "scenario_7": [
        {
            "patient_id": "P001", "name": "Frank Martin",
            "location": {"row": 4, "col": 4},
            "emergency_type": "Cardiac Arrest",
            "severity": "CRITICAL",
            "required_specialist": "Cardiologist",
            "required_resources": ["ICU"],
            "status": "WAITING"
        }
    ]
}

SCENARIO_DESCRIPTIONS = {
    "scenario_1": {
        "name": "Single Emergency",
        "description": "One critical cardiac patient requires ICU and Cardiologist. Basic planning and hospital selection.",
        "difficulty": "Basic"
    },
    "scenario_2": {
        "name": "Multiple Simultaneous Emergencies",
        "description": "Three patients with different severity levels arrive simultaneously. Tests resource prioritization.",
        "difficulty": "Intermediate"
    },
    "scenario_3": {
        "name": "Hospital ICU Failure",
        "description": "Critical patient is en route when selected hospital's ICU becomes full. Tests replanning.",
        "difficulty": "Advanced",
        "auto_events": [{"type": "HOSPITAL_ICU_FULL", "hospital_id": "H1", "delay_ticks": 5}]
    },
    "scenario_4": {
        "name": "Traffic Congestion",
        "description": "Patient emergency with major traffic congestion on optimal route. Tests alternative routing.",
        "difficulty": "Intermediate",
        "auto_events": [{"type": "ROAD_CONGESTED", "road_id": "R045", "delay_ticks": 3}]
    },
    "scenario_5": {
        "name": "Doctor Unavailable",
        "description": "Required neurologist becomes unavailable mid-transport. Tests doctor assignment replanning.",
        "difficulty": "Advanced",
        "auto_events": [{"type": "DOCTOR_UNAVAILABLE", "doctor_id": "D07", "delay_ticks": 6}]
    },
    "scenario_6": {
        "name": "Two Ambulance Conflict",
        "description": "Two ambulances attempt the same route simultaneously. Tests conflict detection and resolution.",
        "difficulty": "Advanced"
    },
    "scenario_7": {
        "name": "Multiple Dynamic Events",
        "description": "Critical patient + ICU failure + traffic + doctor unavailability all occur. Full system stress test.",
        "difficulty": "Expert",
        "auto_events": [
            {"type": "ROAD_CONGESTED", "road_id": "R045", "delay_ticks": 4},
            {"type": "HOSPITAL_ICU_FULL", "hospital_id": "H1", "delay_ticks": 6},
            {"type": "DOCTOR_UNAVAILABLE", "doctor_id": "D01", "delay_ticks": 8}
        ]
    }
}
