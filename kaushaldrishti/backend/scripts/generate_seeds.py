"""
Generates reference CSV datasets:
- data/reference/lgd_districts.csv (144 districts across KA, TN, UP)
- data/reference/trades_master.csv (40 trades across 5 sectors)
- data/reference/glossary.csv (Multilingual translations)
"""

import csv
import os

REFERENCE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "reference")
os.makedirs(REFERENCE_DIR, exist_ok=True)

# 1. Pilot Districts (31 in KA, 38 in TN, 75 in UP = 144)
DISTRICTS = [
    # Karnataka (31)
    ("KA", "Karnataka", "2901", "Bengaluru Urban", 9500000, "urban"),
    ("KA", "Karnataka", "2902", "Bengaluru Rural", 800000, "rural"),
    ("KA", "Karnataka", "2903", "Mysuru", 2400000, "urban"),
    ("KA", "Karnataka", "2904", "Belagavi", 3600000, "rural"),
    ("KA", "Karnataka", "2905", "Dharwad", 1400000, "urban"),
    ("KA", "Karnataka", "2906", "Dakshina Kannada", 1700000, "urban"),
    ("KA", "Karnataka", "2907", "Tumakuru", 2100000, "rural"),
    ("KA", "Karnataka", "2908", "Shivamogga", 1400000, "rural"),
    ("KA", "Karnataka", "2909", "Ballari", 1900000, "rural"),
    ("KA", "Karnataka", "2910", "Kalaburagi", 2000000, "aspirational"),
    ("KA", "Karnataka", "2911", "Vijayapura", 1700000, "rural"),
    ("KA", "Karnataka", "2912", "Davanagere", 1500000, "rural"),
    ("KA", "Karnataka", "2913", "Udupi", 950000, "urban"),
    ("KA", "Karnataka", "2914", "Hassan", 1400000, "rural"),
    ("KA", "Karnataka", "2915", "Mandya", 1450000, "rural"),
    ("KA", "Karnataka", "2916", "Chikkamagaluru", 900000, "rural"),
    ("KA", "Karnataka", "2917", "Bagalkote", 1500000, "rural"),
    ("KA", "Karnataka", "2918", "Bidar", 1350000, "aspirational"),
    ("KA", "Karnataka", "2919", "Chamarajanagar", 820000, "rural"),
    ("KA", "Karnataka", "2920", "Chikkaballapura", 1000000, "rural"),
    ("KA", "Karnataka", "2921", "Chitradurga", 1300000, "rural"),
    ("KA", "Karnataka", "2922", "Gadag", 850000, "rural"),
    ("KA", "Karnataka", "2923", "Haveri", 1300000, "rural"),
    ("KA", "Karnataka", "2924", "Kodagu", 450000, "rural"),
    ("KA", "Karnataka", "2925", "Kolar", 1250000, "rural"),
    ("KA", "Karnataka", "2926", "Koppal", 1150000, "aspirational"),
    ("KA", "Karnataka", "2927", "Raichur", 1550000, "aspirational"),
    ("KA", "Karnataka", "2928", "Ramanagara", 900000, "rural"),
    ("KA", "Karnataka", "2929", "Uttara Kannada", 1150000, "rural"),
    ("KA", "Karnataka", "2930", "Yadgir", 950000, "aspirational"),
    ("KA", "Karnataka", "2931", "Vijayanagara", 1100000, "rural"),

    # Tamil Nadu (38)
    ("TN", "Tamil Nadu", "3301", "Chennai", 6800000, "urban"),
    ("TN", "Tamil Nadu", "3302", "Coimbatore", 2900000, "urban"),
    ("TN", "Tamil Nadu", "3303", "Madurai", 2400000, "urban"),
    ("TN", "Tamil Nadu", "3304", "Tiruchirappalli", 2100000, "urban"),
    ("TN", "Tamil Nadu", "3305", "Salem", 2800000, "urban"),
    ("TN", "Tamil Nadu", "3306", "Tirunelveli", 1400000, "rural"),
    ("TN", "Tamil Nadu", "3307", "Tiruppur", 2000000, "urban"),
    ("TN", "Tamil Nadu", "3308", "Erode", 1850000, "rural"),
    ("TN", "Tamil Nadu", "3309", "Vellore", 1300000, "urban"),
    ("TN", "Tamil Nadu", "3310", "Thoothukudi", 1400000, "rural"),
    ("TN", "Tamil Nadu", "3311", "Dindigul", 1750000, "rural"),
    ("TN", "Tamil Nadu", "3312", "Thanjavur", 1900000, "rural"),
    ("TN", "Tamil Nadu", "3313", "Ranipet", 1000000, "rural"),
    ("TN", "Tamil Nadu", "3314", "Sivaganga", 1100000, "rural"),
    ("TN", "Tamil Nadu", "3315", "Virudhunagar", 1600000, "aspirational"),
    ("TN", "Tamil Nadu", "3316", "Kanchipuram", 1150000, "urban"),
    ("TN", "Tamil Nadu", "3317", "Chengalpattu", 2100000, "urban"),
    ("TN", "Tamil Nadu", "3318", "Cuddalore", 2100000, "rural"),
    ("TN", "Tamil Nadu", "3319", "Dharmapuri", 1250000, "rural"),
    ("TN", "Tamil Nadu", "3320", "Kallakurichi", 1100000, "rural"),
    ("TN", "Tamil Nadu", "3321", "Kanyakumari", 1550000, "rural"),
    ("TN", "Tamil Nadu", "3322", "Karur", 850000, "rural"),
    ("TN", "Tamil Nadu", "3323", "Krishnagiri", 1550000, "rural"),
    ("TN", "Tamil Nadu", "3324", "Mayiladuthurai", 750000, "rural"),
    ("TN", "Tamil Nadu", "3325", "Nagapattinam", 600000, "rural"),
    ("TN", "Tamil Nadu", "3326", "Namakkal", 1400000, "rural"),
    ("TN", "Tamil Nadu", "3327", "Nilgiris", 600000, "rural"),
    ("TN", "Tamil Nadu", "3328", "Perambalur", 450000, "rural"),
    ("TN", "Tamil Nadu", "3329", "Pudukkottai", 1300000, "rural"),
    ("TN", "Tamil Nadu", "3330", "Ramanathapuram", 1100000, "aspirational"),
    ("TN", "Tamil Nadu", "3331", "Tenkasi", 1150000, "rural"),
    ("TN", "Tamil Nadu", "3332", "Theni", 1000000, "rural"),
    ("TN", "Tamil Nadu", "3333", "Tirupathur", 950000, "rural"),
    ("TN", "Tamil Nadu", "3334", "Tiruvallur", 3000000, "urban"),
    ("TN", "Tamil Nadu", "3335", "Tiruvannamalai", 1950000, "rural"),
    ("TN", "Tamil Nadu", "3336", "Tiruvarur", 1050000, "rural"),
    ("TN", "Tamil Nadu", "3337", "Viluppuram", 1650000, "rural"),
    ("TN", "Tamil Nadu", "3338", "Ariyalur", 650000, "rural"),

    # Uttar Pradesh (75)
    ("UP", "Uttar Pradesh", "0901", "Lucknow", 4100000, "urban"),
    ("UP", "Uttar Pradesh", "0902", "Kanpur Nagar", 3900000, "urban"),
    ("UP", "Uttar Pradesh", "0903", "Varanasi", 3100000, "urban"),
    ("UP", "Uttar Pradesh", "0904", "Prayagraj", 4900000, "urban"),
    ("UP", "Uttar Pradesh", "0905", "Agra", 3700000, "urban"),
    ("UP", "Uttar Pradesh", "0906", "Meerut", 2900000, "urban"),
    ("UP", "Uttar Pradesh", "0907", "Ghaziabad", 3900000, "urban"),
    ("UP", "Uttar Pradesh", "0908", "Gautam Buddha Nagar", 1800000, "urban"),
    ("UP", "Uttar Pradesh", "0909", "Bareilly", 3650000, "urban"),
    ("UP", "Uttar Pradesh", "0910", "Aligarh", 3050000, "rural"),
    ("UP", "Uttar Pradesh", "0911", "Moradabad", 2550000, "urban"),
    ("UP", "Uttar Pradesh", "0912", "Gorakhpur", 3700000, "urban"),
    ("UP", "Uttar Pradesh", "0913", "Saharanpur", 2850000, "rural"),
    ("UP", "Uttar Pradesh", "0914", "Firozabad", 2050000, "rural"),
    ("UP", "Uttar Pradesh", "0915", "Jhansi", 1650000, "urban"),
    ("UP", "Uttar Pradesh", "0916", "Muzaffarnagar", 2400000, "rural"),
    ("UP", "Uttar Pradesh", "0917", "Mathura", 2100000, "rural"),
    ("UP", "Uttar Pradesh", "0918", "Ayodhya", 2050000, "rural"),
    ("UP", "Uttar Pradesh", "0919", "Rampur", 1900000, "rural"),
    ("UP", "Uttar Pradesh", "0920", "Shahjahanpur", 2500000, "rural"),
    ("UP", "Uttar Pradesh", "0921", "Farrukhabad", 1600000, "rural"),
    ("UP", "Uttar Pradesh", "0922", "Budaun", 2600000, "rural"),
    ("UP", "Uttar Pradesh", "0923", "Mau", 1800000, "rural"),
    ("UP", "Uttar Pradesh", "0924", "Hapur", 1150000, "rural"),
    ("UP", "Uttar Pradesh", "0925", "Etawah", 1300000, "rural"),
    ("UP", "Uttar Pradesh", "0926", "Mirzapur", 2100000, "rural"),
    ("UP", "Uttar Pradesh", "0927", "Sambhal", 1800000, "rural"),
    ("UP", "Uttar Pradesh", "0928", "Amroha", 1550000, "rural"),
    ("UP", "Uttar Pradesh", "0929", "Hardoi", 3300000, "rural"),
    ("UP", "Uttar Pradesh", "0930", "Fatehpur", 2150000, "aspirational"),
    ("UP", "Uttar Pradesh", "0931", "Raebareli", 2800000, "rural"),
    ("UP", "Uttar Pradesh", "0932", "Jalaun", 1400000, "rural"),
    ("UP", "Uttar Pradesh", "0933", "Sitapur", 3650000, "rural"),
    ("UP", "Uttar Pradesh", "0934", "Bahraich", 2850000, "aspirational"),
    ("UP", "Uttar Pradesh", "0935", "Unnao", 2600000, "rural"),
    ("UP", "Uttar Pradesh", "0936", "Jaunpur", 3700000, "rural"),
    ("UP", "Uttar Pradesh", "0937", "Lakhimpur Kheri", 3350000, "rural"),
    ("UP", "Uttar Pradesh", "0938", "Hathras", 1300000, "rural"),
    ("UP", "Uttar Pradesh", "0939", "Banda", 1450000, "rural"),
    ("UP", "Uttar Pradesh", "0940", "Pilibhit", 1700000, "rural"),
    ("UP", "Uttar Pradesh", "0941", "Barabanki", 2700000, "rural"),
    ("UP", "Uttar Pradesh", "0942", "Gonda", 2800000, "rural"),
    ("UP", "Uttar Pradesh", "0943", "Basti", 2050000, "rural"),
    ("UP", "Uttar Pradesh", "0944", "Deoria", 2550000, "rural"),
    ("UP", "Uttar Pradesh", "0945", "Ghazipur", 3000000, "rural"),
    ("UP", "Uttar Pradesh", "0946", "Sultanpur", 1950000, "rural"),
    ("UP", "Uttar Pradesh", "0947", "Azamgarh", 3800000, "rural"),
    ("UP", "Uttar Pradesh", "0948", "Bijnor", 3100000, "rural"),
    ("UP", "Uttar Pradesh", "0949", "Ballia", 2700000, "rural"),
    ("UP", "Uttar Pradesh", "0950", "Bhadohi", 1300000, "rural"),
    ("UP", "Uttar Pradesh", "0951", "Shamli", 1100000, "rural"),
    ("UP", "Uttar Pradesh", "0952", "Kasganj", 1200000, "rural"),
    ("UP", "Uttar Pradesh", "0953", "Amethi", 1550000, "rural"),
    ("UP", "Uttar Pradesh", "0954", "Chandauli", 1600000, "aspirational"),
    ("UP", "Uttar Pradesh", "0955", "Balrampur", 1800000, "aspirational"),
    ("UP", "Uttar Pradesh", "0956", "Siddharthnagar", 2150000, "aspirational"),
    ("UP", "Uttar Pradesh", "0957", "Sonbhadra", 1550000, "aspirational"),
    ("UP", "Uttar Pradesh", "0958", "Kaushambi", 1350000, "rural"),
    ("UP", "Uttar Pradesh", "0959", "Lalitpur", 1000000, "rural"),
    ("UP", "Uttar Pradesh", "0960", "Chitrakoot", 850000, "aspirational"),
    ("UP", "Uttar Pradesh", "0961", "Mahoba", 750000, "rural"),
    ("UP", "Uttar Pradesh", "0962", "Hamirpur", 900000, "rural"),
    ("UP", "Uttar Pradesh", "0963", "Auraiya", 1150000, "rural"),
    ("UP", "Uttar Pradesh", "0964", "Kannauj", 1400000, "rural"),
    ("UP", "Uttar Pradesh", "0965", "Kanpur Dehat", 1500000, "rural"),
    ("UP", "Uttar Pradesh", "0966", "Shravasti", 950000, "aspirational"),
    ("UP", "Uttar Pradesh", "0967", "Maharajganj", 2250000, "rural"),
    ("UP", "Uttar Pradesh", "0968", "Kushinagar", 2950000, "rural"),
    ("UP", "Uttar Pradesh", "0969", "Sant Kabir Nagar", 1450000, "rural"),
    ("UP", "Uttar Pradesh", "0970", "Baghpat", 1100000, "rural"),
    ("UP", "Uttar Pradesh", "0971", "Pratapgarh", 2650000, "rural"),
    ("UP", "Uttar Pradesh", "0972", "Mainpuri", 1550000, "rural"),
    ("UP", "Uttar Pradesh", "0973", "Etah", 1450000, "rural"),
    ("UP", "Uttar Pradesh", "0974", "Balia", 1850000, "rural"),
    ("UP", "Uttar Pradesh", "0975", "Kushinagar Rural", 950000, "rural"),
]

