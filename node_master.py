import os, sys, subprocess, time, requests
from datetime import datetime

SERVER = os.environ.get("SERVER", "http://localhost:8000")
SESSION_FILE = ".session_master"

def clear_screen():
    # Clears the terminal screen for both Windows and Linux/WSL
    os.system('cls' if os.name == 'nt' else 'clear')

def live_monitoring(token):
    print("\n[+] Initialising Live Monitoring Server Link...")
    time.sleep(1)
    
    while True:
        try:
            # 1. Fetch all complaints from the server
            r = requests.get(f"{SERVER}/complaints", headers={"X-Token": token})
            if not r.ok:
                print("Error connecting to server data. Retrying...")
                time.sleep(3)
                continue
                
            complaints = r.json()
            
            # 2. Draw the Dashboard UI
            clear_screen()
            print("=" * 85)
            print(f"  📡 SYSTEM MASTER : LIVE NETWORK MONITORING DASHBOARD   |   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 85)
            
            if not complaints:
                print("\n  [!] Database is empty. Waiting for network traffic...")
            else:
                # Extract unique IP addresses currently in the system
                ips = set(c.get("ip_address", "Unknown") for c in complaints)
                print(f"\n  🟢 ACTIVE CONNECTED NODES (IPs): {', '.join(ips)}\n")
                
                # Table Header
                print(f"  {'ID':<10} | {'DEPT':<10} | {'STATUS':<15} | {'ORIGIN IP':<15} | {'LATEST ACTION'}")
                print("  " + "-" * 81)
                
                # 3. Fetch the latest action for each complaint dynamically
                for c in complaints:
                    cid = c['id']
                    
                    # Ping the track endpoint to get the absolute latest action timestamp
                    tr = requests.get(f"{SERVER}/track/{cid}")
                    last_action = "None"
                    if tr.ok:
                        last_action = tr.json().get("last_action", "None")
                    
                    # Truncate long actions so they fit nicely in the terminal table
                    if len(last_action) > 22: 
                        last_action = last_action[:19] + "..."
                        
                    print(f"  {cid:<10} | {c['department']:<10} | {c['status']:<15} | {c.get('ip_address', 'Unknown'):<15} | {last_action}")
            
            print("\n" + "=" * 85)
            print("  Refreshing network data every 3 seconds... (Press Ctrl+C to exit monitor mode)")
            
            # 4. Wait 3 seconds and loop again
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\n\n[!] Exiting Live Monitor Mode...")
            time.sleep(1)
            break
        except Exception as e:
            print(f"\n[!] Network Error: {e}")
            time.sleep(3)

def main():
    print("--- ⚠️ SERVER MASTER CONTROL TERMINAL ⚠️ ---")
    
    # Check for existing session token
    token = ""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            token = f.read().strip()
            
    # Master Login Loop
    while not token:
        print("\n=== MASTER LOGIN REQUIRED ===")
        user = input("Username: ")
        pwd = input("Password: ")
        try:
            r = requests.post(f"{SERVER}/login", json={"username": user, "password": pwd})
            if r.ok:
                token = r.json()["token"]
                with open(SESSION_FILE, "w") as f: f.write(token)
                print("[+] Master Authentication Successful.\n")
            else:
                print("[!] Invalid credentials. Try again.")
        except Exception as e:
            print(f"[!] Server offline: Make sure server.py is running. Error: {e}")
            return

    # Master Menu
    while True:
        print("\n" + "*"*40)
        print("           MASTER CORE MENU")
        print("*"*40)
        print(" [1] Enter Live Monitoring Dashboard 📡")
        print(" [2] Open Standard Admin Client (Manage Data)")
        print(" [3] Logout")
        print(" [4] Exit")
        
        choice = input("\nSelect Protocol (1-4): ").strip()
        
        if choice == "1":
            live_monitoring(token)
        elif choice == "2":
            # Passes control to client.py just like the other nodes
            os.environ["SERVER"] = SERVER
            os.environ["SESSION_FILE"] = SESSION_FILE
            subprocess.run([sys.executable, "client.py"])
        elif choice == "3":
            if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
            print("\n[+] Master Session Terminated.")
            break
        elif choice == "4":
            print("\n[+] Shutting down Master Terminal.")
            break
        else:
            print("[!] Invalid input.")

if __name__ == "__main__":
    main()