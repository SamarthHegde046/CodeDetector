# init_database.py - Initialize MongoDB Database with Schema and Sample Data

from models import Database, UserModel, JobModel, ApplicationModel
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def init_database_with_sample_data():
    """Initialize database with schema and optional sample data"""
    
    print("=" * 60)
    print("MongoDB Database Initialization Script")
    print("=" * 60)
    print()
    
    # Initialize database
    print("Step 1: Connecting to MongoDB...")
    db = Database()
    print("✓ Connected successfully!")
    print()
    
    # Create collections with schema validation
    print("Step 2: Creating collections with schema validation...")
    db.initialize_collections()
    print()
    
    # Create indexes
    print("Step 3: Creating database indexes...")
    db.create_indexes()
    print()
    
    # Initialize models
    user_model = UserModel(db.db)
    job_model = JobModel(db.db)
    application_model = ApplicationModel(db.db)
    
    print("=" * 60)
    print("Database Schema Created Successfully!")
    print("=" * 60)
    print()
    
    # Ask if user wants sample data
    response = input("Do you want to add sample data for testing? (yes/no): ").lower()
    
    if response == 'yes' or response == 'y':
        print("\nAdding sample data...")
        add_sample_data(user_model, job_model, application_model)
    else:
        print("\nSkipping sample data creation.")
    
    print()
    print("=" * 60)
    print("Database Initialization Complete!")
    print("=" * 60)
    print()
    print("You can now start your Flask application:")
    print("  python app.py")
    print()


def add_sample_data(user_model, job_model, application_model):
    """Add sample data for testing"""
    
    # Sample Recruiters
    recruiters = [
        {
            'email': 'recruiter1@techcorp.com',
            'password': 'password123',
            'name': 'John Smith',
            'company': 'TechCorp Solutions',
            'role': 'recruiter'
        },
        {
            'email': 'recruiter2@innovateai.com',
            'password': 'password123',
            'name': 'Sarah Johnson',
            'company': 'InnovateAI Labs',
            'role': 'recruiter'
        },
        {
            'email': 'recruiter3@cloudtech.com',
            'password': 'password123',
            'name': 'Michael Chen',
            'company': 'CloudTech Industries',
            'role': 'recruiter'
        }
    ]
    
    # Sample Candidates
    candidates = [
        {
            'email': 'candidate1@email.com',
            'password': 'password123',
            'name': 'Alice Williams',
            'role': 'candidate',
            'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'MongoDB']
        },
        {
            'email': 'candidate2@email.com',
            'password': 'password123',
            'name': 'Bob Martinez',
            'role': 'candidate',
            'skills': ['Java', 'Spring Boot', 'MySQL', 'Docker', 'Kubernetes']
        },
        {
            'email': 'candidate3@email.com',
            'password': 'password123',
            'name': 'Carol Davis',
            'role': 'candidate',
            'skills': ['Python', 'Django', 'PostgreSQL', 'AWS', 'Machine Learning']
        },
        {
            'email': 'candidate4@email.com',
            'password': 'password123',
            'name': 'David Lee',
            'role': 'candidate',
            'skills': ['React', 'TypeScript', 'GraphQL', 'Next.js', 'TailwindCSS']
        }
    ]
    
    print("\n  Creating recruiters...")
    recruiter_ids = []
    for rec in recruiters:
        password = rec.pop('password')
        password_hash = generate_password_hash(password)
        
        rec_id = user_model.create_user(
            email=rec['email'],
            password_hash=password_hash,
            role=rec['role'],
            name=rec['name'],
            company=rec['company']
        )
        recruiter_ids.append(str(rec_id))
        print(f"    ✓ Created {applications_created} applications")
    
    print("\n  Sample data creation complete!")
    print()
    print("  Test Accounts Created:")
    print("  " + "=" * 56)
    print("\n  Recruiters:")
    for rec in recruiters:
        print(f"    Email: {rec['email']}")
        print(f"    Password: password123")
        print(f"    Company: {rec['company']}")
        print()
    
    print("  Candidates:")
    for cand in candidates:
        print(f"    Email: {cand['email']}")
        print(f"    Password: password123")
        print(f"    Name: {cand['name']}")
        print()
    
    print(f"  Total Jobs Created: {len(job_ids)}")
    print(f"  Total Applications: {applications_created}")


def verify_database():
    """Verify database setup"""
    print("\nVerifying database setup...")
    print("-" * 60)
    
    db = Database()
    
    # Check collections
    collections = db.db.list_collection_names()
    print(f"\n✓ Collections found: {', '.join(collections)}")
    
    # Count documents
    user_count = db.db.users.count_documents({})
    job_count = db.db.jobs.count_documents({})
    app_count = db.db.applications.count_documents({})
    
    print(f"\nDocument counts:")
    print(f"  Users: {user_count}")
    print(f"  Jobs: {job_count}")
    print(f"  Applications: {app_count}")
    
    # Check indexes
    print(f"\nIndexes:")
    print(f"  Users: {len(list(db.db.users.list_indexes()))} indexes")
    print(f"  Jobs: {len(list(db.db.jobs.list_indexes()))} indexes")
    print(f"  Applications: {len(list(db.db.applications.list_indexes()))} indexes")
    
    print("\n✓ Database verification complete!")


def reset_database():
    """Reset database - delete all data"""
    print("\n" + "!" * 60)
    print("WARNING: This will delete ALL data from the database!")
    print("!" * 60)
    
    response = input("\nAre you sure you want to reset the database? (yes/no): ").lower()
    
    if response == 'yes':
        db = Database()
        
        print("\nDeleting all collections...")
        db.db.users.drop()
        db.db.jobs.drop()
        db.db.applications.drop()
        
        print("✓ All collections deleted!")
        print("\nRe-initializing schema...")
        
        db.initialize_collections()
        db.create_indexes()
        
        print("✓ Database reset complete!")
    else:
        print("\nReset cancelled.")


def show_menu():
    """Show interactive menu"""
    while True:
        print("\n" + "=" * 60)
        print("MongoDB Database Manager")
        print("=" * 60)
        print("\n1. Initialize Database (with schema)")
        print("2. Initialize with Sample Data")
        print("3. Verify Database")
        print("4. Reset Database (DELETE ALL DATA)")
        print("5. Exit")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            db = Database()
            db.initialize_collections()
            db.create_indexes()
            print("\n✓ Database initialized successfully!")
            
        elif choice == '2':
            init_database_with_sample_data()
            
        elif choice == '3':
            verify_database()
            
        elif choice == '4':
            reset_database()
            
        elif choice == '5':
            print("\nGoodbye!")
            break
            
        else:
            print("\n❌ Invalid choice. Please try again.")

