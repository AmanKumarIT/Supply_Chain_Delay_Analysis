// Create city nodes
CREATE (:City {name: "Delhi"})
CREATE (:City {name: "Mumbai"})
CREATE (:City {name: "Chennai"})

// Create weighted route edges
MATCH (a:City {name: "Delhi"}), (b:City {name: "Mumbai"})
CREATE (a)-[:ROUTE {time: 10, cost: 100, distance: 1400}]->(b)

MATCH (a:City {name: "Mumbai"}), (b:City {name: "Chennai"})
CREATE (a)-[:ROUTE {time: 8, cost: 80, distance: 1340}]->(b)

MATCH (a:City {name: "Delhi"}), (b:City {name: "Chennai"})
CREATE (a)-[:ROUTE {time: 16, cost: 160, distance: 2200}]->(b)
