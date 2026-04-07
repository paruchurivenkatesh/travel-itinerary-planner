from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import random

class Action(BaseModel):
    action_type: str  # "add_activity", "remove_activity", "finish"
    activity_id: Optional[int] = None

class Observation(BaseModel):
    current_day: int
    selected_activities: List[str]
    budget_left: float
    total_days: int
    destination: str
    available_activities: List[Dict[str, Any]]

class Reward(BaseModel):
    value: float
    explanation: str = ""

class Info(BaseModel):
    message: str = ""

class TravelItineraryPlannerEnv:
    """
    Travel Itinerary Planner Environment: plan realistic vacation itineraries with budget and schedule constraints.
    The agent must build a set of activities that covers required points of interest and stays within budget.
    """
    def __init__(self, task: str = "easy"):
        self.task = task
        self._setup_task()
        self.reset()

    def _setup_task(self):
        if self.task == "easy":
            self.total_days = 1
            self.budget = 500
            self.destination = "Paris"
            self.required_activities = ["Eiffel Tower"]
            self.activities = [
                {"id": 0, "name": "Eiffel Tower", "cost": 50, "type": "attraction"},
                {"id": 1, "name": "Louvre Museum", "cost": 40, "type": "museum"},
                {"id": 2, "name": "Seine River Cruise", "cost": 30, "type": "activity"},
                {"id": 3, "name": "Café Visit", "cost": 20, "type": "food"},
            ]
        elif self.task == "medium":
            self.total_days = 3
            self.budget = 1000
            self.destination = "Tokyo"
            self.required_activities = ["Mount Fuji", "Shibuya Crossing"]
            self.activities = [
                {"id": 0, "name": "Mount Fuji", "cost": 100, "type": "attraction"},
                {"id": 1, "name": "Shibuya Crossing", "cost": 0, "type": "attraction"},
                {"id": 2, "name": "Sushi Dinner", "cost": 80, "type": "food"},
                {"id": 3, "name": "Temple Visit", "cost": 50, "type": "cultural"},
                {"id": 4, "name": "Shopping", "cost": 150, "type": "activity"},
                {"id": 5, "name": "Hotel Stay", "cost": 200, "type": "accommodation"},
            ]
        elif self.task == "hard":
            self.total_days = 7
            self.budget = 2000
            self.destination = "Europe Tour"
            self.required_activities = ["Eiffel Tower", "Colosseum", "Big Ben"]
            self.activities = [
                {"id": 0, "name": "Eiffel Tower", "cost": 50, "type": "attraction"},
                {"id": 1, "name": "Louvre", "cost": 40, "type": "museum"},
                {"id": 2, "name": "Colosseum", "cost": 60, "type": "attraction"},
                {"id": 3, "name": "Vatican Visit", "cost": 45, "type": "cultural"},
                {"id": 4, "name": "Big Ben", "cost": 30, "type": "attraction"},
                {"id": 5, "name": "London Eye", "cost": 70, "type": "activity"},
                {"id": 6, "name": "Fine Dining", "cost": 100, "type": "food"},
                {"id": 7, "name": "Train Travel", "cost": 150, "type": "transport"},
                {"id": 8, "name": "Hotel Stay", "cost": 250, "type": "accommodation"},
                {"id": 9, "name": "Guided Tour", "cost": 80, "type": "activity"},
            ]
        else:
            raise ValueError("Unknown task")

    def reset(self) -> Observation:
        self.current_day = 1
        self.selected_activities = []
        self.budget_left = self.budget
        self.done = False
        return self.state()

    def step(self, action: Action) -> tuple[Observation, Reward, bool, Info]:
        if self.done:
            return self.state(), Reward(value=0.0, explanation="Planning already completed."), True, Info(message="Trip already finalized")

        reward_value = 0.0
        explanation = ""
        message = ""

        if action.action_type == "add_activity":
            activity = self._get_activity(action.activity_id)
            if activity and self.budget_left >= activity['cost'] and activity['name'] not in self.selected_activities:
                self.selected_activities.append(activity['name'])
                self.budget_left -= activity['cost']
                if activity['name'] in self.required_activities:
                    reward_value = 0.2
                    explanation = f"Added required activity: {activity['name']}!"
                else:
                    reward_value = 0.1
                    explanation = f"Added additional activity: {activity['name']}"
            else:
                reward_value = -0.1
                explanation = "Invalid activity - budget exceeded or duplicate!"
                message = "Could not add activity"

        elif action.action_type == "remove_activity":
            if action.activity_id is not None:
                activity = self._get_activity(action.activity_id)
                if activity and activity['name'] in self.selected_activities:
                    self.selected_activities.remove(activity['name'])
                    self.budget_left += activity['cost']
                    reward_value = -0.05  # Small penalty for changing plans
                    explanation = f"Removed activity: {activity['name']} (changed mind?)"
                else:
                    reward_value = -0.1
                    explanation = "Activity not selected or invalid"
            else:
                reward_value = -0.1
                explanation = "No activity_id provided for removal"

        elif action.action_type == "finish":
            self.done = True
            score = self._grade()
            reward_value = score
            explanation = f"Planning completed with score: {score}"
            message = "Trip completed"

        else:
            reward_value = -0.05
            explanation = "Unknown action type. Use add_activity, remove_activity, or finish."
            message = "Command not recognized"

        # Check budget depletion
        if self.budget_left <= 0:
            self.done = True
            explanation += " (Budget exhausted!)"
            message = "Budget exhausted - trip ended"

        obs = self.state()
        return obs, Reward(value=reward_value, explanation=explanation), self.done, Info(message=message)

    def state(self) -> Observation:
        return Observation(
            current_day=self.current_day,
            selected_activities=self.selected_activities,
            budget_left=self.budget_left,
            total_days=self.total_days,
            destination=self.destination,
            available_activities=self.activities
        )

    def _get_activity(self, activity_id: int) -> Optional[Dict[str, Any]]:
        for act in self.activities:
            if act['id'] == activity_id:
                return act
        return None

    def _grade(self) -> float:
        score = 0.0
        required_count = len(self.required_activities)
        included_required = sum(1 for req in self.required_activities if req in self.selected_activities)
        score += (included_required / required_count) * 0.6  # 60% for required activities

        # 20% for budget efficiency (don't waste money!)
        budget_used = self.budget - self.budget_left
        efficiency = min(budget_used / self.budget, 1.0)
        score += efficiency * 0.2

        # 20% for activity variety (explore different types of travel activities)
        types = set(act['type'] for act in self.activities if act['name'] in self.selected_activities)
        variety_score = len(types) / len(set(act['type'] for act in self.activities))
        score += variety_score * 0.2

        return min(score, 1.0)