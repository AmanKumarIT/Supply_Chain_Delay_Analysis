from fastapi import APIRouter
from app.api.endpoints import simulate, reroute, status, routes, monitor

router = APIRouter()
router.include_router(simulate.router, prefix="/simulate", tags=["Simulation"])
router.include_router(reroute.router,  prefix="/reroute",  tags=["Rerouting"])
router.include_router(status.router,   prefix="/status",   tags=["Status"])
router.include_router(routes.router,   prefix="/routes",   tags=["Routes"])
router.include_router(monitor.router,  prefix="/monitor",  tags=["Monitoring"])
