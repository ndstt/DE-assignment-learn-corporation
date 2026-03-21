# ----------------------------
# Config
# ----------------------------
import pandas as pd

NOW = pd.Timestamp("2026-03-21 12:00:00")

FIRST_NAMES = [
    "กิตติ", "กิตติพงศ์", "กิตติศักดิ์", "เกียรติศักดิ์", "ขวัญชนก", "จิรภัทร",
    "จิราพร", "ชญานี", "ชยพล", "ณัฐชา", "ณัฐณิชา", "ณัฐพล", "ณัฐพงศ์",
    "ณัฐวุฒิ", "ดวงกมล", "ธนกร", "ธนภัทร", "ธนวัฒน์", "ธัญญรัตน์", "นภัสสร",
    "นิธิศ", "ปกรณ์", "ปวีณ์ธิดา", "ปิยฉัตร", "ปิยธิดา", "พงศกร", "พชร",
    "พัชรินทร์", "พิมพ์ชนก", "ภควัต", "ภัทรพล", "ภัทรวดี", "ภาวิณี", "มณฑิตา",
    "รวิภา", "วรภัทร", "วรัญญา", "ศศิธร", "ศุภกร", "ศุภชัย", "ศุภณัฐ",
    "ศุภมาส", "สิรภพ", "สิรินดา", "สุพิชญา", "อชิรวิชญ์", "อธิชา", "อภิญญา",
    "อภิสิทธิ์", "อรจิรา", "อริสรา"
]

LAST_NAMES = [
    "กาญจนวัฒน์", "เกษมสันต์", "โฆษิตพัฒน์", "จงเจริญ", "จันทร์โอภาส", "เจริญกิจ",
    "ชำนาญกิจ", "ณรงค์เดช", "ดิลกภัทร", "ตันติวัฒนกุล", "ทวีทรัพย์", "ทองประเสริฐ",
    "ธีรพงศ์ไพศาล", "นาคสกุล", "บุญญาภิรักษ์", "ประภาพันธ์", "ปรีชากุล",
    "ผดุงศักดิ์", "พัฒนพงศ์", "ภักดีวิจิตร", "มงคลสวัสดิ์", "รัตนวราหะ",
    "รุ่งเรืองชัย", "ลาภอนันต์", "วัฒนชัย", "วาณิชกุล", "ศรีสวัสดิ์", "ศุภเดช",
    "สกุลรุ่งเรือง", "สถาพรพิพัฒน์", "สุคนธสวัสดิ์", "สุทธิพงศ์", "อนันตกุล",
    "อรรถวิทย์", "อัครเดชานนท์", "อินทรประสิทธิ์"
]

# ใช้ชื่อธุรกิจ/สถาบัน/โรงเรียนในเครือ LEARN ให้ใกล้เคียงโลกจริง
SCHOOL_NAMES = [
    "OnDemand",
    "Ignite by OnDemand",
    "TCASter",
    "Learnneo",
    "Premier Prep by OnDemand",
    "EduSmith",
    "Code Genius",
    "APPA",
    "Learn Education",
    "Crest School",
    "Learn Satit Pattana School (LSP School)",
    "Satit Pattana School (STP School)",
    "Skooldio",
    "Skooldio Tech",
]

ADULT_INSTITUTIONS = {"Skooldio", "Skooldio Tech"}
ADULT_GRADE = "ไม่ระบุ (วัยทำงาน)"

K12_GRADES = [
    "ประถมศึกษาปีที่ 4",
    "ประถมศึกษาปีที่ 5",
    "ประถมศึกษาปีที่ 6",
    "มัธยมศึกษาปีที่ 1",
    "มัธยมศึกษาปีที่ 2",
    "มัธยมศึกษาปีที่ 3",
    "มัธยมศึกษาปีที่ 4",
    "มัธยมศึกษาปีที่ 5",
    "มัธยมศึกษาปีที่ 6",
]

CHANNEL_VARIANTS = {
    "facebook_ads": ["facebook", "Facebook", "FACEBOOK", "FB Ads", "fb ads"],
    "google_ads": ["google", "Google", "GOOGLE ADS", "google ads"],
    "line": ["line", "LINE", "Line OA", "line oa"],
    "website": ["website", "Website", "WEB", "web form"],
    "referral": ["referral", "Referral", "friend referral", "Friend Referral"],
    "tiktok": ["tiktok", "TikTok", "TIKTOK ADS", "tiktok ads"],
}

