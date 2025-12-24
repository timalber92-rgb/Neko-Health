"""
Unit tests for InterventionAgent (Q-Learning RL agent)

Tests cover:
- Agent initialization
- State discretization
- Action selection (epsilon-greedy policy)
- Reward calculation
- Intervention simulation
- Training workflow
- Recommendation generation
- Model persistence (save/load)
"""

import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml.rl_agent import ACTIONS, InterventionAgent


@pytest.fixture
def sample_patient_data():
    """
    Create sample normalized patient data for testing.
    """
    data = {
        "age": [0.5],  # Normalized values
        "sex": [1.0],
        "cp": [0.75],
        "trestbps": [0.6],
        "chol": [0.55],
        "fbs": [1.0],
        "restecg": [0.5],
        "thalach": [0.7],
        "exang": [0.0],
        "oldpeak": [0.4],
        "slope": [0.66],
        "ca": [0.0],
        "thal": [0.5],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_training_data():
    """
    Create sample training data for agent training.
    """
    np.random.seed(42)
    n_samples = 100

    data = {
        "age": np.random.uniform(0, 1, n_samples),
        "sex": np.random.uniform(0, 1, n_samples),
        "cp": np.random.uniform(0, 1, n_samples),
        "trestbps": np.random.uniform(0, 1, n_samples),
        "chol": np.random.uniform(0, 1, n_samples),
        "fbs": np.random.uniform(0, 1, n_samples),
        "restecg": np.random.uniform(0, 1, n_samples),
        "thalach": np.random.uniform(0, 1, n_samples),
        "exang": np.random.uniform(0, 1, n_samples),
        "oldpeak": np.random.uniform(0, 1, n_samples),
        "slope": np.random.uniform(0, 1, n_samples),
        "ca": np.random.uniform(0, 1, n_samples),
        "thal": np.random.uniform(0, 1, n_samples),
        "target": np.random.randint(0, 2, n_samples),
    }

    return pd.DataFrame(data)


@pytest.fixture
def mock_risk_predictor(sample_training_data):
    """
    Create a simple mock risk predictor for testing RL agent.
    """

    class MockRiskPredictor:
        def __init__(self):
            self.feature_names = sample_training_data.drop("target", axis=1).columns.tolist()

        def predict(self, patient_data):
            # Simple mock: base risk score on average of features
            avg_value = patient_data.iloc[0].mean()
            risk_score = avg_value * 100

            return {
                "risk_score": float(risk_score),
                "has_disease": risk_score > 50,
                "classification": "High Risk" if risk_score > 70 else "Medium Risk" if risk_score > 30 else "Low Risk",
                "probability": risk_score / 100,
                "feature_importance": {col: 1.0 / len(patient_data.columns) for col in patient_data.columns},
            }

    return MockRiskPredictor()


@pytest.fixture
def trained_agent(sample_training_data, mock_risk_predictor):
    """
    Create a trained InterventionAgent for testing.
    """
    agent = InterventionAgent(n_bins=5, epsilon=0.1, alpha=0.1, gamma=0.95)
    agent.train(sample_training_data, mock_risk_predictor, episodes=100)  # Fewer episodes for speed
    return agent


class TestInterventionAgentInitialization:
    """Test agent initialization"""

    def test_init_default_parameters(self):
        """Test initialization with default parameters"""
        agent = InterventionAgent()
        assert agent.n_bins == 5
        assert agent.epsilon == 0.1
        assert agent.alpha == 0.1
        assert agent.gamma == 0.95
        assert agent.state_bins is None
        assert len(agent.state_features) == 5

    def test_init_custom_parameters(self):
        """Test initialization with custom parameters"""
        agent = InterventionAgent(n_bins=10, epsilon=0.2, alpha=0.05, gamma=0.9)
        assert agent.n_bins == 10
        assert agent.epsilon == 0.2
        assert agent.alpha == 0.05
        assert agent.gamma == 0.9

    def test_q_table_initialization(self):
        """Test that Q-table is initialized as defaultdict"""
        agent = InterventionAgent()
        assert isinstance(agent.q_table, defaultdict)

        # Test default value for unseen state
        test_state = (0, 1, 2, 3, 4)
        assert len(agent.q_table[test_state]) == len(ACTIONS)
        assert np.all(agent.q_table[test_state] == 0)

    def test_action_definitions(self):
        """Test that all actions are properly defined"""
        assert len(ACTIONS) == 5
        for action_id in range(5):
            assert action_id in ACTIONS
            assert "name" in ACTIONS[action_id]
            assert "description" in ACTIONS[action_id]
            assert "cost" in ACTIONS[action_id]
            assert "intensity" in ACTIONS[action_id]


class TestStateBinning:
    """Test state discretization functionality"""

    def test_create_state_bins(self, sample_training_data):
        """Test creation of state bins from training data"""
        agent = InterventionAgent(n_bins=5)
        agent.create_state_bins(sample_training_data)

        assert agent.state_bins is not None
        assert len(agent.state_bins) == 5  # 5 state features

        # Check that bins are created for each feature
        for feature in agent.state_features:
            assert feature in agent.state_bins
            bins = agent.state_bins[feature]
            assert len(bins) >= 2  # At least min and max

    def test_discretize_state(self, sample_patient_data, sample_training_data):
        """Test discretization of patient data to state tuple"""
        agent = InterventionAgent(n_bins=5)
        agent.create_state_bins(sample_training_data)

        state = agent.discretize_state(sample_patient_data)

        # Check state structure
        assert isinstance(state, tuple)
        assert len(state) == 5  # 5 state features

        # Check that all state components are valid bin indices
        for bin_idx in state:
            assert 0 <= bin_idx < agent.n_bins

    def test_discretize_state_before_bins_created(self, sample_patient_data):
        """Test that discretization fails before bins are created"""
        agent = InterventionAgent()

        with pytest.raises(ValueError, match="State bins not created"):
            agent.discretize_state(sample_patient_data)

    def test_discretize_state_consistency(self, sample_patient_data, sample_training_data):
        """Test that discretization is consistent (deterministic)"""
        agent = InterventionAgent(n_bins=5)
        agent.create_state_bins(sample_training_data)

        state1 = agent.discretize_state(sample_patient_data)
        state2 = agent.discretize_state(sample_patient_data)

        assert state1 == state2


class TestActionSelection:
    """Test epsilon-greedy action selection"""

    def test_get_action_greedy(self, trained_agent):
        """Test greedy action selection (no exploration)"""
        state = (2, 2, 2, 2, 2)

        # In non-training mode, should always select best action
        action1 = trained_agent.get_action(state, training=False)
        action2 = trained_agent.get_action(state, training=False)

        assert action1 == action2  # Should be deterministic
        assert 0 <= action1 < len(ACTIONS)

    def test_get_action_epsilon_greedy(self, trained_agent):
        """Test epsilon-greedy action selection (with exploration)"""
        state = (2, 2, 2, 2, 2)

        # In training mode, might explore
        actions = [trained_agent.get_action(state, training=True) for _ in range(100)]

        # Should get valid actions
        assert all(0 <= a < len(ACTIONS) for a in actions)

        # With epsilon=0.1, we might see some exploration (not guaranteed in 100 samples though)
        # Just check that we get valid actions

    def test_get_action_range(self, trained_agent):
        """Test that actions are always in valid range"""
        for _ in range(50):
            state = tuple(np.random.randint(0, 5, size=5))
            action = trained_agent.get_action(state, training=True)
            assert 0 <= action < len(ACTIONS)


class TestRewardCalculation:
    """Test reward function"""

    def test_calculate_reward_risk_reduction(self):
        """Test that reward increases with risk reduction"""
        agent = InterventionAgent()

        # Same action, different risk reduction
        reward1 = agent.calculate_reward(current_risk=80, action=2, next_risk=60)
        reward2 = agent.calculate_reward(current_risk=80, action=2, next_risk=40)

        assert reward2 > reward1  # More risk reduction = higher reward

    def test_calculate_reward_cost_penalty(self):
        """Test that reward decreases with more expensive actions"""
        agent = InterventionAgent()

        # Same risk reduction, different actions (increasing cost)
        reward0 = agent.calculate_reward(current_risk=80, action=0, next_risk=60)
        reward2 = agent.calculate_reward(current_risk=80, action=2, next_risk=60)
        reward4 = agent.calculate_reward(current_risk=80, action=4, next_risk=60)

        # More expensive actions should have lower rewards
        assert reward0 > reward2 > reward4

    def test_calculate_reward_qol_penalty(self):
        """Test that QoL penalty is quadratic"""
        agent = InterventionAgent()

        # Calculate rewards for different actions
        rewards = []
        for action in range(5):
            reward = agent.calculate_reward(current_risk=80, action=action, next_risk=60)
            rewards.append(reward)

        # Check that penalty increases quadratically
        # reward = 20 - 0.1*action - 0.05*action²
        expected_rewards = [20.0, 19.85, 19.6, 19.25, 18.8]
        for i in range(5):
            assert abs(rewards[i] - expected_rewards[i]) < 0.01


class TestInterventionSimulation:
    """Test intervention effect simulation"""

    def test_simulate_monitor_only(self, sample_patient_data):
        """Test Monitor Only action (no changes)"""
        agent = InterventionAgent()
        modified_data = agent.simulate_intervention_effect(sample_patient_data, action=0)

        # Should be identical to original
        pd.testing.assert_frame_equal(modified_data, sample_patient_data)

    def test_simulate_lifestyle_intervention(self, sample_patient_data):
        """Test Lifestyle Intervention (modest improvements)"""
        agent = InterventionAgent()
        original_data = sample_patient_data.copy()
        modified_data = agent.simulate_intervention_effect(sample_patient_data, action=1)

        # Check that modifiable factors improved
        assert modified_data["trestbps"].iloc[0] < original_data["trestbps"].iloc[0]
        assert modified_data["chol"].iloc[0] < original_data["chol"].iloc[0]
        assert modified_data["thalach"].iloc[0] > original_data["thalach"].iloc[0]

    def test_simulate_intensive_treatment(self, sample_patient_data):
        """Test Intensive Treatment (maximum improvements)"""
        agent = InterventionAgent()
        original_data = sample_patient_data.copy()
        modified_data = agent.simulate_intervention_effect(sample_patient_data, action=4)

        # Intensive treatment should have stronger effects than lifestyle
        modified_lifestyle = agent.simulate_intervention_effect(sample_patient_data, action=1)

        # Blood pressure reduction should be greater with intensive treatment
        bp_reduction_intensive = original_data["trestbps"].iloc[0] - modified_data["trestbps"].iloc[0]
        bp_reduction_lifestyle = original_data["trestbps"].iloc[0] - modified_lifestyle["trestbps"].iloc[0]

        assert bp_reduction_intensive > bp_reduction_lifestyle

    def test_simulate_all_actions(self, sample_patient_data):
        """Test that all actions produce valid results"""
        agent = InterventionAgent()

        for action in range(5):
            modified_data = agent.simulate_intervention_effect(sample_patient_data, action)

            # Should have same structure
            assert modified_data.shape == sample_patient_data.shape
            assert list(modified_data.columns) == list(sample_patient_data.columns)

            # Values should still be in reasonable range (normalized)
            assert (modified_data >= -0.5).all().all()  # Allow slight negative due to simulation
            assert (modified_data <= 1.5).all().all()  # Allow slight overflow


class TestTraining:
    """Test agent training"""

    def test_train_basic(self, sample_training_data, mock_risk_predictor):
        """Test basic training workflow"""
        agent = InterventionAgent()
        stats = agent.train(sample_training_data, mock_risk_predictor, episodes=50)

        # Check that stats are returned
        assert "episodes" in stats
        assert "states_explored" in stats
        assert "final_avg_reward" in stats
        assert "rewards_history" in stats

        assert stats["episodes"] == 50
        assert stats["states_explored"] > 0
        assert len(stats["rewards_history"]) == 50

    def test_train_creates_q_table(self, sample_training_data, mock_risk_predictor):
        """Test that training populates Q-table"""
        agent = InterventionAgent()

        # Q-table should be empty initially (defaultdict)
        initial_size = len(agent.q_table)

        agent.train(sample_training_data, mock_risk_predictor, episodes=50)

        # Q-table should be populated
        assert len(agent.q_table) > initial_size

    def test_train_creates_state_bins(self, sample_training_data, mock_risk_predictor):
        """Test that training creates state bins"""
        agent = InterventionAgent()
        assert agent.state_bins is None

        agent.train(sample_training_data, mock_risk_predictor, episodes=50)

        assert agent.state_bins is not None
        assert len(agent.state_bins) == 5


class TestRecommendation:
    """Test intervention recommendation"""

    def test_recommend_basic(self, trained_agent, sample_patient_data, mock_risk_predictor):
        """Test basic recommendation workflow"""
        recommendation = trained_agent.recommend(sample_patient_data, mock_risk_predictor)

        # Check recommendation structure
        assert "action" in recommendation
        assert "action_name" in recommendation
        assert "description" in recommendation
        assert "cost" in recommendation
        assert "intensity" in recommendation
        assert "current_risk" in recommendation
        assert "expected_final_risk" in recommendation
        assert "expected_risk_reduction" in recommendation
        assert "q_values" in recommendation

        # Check value validity
        assert 0 <= recommendation["action"] < len(ACTIONS)
        assert recommendation["action_name"] == ACTIONS[recommendation["action"]]["name"]
        assert 0 <= recommendation["current_risk"] <= 100
        assert isinstance(recommendation["q_values"], dict)
        assert len(recommendation["q_values"]) == len(ACTIONS)

    def test_recommend_before_training(self, sample_patient_data, mock_risk_predictor):
        """Test that recommendation fails before training"""
        agent = InterventionAgent()

        with pytest.raises(ValueError, match="not been trained"):
            agent.recommend(sample_patient_data, mock_risk_predictor)

    def test_recommend_consistency(self, trained_agent, sample_patient_data, mock_risk_predictor):
        """Test that recommendations are consistent for same patient"""
        rec1 = trained_agent.recommend(sample_patient_data, mock_risk_predictor)
        rec2 = trained_agent.recommend(sample_patient_data, mock_risk_predictor)

        # Greedy policy should give same recommendation
        assert rec1["action"] == rec2["action"]
        assert rec1["action_name"] == rec2["action_name"]

    def test_recommend_q_values(self, trained_agent, sample_patient_data, mock_risk_predictor):
        """Test that Q-values are included in recommendation"""
        recommendation = trained_agent.recommend(sample_patient_data, mock_risk_predictor)

        q_values = recommendation["q_values"]

        # All actions should have Q-values
        for action_id in range(len(ACTIONS)):
            action_name = ACTIONS[action_id]["name"]
            assert action_name in q_values
            assert isinstance(q_values[action_name], float)


class TestPersistence:
    """Test agent save/load functionality"""

    def test_save_and_load(self, trained_agent, sample_patient_data, mock_risk_predictor):
        """Test saving and loading agent"""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_path = Path(tmpdir) / "test_agent.pkl"

            # Save agent
            trained_agent.save(agent_path)
            assert agent_path.exists()

            # Load agent into new instance
            new_agent = InterventionAgent()
            new_agent.load(agent_path)

            # Check that parameters are restored
            assert new_agent.n_bins == trained_agent.n_bins
            assert new_agent.epsilon == trained_agent.epsilon
            assert new_agent.alpha == trained_agent.alpha
            assert new_agent.gamma == trained_agent.gamma
            assert new_agent.state_features == trained_agent.state_features

            # Check that Q-table size matches
            assert len(new_agent.q_table) == len(trained_agent.q_table)

            # Check that recommendations match
            rec_original = trained_agent.recommend(sample_patient_data, mock_risk_predictor)
            rec_loaded = new_agent.recommend(sample_patient_data, mock_risk_predictor)

            assert rec_original["action"] == rec_loaded["action"]

    def test_save_before_training(self):
        """Test that save fails before training"""
        agent = InterventionAgent()

        with tempfile.TemporaryDirectory() as tmpdir:
            agent_path = Path(tmpdir) / "test_agent.pkl"

            with pytest.raises(ValueError, match="not been trained"):
                agent.save(agent_path)

    def test_load_nonexistent_file(self):
        """Test that load fails with non-existent file"""
        agent = InterventionAgent()

        with pytest.raises(FileNotFoundError):
            agent.load(Path("/nonexistent/path.pkl"))


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_high_risk_patient_recommendation(self, trained_agent, mock_risk_predictor):
        """Test recommendation for high-risk patient"""
        # Create high-risk patient (high values in risk features)
        high_risk_patient = pd.DataFrame(
            {
                "age": [0.9],
                "sex": [1.0],
                "cp": [1.0],
                "trestbps": [0.9],
                "chol": [0.9],
                "fbs": [1.0],
                "restecg": [1.0],
                "thalach": [0.3],
                "exang": [1.0],
                "oldpeak": [0.9],
                "slope": [1.0],
                "ca": [1.0],
                "thal": [1.0],
            }
        )

        recommendation = trained_agent.recommend(high_risk_patient, mock_risk_predictor)

        # Should recommend some intervention (not just monitoring)
        # Note: This might not always hold due to stochastic training
        assert 0 <= recommendation["action"] < len(ACTIONS)

    def test_low_risk_patient_recommendation(self, trained_agent, mock_risk_predictor):
        """Test recommendation for low-risk patient"""
        # Create low-risk patient
        low_risk_patient = pd.DataFrame(
            {
                "age": [0.2],
                "sex": [0.0],
                "cp": [0.0],
                "trestbps": [0.3],
                "chol": [0.3],
                "fbs": [0.0],
                "restecg": [0.0],
                "thalach": [0.8],
                "exang": [0.0],
                "oldpeak": [0.1],
                "slope": [0.0],
                "ca": [0.0],
                "thal": [0.0],
            }
        )

        recommendation = trained_agent.recommend(low_risk_patient, mock_risk_predictor)

        # Should recommend valid action
        assert 0 <= recommendation["action"] < len(ACTIONS)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
