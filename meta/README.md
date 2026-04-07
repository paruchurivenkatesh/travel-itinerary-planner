# Travel Itinerary Planner

**"Because planning a great vacation requires more than just picking tourist sites."** ✈️

This OpenEnv environment transforms AI agents into travel planners, building destination itineraries with budget and schedule constraints. Agents must choose activities, satisfy required stops, and manage trip budgets across increasing difficulty.

### Why This Environment Works:
- **Real-World Application**: Travel planning is a common task that requires optimization and preference management.
- **Practical Design**: Agents practice budgeting, required stops, and variety of activities.
- **Professional Depth**: Full reinforcement learning with meaningful rewards and constraints.

## Description

The Travel Itinerary Planner is a reinforcement learning environment where an AI agent must plan a travel itinerary by selecting activities within budget constraints. The environment simulates real-world travel planning tasks with varying levels of complexity.

### Environment Details

- **Observation Space**: Current day, selected activities, remaining budget, trip duration, destination, and list of available activities.
- **Action Space**: Add or remove activities by ID, or finish planning.
- **Reward Function**: Partial rewards for adding activities (higher for required activities), penalties for invalid actions, final score based on required activities included, budget efficiency, and activity variety.
- **Episode Termination**: When agent chooses to finish, budget is exhausted, or maximum steps reached.

### Tasks

- **Easy**: Plan a 1-day trip to Paris with a $500 budget. Must include the Eiffel Tower.
- **Medium**: Plan a 3-day trip to Tokyo with a $1000 budget. Must include Mount Fuji and Shibuya Crossing.
- **Hard**: Plan a 7-day Europe tour with a $2000 budget. Must include Eiffel Tower, Colosseum, and Big Ben.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/travel-itinerary-planner-env.git
   cd travel-itinerary-planner-env
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Local Development

1. Run the environment locally:
   ```python
   from travel_itinerary_planner import TravelItineraryPlannerEnv

   env = TravelItineraryPlannerEnv(task="easy")  # Paris itinerary
   obs = env.reset()
   print(f"Destination: {obs.destination}")  # Paris
   print(f"Budget left: {obs.budget_left}")  # 500.0
   print("Available activities:", [a["name"] for a in obs.available_activities])
   ```
   ```

2. Run the web server:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 7860
   ```

3. Test the API:
   - POST /reset: Launch new itinerary
   - POST /step: Take planning action (body: {"action_type": "add_activity", "activity_id": 0})
   - GET /state: Get current trip status

## Baseline Inference

To run the baseline with OpenAI API:

1. Set environment variables:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   export API_BASE_URL="https://api.openai.com/v1"  # or your custom endpoint
   export MODEL_NAME="gpt-3.5-turbo"
   export HF_TOKEN="your-hf-token"  # if needed
   export TASK="easy"  # Choose: easy (Paris), medium (Tokyo), hard (Europe)
   ```

2. Run inference:
   ```bash
   python inference.py
   ```

This will run episodes for all tasks and output structured logs.

## Deployment to Hugging Face Spaces

1. Create a new Space on Hugging Face:
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Choose "Docker" as the SDK
   - Connect your GitHub repository

2. The Space will automatically build and deploy using the Dockerfile.

3. Your Space URL will be something like: https://yourusername-travel-itinerary-planner.hf.space

4. The Space should respond to:
   - Health check: GET /health
   - Environment API: POST /reset, POST /step, GET /state

## Docker Build (Local Testing)

```bash
docker build -t travel-itinerary-planner .
docker run -p 7860:7860 travel-itinerary-planner
```

## Testing

Run the test suite:

```bash
pip install pytest
python -m pytest tests/ -v
```

All 8 tests should pass, covering initialization, actions, rewards, and scoring.

## Project Structure

```
travel-itinerary-planner-env/
├── travel_itinerary_planner/
│   ├── __init__.py
│   └── env.py
├── app.py
├── inference.py
├── openenv.yaml
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── README.md
└── .gitignore
```

## API Specification

### Models

- **Action**: `{"action_type": str, "activity_id": int | null}`
- **Observation**: `{"current_day": int, "selected_activities": [str], "budget_left": float, "total_days": int, "destination": str, "available_activities": [dict]}`
- **Reward**: `{"value": float, "explanation": str}`
- **Info**: `{"message": str}`

### Endpoints

- `POST /reset` → `Observation`
- `POST /step` (Action) → `{"observation": Observation, "reward": Reward, "done": bool, "info": Info}`
- `GET /state` → `Observation`
- `GET /health` → `{"status": "healthy"}`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Run tests
5. Submit a pull request

## License

MIT License