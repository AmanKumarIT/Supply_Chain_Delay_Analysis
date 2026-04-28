import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const client = axios.create({ baseURL: BASE_URL });

export const getRoutes    = ()                  => client.get("/routes");
export const getStatus    = ()                  => client.get("/status");
export const simulate     = (payload)           => client.post("/simulate", payload);
export const reroute      = (payload)           => client.post("/reroute", payload);
export const monitorRoute = (source, target)    => client.get(`/monitor?source=${source}&target=${target}`);
