import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    
    neo4j_uri: str = os.getenv("NEO4J_URI", "")
    neo4j_user: str = os.getenv("NEO4J_USER", "")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "")
    
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "supply_chain")
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    model_path: str = os.getenv("MODEL_PATH", "app/ml/model.pkl")
    reroute_risk_threshold: float = float(os.getenv("REROUTE_RISK_THRESHOLD", "0.6"))
    
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")
    monitor_interval_seconds: int = int(os.getenv("MONITOR_INTERVAL", "30"))

settings = Settings()