# 2. Priority Sectors & Trades (5 Sectors x 8 Trades = 40)
TRADES = [
    # Automotive (8)
    ("AUTO", "Automotive", "EV Service Technician", "7231.0101", "ASC/Q1402", 4, 6, ["EV Mechanic", "Electric Vehicle Technician", "EV Battery Specialist", "ईवी तकनीशियन", "ಇವಿ ತಂತ್ರಜ್ಞ", "மின்சார வாகன மெக்கானிக்"], ["ev.*tech", "electric.*vehicle", "battery.*service"]),
    ("AUTO", "Automotive", "Motor Vehicle Mechanic", "7231.0100", "ASC/Q1401", 4, 12, ["Auto Mechanic", "Vehicle Mechanic", "Automobile Service Technician", "मोटर वाहन मैकेनिक", "ಮೋಟಾರ್ ವಾಹನ ಮೆಕ್ಯಾನಿಕ್"], ["mechanic.*auto", "vehicle.*repair"]),
    ("AUTO", "Automotive", "Auto Body Repair Technician", "7213.0100", "ASC/Q1410", 3, 6, ["Denter", "Panel Beater", "Body Shop Technician"], ["denting.*painting", "body.*repair"]),
    ("AUTO", "Automotive", "Auto Electrician", "7412.0100", "ASC/Q1408", 4, 6, ["Vehicle Electrician", "Automotive Wiring Specialist"], ["auto.*electrician", "vehicle.*wiring"]),
    ("AUTO", "Automotive", "Two Wheeler Service Technician", "7231.0200", "ASC/Q1411", 3, 6, ["Bike Mechanic", "Two Wheeler Mechanic"], ["bike.*repair", "two.*wheeler"]),
    ("AUTO", "Automotive", "CNC Machining Technician", "7223.0100", "ASC/Q3501", 4, 6, ["CNC Operator", "CNC Milling Specialist"], ["cnc.*operator", "cnc.*machin"]),
    ("AUTO", "Automotive", "Vehicle Painter", "7132.0100", "ASC/Q1412", 3, 6, ["Automotive Painter", "Spray Painter"], ["spray.*paint", "auto.*paint"]),
    ("AUTO", "Automotive", "Quality Control Inspector (Auto)", "7543.0100", "ASC/Q6301", 4, 6, ["Automotive QC", "Vehicle Inspector"], ["quality.*control.*auto", "inspection.*auto"]),

    # Healthcare (8)
    ("HEALTH", "Healthcare", "General Duty Assistant", "5321.0100", "HSS/Q5101", 3, 4, ["GDA", "Nursing Assistant", "Patient Care Assistant", "जीडीए", "ಸಾಮಾನ್ಯ ಕರ್ತವ್ಯ ಸಹಾಯಕ", "பொது கடமை உதவியாளர்"], ["general.*duty", "patient.*care", "nursing.*assistant"]),
    ("HEALTH", "Healthcare", "Nursing Associate", "3221.0100", "HSS/Q5102", 5, 12, ["Staff Nurse", "Junior Nurse", "Clinical Nurse"], ["nursing", "registered.*nurse"]),
    ("HEALTH", "Healthcare", "Phlebotomist", "3212.0100", "HSS/Q0501", 4, 3, ["Blood Collection Technician", "Lab Sample Collector"], ["phlebotom", "blood.*collection"]),
    ("HEALTH", "Healthcare", "Home Health Aide", "5322.0100", "HSS/Q5103", 3, 4, ["Elder Care Assistant", "Home Care Nurse"], ["home.*care", "elder.*care"]),
    ("HEALTH", "Healthcare", "Medical Laboratory Technician", "3212.0200", "HSS/Q0301", 4, 12, ["MLT", "Pathology Lab Technician"], ["lab.*technician", "pathology.*tech"]),
    ("HEALTH", "Healthcare", "Emergency Medical Technician", "3258.0100", "HSS/Q2301", 4, 6, ["EMT", "Ambulance Technician", "Paramedic"], ["paramedic", "emergency.*medical"]),
    ("HEALTH", "Healthcare", "Dialysis Technician", "3211.0100", "HSS/Q2701", 4, 6, ["Renal Dialysis Technician"], ["dialysis"]),
    ("HEALTH", "Healthcare", "Radiology Technician", "3211.0200", "HSS/Q0201", 4, 12, ["X-Ray Technician", "Imaging Technologist"], ["x.*ray", "radiology", "ct.*scan"]),

    # Electronics and Hardware (8)
    ("ELECT", "Electronics and Hardware", "Electronics Mechanic", "7421.0100", "ELE/Q3101", 4, 12, ["Electronics Technician", "Hardware Repairer"], ["electronics.*repair", "circuit.*board"]),
    ("ELECT", "Electronics and Hardware", "SMT Operator", "8212.0100", "ELE/Q0102", 3, 3, ["Surface Mount Operator", "SMD Line Operator"], ["smt.*operator", "surface.*mount"]),
    ("ELECT", "Electronics and Hardware", "CCTV Installation Technician", "7421.0200", "ELE/Q4605", 4, 3, ["Security System Installer", "Surveillance Tech"], ["cctv.*install", "surveillance.*tech"]),
    ("ELECT", "Electronics and Hardware", "Mobile Phone Repair Technician", "7422.0100", "ELE/Q8104", 4, 3, ["Smartphone Repairer", "Mobile Hardware Tech"], ["mobile.*repair", "smartphone.*repair"]),
    ("ELECT", "Electronics and Hardware", "Solar Panel Installation Technician", "7411.0100", "ELE/Q5901", 4, 4, ["Solar PV Installer", "Rooftop Solar Tech"], ["solar.*installer", "solar.*panel"]),
    ("ELECT", "Electronics and Hardware", "Field Technician - Computing", "3511.0100", "ELE/Q4601", 4, 6, ["Desktop Support Engineer", "Hardware Support"], ["desktop.*support", "hardware.*tech"]),
    ("ELECT", "Electronics and Hardware", "Wireman", "7411.0200", "ELE/Q6001", 3, 6, ["Domestic Wireman", "Electrical Fitter"], ["wireman", "wiring.*tech"]),
    ("ELECT", "Electronics and Hardware", "PCB Assembly Technician", "8212.0200", "ELE/Q0101", 3, 3, ["PCB Assembler", "Component Placement Operator"], ["pcb.*assembl", "soldering.*tech"]),

    # Construction (8)
    ("CONST", "Construction", "Electrician (Construction)", "7137.0100", "CON/Q0601", 4, 6, ["Building Electrician", "Site Electrician", "इलेक्ट्रीशियन", "ವಿದ್ಯುತ್ ತಂತ್ರಜ್ಞ", "மின் பணியாளர்"], ["electrician", "electrical.*fitter"]),
    ("CONST", "Construction", "Plumber (General)", "7126.0100", "CON/Q0602", 3, 6, ["Pipe Fitter", "Sanitary Fitter", "प्लंबर", "ಪ್ಲಂಬರ್", "குழாய் பொருத்துநர்"], ["plumber", "pipe.*fitter"]),
    ("CONST", "Construction", "Welder (Arc & Gas)", "7212.0100", "CON/Q0201", 4, 6, ["MIG Welder", "TIG Welder", "Fabricator"], ["welder", "welding.*tech"]),
    ("CONST", "Construction", "Mason (General)", "7112.0100", "CON/Q0101", 3, 6, ["Bricklayer", "Construction Worker", "राजमिस्त्री", "ಮೇಸ್ತ್ರಿ", "கொத்தனார்"], ["mason", "bricklayer"]),
    ("CONST", "Construction", "Shuttering Carpenter", "7115.0100", "CON/Q0301", 3, 6, ["Formwork Carpenter", "Centering Worker"], ["carpenter", "shuttering"]),
    ("CONST", "Construction", "Bar Bender & Steel Fixer", "7214.0100", "CON/Q0203", 3, 3, ["Rebar Worker", "Steel Fixer"], ["bar.*bender", "steel.*fixer"]),
    ("CONST", "Construction", "Construction Site Supervisor", "3123.0100", "CON/Q0701", 5, 12, ["Site Incharge", "Foreman"], ["site.*supervisor", "construction.*foreman"]),
    ("CONST", "Construction", "Scaffolder", "7119.0100", "CON/Q0303", 3, 3, ["Staging Erector", "Scaffolding Technician"], ["scaffold"]),

    # Logistics and Supply Chain (8)
    ("LOGIS", "Logistics and Supply Chain", "Warehouse Associate", "4321.0100", "LSC/Q0101", 3, 3, ["Warehouse Picker", "Stock Assistant", "गोदाम सहायक", "ಗೋದಾಮು ಸಹಾಯಕ", "கிடங்கு உதவியாளர்"], ["warehouse.*associate", "picker.*packer"]),
    ("LOGIS", "Logistics and Supply Chain", "Forklift Operator", "8344.0100", "LSC/Q0107", 4, 3, ["Reach Truck Driver", "MHE Operator"], ["forklift", "mhe.*operator"]),
    ("LOGIS", "Logistics and Supply Chain", "Last-Mile Delivery Executive", "8321.0100", "LSC/Q0301", 3, 2, ["Delivery Boy", "Rider", "Courier Executive"], ["delivery.*boy", "delivery.*rider", "courier"]),
    ("LOGIS", "Logistics and Supply Chain", "Freight Handler", "9333.0100", "LSC/Q0104", 2, 2, ["Loader Unloader", "Cargo Handler"], ["cargo.*handler", "freight.*loader"]),
    ("LOGIS", "Logistics and Supply Chain", "Inventory Clerk", "4321.0200", "LSC/Q0102", 4, 4, ["Stock Controller", "Inventory Assistant"], ["inventory.*clerk", "stock.*keeper"]),
    ("LOGIS", "Logistics and Supply Chain", "Supply Chain Assistant", "4323.0100", "LSC/Q2301", 4, 6, ["Logistics Coordinator", "Dispatch Clerk"], ["supply.*chain", "dispatch.*clerk"]),
    ("LOGIS", "Logistics and Supply Chain", "Cold Chain Technician", "7127.0100", "LSC/Q0401", 4, 6, ["Refrigerated Logistics Tech", "Cold Storage Operator"], ["cold.*chain", "refrigerat.*logistics"]),
    ("LOGIS", "Logistics and Supply Chain", "Courier Delivery Executive", "8321.0200", "LSC/Q0302", 3, 2, ["Parcel Delivery Agent", "Post Courier Runner"], ["parcel.*delivery", "courier.*agent"]),
]

