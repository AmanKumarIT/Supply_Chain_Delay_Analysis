import { useState, useEffect } from "react";
import MapView from "./components/MapView";
import Dashboard from "./components/Dashboard";
import Alerts from "./components/Alerts";
import { getRoutes } from "./services/api";

function App() {
  const [routes, setRoutes] = useState([]);
  const [rerouted, setRerouted] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [routeGeometry, setRouteGeometry] = useState([]);
  const [rerouteGeometry, setRerouteGeometry] = useState([]);

  useEffect(() => {
    getRoutes()
      .then((res) => setRoutes(res.data))
      .catch((err) => console.error("Failed to fetch routes", err));
  }, []);

  return (
    <div className="layout-container">
      <Dashboard
        setRerouted={setRerouted}
        setAlerts={setAlerts}
        setRouteGeometry={setRouteGeometry}
        setRerouteGeometry={setRerouteGeometry}
      >
        <MapView
          routes={routes}
          rerouted={rerouted}
          routeGeometry={routeGeometry}
          rerouteGeometry={rerouteGeometry}
        />
      </Dashboard>
      <div style={{ position: 'fixed', bottom: '16px', right: '16px', zIndex: 50 }}>
        <Alerts alerts={alerts} />
      </div>
    </div>
  );
}

export default App;
