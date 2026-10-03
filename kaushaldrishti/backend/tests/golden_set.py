"""
Golden Test Set for Taxonomy Matcher & Geography Resolver.
Contains 64 test cases across Latin, Devanagari, Kannada, and Tamil.
"""

GOLDEN_TAXONOMY_CASES = [
    # ─── English (Latin) Automotive (8) ──────────────────────────────────
    ("EV Service Technician", "EV Service Technician", "Automotive"),
    ("Electric Vehicle Maintenance Specialist", "EV Service Technician", "Automotive"),
    ("Auto Mechanic for 4-wheeler workshop", "Motor Vehicle Mechanic", "Automotive"),
    ("Automobile Denter and Panel Beater", "Auto Body Repair Technician", "Automotive"),
    ("Auto Electrician with wiring experience", "Auto Electrician", "Automotive"),
    ("Bike Repair Technician / Two Wheeler", "Two Wheeler Service Technician", "Automotive"),
    ("CNC Milling Machine Operator", "CNC Machining Technician", "Automotive"),
    ("Spray Painter for Car Workshop", "Vehicle Painter", "Automotive"),

    # ─── English (Latin) Healthcare (8) ──────────────────────────────────
    ("General Duty Assistant at District Hospital", "General Duty Assistant", "Healthcare"),
    ("Nursing Assistant / Ward Care", "General Duty Assistant", "Healthcare"),
    ("Staff Nurse ICU Junior", "Nursing Associate", "Healthcare"),
    ("Blood Sample Collector / Phlebotomist", "Phlebotomist", "Healthcare"),
    ("Elder Care Home Health Aide", "Home Health Aide", "Healthcare"),
    ("Medical Lab Technician Pathology", "Medical Laboratory Technician", "Healthcare"),
    ("Emergency Medical Technician Paramedic", "Emergency Medical Technician", "Healthcare"),
    ("Dialysis Unit Technician", "Dialysis Technician", "Healthcare"),

    # ─── English (Latin) Electronics & Hardware (8) ──────────────────────
    ("Electronics Repair Mechanic", "Electronics Mechanic", "Electronics and Hardware"),
    ("SMT Line Machine Operator", "SMT Operator", "Electronics and Hardware"),
    ("CCTV Installation & Surveillance Tech", "CCTV Installation Technician", "Electronics and Hardware"),
    ("Mobile Phone Hardware Repairer", "Mobile Phone Repair Technician", "Electronics and Hardware"),
    ("Rooftop Solar Panel Installer", "Solar Panel Installation Technician", "Electronics and Hardware"),
    ("Desktop Support Engineer IT Hardware", "Field Technician - Computing", "Electronics and Hardware"),
    ("Domestic Wireman Electrician", "Wireman", "Electronics and Hardware"),
    ("PCB Assembler and Component Soldering", "PCB Assembly Technician", "Electronics and Hardware"),

    # ─── English (Latin) Construction (8) ────────────────────────────────
    ("Building Electrician for residential project", "Electrician (Construction)", "Construction"),
    ("Plumber for sanitary pipe fitting", "Plumber (General)", "Construction"),
    ("Arc and Gas Welder MIG TIG", "Welder (Arc & Gas)", "Construction"),
    ("Mason for brickwork construction", "Mason (General)", "Construction"),
    ("Shuttering Carpenter for concrete slab", "Shuttering Carpenter", "Construction"),
    ("Bar Bender and Rebar Steel Fixer", "Bar Bender & Steel Fixer", "Construction"),
    ("Construction Site Supervisor / Foreman", "Construction Site Supervisor", "Construction"),
    ("Staging Scaffolder for high-rise", "Scaffolder", "Construction"),

    # ─── English (Latin) Logistics (8) ───────────────────────────────────
    ("Warehouse Picker and Packer Associate", "Warehouse Associate", "Logistics and Supply Chain"),
    ("Forklift Operator Heavy MHE", "Forklift Operator", "Logistics and Supply Chain"),
    ("Last-Mile Delivery Boy / Courier Rider", "Last-Mile Delivery Executive", "Logistics and Supply Chain"),
    ("Cargo Loader and Freight Handler", "Freight Handler", "Logistics and Supply Chain"),
    ("Inventory Stock Controller Clerk", "Inventory Clerk", "Logistics and Supply Chain"),
    ("Logistics Dispatch Supply Chain Assistant", "Supply Chain Assistant", "Logistics and Supply Chain"),
    ("Cold Storage Refrigeration Tech", "Cold Chain Technician", "Logistics and Supply Chain"),
    ("Express Parcel Delivery Agent", "Courier Delivery Executive", "Logistics and Supply Chain"),

    # ─── Hindi (Devanagari) (8) ──────────────────────────────────────────
    ("ईवी सर्विस तकनीशियन", "EV Service Technician", "Automotive"),
    ("मोटर वाहन मैकेनिक वर्कशॉप", "Motor Vehicle Mechanic", "Automotive"),
    ("जीडीए मरीज देखभाल सहायक", "General Duty Assistant", "Healthcare"),
    ("मोबाइल फोन रिपेयर तकनीशियन", "Mobile Phone Repair Technician", "Electronics and Hardware"),
    ("सोलर पैनल स्थापना तकनीशियन", "Solar Panel Installation Technician", "Electronics and Hardware"),
    ("भवन इलेक्ट्रीशियन", "Electrician (Construction)", "Construction"),
    ("नलसाज प्लंबर", "Plumber (General)", "Construction"),
    ("राजमिस्त्री निर्माण कार्य", "Mason (General)", "Construction"),

    # ─── Kannada (8) ─────────────────────────────────────────────────────
    ("ಇವಿ ತಂತ್ರಜ್ಞ", "EV Service Technician", "Automotive"),
    ("ಮೋಟಾರ್ ವಾಹನ ಮೆಕ್ಯಾನಿಕ್", "Motor Vehicle Mechanic", "Automotive"),
    ("ಸಾಮಾನ್ಯ ಕರ್ತವ್ಯ ಸಹಾಯಕ ಆಸ್ಪತ್ರೆ", "General Duty Assistant", "Healthcare"),
    ("ವಿದ್ಯುತ್ ತಂತ್ರಜ್ಞ ನಿರ್ಮಾಣ", "Electrician (Construction)", "Construction"),
    ("ಪ್ಲಂಬರ್ ಪೈಪ್ ಫಿಟ್ಟಿಂಗ್", "Plumber (General)", "Construction"),
    ("ಮೇಸ್ತ್ರಿ ಗಾರೆ ಕೆಲಸ", "Mason (General)", "Construction"),
    ("ಗೋದಾಮು ಸಹಾಯಕ ಪ್ಯಾಕರ್", "Warehouse Associate", "Logistics and Supply Chain"),
    ("ಮೊಬೈಲ್ ರಿಪೇರಿ ತಂತ್ರಜ್ಞ", "Mobile Phone Repair Technician", "Electronics and Hardware"),

    # ─── Tamil (8) ───────────────────────────────────────────────────────
    ("மின்சார வாகன மெக்கானிக்", "EV Service Technician", "Automotive"),
    ("வாகன பழுதுபார்ப்பவர்", "Motor Vehicle Mechanic", "Automotive"),
    ("பொது கடமை உதவியாளர் மருத்துவமனை", "General Duty Assistant", "Healthcare"),
    ("மின் பணியாளர் கட்டுமான பணி", "Electrician (Construction)", "Construction"),
    ("குழாய் பொருத்துநர் பிளம்பர்", "Plumber (General)", "Construction"),
    ("கொத்தனார் கட்டட வேலை", "Mason (General)", "Construction"),
    ("கிடங்கு உதவியாளர்", "Warehouse Associate", "Logistics and Supply Chain"),
    ("கைப்பேசி பழுதுபார்க்கும் தொழில்நுட்ப வல்லுநர்", "Mobile Phone Repair Technician", "Electronics and Hardware"),
]