# 3. Multilingual Glossary
GLOSSARY = [
    # Key, en, hi, kn, ta, category
    ("app_title", "KaushalDrishti", "कौशल दृष्टि", "ಕೌಶಲ ದೃಷ್ಟಿ", "கௌசல் திருஷ்டி", "ui"),
    ("ministry_name", "Ministry of Skill Development & Entrepreneurship", "कौशल विकास एवं उद्यमशीलता मंत्रालय", "ಕೌಶಲ್ಯ ಅಭಿವೃದ್ಧಿ ಮತ್ತು ಉದ್ಯಮಶೀಲತೆ ಸಚಿವಾಲಯ", "திறன் மேம்பாடு மற்றும் தொழில்முனைவோர் அமைச்சகம்", "ui"),
    ("national_overview", "National Overview", "राष्ट्रीय अवलोकन", "ರಾಷ್ಟ್ರೀಯ ಅವಲೋಕನ", "தேசிய கண்ணோட்டம்", "nav"),
    ("state_explorer", "State & District Explorer", "राज्य एवं जिला अन्वेषक", "ರಾಜ್ಯ ಮತ್ತು ಜಿಲ್ಲಾ ಅನ್ವೇಷಕ", "மாநில மற்றும் மாவட்ட ஆய்வாளர்", "nav"),
    ("forecast_centre", "Forecast Centre", "पूर्वानुमान केंद्र", "ಮುನ್ಸೂಚನಾ ಕೇಂದ್ರ", "முன்கணிப்பு மையம்", "nav"),
    ("early_warning", "Early Warning Centre", "पूर्व चेतावनी केंद्र", "ಮುನ್ನೆಚ್ಚರಿಕೆ ಕೇಂದ್ರ", "முன்னெச்சரிக்கை மையம்", "nav"),
    ("scenario_lab", "Policy Scenario Lab", "नीति परिदृश्य प्रयोगशाला", "ನೀತಿ ಸನ್ನಿವೇಶ ಪ್ರಯೋಗಾಲಯ", "கொள்கை காட்சி ஆய்வகம்", "nav"),
    ("methodology", "Methodology & Validation", "कार्यप्रणाली एवं सत्यापन", "ವಿಧಾನ ಮತ್ತು ಮೌಲ್ಯೀಕರಣ", "முறை மற்றும் சரிபார்ப்பு", "nav"),

    # Flags
    ("flag_acute_shortage", "Acute Shortage", "गंभीर कमी", "ತೀವ್ರ ಕೊರತೆ", "கடுமையான பற்றாக்குறை", "flag"),
    ("flag_emerging_shortage", "Emerging Shortage", "उभरती कमी", "ಹೊರಹೊಮ್ಮುತ್ತಿರುವ ಕೊರತೆ", "வளர்ந்து வரும் பற்றாக்குறை", "flag"),
    ("flag_approaching_saturation", "Approaching Saturation", "संतृप्ति के निकट", "ಸಂಪೃಕ್ತತೆಯ ಸಮೀಪಿಸುತ್ತಿದೆ", "செறிவூட்டலை நெருங்குகிறது", "flag"),
    ("flag_saturated", "Saturated", "संतृप्त", "ಸಂಪೃಕ್ತವಾಗಿದೆ", "செறிவூட்டப்பட்டது", "flag"),
    ("flag_stable", "Stable", "स्थिर", "ಸ್ಥಿರ", "நிலையான", "flag"),
    ("overlay_rapid_growth", "Rapid Growth", "तीव्र वृद्धि", "ವೇಗದ ಬೆಳವಣಿಗೆ", "வேகமான வளர்ச்சி", "overlay"),
    ("overlay_volatile", "Volatile", "अस्थिर", "ಚಂಚಲ", "நிலையற்ற", "overlay"),

    # Metrics & Badges
    ("demand_index", "Labour Demand Index (LDI)", "श्रम मांग सूचकांक (LDI)", "ಕಾರ್ಮಿಕ ಬೇಡಿಕೆ ಸೂಚ್ಯಂಕ (LDI)", "தொழிலாளர் தேவை குறியீடு (LDI)", "metric"),
    ("forecast_demand", "Forecast Demand", "अनुमानित मांग", "ಮುನ್ಸೂಚಿತ ಬೇಡಿಕೆ", "முன்கணிப்பு தேவை", "metric"),
    ("projected_supply", "Projected Supply", "अनुमानित आपूर्ति", "ಅಂದಾಜು ಪೂರೈಕೆ", "திட்டமிடப்பட்ட விநியோகம்", "metric"),
    ("net_gap", "Projected Gap", "अनुमानित अंतर", "ಅಂದಾಜು ಅಂತರ", "திட்டமிடப்பட்ட இடைவெளி", "metric"),
    ("confidence_high", "High Confidence", "उच्च विश्वसनीयता", "ಹೆಚ್ಚಿನ ವಿಶ್ವಾಸಾರ್ಹತೆ", "அதிக நம்பிக்கை", "badge"),
    ("confidence_medium", "Medium Confidence", "मध्यम विश्वसनीयता", "ಮಧ್ಯಮ ವಿಶ್ವಾಸಾರ್ಹತೆ", "நடுத்தர நம்பிக்கை", "badge"),
    ("confidence_low", "Low Confidence", "निम्न विश्वसनीयता", "ಕಡಿಮೆ ವಿಶ್ವಾಸಾರ್ಹತೆ", "குறைந்த நம்பிக்கை", "badge"),

    # Data Modes
    ("mode_live", "Live", "लाइव", "ಲೈವ್", "நேரலை", "data_mode"),
    ("mode_public_aggregate", "Public Aggregate", "सार्वजनिक समुच्चय", "ಸಾರ್ವಜನಿಕ ಒಟ್ಟುಗೂಡಿಸುವಿಕೆ", "பொது ஒருங்கிணைப்பு", "data_mode"),
    ("mode_partner", "Partner Data", "साझेदार डेटा", "ಪಾಲುದಾರ ಡೇಟಾ", "கூட்டாளி தரவு", "data_mode"),
    ("mode_synthetic", "Synthetic", "सिंथेटिक (प्रदर्शनात्मक)", "ಕೃತಕ (ಮಾದರಿ)", "செயற்கை (மாதிரி)", "data_mode"),

    # Actions
    ("action_review_seats", "Review next-cycle seat allocation and centre capacity", "अगले चक्र के सीट आवंटन और केंद्र क्षमता की समीक्षा करें", "ಮುಂದಿನ ಚಕ್ರದ ಸೀಟು ಹಂಚಿಕೆ ಮತ್ತು ಕೇಂದ್ರದ ಸಾಮರ್ಥ್ಯವನ್ನು ಪರಿಶೀಲಿಸಿ", "அடுத்த சுழற்சி இட ஒதுக்கீடு மற்றும் மையத் திறனை மதிப்பாய்வு செய்யவும்", "action"),
    ("action_expand_training", "Priority expansion of training batches recommended", "प्रशिक्षण बैचों के प्राथमिकता विस्तार की सिफारिश", "ತರಬೇತಿ ಬ್ಯಾಚ್‌ಗಳ ಆದ್ಯತೆಯ ವಿಸ್ತರಣೆಯನ್ನು ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ", "பயிற்சி தொகுதிகளின் முன்னுரிமை விரிவாக்கம் பரிந்துரைக்கப்படுகிறது", "action"),
    ("action_consolidate_capacity", "Consolidate existing training capacity to prevent oversaturation", "अति-संतृप्ति को रोकने के लिए मौजूदा क्षमता को सुदृढ़ करें", "ಅತಿಯಾದ ಸಂಪೃಕ್ತತೆಯನ್ನು ತಡೆಗಟ್ಟಲು ಅಸ್ತಿತ್ವದಲ್ಲಿರುವ ಸಾಮರ್ಥ್ಯವನ್ನು ಕ್ರೋಢೀಕರಿಸಿ", "அதிக செறிவூட்டலைத் தடுக்க தற்போதைய திறனை ஒருங்கிணைக்கவும்", "action"),
]


def generate_lgd_districts():
    path = os.path.join(REFERENCE_DIR, "lgd_districts.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["state_code", "state_name", "lgd_code", "district_name", "population_working_age", "urban_rural_aspirational"])
        for row in DISTRICTS:
            writer.writerow(row)
    print(f"[OK] Generated {len(DISTRICTS)} districts in {path}")


def generate_trades_master():
    path = os.path.join(REFERENCE_DIR, "trades_master.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sector_code", "sector_name", "trade_name", "nco_code", "qp_code", "nsqf_level", "course_months", "aliases_pipe", "patterns_pipe"])
        for row in TRADES:
            aliases_pipe = "|".join(row[7])
            patterns_pipe = "|".join(row[8])
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], aliases_pipe, patterns_pipe])
    print(f"[OK] Generated {len(TRADES)} trades across 5 sectors in {path}")


def generate_glossary():
    path = os.path.join(REFERENCE_DIR, "glossary.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "en", "hi", "kn", "ta", "category"])
        for row in GLOSSARY:
            writer.writerow(row)
    print(f"[OK] Generated {len(GLOSSARY)} glossary entries in {path}")


if __name__ == "__main__":
    generate_lgd_districts()
    generate_trades_master()
    generate_glossary()
