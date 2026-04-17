import oracledb

LIB_DIR = r""


DB_USER = ""
DB_PASS = ""
DB_DSN  = ""

if LIB_DIR:
    oracledb.init_oracle_client(lib_dir=LIB_DIR)
else: oracledb.enable_thin_mode()

conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
cursor = conn.cursor()
print("Connected to Oracle Database\n")


def option1():
    cursor.execute("""
    SELECT s.station_id, s.station_name, s.location_address, s.total_ports, d.network_type, d.max_voltage
    FROM stations s
    LEFT JOIN station_details d ON s.station_id = d.station_id""")

    rows = cursor.fetchall()

    print("\nStations:\n")
    for row in rows:
        print(f"station_id: {row[0]}, station_name: {row[1]}, location_address: {row[2]}, total_ports: {row[3]}, network_type: {row[4]}, max_voltage: {row[5]}")

    if(len(rows)==0):
        print("No stations found.")


def option2():

    location = input("Enter location: ")
    network = input("Enter network type: ")

    cursor.execute("""
        SELECT s.station_id, s.station_name
        FROM stations s
        JOIN station_details d ON s.station_id = d.station_id
        WHERE s.location_address = :1
            AND d.network_type = :2""",[location, network])

    rows = cursor.fetchall()

    print("\nStations:")
    for row in rows:
        print(f"station_id: {row[0]}, station_name: {row[1]}")
    
    if(len(rows)==0):
        print("No stations found.")


def option3():

    name = input("Enter station name: ")

    cursor.execute("""
        SELECT m.log_id, m.issue_description
        FROM stations s
        JOIN maintenance_logs m ON s.station_id = m.station_id
        WHERE s.station_name = :1""",[name])

    rows = cursor.fetchall()

    print("\nMaintenance logs:")
    for row in rows:
        print(f"log_id: {row[0]}, issue_description: {row[1]}")
    
    if(len(rows)==0):
        print("No maintenance logs found.")

def option4():

    log_id = input("Enter log ID: ")
    station_id = input("Enter station ID: ")
    issue = input("Enter issue description: ")

    cursor.execute("""INSERT INTO maintenance_logs (log_id, station_id, issue_description) VALUES (:1, :2, :3)""", [log_id, station_id, issue])

    conn.commit()
    print("\nMaintenance log added.")


def option5():

    session_id = input("Enter session ID: ")
    user_id = input("Enter user ID: ")
    station_id = input("Enter station ID: ")
    energy = input("Enter energy used (kWh): ")

    cursor.execute("""INSERT INTO charging_sessions (session_id, user_id, station_id, energy_consumed_kwh) VALUES (:1, :2, :3, :4)""", [session_id, user_id, station_id, energy])

    conn.commit()
    print("\nCharging session recorded.")


while True:

    print("\nSelect an action.\n")
    print("1. View database stations and details.")
    print("2. Search stations based on network.")
    print("3. Search through a station's maintenance logs.")
    print("4. Add issue to a station's maintenance log.")
    print("5. Add session data to a station's session history.")
    print("0. Exit")

    userInput = input("\n")
    
    if userInput=="1":
        option1()
    elif userInput=="2":
        option2()
    elif userInput=="3":
        option3()
    elif userInput=="4":
        option4()
    elif userInput=="5":
        option5()
    elif userInput=="0":
        break
    else:
        print("Invalid option.")



cursor.close()
conn.close()
print("Oracle connection closed.")