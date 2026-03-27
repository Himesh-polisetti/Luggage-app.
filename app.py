import streamlit as st
import sqlite3

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Luggage App", layout="wide")

# ---------------- CLEAN UI ----------------
st.markdown("""
<style>
body {
    background-color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

# Users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT,
    role TEXT,
    location TEXT,
    phone TEXT
)
''')

# Requests table
c.execute('''
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    location TEXT,
    delivery TEXT,
    bags INTEGER,
    date TEXT,
    status TEXT
)
''')

# Complaints table
c.execute('''
CREATE TABLE IF NOT EXISTS complaints (
    name TEXT,
    issue TEXT
)
''')

conn.commit()

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- MENU ----------------
menu = st.radio(
    "Menu",
    ["Home", "Help", "Services", "Complaint"],
    horizontal=True
)

# ---------------- MENU PAGES ----------------

if menu == "Help":
    st.title("❓ Help - How to Use")

    st.write("""
    1. Signup as Customer or Host  
    2. Customer → Create luggage request  
    3. Host → View nearby requests  
    4. Host accepts request  
    5. Contact customer via phone  
    """)

    st.info("💡 Pickup location should match host location")
    st.stop()

elif menu == "Services":
    st.title("🛠 Customer Support")

    st.write("""
    📞 Helpline: 9876543210  
    📧 Email: support@luggageapp.com  
    🕒 Available: 9 AM – 9 PM  
    """)

    st.success("We are here to help you!")
    st.stop()

elif menu == "Complaint":
    st.title("⚠ Register Complaint")

    name = st.text_input("Your Name")
    issue = st.text_area("Describe your issue")

    if st.button("Submit Complaint"):
        c.execute("INSERT INTO complaints VALUES (?, ?)", (name, issue))
        conn.commit()
        st.success("✅ Complaint submitted successfully!")

    st.stop()

# ---------------- CITIES ----------------
cities = [
    "Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Kurnool",
    "Nellore", "Rajahmundry", "Kakinada", "Anantapur", "Kadapa",
    "Chittoor", "Eluru", "Srikakulam", "Ongole", "Vizianagaram"
]

# ---------------- LOGIN / SIGNUP ----------------
if st.session_state.user is None:

    st.title("🎒 Luggage Storage Platform")

    option = st.radio("Choose Option", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Signup":
        role = st.selectbox("Role", ["Customer", "Host"])
        location = st.selectbox("Select Location", cities)
        phone = st.text_input("Phone Number")

        if st.button("Signup"):
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                      (username, password, role, location, phone))
            conn.commit()
            st.success("✅ Account created! Please login.")

    if option == "Login":
        if st.button("Login"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?",
                      (username, password))
            user = c.fetchone()

            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    username, password, role, user_location, phone = user

    st.sidebar.write(f"👤 {username} ({role})")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    st.divider()

    # -------- CUSTOMER --------
    if role == "Customer":
        st.title("📦 Create Luggage Request")

        col1, col2 = st.columns(2)

        with col1:
            location = st.selectbox("📍 Pickup Location", cities)
            bags = st.number_input("🎒 Number of Bags", min_value=1)

        with col2:
            delivery = st.selectbox("🚚 Delivery Location", cities)
            date = st.date_input("📅 Date")

        if st.button("🚀 Submit Request"):
            c.execute('''
            INSERT INTO requests (username, location, delivery, bags, date, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, location, delivery, bags, str(date), "Pending"))
            conn.commit()
            st.success("✅ Request submitted successfully!")

    # -------- HOST --------
    elif role == "Host":
        st.title("🏠 Nearby Requests")

        c.execute("SELECT * FROM requests WHERE location=?", (user_location,))
        data = c.fetchall()

        if not data:
            st.info("No requests in your location")

        for row in data:
            request_id = row[0]
            customer_name = row[1]

            # Get customer phone
            c.execute("SELECT phone FROM users WHERE username=?", (customer_name,))
            phone_data = c.fetchone()
            customer_phone = phone_data[0] if phone_data else "N/A"

            st.markdown(f"""
            **📌 Request ID:** {row[0]}  
            **👤 User:** {row[1]}  
            **📍 Pickup:** {row[2]}  
            **🚚 Delivery:** {row[3]}  
            **🎒 Bags:** {row[4]}  
            **📅 Date:** {row[5]}  
            **📊 Status:** {row[6]}  
            """)

            if row[6] == "Accepted":
                st.success(f"📞 Customer Phone: {customer_phone}")

            if row[6] == "Pending":
                if st.button(f"✅ Accept {request_id}"):
                    c.execute("UPDATE requests SET status='Accepted' WHERE id=?", (request_id,))
                    conn.commit()
                    st.success("Accepted!")
                    st.rerun()

            st.divider()