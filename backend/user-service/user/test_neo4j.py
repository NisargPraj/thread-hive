import os
import sys

# Add the root directory of your project to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the environment variable for Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from .utils.neo4j_conn import neo4j_connection

def test_neo4j_connection():
    try:
        query = "RETURN 'Connection Successful' AS message"
        result = neo4j_connection.query(query)
        for record in result:
            print(f"Query result: {record['message']}")
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")

if __name__ == "__main__":
    test_neo4j_connection()
