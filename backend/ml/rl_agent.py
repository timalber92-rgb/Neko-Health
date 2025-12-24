"""
Reinforcement Learning Agent for HealthGuard

This module implements a Q-Learning agent that recommends optimal intervention
strategies for cardiovascular disease prevention. The agent learns from simulated
patient trajectories to balance risk reduction, treatment costs, and quality of life.
"""

import logging
import pickle
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from .intervention_utils import apply_intervention_effects

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Action definitions (intervention strategies)
ACTIONS = {
    0: {
        "name": "Monitor Only",
        "description": "Quarterly checkups with no active intervention",
        "cost": "Low ($)",
        "intensity": "Minimal",
    },
    1: {
        "name": "Lifestyle Intervention",
        "description": "Diet and exercise program with regular monitoring",
        "cost": "Low ($$)",
        "intensity": "Moderate",
    },
    2: {
        "name": "Single Medication",
        "description": "Single medication (e.g., statin or beta-blocker)",
        "cost": "Medium ($$$)",
        "intensity": "Moderate",
    },
    3: {
        "name": "Combination Therapy",
        "description": "Medication plus supervised lifestyle program",
        "cost": "High ($$$$)",
        "intensity": "High",
    },
    4: {
        "name": "Intensive Treatment",
        "description": "Multiple medications with intensive lifestyle management",
        "cost": "Very High ($$$$$)",
        "intensity": "Very High",
    },
}


