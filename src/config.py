from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    larpan1_url: str = Field(..., description="The URL of the LARPAn1 core API endpoint")
    mongo_uri: str = Field(..., description="MongoDB URI for database state")
    nitter_instances: str = Field(default="https://nitter.net", description="Comma-separated Nitter instance URLs")
    nitter_topics: str = Field(..., description="Comma-separated topics to monitor")
    poll_interval_minutes: int = Field(default=15, ge=1, description="How often to poll Nitter RSS feeds in minutes")
    
    groq_api_key: str = Field(..., description="Groq API Key for DSPy models")
    nvidia_api_key: str = Field(..., description="NVIDIA API Key for Mistral Gatekeeper")
    
    ifttt_webhook_key: str = Field(..., description="IFTTT Webhook Key")
    ifttt_event_name: str = Field(..., description="IFTTT Event Name")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def instances_list(self) -> List[str]:
        return [i.strip() for i in self.nitter_instances.split(",") if i.strip()]

    @property
    def topics_list(self) -> List[str]:
        return [t.strip() for t in self.nitter_topics.split(",") if t.strip()]

settings = Settings()