EVENT_VARIANTS = {
    "view_lesson": ["view_lesson", "View_Lesson", "view lesson", "VIEW LESSON"],
    "watch_video": ["watch_video", "Watch_Video", "watch video", "WATCH VIDEO"],
    "practice": ["practice", "Practice", "PRACTICE"],
    "quiz_start": ["quiz_start", "Quiz_Start", "quiz start", "QUIZ START"],
    "quiz_submit": ["quiz_submit", "Quiz_Submit", "quiz submit", "QUIZ SUBMIT"],
    "assignment_submit": [
        "assignment_submit", "Assignment_Submit", "assignment submit", "ASSIGNMENT SUBMIT"
    ],
    "live_class_join": ["live_class_join", "Live_Class_Join", "live class join"],
}

K12_SUBJECTS_AND_CHAPTERS = {
    "คณิตศาสตร์": ["เศษส่วน", "สมการเชิงเส้น", "เรขาคณิต", "สถิติ", "ความน่าจะเป็น"],
    "วิทยาศาสตร์": ["สารและสมบัติ", "แรงและการเคลื่อนที่", "พลังงาน", "โลกและอวกาศ", "ชีววิทยาเบื้องต้น"],
    "ภาษาอังกฤษ": ["Grammar", "Reading Comprehension", "Vocabulary", "Writing Skills", "Speaking"],
    "ฟิสิกส์": ["การเคลื่อนที่แนวตรง", "แรง", "พลังงาน", "คลื่น", "ไฟฟ้า"],
    "เคมี": ["อะตอม", "ตารางธาตุ", "พันธะเคมี", "ปฏิกิริยาเคมี", "สโตอิชิโอเมทรี"],
    "ชีววิทยา": ["เซลล์", "พันธุศาสตร์", "นิเวศวิทยา", "ระบบร่างกายมนุษย์", "วิวัฒนาการ"],
}

ADULT_SUBJECTS_AND_CHAPTERS = {
    "Data Analytics": ["SQL Basics", "Filtering & Sorting", "JOIN", "Aggregation", "Dashboard Thinking"],
    "Data Engineering": ["Data Modeling", "ETL/ELT", "Data Warehouse", "Data Pipeline", "Batch vs Streaming"],
    "Business Intelligence": ["Spreadsheet Analysis", "Looker Studio", "Power BI", "Metrics Design", "Storytelling"],
    "Programming": ["Python Basics", "Functions", "Pandas", "APIs", "Automation"],
}

PLATFORMS = ["ios", "android", "web", "tablet_web"]

# (product_name, product_type, amount, brand_name, audience)
PRODUCT_CATALOG = [
    ("UpSkill ฟิสิกส์ A-Level", "course", 4000, "OnDemand", "k12"),
    ("Upskill เคมี A-Level (Dek 69)", "course", 4000, "OnDemand", "k12"),
    ("UpSkill ชีววิทยา A-Level", "course", 4000, "OnDemand", "k12"),
    ("Upskill A-Level English", "course", 4900, "OnDemand", "k12"),
    ("Pack UpSkill TCAS 4 วิชา (ฟิสิกส์, เคมี, ชีวะ, คณิต)", "pack", 11900, "OnDemand", "k12"),
    ("SOS Upgrade ฟิสิกส์ TCAS", "course", 5500, "OnDemand", "k12"),
    ("SQL for Data Analytics", "online_course", 2990, "Skooldio", "adult"),
    ("Guided Project: SQL for Data Analytics", "guided_project", 990, "Skooldio", "adult"),
    ("Advanced SQL for Data Analytics with BigQuery", "online_course", 2990, "Skooldio", "adult"),
]

PAYMENT_STATUS_VARIANTS = {
    "success": ["success", "SUCCESS", "Success", "paid", "Paid", "completed", "Completed"],
    "pending": ["pending", "PENDING", "Pending", "processing", "Processing"],
    "failed": ["failed", "FAILED", "Failed", "cancelled", "Cancelled", "refunded", "Refunded"],
}