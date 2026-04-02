import oracledb
import pandas as pd

# Add this before creating sess_data

# --- SETUP ---
# Update this path to your Instant Client location
LIB_DIR = r"C:\Users\dblou\Downloads\Databases\instantclient_23_0" 
DB_USER = "DEMITRYLOUINE_SCHEMA_R3LQP"
DB_PASS = "ZM#BXRAUDJ5W8TWKQCI2cMSXV24GXE"
DB_DSN  = "db.freesql.com:1521/23ai_34ui2"

# Initialize Thick Mode for Oracle connection
oracledb.init_oracle_client(lib_dir=LIB_DIR)

def normalized_bulk_load(file_path):
    try:
        # 1. Load data using pandas for easier manipulation [cite: 1, 9]
        df = pd.read_csv(file_path)
        df['Charging Cost (USD)'] = df['Charging Cost (USD)'].replace(r'[\$,]', '', regex=True).astype(float)
        df['Battery Capacity (kWh)'] = df['Battery Capacity (kWh)'].fillna(0)
        df['Vehicle Age (years)'] = df['Vehicle Age (years)'].fillna(0)
        df['Energy Consumed (kWh)'] = df['Energy Consumed (kWh)'].fillna(0)
        df['Charging Cost (USD)'] = df['Charging Cost (USD)'].fillna(0)

        
        # 2. Connect to Database
        conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
        cursor = conn.cursor()

        # --- TABLE 1: VEHICLES ---
        # Get unique vehicle models and their battery capacities [cite: 1, 15]
        vehicles = df[['Vehicle Model', 'Battery Capacity (kWh)']].drop_duplicates()
        v_data = [tuple(x) for x in vehicles.values]
        # Change the SQL command to only insert if the model doesn't exist
        cursor.executemany("""INSERT INTO Vehicles (model, battery_capacity) SELECT :1, :2 FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM Vehicles WHERE model = :1)""", v_data)

        # --- TABLE 2: STATIONS ---
        # Get unique stations and their locations [cite: 2, 10]
        stations = df[['Charging Station ID', 'Charging Station Location', 'Charger Type']].drop_duplicates()
        st_data = [tuple(x) for x in stations.values]
        # Insert only if the station_id doesn't exist
        cursor.executemany("""INSERT INTO Stations (station_id, location, charger_type)SELECT :1, :2, :3 FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM Stations WHERE station_id = :1)""", st_data)

        # --- TABLE 3: USERS ---
        # Get unique users 
        users = df[['User ID', 'User Type', 'Vehicle Age (years)']].drop_duplicates('User ID')
        u_data = [tuple(x) for x in users.values]
        # Insert only if the user_id doesn't exist
        cursor.executemany("""INSERT INTO Users (user_id, user_type, vehicle_age)SELECT :1, :2, :3 FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM Users WHERE user_id = :1)""", u_data)

        # --- TABLE 4: SESSIONS (The main fact table) ---
        # Extract the core transaction data [cite: 3, 10]
        sessions = df[[
            'User ID', 'Vehicle Model', 'Charging Station ID', 
            'Charging Start Time', 'Charging End Time', 'Energy Consumed (kWh)', 'Charging Cost (USD)'
        ]]
        sess_data = [tuple(x) for x in sessions.values]
        cursor.executemany(
            "INSERT INTO ChargingSessions (user_id, vehicle_model, station_id, start_time, end_time, energy, cost) "
            "VALUES (:1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:5, 'YYYY-MM-DD HH24:MI:SS'), :6, :7)", 
            sess_data
        )

        # Commit all changes
        conn.commit()
        print("Successfully normalized and loaded data into 4 tables.")

    except Exception as e:
        print(f"Error during bulk load: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

# Run the function
normalized_bulk_load('ev_charging_patterns.csv')