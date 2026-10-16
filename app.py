import sqlite3
import pandas as pd
import streamlit as st

# Database Connection (SQLite)
conn = sqlite3.connect("hospital.db", check_same_thread=False)
cursor = conn.cursor()

# Create Tables
cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        disease TEXT,
        doctor TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        specialization TEXT
    )
""")

# Seed default doctors if table is empty
cursor.execute("SELECT COUNT(*) FROM doctors")
if cursor.fetchone()[0] == 0:
  default_docs = [
      ("Dr. Sharma", "Cardiologist"),
      ("Dr. Verma", "Neurologist"),
      ("Dr. Gupta", "General Physician"),
      ("Dr. Mehta", "Orthopedic"),
  ]
  cursor.executemany(
      "INSERT INTO doctors (name, specialization) VALUES (?, ?)", default_docs
  )
  conn.commit()

# Page Config
st.set_page_config(
    page_title="Advanced Smart Hospital System", page_icon="🏥", layout="wide"
)

st.title("🏥 Advanced Smart Hospital Management System")
st.write(
    "Powered by Python, Streamlit & SQLite — Fully Loaded with Analytics,"
    " Billing & Management."
)

# Sidebar Navigation
menu = [
    "📊 Live Dashboard & Analytics",
    "📝 Register Patient",
    "🔍 Search Patient",
    "❌ Discharge Patient",
    "🧾 Bill & Prescription",
    "👨‍⚕️ Doctor Management",
]
choice = st.sidebar.selectbox("Hospital Navigation", menu)

# 1. LIVE DASHBOARD & ANALYTICS
if choice == "📊 Live Dashboard & Analytics":
  st.subheader("📊 Hospital Overview & Analytics")

  cursor.execute("SELECT * FROM patients ORDER BY id DESC")
  data = cursor.fetchall()

  if data:
    total_patients = len(data)
    st.metric(
        label="Total Admitted Patients",
        value=total_patients,
        delta="Fully Operational 🟢",
    )
    st.markdown("---")

    df = pd.DataFrame(
        data,
        columns=[
            "ID",
            "Patient Name",
            "Age",
            "Gender",
            "Disease",
            "Assigned Doctor",
            "Admission Time",
        ],
    )

    col1, col2 = st.columns(2)

    with col1:
      st.markdown("### 📋 Recent Patients List")
      st.dataframe(df, use_container_width=True)

    with col2:
      st.markdown("### 📈 Patients per Doctor Analytics")
      doc_counts = df["Assigned Doctor"].value_counts()
      st.bar_chart(doc_counts)

  else:
    st.info(
        "No patient records found yet. Use 'Register Patient' from the sidebar"
        " to start."
    )

# 2. REGISTER PATIENT
elif choice == "📝 Register Patient":
  st.subheader("📝 New Patient Admission Form")

  # Fetch doctors dynamically from DB
  cursor.execute(
      "SELECT name || ' (' || specialization || ')' FROM doctors"
  )
  doc_rows = cursor.fetchall()
  doctor_list = [row[0] for row in doc_rows] if doc_rows else ["General Doctor"]

  with st.form("patient_form", clear_on_submit=True):
    name = st.text_input("Patient Full Name")

    col1, col2 = st.columns(2)
    with col1:
      age = st.number_input("Age", min_value=1, max_value=120, step=1)
      gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    with col2:
      disease = st.text_input("Medical Diagnosis / Disease")
      doctor = st.selectbox("Assign Doctor", doctor_list)

    submitted = st.form_submit_button("Admit Patient")

    if submitted:
      if name.strip() and disease.strip():
        cursor.execute(
            "INSERT INTO patients (name, age, gender, disease, doctor) VALUES"
            " (?, ?, ?, ?, ?)",
            (name, age, gender, disease, doctor),
        )
        conn.commit()
        st.success(
            f"✅ Patient **{name}** successfully admitted under **{doctor}**!"
        )
      else:
        st.error("⚠️ Please fill in all required text fields.")

# 3. SEARCH PATIENT
elif choice == "🔍 Search Patient":
  st.subheader("🔍 Search Patient Records")
  search_query = st.text_input("Type patient name to search...")

  if search_query:
    cursor.execute(
        "SELECT * FROM patients WHERE name LIKE ?", ("%" + search_query + "%",)
    )
    results = cursor.fetchall()

    if results:
      st.success(f"Found {len(results)} matching record(s):")
      df_search = pd.DataFrame(
          results,
          columns=[
              "ID",
              "Patient Name",
              "Age",
              "Gender",
              "Disease",
              "Assigned Doctor",
              "Admission Time",
          ],
      )
      st.dataframe(df_search, use_container_width=True)
    else:
      st.warning("No matching patient records found.")

# 4. DISCHARGE PATIENT
elif choice == "❌ Discharge Patient":
  st.subheader("❌ Patient Discharge Panel")

  cursor.execute("SELECT id, name, disease, doctor FROM patients")
  patients = cursor.fetchall()

  if patients:
    patient_dict = {
        f"ID: {p[0]} | {p[1]} ({p[2]}) - {p[3]}": p[0] for p in patients
    }
    selected_p = st.selectbox(
        "Select Patient to Discharge", list(patient_dict.keys())
    )

    if st.button("Discharge Patient (Remove Record)"):
      p_id = patient_dict[selected_p]
      cursor.execute("DELETE FROM patients WHERE id = ?", (p_id,))
      conn.commit()
      st.success(
          f"✅ Patient successfully discharged and record archived!"
      )
      st.rerun()
  else:
    st.info("No active patients available for discharge.")

# 5. BILL & PRESCRIPTION

elif choice == "🧾 Bill & Prescription":
  st.subheader("🧾 Digital Prescription & Bill Generator")

  cursor.execute("SELECT id, name, disease, doctor FROM patients")
  patients = cursor.fetchall()

  if patients:
    p_dict = {f"ID: {p[0]} - {p[1]}": p for p in patients}
    chosen = st.selectbox("Select Patient", list(p_dict.keys()))
    p_data = p_dict[chosen]

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
      room_charges = st.number_input(
          "Room & Facilities Charges (₹)", min_value=0.0, value=2000.0, step=500.0
      )
      doc_fee = st.number_input(
          "Doctor Consultation Fee (₹)", min_value=0.0, value=1000.0, step=100.0
      )
      medicine_cost = st.number_input(
          "Pharmacy / Medicines Cost (₹)", min_value=0.0, value=500.0, step=100.0
      )

    with col2:
      st.markdown("### 🏥 Hospital Invoice Preview")
      total_bill = room_charges + doc_fee + medicine_cost

      st.markdown(f"""
            **Patient Name:** {p_data[1]}  
            **Diagnosis:** {p_data[2]}  
            **Attending Doctor:** {p_data[3]}  
            ----------------------------------  
            * Room Charges: ₹{room_charges}  
            * Doctor Fee: ₹{doc_fee}  
            * Medicines: ₹{medicine_cost}  
            ----------------------------------  
            ### **Total Payable: ₹{total_bill}**  
            """)
      if st.button("🖨️ Print / Save Invoice"):
        st.success("🎉 Invoice generated successfully for " + p_data[1] + "!")
  else:
    st.warning("No patients found to generate bills.")
           
# 6. DOCTOR MANAGEMENT
elif choice == "👨‍⚕️ Doctor Management":
  st.subheader("👨‍⚕️ Hospital Doctor Directory")

  with st.form("doc_form", clear_on_submit=True):
    doc_name = st.text_input("Doctor Name (e.g., Dr. Kapoor)")
    doc_spec = st.text_input("Specialization (e.g., Pediatrian)")
    add_doc = st.form_submit_button("Add New Doctor")

    if add_doc:
      if doc_name.strip() and doc_spec.strip():
        cursor.execute(
            "INSERT INTO doctors (name, specialization) VALUES (?, ?)",
            (doc_name, doc_spec),
        )
        conn.commit()
        st.success(f"✅ Doctor **{doc_name} ({doc_spec})** added successfully!")
        st.rerun()
      else:
        st.error("Please fill in both fields.")

  st.markdown("### 📋 Current Active Doctors")
  cursor.execute("SELECT * FROM doctors")
  doc_data = cursor.fetchall()
  if doc_data:
    df_doc = pd.DataFrame(doc_data, columns=["ID", "Doctor Name", "Specialization"])
    st.dataframe(df_doc, use_container_width=True)