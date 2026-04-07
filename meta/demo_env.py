#!/usr/bin/env python3
"""
Simple test script to run the Travel Itinerary Planner environment manually.
This demonstrates the environment without requiring API keys.
"""

from travel_itinerary_planner import TravelItineraryPlannerEnv, Action

def test_task(task_name):
    print(f"\n=== Testing {task_name.upper()} Task ===")
    env = TravelItineraryPlannerEnv(task=task_name)
    obs = env.reset()
    print("Initial observation:")
    print(f"  Day: {obs.current_day}")
    print(f"  Budget: ${obs.budget_left}")
    print(f"  Destination: {obs.destination}")
    print(f"  Available activities: {len(obs.available_activities)}")

    # Simulate some actions
    actions = [
        Action(action_type="add_activity", activity_id=0),  # Add first activity
        Action(action_type="add_activity", activity_id=1),  # Add second
        Action(action_type="finish")  # Finish planning
    ]

    total_reward = 0
    for i, action in enumerate(actions, 1):
        print(f"\nStep {i}: {action.action_type}")
        if action.activity_id is not None:
            activity = next((a for a in obs.available_activities if a['id'] == action.activity_id), None)
            if activity:
                print(f"  Adding: {activity['name']} (${activity['cost']})")

        obs, reward, done, info = env.step(action)
        total_reward += reward.value
        print(f"  Reward: {reward.value} ({reward.explanation})")
        print(f"  Budget left: ${obs.budget_left}")
        print(f"  Selected: {obs.selected_activities}")
        print(f"  Done: {done}")

        if done:
            final_score = env._grade()
            print(f"  Final score: {final_score}")
            break

    print(f"Total reward: {total_reward}")

def main():
    print("Testing Travel Itinerary Planner Environment")
    print("=" * 50)

    for task in ["easy", "medium", "hard"]:
        test_task(task)

    print("\n" + "=" * 50)
    print("All tests completed successfully!")

if __name__ == "__main__":
    main()