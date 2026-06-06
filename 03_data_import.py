import pandas as pd
import mysql.connector
from mysql.connector import Error
import sys

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Anushka@18',  # Change this to your MySQL password
    'database': 'job_market_db'
}

def connect_to_db():
    """Establish connection to MySQL database"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("[OK] Connected to MySQL database")
            return connection
    except Error as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

def insert_company(cursor, company_name, company_description):
    """Insert or get company_id"""
    try:
        query = "SELECT company_id FROM companies WHERE company_name = %s"
        cursor.execute(query, (company_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        insert_query = "INSERT INTO companies (company_name, company_description) VALUES (%s, %s)"
        cursor.execute(insert_query, (company_name, company_description))
        return cursor.lastrowid
        
    except Exception as e:
        return None

def insert_location(cursor, city, state, country):
    """Insert or get location_id"""
    try:
        query = "SELECT location_id FROM locations WHERE city = %s AND state = %s AND country = %s"
        cursor.execute(query, (city, state, country))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        insert_query = "INSERT INTO locations (city, state, country) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (city, state, country))
        return cursor.lastrowid
        
    except Exception as e:
        return None

def insert_job(cursor, row, company_id, location_id):
    """Insert job record"""
    try:
        query = """
        INSERT INTO jobs 
        (job_id, job_title, company_id, location_id, job_description, 
         job_type, is_remote, posting_date, job_link, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            str(row['job_id']),
            str(row['job_title'])[:255],
            company_id,
            location_id,
            str(row['job_description']),
            str(row['job_type'])[:50],
            int(row['is_remote']),
            row['posting_date'],
            str(row['job_link'])[:500],
            str(row['category'])[:100]
        )
        
        cursor.execute(query, values)
        
    except Exception as e:
        raise

def import_jobs_data(connection, csv_file):
    """Import jobs data from CSV to MySQL"""
    print(f"\nImporting jobs from {csv_file}...")
    
    try:
        df_jobs = pd.read_csv(csv_file)
        cursor = connection.cursor()
        
        total_jobs = 0
        failed_jobs = 0
        
        for idx, row in df_jobs.iterrows():
            try:
                company_id = insert_company(cursor, row['company_name'], row['company_description'])
                location_id = insert_location(cursor, row['city'], row['state'], row['country'])
                insert_job(cursor, row, company_id, location_id)
                
                total_jobs += 1
                
                if (idx + 1) % 100 == 0:
                    print(f"  Processed {idx + 1} jobs...")
                    connection.commit()
                    
            except Exception as e:
                failed_jobs += 1
                continue
        
        connection.commit()
        print(f"[OK] Jobs imported: {total_jobs} success, {failed_jobs} failed")
        return total_jobs
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return 0

def import_skills_data(connection, csv_file):
    """Import skills data from CSV to MySQL"""
    print(f"\nImporting skills from {csv_file}...")
    
    try:
        df_skills = pd.read_csv(csv_file)
        cursor = connection.cursor()
        
        unique_skills = df_skills['skill'].unique()
        print(f"Found {len(unique_skills)} unique skills")
        
        skill_map = {}
        for skill in unique_skills:
            try:
                query = "SELECT skill_id FROM skills WHERE skill_name = %s"
                cursor.execute(query, (skill,))
                result = cursor.fetchone()
                
                if result:
                    skill_map[skill] = result[0]
                else:
                    insert_query = "INSERT INTO skills (skill_name) VALUES (%s)"
                    cursor.execute(insert_query, (skill,))
                    skill_map[skill] = cursor.lastrowid
                    
            except Exception as e:
                continue
        
        connection.commit()
        print(f"[OK] Skills imported: {len(skill_map)} unique skills")
        
        print("Linking jobs with skills...")
        total_links = 0
        failed_links = 0
        
        for idx, row in df_skills.iterrows():
            try:
                job_id = str(row['job_id'])
                skill_id = skill_map.get(row['skill'])
                
                if skill_id:
                    insert_query = "INSERT INTO job_skills (job_id, skill_id) VALUES (%s, %s)"
                    cursor.execute(insert_query, (job_id, skill_id))
                    total_links += 1
                    
                if (idx + 1) % 1000 == 0:
                    connection.commit()
                    
            except Exception as e:
                failed_links += 1
                continue
        
        connection.commit()
        print(f"[OK] Job-skill links: {total_links} created, {failed_links} failed")
        
    except Exception as e:
        print(f"[ERROR] {e}")

def main():
    print("="*50)
    print("Job Market Analytics - Data Import")
    print("="*50)
    
    connection = connect_to_db()
    
    if not connection:
        print("[ERROR] Failed to connect to database")
        sys.exit(1)
    
    try:
        import_jobs_data(connection, 'cleaned_jobs.csv')
        import_skills_data(connection, 'extracted_skills.csv')
        
        print("\n" + "="*50)
        print("[OK] Data import complete!")
        print("="*50)
        
        cursor = connection.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM companies")
        total_companies = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM locations")
        total_locations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM skills")
        total_skills = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM job_skills")
        total_job_skills = cursor.fetchone()[0]
        
        print(f"\nDatabase Summary:")
        print(f"  Total jobs: {total_jobs}")
        print(f"  Total companies: {total_companies}")
        print(f"  Total locations: {total_locations}")
        print(f"  Total skills: {total_skills}")
        print(f"  Job-skill links: {total_job_skills}")
        
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if connection.is_connected():
            connection.close()
            print("\n[OK] Database connection closed")

if __name__ == "__main__":
    main()