class InterventionAgent:
    """
    Q-Learning agent for cardiovascular disease intervention optimization.

    Uses tabular Q-learning with epsilon-greedy exploration to learn optimal
    intervention strategies. The agent balances risk reduction against treatment
    costs and quality of life impacts.

    Attributes:
        n_bins: Number of discretization bins per feature
        epsilon: Exploration rate for epsilon-greedy policy
        alpha: Learning rate
        gamma: Discount factor
        q_table: Dictionary mapping (state, action) -> Q-value
        state_bins: Discretization boundaries for each feature
    """

    def __init__(self, n_bins: int = 5, epsilon: float = 0.1, alpha: float = 0.1, gamma: float = 0.95):
        """
        Initialize Q-Learning agent.

        Args:
            n_bins: Number of bins for discretizing continuous features (default: 5)
            epsilon: Exploration probability for epsilon-greedy (default: 0.1)
            alpha: Learning rate, controls how much Q-values update (default: 0.1)
            gamma: Discount factor, importance of future rewards (default: 0.95)
        """
        self.n_bins = n_bins
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.q_table = defaultdict(lambda: np.zeros(len(ACTIONS)))
        self.state_bins: Optional[Dict[str, np.ndarray]] = None

        # Features to use for state representation (key clinical indicators)
        self.state_features = ["age", "trestbps", "chol", "thalach", "oldpeak"]

        logger.info(f"Initialized InterventionAgent: n_bins={n_bins}, " f"epsilon={epsilon}, alpha={alpha}, gamma={gamma}")

    def create_state_bins(self, data: pd.DataFrame) -> None:
        """
        Create discretization bins for continuous features.

        Uses quantile-based binning to ensure roughly equal number of samples
        in each bin, which improves learning efficiency.

        Args:
            data: DataFrame with patient data to determine bin boundaries
        """
        self.state_bins = {}

        for feature in self.state_features:
            if feature in data.columns:
                # Use quantile-based binning for better distribution
                bins = pd.qcut(data[feature], q=self.n_bins, labels=False, duplicates="drop", retbins=True)[1]
                self.state_bins[feature] = bins
                logger.info(f"Created {len(bins)-1} bins for feature '{feature}'")
            else:
                logger.warning(f"Feature '{feature}' not found in data")

    def discretize_state(self, patient_data: pd.DataFrame) -> Tuple:
        """
        Convert continuous patient features to discrete state representation.

        Maps patient features to bins to create a discrete state space that
        the Q-learning agent can work with.

        Args:
            patient_data: DataFrame with single patient's features (normalized)

        Returns:
            Tuple representing discrete state (age_bin, bp_bin, chol_bin, hr_bin, oldpeak_bin)

        Raises:
            ValueError: If state bins haven't been created yet
        """
        if self.state_bins is None:
            raise ValueError("State bins not created. Call create_state_bins() or train() first.")

        state = []
        for feature in self.state_features:
            if feature not in patient_data.columns:
                raise ValueError(f"Feature '{feature}' not found in patient data")

            value = patient_data[feature].iloc[0]
            bins = self.state_bins[feature]

            # Find which bin this value falls into
            bin_idx = np.digitize(value, bins) - 1
            # Clip to valid range [0, n_bins-1]
            bin_idx = max(0, min(bin_idx, self.n_bins - 1))
            state.append(bin_idx)

        return tuple(state)

    def get_action(self, state: Tuple, training: bool = False) -> int:
        """
        Select action using epsilon-greedy policy.

        During training, explores with probability epsilon. During inference,
        always selects the action with highest Q-value (greedy).

        Args:
            state: Discrete state tuple
            training: If True, use epsilon-greedy; if False, use greedy policy

        Returns:
            Action index (0-4)
        """
        if training and np.random.random() < self.epsilon:
            # Explore: random action
            action = np.random.randint(0, len(ACTIONS))
        else:
            # Exploit: best known action
            action = int(np.argmax(self.q_table[state]))

        return action

    def calculate_reward(self, current_risk: float, action: int, next_risk: float) -> float:
        """
        Calculate reward for a state-action-next_state transition.

        Reward function balances:
        - Risk reduction (primary goal)
        - Treatment cost (penalize expensive interventions)
        - Quality of life (penalize intensive treatments)

        Args:
            current_risk: Current risk score (0-100%)
            action: Action taken (0-4)
            next_risk: Resulting risk score after intervention (0-100%)

        Returns:
            Reward value (higher is better)
        """
        # Risk reduction component (positive reward for reducing risk)
        risk_reduction = current_risk - next_risk

        # Cost penalty (penalize more expensive treatments)
        cost_penalty = action * 0.1  # Linear cost increase with action intensity

        # Quality of life penalty (intensive treatments reduce QoL)
        qol_penalty = (action**2) * 0.05  # Quadratic penalty for intensive treatments

        # Combined reward
        reward = risk_reduction - cost_penalty - qol_penalty

        return reward

    def simulate_intervention_effect(self, patient_data: pd.DataFrame, action: int) -> pd.DataFrame:
        """
        Simulate the effect of an intervention on patient metrics.

        Uses smart intervention logic with bounds checking to prevent
        paradoxical risk increases for healthy patients.

        Args:
            patient_data: Current patient features
            action: Intervention action (0-4)

        Returns:
            Modified patient features after intervention
        """
        # Use centralized intervention logic with adaptive effects
        return apply_intervention_effects(patient_data, action)

    def train(self, data: pd.DataFrame, risk_predictor, episodes: int = 10000) -> Dict[str, Any]:
        """
        Train Q-table using simulated patient trajectories.

        Simulates interventions on random patients from the dataset and learns
        optimal policies through Q-learning updates.

        Args:
            data: Training data with patient features
            risk_predictor: Trained RiskPredictor model to estimate risk scores
            episodes: Number of training episodes (default: 10000)

        Returns:
            Dictionary with training statistics
        """
        logger.info(f"Starting Q-Learning training for {episodes} episodes...")

        # Create state bins from training data
        self.create_state_bins(data)

        # Remove target column if present
        feature_data = data.drop("target", axis=1, errors="ignore")

        # Training statistics
        rewards_history = []
        q_value_changes = []

        for episode in range(episodes):
            # Sample random patient from data
            patient_idx = np.random.randint(0, len(feature_data))
            patient_data = feature_data.iloc[[patient_idx]]

            # Get current state and risk
            state = self.discretize_state(patient_data)
            current_prediction = risk_predictor.predict(patient_data)
            current_risk = current_prediction["risk_score"]

            # Select action (epsilon-greedy during training)
            action = self.get_action(state, training=True)

            # Simulate intervention effect
            modified_data = self.simulate_intervention_effect(patient_data, action)

            # Get next state and risk
            next_state = self.discretize_state(modified_data)
            next_prediction = risk_predictor.predict(modified_data)
            next_risk = next_prediction["risk_score"]

            # Calculate reward
            reward = self.calculate_reward(current_risk, action, next_risk)
            rewards_history.append(reward)

            # Q-Learning update
            old_q = self.q_table[state][action]
            next_max_q = np.max(self.q_table[next_state])

            # Q(s,a) = Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
            new_q = old_q + self.alpha * (reward + self.gamma * next_max_q - old_q)
            self.q_table[state][action] = new_q

            q_value_changes.append(abs(new_q - old_q))

            # Log progress
            if (episode + 1) % 2000 == 0:
                avg_reward = np.mean(rewards_history[-2000:])
                avg_q_change = np.mean(q_value_changes[-2000:])
                logger.info(
                    f"Episode {episode + 1}/{episodes} - "
                    f"Avg Reward: {avg_reward:.3f}, "
                    f"Avg Q-Change: {avg_q_change:.4f}"
                )

        logger.info("Training complete")
        logger.info(f"Total states explored: {len(self.q_table)}")
        logger.info(f"Final average reward: {np.mean(rewards_history[-1000:]):.3f}")

        return {
            "episodes": episodes,
            "states_explored": len(self.q_table),
            "final_avg_reward": np.mean(rewards_history[-1000:]),
            "rewards_history": rewards_history,
        }

    def recommend(self, patient_data: pd.DataFrame, risk_predictor) -> Dict[str, Any]:
        """
        Recommend optimal intervention for a patient.

        Uses the learned Q-table to select the best intervention strategy,
        considering both effectiveness and cost.

        Args:
            patient_data: Patient features (must be normalized)
            risk_predictor: Trained RiskPredictor to estimate risk scores

        Returns:
            Dictionary containing:
                - action: Recommended action index (0-4)
                - action_name: Human-readable action name
                - description: Detailed action description
                - cost: Estimated cost level
                - intensity: Treatment intensity
                - expected_risk_reduction: Estimated reduction in risk score
                - current_risk: Current risk score
                - expected_final_risk: Expected risk after intervention
                - q_values: Q-values for all actions (for debugging)

        Raises:
            ValueError: If agent hasn't been trained yet
        """
        if self.state_bins is None:
            raise ValueError("Agent has not been trained yet. Call train() first.")

        # Get current state and risk
        state = self.discretize_state(patient_data)
        current_prediction = risk_predictor.predict(patient_data)
        current_risk = current_prediction["risk_score"]

        # Get best action (greedy policy for inference)
        action = self.get_action(state, training=False)
        action_info = ACTIONS[action]

        # Simulate expected outcome
        modified_data = self.simulate_intervention_effect(patient_data, action)
        next_prediction = risk_predictor.predict(modified_data)
        expected_risk = next_prediction["risk_score"]

        # Get all Q-values for transparency
        q_values = {ACTIONS[a]["name"]: float(self.q_table[state][a]) for a in range(len(ACTIONS))}

        recommendation = {
            "action": int(action),
            "action_name": action_info["name"],
            "description": action_info["description"],
            "cost": action_info["cost"],
            "intensity": action_info["intensity"],
            "current_risk": float(current_risk),
            "expected_final_risk": float(expected_risk),
            "expected_risk_reduction": float(current_risk - expected_risk),
            "q_values": q_values,
        }

        logger.info(f"Recommendation: {action_info['name']} " f"(risk {current_risk:.1f}% → {expected_risk:.1f}%)")

        return recommendation

    def save(self, path: Path) -> None:
        """
        Save trained Q-table and agent parameters to disk.

        Args:
            path: Path to save the agent (.pkl file)

        Raises:
            ValueError: If agent hasn't been trained
            IOError: If file cannot be written
        """
        if self.state_bins is None:
            raise ValueError("Agent has not been trained yet. Call train() first.")

        try:
            agent_data = {
                "q_table": dict(self.q_table),  # Convert defaultdict to dict
                "state_bins": self.state_bins,
                "n_bins": self.n_bins,
                "epsilon": self.epsilon,
                "alpha": self.alpha,
                "gamma": self.gamma,
                "state_features": self.state_features,
            }

            with open(path, "wb") as f:
                pickle.dump(agent_data, f)

            logger.info(f"Agent saved to {path}")

        except Exception as e:
            logger.error(f"Failed to save agent: {str(e)}")
            raise IOError(f"Failed to save agent: {str(e)}") from e

    def load(self, path: Path) -> None:
        """
        Load trained Q-table and agent parameters from disk.

        Args:
            path: Path to saved agent file (.pkl)

        Raises:
            FileNotFoundError: If agent file doesn't exist
            IOError: If file cannot be read or is corrupted
        """
        if not path.exists():
            raise FileNotFoundError(f"Agent file not found: {path}")

        try:
            with open(path, "rb") as f:
                agent_data = pickle.load(f)

            self.q_table = defaultdict(lambda: np.zeros(len(ACTIONS)), agent_data["q_table"])
            self.state_bins = agent_data["state_bins"]
            self.n_bins = agent_data["n_bins"]
            self.epsilon = agent_data["epsilon"]
            self.alpha = agent_data["alpha"]
            self.gamma = agent_data["gamma"]
            self.state_features = agent_data["state_features"]

            logger.info(f"Agent loaded from {path}")
            logger.info(f"States in Q-table: {len(self.q_table)}")

        except Exception as e:
            logger.error(f"Failed to load agent: {str(e)}")
            raise IOError(f"Failed to load agent: {str(e)}") from e


