import oracledb

# --- CONFIGURATION ---
LIB_DIR = r"C:\Users\dblou\Downloads\Databases\instantclient_23_0"
DB_USER = "DEMITRYLOUINE_SCHEMA_R3LQP"
DB_PASS = "ZM#BXRAUDJ5W8TWKQCI2cMSXV24GXE"
DB_DSN  = "db.freesql.com:1521/23ai_34ui2"

# 1. Initialize Thick Mode
if LIB_DIR:
    oracledb.init_oracle_client(lib_dir=LIB_DIR)
else: 
    oracledb.enable_thin_mode()

# 2. Establish Connection
conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
cursor = conn.cursor()
print("Connected to EV Charging Database")

# --- 3. CREATE (Insert a new Station) ---
def create_station(station_id, location, charger_type):
    sql = "INSERT INTO Stations (station_id, location, charger_type) VALUES (:1, :2, :3)"
    try:
        cursor.execute(sql, [station_id, location, charger_type])
        conn.commit()
        print(f"Success: Station {station_id} created.")
    except oracledb.Error as e:
        print(f"Error creating station: {e}")

# --- 4. READ (Fetch all sessions for a specific user) ---
def read_user_sessions(user_id):
    print(f"\n--- Charging Sessions for {user_id} ---")
    sql = """
        SELECT session_id, vehicle_model, energy, cost, start_time 
        FROM ChargingSessions 
        WHERE user_id = :1
    """
    cursor.execute(sql, [user_id])
    rows = cursor.fetchall()
    if not rows:
        print("No sessions found.")
    for row in rows:
        print(f"ID: {row[0]} | Vehicle: {row[1]} | Energy: {row[2]}kWh | Cost: ${row[3]} | Date: {row[4]}")

# --- 5. UPDATE (Modify a user's vehicle age) ---
def update_user_vehicle_age(user_id, new_age):
    sql = "UPDATE Users SET vehicle_age = :1 WHERE user_id = :2"
    cursor.execute(sql, [new_age, user_id])
    if cursor.rowcount == 0:
        print(f"No user found with ID: {user_id}")
    else:
        conn.commit()
        print(f"Success: Updated vehicle age for {user_id} to {new_age} years.")

# --- 6. DELETE (Remove a specific charging session) ---
def delete_session(session_id):
    sql = "DELETE FROM ChargingSessions WHERE session_id = :1"
    cursor.execute(sql, [session_id])
    if cursor.rowcount == 0:
        print(f"No session found with ID: {session_id}")
    else:
        conn.commit()
        print(f"Success: Session {session_id} deleted.")

# --- TEST EXAMPLES ---
# 1. Create a new station
create_station("Station_999", "Lakeland", "DC Fast Charger")

# 2. Update a user's data
update_user_vehicle_age("User_1", 3.5)

# 3. Read sessions (Example ID from your CSV)
read_user_sessions("User_1")

# 4. Cleanup (Closing connection)
cursor.close()
conn.close()