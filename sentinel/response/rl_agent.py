"""Reinforcement Learning agent for optimal response actions."""
import logging
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from collections import deque
import json
import os

logger = logging.getLogger(__name__)


class RLResponseAgent:
    """Q-Learning agent for learning optimal response actions."""
    
    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.95,
                 epsilon: float = 0.1, epsilon_decay: float = 0.995):
        """
        Initialize RL agent.
        
        Args:
            learning_rate: Learning rate (alpha)
            discount_factor: Discount factor (gamma)
            epsilon: Exploration rate
            epsilon_decay: Epsilon decay rate
        """
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = 0.01
        
        # Q-table: state -> action -> Q-value
        self.q_table: Dict[str, Dict[str, float]] = {}
        
        # Action space
        self.actions = [
            'monitor',
            'rate_limit',
            'block_ip',
            'isolate_container',
            'redirect_to_honeypot'
        ]
        
        # Experience replay buffer
        self.memory = deque(maxlen=10000)
        
        # Performance tracking
        self.episode_rewards = []
        self.action_counts = {action: 0 for action in self.actions}
        
        logger.info(f"RL Agent initialized (lr={learning_rate}, gamma={discount_factor}, epsilon={epsilon})")
        
        # Load existing Q-table if available
        self._load_q_table()
    
    def get_state(self, alert: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Convert alert and context to state representation.
        
        Args:
            alert: Alert dictionary
            context: Additional context (time of day, network load, etc.)
            
        Returns:
            State string
        """
        severity = alert.get('severity', 'low')
        confidence = alert.get('score', 0.0)
        
        # Discretize confidence
        conf_bucket = 'high' if confidence > 0.8 else 'medium' if confidence > 0.5 else 'low'
        
        # Time of day (business hours vs off-hours)
        hour = context.get('hour', 12)
        time_bucket = 'business' if 9 <= hour <= 17 else 'off_hours'
        
        # Network load
        load = context.get('network_load', 0.5)
        load_bucket = 'high' if load > 0.7 else 'medium' if load > 0.3 else 'low'
        
        # Has TI confirmation
        ti_confirmed = 'ti_yes' if context.get('ti_malicious', False) else 'ti_no'
        
        state = f"{severity}_{conf_bucket}_{time_bucket}_{load_bucket}_{ti_confirmed}"
        return state
    
    def select_action(self, state: str, training: bool = True) -> str:
        """
        Select action using epsilon-greedy policy.
        
        Args:
            state: Current state
            training: Whether in training mode
            
        Returns:
            Selected action
        """
        # Initialize state in Q-table if not exists
        if state not in self.q_table:
            self.q_table[state] = {action: 0.0 for action in self.actions}
        
        # Epsilon-greedy exploration
        if training and np.random.random() < self.epsilon:
            action = np.random.choice(self.actions)
            logger.debug(f"Exploring: selected {action}")
        else:
            # Exploit: choose best action
            q_values = self.q_table[state]
            max_q = max(q_values.values())
            # Handle ties randomly
            best_actions = [a for a, q in q_values.items() if q == max_q]
            action = np.random.choice(best_actions)
            logger.debug(f"Exploiting: selected {action} (Q={max_q:.3f})")
        
        self.action_counts[action] += 1
        return action
    
    def calculate_reward(self, action: str, outcome: Dict[str, Any]) -> float:
        """
        Calculate reward based on action outcome.
        
        Args:
            action: Action taken
            outcome: Outcome dictionary with metrics
            
        Returns:
            Reward value
        """
        reward = 0.0
        
        # Positive rewards
        if outcome.get('threat_stopped', False):
            reward += 10.0  # Successfully stopped threat
        
        if outcome.get('false_positive', False):
            reward -= 5.0  # Penalty for false positive
        
        # Business impact penalties
        services_disrupted = outcome.get('services_disrupted', 0)
        reward -= services_disrupted * 2.0
        
        users_affected = outcome.get('users_affected', 0)
        reward -= users_affected * 0.1
        
        # Response time bonus
        response_time = outcome.get('response_time', 10.0)
        if response_time < 5.0:
            reward += 2.0  # Fast response bonus
        
        # Action-specific adjustments
        if action == 'monitor' and outcome.get('threat_stopped', False):
            reward -= 3.0  # Should have taken stronger action
        
        if action == 'isolate_container' and not outcome.get('threat_stopped', False):
            reward -= 2.0  # Overly aggressive for non-threat
        
        return reward
    
    def update_q_value(self, state: str, action: str, reward: float, 
                       next_state: str, done: bool) -> None:
        """
        Update Q-value using Q-learning update rule.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
        """
        # Initialize states if needed
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in self.actions}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in self.actions}
        
        # Q-learning update
        current_q = self.q_table[state][action]
        
        if done:
            target_q = reward
        else:
            max_next_q = max(self.q_table[next_state].values())
            target_q = reward + self.gamma * max_next_q
        
        # Update Q-value
        new_q = current_q + self.lr * (target_q - current_q)
        self.q_table[state][action] = new_q
        
        logger.debug(f"Q-update: {state} -> {action}: {current_q:.3f} -> {new_q:.3f} (reward={reward:.2f})")
    
    def store_experience(self, state: str, action: str, reward: float,
                        next_state: str, done: bool) -> None:
        """Store experience in replay buffer."""
        self.memory.append((state, action, reward, next_state, done))
    
    def replay_experience(self, batch_size: int = 32) -> None:
        """
        Replay experiences from memory for training.
        
        Args:
            batch_size: Number of experiences to replay
        """
        if len(self.memory) < batch_size:
            return
        
        # Sample random batch
        indices = np.random.choice(len(self.memory), batch_size, replace=False)
        batch = [self.memory[i] for i in indices]
        
        # Update Q-values for batch
        for state, action, reward, next_state, done in batch:
            self.update_q_value(state, action, reward, next_state, done)
    
    def decay_epsilon(self) -> None:
        """Decay exploration rate."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        logger.debug(f"Epsilon decayed to {self.epsilon:.4f}")
    
    def get_policy(self, state: str) -> Dict[str, float]:
        """
        Get action probabilities for a state.
        
        Args:
            state: State string
            
        Returns:
            Dictionary of action -> probability
        """
        if state not in self.q_table:
            return {action: 1.0 / len(self.actions) for action in self.actions}
        
        q_values = self.q_table[state]
        
        # Softmax policy
        exp_q = {a: np.exp(q) for a, q in q_values.items()}
        sum_exp = sum(exp_q.values())
        
        if sum_exp == 0:
            return {action: 1.0 / len(self.actions) for action in self.actions}
        
        return {a: exp_q[a] / sum_exp for a in self.actions}
    
    def save_q_table(self, path: str = "models/rl_q_table.json") -> None:
        """Save Q-table to file."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w') as f:
                json.dump({
                    'q_table': self.q_table,
                    'epsilon': self.epsilon,
                    'action_counts': self.action_counts,
                    'episode_rewards': self.episode_rewards[-100:]  # Last 100
                }, f, indent=2)
            
            logger.info(f"Q-table saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save Q-table: {e}")
    
    def _load_q_table(self, path: str = "models/rl_q_table.json") -> None:
        """Load Q-table from file."""
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                
                self.q_table = data.get('q_table', {})
                self.epsilon = data.get('epsilon', self.epsilon)
                self.action_counts = data.get('action_counts', self.action_counts)
                self.episode_rewards = data.get('episode_rewards', [])
                
                logger.info(f"Q-table loaded from {path} ({len(self.q_table)} states)")
        except Exception as e:
            logger.warning(f"Could not load Q-table: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            'states_learned': len(self.q_table),
            'epsilon': self.epsilon,
            'action_counts': self.action_counts,
            'avg_reward_last_100': np.mean(self.episode_rewards[-100:]) if self.episode_rewards else 0.0,
            'total_episodes': len(self.episode_rewards),
            'memory_size': len(self.memory)
        }
    
    def explain_decision(self, state: str, action: str) -> Dict[str, Any]:
        """
        Explain why an action was chosen.
        
        Args:
            state: State string
            action: Chosen action
            
        Returns:
            Explanation dictionary
        """
        if state not in self.q_table:
            return {
                'reason': 'No experience with this state',
                'q_value': 0.0,
                'policy': {}
            }
        
        q_values = self.q_table[state]
        policy = self.get_policy(state)
        
        return {
            'reason': f"Learned from experience (Q-value: {q_values[action]:.3f})",
            'q_value': q_values[action],
            'all_q_values': q_values,
            'policy': policy,
            'exploration_rate': self.epsilon,
            'times_taken': self.action_counts[action]
        }
