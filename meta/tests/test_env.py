import pytest
from travel_itinerary_planner import TravelItineraryPlannerEnv, Action, Observation, Reward, Info


class TestTravelItineraryPlannerEnv:
    def test_easy_task_initialization(self):
        env = TravelItineraryPlannerEnv(task="easy")
        obs = env.reset()
        assert obs.current_day == 1
        assert obs.budget_left == 500.0
        assert obs.destination == "Paris"
        assert len(obs.available_activities) == 4
        assert obs.total_days == 1

    def test_medium_task_initialization(self):
        env = TravelItineraryPlannerEnv(task="medium")
        obs = env.reset()
        assert obs.current_day == 1
        assert obs.budget_left == 1000.0
        assert obs.destination == "Tokyo"
        assert len(obs.available_activities) == 6
        assert obs.total_days == 3

    def test_hard_task_initialization(self):
        env = TravelItineraryPlannerEnv(task="hard")
        obs = env.reset()
        assert obs.current_day == 1
        assert obs.budget_left == 2000.0
        assert obs.destination == "Europe Tour"
        assert len(obs.available_activities) == 10
        assert obs.total_days == 7

    def test_add_activity_action(self):
        env = TravelItineraryPlannerEnv(task="easy")
        env.reset()
        action = Action(action_type="add_activity", activity_id=0)
        obs, reward, done, info = env.step(action)
        assert "Eiffel Tower" in obs.selected_activities
        assert obs.budget_left == 450.0
        assert reward.value == 0.2  # Required activity
        assert not done

    def test_finish_action(self):
        env = TravelItineraryPlannerEnv(task="easy")
        env.reset()
        action = Action(action_type="finish")
        obs, reward, done, info = env.step(action)
        assert done
        assert reward.value >= 0  # Some score (can be 0 if no activities selected)
        assert reward.value <= 1.0

    def test_invalid_action(self):
        env = TravelItineraryPlannerEnv(task="easy")
        env.reset()
        action = Action(action_type="invalid")
        obs, reward, done, info = env.step(action)
        assert reward.value < 0  # Penalty for invalid action

    def test_budget_constraint(self):
        env = TravelItineraryPlannerEnv(task="easy")
        env.reset()
        # Try to add expensive activities beyond budget
        actions = [
            Action(action_type="add_activity", activity_id=0),  # $50
            Action(action_type="add_activity", activity_id=1),  # $40, total $90
            Action(action_type="add_activity", activity_id=2),  # $30, total $120
            Action(action_type="add_activity", activity_id=3),  # $20, total $140
        ]
        for action in actions:
            obs, reward, done, info = env.step(action)
        # Should still have budget left
        assert obs.budget_left > 0

    def test_grader_scores(self):
        env = TravelItineraryPlannerEnv(task="easy")
        env.reset()
        # Add required activity
        action = Action(action_type="add_activity", activity_id=0)
        env.step(action)
        # Finish
        action = Action(action_type="finish")
        obs, reward, done, info = env.step(action)
        score = env._grade()
        assert 0.0 <= score <= 1.0
        assert score > 0  # Should have some score for including required activity


if __name__ == "__main__":
    pytest.main([__file__])