def main():
    """
    Main function for training and testing the RL agent.

    Demonstrates the complete workflow:
    1. Load risk predictor model
    2. Load training data
    3. Train Q-learning agent
    4. Test recommendations on sample patients
    5. Save trained agent
    """
    import sys
    from pathlib import Path

    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from data.load import load_processed_data
    from ml.risk_predictor import RiskPredictor

    logger.info("=" * 80)
    logger.info("HealthGuard - RL Intervention Agent Training")
    logger.info("=" * 80)

    # Load data
    logger.info("\n[1/5] Loading processed data and risk predictor...")
    train_df, val_df, test_df, scaler = load_processed_data()

    # Load trained risk predictor
    model_path = Path(__file__).parent.parent / "models" / "risk_predictor.pkl"
    if not model_path.exists():
        logger.error(f"Risk predictor not found at {model_path}")
        logger.error("Please train the risk predictor first: python -m ml.risk_predictor")
        return

    predictor = RiskPredictor()
    predictor.load(model_path)
    logger.info("Loaded trained risk predictor")

    # Initialize agent
    logger.info("\n[2/5] Initializing RL agent...")
    agent = InterventionAgent(n_bins=5, epsilon=0.1, alpha=0.1, gamma=0.95)

    # Train agent
    logger.info("\n[3/5] Training RL agent...")
    stats = agent.train(train_df, predictor, episodes=10000)

    # Test on sample patients
    logger.info("\n[4/5] Testing recommendations on sample patients...")
    test_features = test_df.drop("target", axis=1, errors="ignore")

    for i in [0, 10, 20]:  # Test on 3 different patients
        logger.info(f"\n--- Patient {i+1} ---")
        patient = test_features.iloc[[i]]

        # Get risk prediction
        risk_pred = predictor.predict(patient)
        logger.info(f"Current Risk: {risk_pred['risk_score']:.1f}% ({risk_pred['classification']})")

        # Get RL recommendation
        recommendation = agent.recommend(patient, predictor)
        logger.info(f"Recommended Intervention: {recommendation['action_name']}")
        logger.info(f"Expected Risk Reduction: {recommendation['expected_risk_reduction']:.1f}%")
        logger.info(f"Cost: {recommendation['cost']}, Intensity: {recommendation['intensity']}")

    # Save agent
    logger.info("\n[5/5] Saving trained agent...")
    agent_dir = Path(__file__).parent.parent / "models"
    agent_dir.mkdir(exist_ok=True)
    agent_path = agent_dir / "intervention_agent.pkl"
    agent.save(agent_path)

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Episodes: {stats['episodes']}")
    logger.info(f"States Explored: {stats['states_explored']}")
    logger.info(f"Final Avg Reward: {stats['final_avg_reward']:.3f}")
    logger.info(f"\nAgent saved to: {agent_path}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
