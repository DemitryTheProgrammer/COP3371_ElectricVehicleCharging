import streamlit as st
import oracledb
import pandas as pd

# --- DATABASE SETUP ---
LIB_DIR = r"C:\Users\dblou\Downloads\Databases\instantclient_23_0"
DB_USER = "DEMITRYLOUINE_SCHEMA_R3LQP"
DB_PASS = "ZM#BXRAUDJ5W8TWKQCI2cMSXV24GXE"
DB_DSN  = "db.freesql.com:1521/23ai_34ui2"

# Initialize Oracle Client for Thick Mode
@st.cache_resource
def init_db():
    if LIB_DIR:
        try:
            oracledb.init_oracle_client(lib_dir=LIB_DIR)
        except Exception as e:
            st.error(f"Error initializing Oracle Client: {e}")

init_db()

def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

# --- STREAMLIT UI ---
st.title("EV Charging Management System")
st.subheader("Station Infrastructure & Session Monitoring")

menu = ["Dashboard", "Add Station", "Update Station", "Remove Station"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- READ / DASHBOARD ---
if choice == "Dashboard":
    st.write("### Charging Sessions Overview")
    try:
        conn = get_connection()
        # Fetch Sessions joined with User/Station info for a better view
        query = """
            SELECT s.session_id, u.user_id, st.location, s.energy, s.cost, s.start_time
            FROM ChargingSessions s
            JOIN Users u ON s.user_id = u.user_id
            JOIN Stations st ON s.station_id = st.station_id
            ORDER BY s.start_time DESC
            FETCH FIRST 20 ROWS ONLY
        """
        df = pd.read_sql(query, conn)
        st.dataframe(df)

        st.write("### Active Stations")
        df_stations = pd.read_sql("SELECT * FROM Stations", conn)
        st.table(df_stations)
        
        conn.close()
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

# --- CREATE ---
elif choice == "Add Station":
    st.write("### Register New Charging Station")
    col1, col2 = st.columns(2)
    with col1:
        s_id = st.text_input("Station ID (e.g., Station_999)")
        s_loc = st.selectbox("Location", ["Houston", "New York", "San Francisco", "Los Angeles", "Chicago"])
    with col2:
        s_type = st.selectbox("Charger Type", ["DC Fast Charger", "Level 1", "Level 2"])

    if st.button("Register Station"):
        if s_id:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO Stations (station_id, location, charger_type) VALUES (:1, :2, :3)", [s_id, s_loc, s_type])
                conn.commit()
                st.success(f"Station {s_id} added successfully to {s_loc}!")
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please provide a Station ID.")

# --- UPDATE ---
elif choice == "Update Station":
    st.write("### Update Station Details")
    s_id_to_update = st.text_input("Enter Station ID to modify")
    new_type = st.selectbox("New Charger Type", ["DC Fast Charger", "Level 1", "Level 2"])

    if st.button("Update Hardware"):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE Stations SET charger_type = :1 WHERE station_id = :2", [new_type, s_id_to_update])
            if cur.rowcount > 0:
                conn.commit()
                st.success(f"Infrastructure updated for {s_id_to_update}")
            else:
                st.warning("Station ID not found.")
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Error: {e}")

# --- DELETE ---
elif choice == "Remove Station":
    st.write("### Decommission Station")
    st.error("Warning: This action cannot be undone.")
    s_id_to_delete = st.text_input("Enter Station ID to Delete")

    if st.button("Confirm Deletion"):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM Stations WHERE station_id = :1", [s_id_to_delete])
            if cur.rowcount > 0:
                conn.commit()
                st.info(f"Station {s_id_to_delete} has been removed from the network.")
            else:
                st.warning("No station found with that ID.")
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Error: {e} (Note: You cannot delete stations with active charging sessions).")

# run using: streamlit run app.py