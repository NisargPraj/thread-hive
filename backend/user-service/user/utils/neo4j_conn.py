from neo4j import GraphDatabase
from django.conf import settings
import os


class Neo4jConnection:
    def __init__(self, uri, username, password):
        if not uri or not username or not password:
            raise ValueError("Missing Neo4j connection parameters. Ensure NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD are set.")

        self._driver = GraphDatabase.driver(uri, auth=(username, password))


    def close(self):
        self._driver.close()

    def query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]


# Initialize the connection using settings
neo4j_connection = Neo4jConnection(
    uri=settings.NEO4J_URI,
    username=settings.NEO4J_USERNAME,
    password=settings.NEO4J_PASSWORD
)
