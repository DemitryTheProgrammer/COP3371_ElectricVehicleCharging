import oracledb
import csv

# --- SETUP ---
LIB_DIR = r"" 
DB_USER = ""
DB_PASS = ""
DB_DSN = ""

try:
    oracledb.init_oracle_client(lib_dir=LIB_DIR)
except Exception as e:
    print(f"Oracle Client info: {e}")

def bulk_load_normalized(file_path):
    conn = None
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
        cursor = conn.cursor()

        # Data containers to hold unique records for parent tables
        unique_users = {}    # {user_id: (user_id, email)}
        unique_stations = {} # {station_id: (station_id, name, address)}
        station_details = {} # {station_id: (station_id, network_type)}
        sessions_list = []   # List of tuples for the linking table

        print("Reading and processing CSV data...")
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                u_id = int(row['user_id'])
                s_id = int(row['station_id'])
                
                # Handle missing energy values
                energy_val = row['energy_consumed_kwh'].strip()
                energy = float(energy_val) if energy_val else None
                
                # 1. Collect Unique Users
                if u_id not in unique_users:
                    unique_users[u_id] = (u_id, row['email'])
                
                # 2. Collect Unique Stations and Details
                if s_id not in unique_stations:
                    unique_stations[s_id] = (s_id, row['station_name'], row['location_address'])
                    station_details[s_id] = (s_id, row['network_type'])
                
                # 3. Collect Sessions (Every row in CSV is a session)
                # We use 'i' as a generated session_id
                sessions_list.append((i, u_id, s_id, energy))

        # --- BULK INSERTION ---
        
        print("Loading Users...")
        cursor.executemany("INSERT INTO users (user_id, email) VALUES (:1, :2)", 
                           list(unique_users.values()))
        
        print("Loading Stations...")
        cursor.executemany("INSERT INTO stations (station_id, station_name, location_address) VALUES (:1, :2, :3)", 
                           list(unique_stations.values()))
        
        print("Loading Station Details...")
        cursor.executemany("INSERT INTO station_details (station_id, network_type) VALUES (:1, :2)", 
                           list(station_details.values()))
        
        print("Loading Charging Sessions...")
        cursor.executemany("INSERT INTO charging_sessions (session_id, user_id, station_id, energy_consumed_kwh) VALUES (:1, :2, :3, :4)", 
                           sessions_list)

        conn.commit()
        print("\nSUCCESS: All normalized tables have been loaded.")

    except oracledb.Error as e:
        print(f"\nDATABASE ERROR: {e}")
        if conn: conn.rollback()
    except Exception as e:
        print(f"\nPYTHON ERROR: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    bulk_load_normalized('ev_charging_patterns_cleaned.csv')