GOLDEN_GEO_CASES = [
    # Bangalore variations
    ("Bangalore", "Bengaluru Urban"),
    ("Bengaluru", "Bengaluru Urban"),
    ("Bangalore Urban", "Bengaluru Urban"),
    ("Bangalore Rural", "Bengaluru Rural"),
    ("Mysore", "Mysuru"),
    ("Belgaum", "Belagavi"),
    ("Hubli", "Dharwad"),
    ("Mangalore", "Dakshina Kannada"),
    # Tamil Nadu variations
    ("Madras", "Chennai"),
    ("Chennai", "Chennai"),
    ("Coimbatore", "Coimbatore"),
    ("Trichy", "Tiruchirappalli"),
    ("Salem", "Salem"),
    ("Madurai", "Madurai"),
    ("Tuticorin", "Thoothukudi"),
    # UP variations
    ("Allahabad", "Prayagraj"),
    ("Prayagraj", "Prayagraj"),
    ("Banaras", "Varanasi"),
    ("Kashi", "Varanasi"),
    ("Noida", "Gautam Buddha Nagar"),
    ("Greater Noida", "Gautam Buddha Nagar"),
    ("Kanpur", "Kanpur Nagar"),
    ("Lucknow", "Lucknow"),
    ("Faizabad", "Ayodhya"),
    ("Agra", "Agra"),
]
