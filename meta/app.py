from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from travel_itinerary_planner import TravelItineraryPlannerEnv, Action, Observation, Reward, Info
import os

# Global environment instance - in production, consider session management
env = None

def get_env() -> TravelItineraryPlannerEnv:
    global env
    if env is None:
        task = os.getenv("TASK", "easy")  # Allow setting task via env var
        env = TravelItineraryPlannerEnv(task=task)
    return env

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    get_env()
    yield
    # Shutdown (if needed)
    pass

app = FastAPI(
    title="Travel Itinerary Planner",
    description="API for planning travel itineraries with budget and activity constraints.",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/reset", response_model=Observation)
async def reset():
    """Reset the environment and return initial observation."""
    env_instance = get_env()
    obs = env_instance.reset()
    return obs

@app.post("/step")
async def step(action: Action):
    """Take a step in the environment."""
    env_instance = get_env()
    try:
        obs, reward, done, info = env_instance.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": reward.model_dump(),
            "done": done,
            "info": info.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state", response_model=Observation)
async def get_state():
    """Get the current state of the environment."""
    env_instance = get_env()
    return env_instance.state()

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)