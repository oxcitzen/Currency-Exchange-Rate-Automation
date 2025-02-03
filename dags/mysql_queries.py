import pymysql
from datetime import datetime
import sys


MYSQL_CONFIG = {
    "host": "mysql",
    "user": "root",
    "password": "root",
    "database": "mysql",
}

def run_mysql_queries(**kwargs):
    try:
        
        connection = pymysql.connect(**MYSQL_CONFIG)
        print("Successfully connected to MySQL")
        print(datetime.now())
        
        cursor = connection.cursor()
        
        
        create_table_query = """
            CREATE TABLE IF NOT EXISTS currency_exchange_rates (
                currency VARCHAR(20),
                rate FLOAT,
                date DATE,
                PRIMARY KEY (currency, date)
            );
        """
        
        truncate_table_query = "TRUNCATE TABLE currency_exchange_rates;"
        
        current_time = datetime.now().strftime("%Y%m%d_%H%M") 
        
        load_data_query = f"""
            LOAD DATA INFILE '/store_files_mysql/currency_rates.csv'
            INTO TABLE currency_exchange_rates
            FIELDS TERMINATED BY ','
            LINES TERMINATED BY '\n'
            IGNORE 1 ROWS
            (currency, rate, date);
        """
        
        output_file_path = f"/store_files_mysql/currency_rates_{current_time}.csv"
       
        
        # Push the file name to XCom
        task_instance = kwargs['ti']
        task_instance.xcom_push(key="output_file_path", value=current_time)
        print(f"Pushed {current_time} to XCom")
        
        
        #Sort rows based on currency and date
        transform_query = f"""
            SELECT * 
            FROM currency_exchange_rates 
            ORDER BY currency ASC, date DESC
            INTO OUTFILE '{output_file_path}' 
            FIELDS TERMINATED BY ',' 
            LINES TERMINATED BY '\n';

        """
        
        cursor.execute(create_table_query)
        print("Executed: CREATE TABLE query")
        
        cursor.execute(truncate_table_query)
        print("Executed: TRUNCATE TABLE query")
        
        cursor.execute(load_data_query)
        print("Executed: LOAD DATA query")
        
        cursor.execute(transform_query)
        print("Executed: transform_query")
        
        connection.commit()
        cursor.close()
        connection.close()
        print("All queries executed successfully.")
        print("Connection closed")
        
    except pymysql.MySQLError as e:
        print(f"MySQL error occurred: {e}")
        if 'connection' in locals():
            connection.rollback()  
        sys.exit(1)  
        
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        if 'connection' in locals():
            connection.rollback()  
        sys.exit(1)  

if __name__ == "__main__":
    run_mysql_queries()