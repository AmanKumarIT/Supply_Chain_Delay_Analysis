import { MapContainer, TileLayer, Polyline, CircleMarker, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const CITY_COORDS = {
  Delhi:     [28.6139, 77.2090],
  Mumbai:    [19.0760, 72.8777],
  Chennai:   [13.0827, 80.2707],
  Kolkata:   [22.5726, 88.3639],
  Bangalore: [12.9716, 77.5946],
  Hyderabad: [17.3850, 78.4867],
  Ahmedabad: [23.0225, 72.5714],
  Pune:      [18.5204, 73.8567],
  Jaipur:    [26.9124, 75.7873],
  Lucknow:   [26.8467, 80.9462],
};

export default function MapView({ routes, rerouted, routeGeometry, rerouteGeometry }) {
  return (
    <MapContainer center={[20.5937, 78.9629]} zoom={5} style={{ height: "100%", width: "100%" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

      {/* City markers */}
      {Object.entries(CITY_COORDS).map(([city, pos]) => (
        <CircleMarker key={city} center={pos} radius={6} color="#00F2FF" fillColor="#00F2FF" fillOpacity={0.6} weight={2}>
          <Tooltip permanent direction="top" offset={[0, -10]}>
            <span style={{ fontFamily: "'Manrope', sans-serif", fontWeight: 700, fontSize: '11px', letterSpacing: '0.05em' }}>{city.toUpperCase()}</span>
          </Tooltip>
        </CircleMarker>
      ))}

      {/* Fallback: straight-line routes when no road geometry */}
      {(!routeGeometry || routeGeometry.length === 0) && routes.map((route, i) => {
        const from = CITY_COORDS[route.source];
        const to   = CITY_COORDS[route.target];
        if (!from || !to) return null;
        return (
          <Polyline
            key={`route-${i}`}
            positions={[from, to]}
            color="#1b998b"
            weight={2}
            opacity={0.4}
            dashArray="8 4"
          />
        );
      })}

      {/* Real road geometry — primary route */}
      {routeGeometry && routeGeometry.length > 0 && (
        <Polyline
          positions={routeGeometry}
          color="#00F2FF"
          weight={3}
          opacity={0.9}
        />
      )}

      {/* Reroute geometry — alternative route in magenta */}
      {rerouteGeometry && rerouteGeometry.length > 0 && (
        <Polyline
          positions={rerouteGeometry}
          color="#fe00fe"
          weight={3}
          opacity={0.8}
          dashArray="6 3"
        />
      )}
    </MapContainer>
  );
}
