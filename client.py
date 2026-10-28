import os, sys, requests, json

SERVER = os.environ.get("SERVER", "http://localhost:8000")
SESSION_FILE = os.environ.get("SESSION_FILE", ".session")
IS_PUBLIC = os.environ.get("IS_PUBLIC", "False") == "True"

def print_result(data):
    print("\n" + "="*40)
    print(json.dumps(data, indent=2) if isinstance(data, dict) else data)
    print("="*40 + "\n")

def make_req(method, endpoint, payload=None, token=None):
    headers = {"X-Token": token} if token else {}
    url = f"{SERVER}{endpoint}"
    try:
        if method == "GET": r = requests.get(url, headers=headers)
        elif method == "POST": r = requests.post(url, headers=headers, json=payload)
        elif method == "DELETE": r = requests.delete(url, headers=headers)
        
        try: data = r.json()
        except: data = r.text
        
        if not r.ok:
            print(f"\n[!] ERROR {r.status_code}: {data.get('detail', data)}")
        else:
            print_result(data)
        return r.ok, data
    except requests.ConnectionError:
        print("\n[!] CRITICAL ERROR: Could not connect to the server.")
        return False, None

def interactive_public():
    print("\n" + "*"*40)
    print("      PUBLIC COMPLAINT PORTAL      ")
    print("*"*40)
    while True:
        print("Options: [1] Submit Complaint  [2] Track Complaint  [3] Exit")
        choice = input("Select an option (1-3): ").strip()
        
        if choice == "1":
            inst = input("> Institution Name: ")
            cat = input("> Category (fees/harassment/affiliation/faculty/infrastructure): ")
            desc = input("> Description: ")
            make_req("POST", "/complaints", {"institution": inst, "category": cat, "description": desc})
        elif choice == "2":
            cid = input("> Enter Complaint ID (e.g., C-XXXXXX): ")
            make_req("GET", f"/track/{cid}")
        elif choice == "3":
            break
        else:
            print("[!] Invalid choice. Try again.\n")

def interactive_admin():
    token = ""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            token = f.read().strip()
    
    # Login Loop
    while not token:
        print("\n=== SYSTEM LOGIN REQUIRED ===")
        user = input("Username: ")
        pwd = input("Password: ")
        ok, data = make_req("POST", "/login", {"username": user, "password": pwd})
        if ok:
            token = data["token"]
            with open(SESSION_FILE, "w") as f: f.write(token)
            print("[+] Authentication Successful.\n")
        else:
            print("[!] Please try again or press Ctrl+C to quit.\n")

    # Persistent Admin Dashboard
    print("\n" + "*"*50)
    print("             ADMIN DASHBOARD ACTIVE             ")
    print("*"*50)
    print(" "*10 + "THE MENU" + " "*10)
    print("[1] List All \n[2] View Details \n[3] Take Action\n")
    print("[4] Delete (Master) \n[5] Shutdown (Master)  \n[6] Logout  \n[7] Exit")
            
    while True:
        choice = input("Select an option (1-7): ").strip()
        
        if choice == "1":
            make_req("GET", "/complaints", token=token)
        elif choice == "2":
            cid = input("> Enter Complaint ID: ")
            make_req("GET", f"/complaints/{cid}", token=token)
        elif choice == "3":
            cid = input("> Enter Complaint ID: ")
            act = input("> Action taken: ")
            status = input("> New Status (leave blank to keep current): ")
            force_input = input("> Force action override? (y/n): ").strip().lower()
            payload = {"action": act, "force": (force_input == 'y')}
            if status: payload["status"] = status
            make_req("POST", f"/complaints/{cid}/actions", payload, token=token)
        elif choice == "4":
            cid = input("> Enter Complaint ID to permanently delete: ")
            make_req("DELETE", f"/complaints/{cid}", token=token)
        elif choice == "5":
            conf = input("> Are you sure you want to kill the server? (y/n): ").lower()
            if conf == 'y': make_req("POST", "/shutdown", token=token)
        elif choice == "6":
            if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
            token = ""
            print("\n[+] Logged out successfully.")
            interactive_admin() # Restart login loop
            return
        elif choice == "7":
            break
        else:
            print("[!] Invalid choice. Try again.\n")

if __name__ == "__main__":
    try:
        if IS_PUBLIC: interactive_public()
        else: interactive_admin()
    except KeyboardInterrupt:
        print("\n\n[+] Exiting application...")
        sys.exit(0)