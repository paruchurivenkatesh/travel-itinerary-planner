from travel_itinerary_planner import TravelItineraryPlannerEnv, Action

# Initialize the environment
print("TRAVEL ITINERARY PLANNER ENVIRONMENT DEMONSTRATION")
print("=" * 60)
print()

env = TravelItineraryPlannerEnv(task="easy")
print(f"Created environment for task: {env.task}")
print(f"Destination: {env.destination}")
print(f"Budget: ${env.budget}")
print(f"Total days: {env.total_days}")
print(f"Required activities: {env.required_activities}")
print()

# Show initial observation
obs = env.reset()
print("INITIAL OBSERVATION")
print("-" * 30)
print(f"Current day: {obs.current_day}")
print(f"Selected activities: {obs.selected_activities}")
print(f"Budget left: ${obs.budget_left}")
print(f"Total days: {obs.total_days}")
print(f"Destination: {obs.destination}")
print(f"Available activities: {len(obs.available_activities)}")
print()

# Show available activities
print("AVAILABLE ACTIVITIES")
print("-" * 30)
for activity in obs.available_activities:
    required = "[REQUIRED]" if activity['name'] in env.required_activities else "[OPTIONAL]"
    print(f"ID {activity['id']}: {activity['name']} - ${activity['cost']} ({activity['type']}) {required}")
print()

# Demonstrate actions
print("ACTION DEMONSTRATION")
print("-" * 30)

# Action 1: Add Eiffel Tower (required activity)
print("ACTION 1: Add Eiffel Tower (required)")
action1 = Action(action_type="add_activity", activity_id=0)
obs, reward, done, info = env.step(action1)
print(f"Reward: {reward.value} - {reward.explanation}")
print(f"Budget remaining: ${obs.budget_left}")
print(f"Selected activities: {obs.selected_activities}")
print(f"Done: {done}")
print()

# Action 2: Add Louvre Museum (optional activity)
print("ACTION 2: Add Louvre Museum (optional)")
action2 = Action(action_type="add_activity", activity_id=1)
obs, reward, done, info = env.step(action2)
print(f"Reward: {reward.value} - {reward.explanation}")
print(f"Budget remaining: ${obs.budget_left}")
print(f"Selected activities: {obs.selected_activities}")
print(f"Done: {done}")
print()

# Action 3: Try to add Eiffel Tower again (should fail)
print("ACTION 3: Try to add Eiffel Tower again (duplicate)")
action3 = Action(action_type="add_activity", activity_id=0)
obs, reward, done, info = env.step(action3)
print(f"Reward: {reward.value} - {reward.explanation}")
print(f"Budget remaining: ${obs.budget_left}")
print(f"Selected activities: {obs.selected_activities}")
print(f"Done: {done}")
print()

# Action 4: Finish planning
print("ACTION 4: Finish planning")
action4 = Action(action_type="finish")
obs, reward, done, info = env.step(action4)
print(f"Reward: {reward.value} - {reward.explanation}")
print(f"Budget remaining: ${obs.budget_left}")
print(f"Selected activities: {obs.selected_activities}")
print(f"Done: {done}")
print()

# Show final grading
print("FINAL GRADING")
print("-" * 30)
final_score = env._grade()
print(f"Final score: {final_score:.2f}/1.00")
print()

# Calculate components
required_count = len(env.required_activities)
included_required = sum(1 for req in env.required_activities if req in obs.selected_activities)
required_score = (included_required / required_count) * 0.6

budget_used = env.budget - obs.budget_left
efficiency = min(budget_used / env.budget, 1.0)
efficiency_score = efficiency * 0.2

types = set(act['type'] for act in env.activities if act['name'] in obs.selected_activities)
variety_score = len(types) / len(set(act['type'] for act in env.activities)) * 0.2

print("Score breakdown:")
print(f"  Required activities: {included_required}/{required_count} = {required_score:.2f} (60%)")
print(f"  Budget efficiency: ${budget_used}/${env.budget} = {efficiency_score:.2f} (20%)")
print(f"  Activity variety: {len(types)} types = {variety_score:.2f} (20%)")
print()

print("REWARD SYSTEM SUMMARY")
print("-" * 30)
print("+ Add required activity: +0.2 reward")
print("+ Add optional activity: +0.1 reward")
print("- Invalid action (duplicate/budget): -0.1 penalty")
print("+ Finish planning: Final score (0.0-1.0)")
print("+ Final score = 60% required + 20% efficiency + 20% variety")
print()

print("=" * 60)
print("ENVIRONMENT DEMONSTRATION COMPLETE")
print("=" * 60)