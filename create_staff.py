import sys
import os

# Add Services to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Services'))

try:
    from Staff import Staff, Management, CSStaff, Driver, RepoStaff
    from Location import Repository
    from Vehicle import Minivan
except ImportError as e:
    print(f"Error importing services: {e}")
    sys.exit(1)

def create_staff():
    print("--- Create Staff Account ---")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    password = input("Password: ")
    
    print("\nSelect Role:")
    print("1. Management")
    print("2. CS Staff")
    print("3. Driver (Requires Vehicle)")
    print("4. Repo Staff (Requires Repository)")
    
    choice = input("Enter choice (1-4): ")
    
    try:
        if choice == '1':
            staff = Management(first_name, last_name, "Management", password)
        elif choice == '2':
            staff = CSStaff(first_name, last_name, "CS Staff", password)
        elif choice == '3':
            # Simplified for demo - usually would select existing vehicle
            plate = input("Enter Vehicle License Plate: ")
            vehicle = Minivan(plate) 
            staff = Driver(first_name, last_name, "Driver", password, vehicle)
        elif choice == '4':
            # Simplified for demo
            repo_name = input("Enter Repository Name: ")
            address = input("Enter Repository Address: ")
            repo = Repository(address, repo_name)
            staff = RepoStaff(first_name, last_name, "Repo Staff", password, repo)
        else:
            print("Invalid choice.")
            return

        staff.save()
        print(f"\nSUCCESS: Staff created with ID: {staff.ID}")
        print("You can now login with this ID.")
        
    except Exception as e:
        print(f"Error creating staff: {e}")

if __name__ == "__main__":
    create_staff()
