"""
GeoRoutingService — Uses OSMnx to compute real road-following routes
between cities. Falls back to interpolated straight lines if OSMnx
graph download fails (e.g., network issues, large area).

The city-level logical routing decisions (which cities to traverse)
are still handled by NetworkX in routing_service.py. This service
resolves those logical hops into actual road geometry.
"""
import osmnx as ox
import networkx as nx
import math
from typing import List, Tuple, Dict, Optional
from functools import lru_cache

ox.settings.log_console = True
ox.settings.use_cache = True


# City coordinates for geocoding (avoiding external geocoder calls)
CITY_COORDS: Dict[str, Tuple[float, float]] = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Bangalore": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Ahmedabad": (23.0225, 72.5714),
    "Pune": (18.5204, 73.8567),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
}


class GeoRoutingService:
    _graph_cache: Optional[nx.MultiDiGraph] = None

    @classmethod
    def _get_graph(cls) -> Optional[nx.MultiDiGraph]:
        """
        Download the India driving network via OSMnx. This is cached
        after the first successful download. For the first call this
        can take 1-3 minutes depending on network speed.
        
        We use a bbox around the Indian subcontinent to avoid downloading
        the entire planet.
        """
        if cls._graph_cache is not None:
            return cls._graph_cache

        try:
            print("[GeoRouting] Downloading road network (first time only)...")
            # Use a bounding box covering most of India
            # North, South, East, West
            G = ox.graph_from_bbox(
                bbox=(8.0, 35.0, 68.0, 97.5),
                network_type="drive",
                truncate_by_edge=True,
            )
            cls._graph_cache = G
            print(f"[GeoRouting] Road network loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")
            return G
        except Exception as e:
            print(f"[GeoRouting] OSMnx download failed: {e}")
            print("[GeoRouting] Falling back to interpolated routes")
            return None

    @staticmethod
    def get_city_coords(city_name: str) -> Optional[Tuple[float, float]]:
        """Get lat, lng for a known city name."""
        return CITY_COORDS.get(city_name)

    @staticmethod
    def _interpolate_route(
        start: Tuple[float, float], end: Tuple[float, float], num_points: int = 30
    ) -> List[List[float]]:
        """
        Generate a curved interpolated route between two points.
        Adds a slight arc to make routes visually distinguishable from
        straight lines even in fallback mode.
        """
        points = []
        for i in range(num_points + 1):
            t = i / num_points
            lat = start[0] + t * (end[0] - start[0])
            lng = start[1] + t * (end[1] - start[1])

            # Add a slight perpendicular arc offset (Great Circle approximation)
            arc = math.sin(t * math.pi) * 0.8  # arc magnitude in degrees
            # Direction perpendicular to the route
            dx = end[1] - start[1]
            dy = end[0] - start[0]
            length = math.sqrt(dx * dx + dy * dy) or 1
            perp_lat = -dx / length
            perp_lng = dy / length

            lat += perp_lat * arc
            lng += perp_lng * arc
            points.append([round(lat, 6), round(lng, 6)])

        return points

    def get_road_geometry(
        self, origin_city: str, dest_city: str
    ) -> Dict:
        """
        Compute the road-following geometry between two cities.

        Returns:
            {
                "coords": [[lat, lng], ...],
                "distance_km": float,
                "source_coords": [lat, lng],
                "target_coords": [lat, lng],
                "method": "osmnx" | "interpolated"
            }
        """
        origin = self.get_city_coords(origin_city)
        dest = self.get_city_coords(dest_city)

        if not origin or not dest:
            return {
                "coords": [],
                "distance_km": 0,
                "source_coords": list(origin) if origin else [],
                "target_coords": list(dest) if dest else [],
                "method": "error",
                "error": f"Unknown city: {origin_city if not origin else dest_city}",
            }

        G = self._get_graph()

        if G is not None:
            try:
                orig_node = ox.nearest_nodes(G, origin[1], origin[0])
                dest_node = ox.nearest_nodes(G, dest[1], dest[0])

                route = ox.shortest_path(G, orig_node, dest_node, weight="length")

                if route is None:
                    raise ValueError("No route found")

                # Extract coordinates from the route
                coords = []
                for node in route:
                    node_data = G.nodes[node]
                    coords.append([node_data["y"], node_data["x"]])

                # Calculate total distance
                edge_lengths = ox.routing.route_to_gdf(G, route)
                total_distance = edge_lengths["length"].sum() / 1000  # meters -> km

                return {
                    "coords": coords,
                    "distance_km": round(total_distance, 2),
                    "source_coords": list(origin),
                    "target_coords": list(dest),
                    "method": "osmnx",
                }

            except Exception as e:
                print(f"[GeoRouting] OSMnx routing failed ({origin_city}->{dest_city}): {e}")
                # Fall through to interpolation

        # Fallback: interpolated arc
        coords = self._interpolate_route(origin, dest)
        # Haversine distance estimate
        dist_km = self._haversine(origin[0], origin[1], dest[0], dest[1])

        return {
            "coords": coords,
            "distance_km": round(dist_km, 2),
            "source_coords": list(origin),
            "target_coords": list(dest),
            "method": "interpolated",
        }

    def get_multi_hop_geometry(self, city_path: List[str]) -> Dict:
        """
        Given a list of city names (a logical path from NetworkX),
        compute the full road geometry by chaining segment-level routes.
        """
        all_coords = []
        total_distance = 0
        segments = []
        method = "interpolated"

        for i in range(len(city_path) - 1):
            segment = self.get_road_geometry(city_path[i], city_path[i + 1])
            segments.append(segment)

            if segment["method"] == "osmnx":
                method = "osmnx"

            # Avoid duplicating the junction point
            if all_coords and segment["coords"]:
                all_coords.extend(segment["coords"][1:])
            else:
                all_coords.extend(segment["coords"])

            total_distance += segment["distance_km"]

        return {
            "coords": all_coords,
            "distance_km": round(total_distance, 2),
            "city_path": city_path,
            "segments": len(segments),
            "method": method,
        }

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine distance in kilometers."""
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        return R * 2 * math.asin(math.sqrt(a))
