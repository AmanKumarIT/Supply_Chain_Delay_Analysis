from neo4j import GraphDatabase
from app.core.config import settings

class GraphService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )

    def close(self):
        self.driver.close()

    def get_routes(self):
        query = """
            MATCH (a:City)-[r:ROUTE]->(b:City)
            RETURN a.name AS source, b.name AS target,
                   r.time AS time, r.cost AS cost, r.distance AS distance
        """
        try:
            with self.driver.session() as session:
                return session.run(query).data()
        except Exception as e:
            print(f"Neo4j connection failed, using fallback routes: {e}")
            return [
                {"source": "Delhi", "target": "Mumbai", "time": 14.0, "cost": 3000.0, "distance": 1400.0},
                {"source": "Mumbai", "target": "Chennai", "time": 18.0, "cost": 4500.0, "distance": 1330.0},
                {"source": "Delhi", "target": "Chennai", "time": 30.0, "cost": 8000.0, "distance": 2200.0}
            ]

    def get_all_nodes(self):
        query = "MATCH (c:City) RETURN c.name AS name"
        try:
            with self.driver.session() as session:
                return [record["name"] for record in session.run(query)]
        except Exception:
            return ["Delhi", "Mumbai", "Chennai"]
