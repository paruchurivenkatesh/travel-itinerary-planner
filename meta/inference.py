"""
Travel Itinerary Planner - Baseline Inference Script
=====================================================
Trains an AI agent to plan travel itineraries with budget and activity constraints.

Environment variables:
  - OPENAI_API_KEY: OpenAI API key (required)
  - API_BASE_URL: API endpoint (default: https://api.openai.com/v1)
  - MODEL_NAME: Model identifier (default: gpt-3.5-turbo)
  - HF_TOKEN: Hugging Face token (optional, for compatibility)

Output Format:
  [START] task=<task_name> env=travel-itinerary-planner model=<model_name>
  [STEP] step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
  [END] success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import os
import sys
import json
from typing import List, Optional, Tuple
from openai import OpenAI
from travel_itinerary_planner import TravelItineraryPlannerEnv, Action

# Environment configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.getenv("HF_TOKEN")  # For compatibility; not required

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY, base_url=API_BASE_URL)

# Constants
TASKS = ["easy", "medium", "hard"]
MAX_STEPS_PER_TASK = 20
BENCHMARK_NAME = "travel-itinerary-planner"


def log_start(task: str, env: str, model: str) -> None:
    """Emit [START] log line."""
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action_str: str, reward: float, done: bool, error: Optional[str]) -> None:
    """Emit [STEP] log line."""
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action_str} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    """Emit [END] log line."""
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


def sanitize_action_string(action: Action) -> str:
    """Convert action to a readable string for logging."""
    if action.activity_id is not None:
        return f"{action.action_type}({action.activity_id})"
    return action.action_type


def get_action_from_model(observation: dict, available_actions: list) -> Action:
    """Get action from the LLM model."""
    prompt = f"""
You are an AI travel planner building a vacation itinerary. Your goal is to select activities that maximize your trip score.

Current trip status:
- Day: {observation['current_day']}
- Selected activities: {observation['selected_activities']}
- Budget left: ${observation['budget_left']:.2f}
- Total days: {observation['total_days']}
- Destination: {observation['destination']}

Available activities:
{json.dumps(observation['available_activities'], indent=2)}

Instructions:
- Choose the best action to add/remove activities or finish planning.
- Required activities give the highest rewards.
- Aim for variety across activity types.
- Don't exceed the budget.

Output a JSON object:
{{
  "action_type": "add_activity" | "remove_activity" | "finish",
  "activity_id": <integer or null>
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        action_data = json.loads(response.choices[0].message.content.strip())
        return Action(**action_data)
    except Exception:
        # Fallback: finish if any error occurs
        return Action(action_type="finish")


def run_episode(task: str, max_steps: int = MAX_STEPS_PER_TASK) -> Tuple[bool, int, float, List[float]]:
    """
    Run one episode for the given task.
    
    Returns:
        (success, steps_taken, final_score, list_of_rewards)
    """
    env = TravelItineraryPlannerEnv(task=task)
    obs = env.reset()
    
    rewards: List[float] = []
    steps_taken = 0
    success = False
    error_msg: Optional[str] = None
    
    log_start(task=task, env=BENCHMARK_NAME, model=MODEL_NAME)
    
    try:
        for step in range(1, max_steps + 1):
            if env.done:
                break
            
            # Get action from model
            action = get_action_from_model(obs.model_dump(), env.activities)
            action_str = sanitize_action_string(action)
            
            # Take step in environment
            obs, reward, done, info = env.step(action)
            
            reward_value = reward.value
            rewards.append(reward_value)
            steps_taken = step
            
            # Log the step
            log_step(
                step=step,
                action_str=action_str,
                reward=reward_value,
                done=done,
                error=error_msg
            )
            
            if done:
                break
        
        # Compute final score
        final_score = env._grade()
        final_score = min(max(final_score, 0.0), 1.0)  # Clamp to [0, 1]
        success = final_score > 0.0
        
    except Exception as e:
        error_msg = str(e)
        final_score = 0.0
        success = False
    
    finally:
        log_end(success=success, steps=steps_taken, score=final_score, rewards=rewards)
    
    return success, steps_taken, final_score, rewards


def main():
    """Run baseline inference on all tasks."""
    task_results = {}
    
    for task in TASKS:
        try:
            success, steps, score, rewards = run_episode(task)
            task_results[task] = {
                "success": success,
                "steps": steps,
                "score": score,
                "reward_count": len(rewards)
            }
        except Exception as e:
            print(f"Error running task {task}: {e}", file=sys.stderr)
            task_results[task] = {
                "success": False,
                "steps": 0,
                "score": 0.0,
                "reward_count": 0
            }


if __name__ == "__main__":
    main()
