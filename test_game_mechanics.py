#!/usr/bin/env python3
"""
Game Mechanics Unit Tests
Tests the game mechanics features: scoring, strikes, and dynamic timing
"""
import pytest
import time
from face_detector import CameraFaceDetector


class TestGameMechanics:
    """Test suite for game mechanic features"""
    
    @pytest.fixture
    def game(self):
        """Create a game instance for testing"""
        detector = CameraFaceDetector(camera_id=0, use_hardware=False, enable_monitoring=False)
        return detector
    
    def test_game_initialization(self, game):
        """Test that game starts with correct initial state"""
        game.reset_game()
        assert game.score == 0
        assert game.strikes == 0
        assert game.game_over == False
    
    def test_score_increment(self, game):
        """Test that score increments correctly"""
        game.reset_game()
        assert game.score == 0
        game.add_score()
        assert game.score == 1
        game.add_score()
        assert game.score == 2
    
    def test_strike_increment(self, game):
        """Test that strikes increment correctly"""
        game.reset_game()
        assert game.strikes == 0
        game.add_strike()
        assert game.strikes == 1
        game.add_strike()
        assert game.strikes == 2
    
    def test_game_over_at_strike_3(self, game):
        """Test that game ends when strikes reach 3"""
        game.reset_game()
        assert game.game_over == False
        game.add_strike()  # 1
        assert game.game_over == False
        game.add_strike()  # 2
        assert game.game_over == False
        game.add_strike()  # 3
        assert game.game_over == True
    
    def test_switch_time_calculation(self, game):
        """Test that switch time decreases with score"""
        game.reset_game()
        
        # Initial time
        initial_time = game.get_switch_time()
        assert initial_time == 3.0
        
        # After score increases
        game.add_score()
        time_at_score_1 = game.get_switch_time()
        assert time_at_score_1 == 2.9
        
        game.add_score()
        time_at_score_2 = game.get_switch_time()
        assert time_at_score_2 == 2.8
        
        # Verify it decreases
        assert time_at_score_1 < initial_time
        assert time_at_score_2 < time_at_score_1
    
    def test_switch_time_minimum(self, game):
        """Test that switch time has a minimum of 0.5 seconds"""
        game.reset_game()
        
        # Add many scores to exceed minimum
        for _ in range(50):
            game.add_score()
        
        current_time = game.get_switch_time()
        assert current_time == 0.5  # Should be minimum
    
    def test_timer_reset(self, game):
        """Test that timer can be reset"""
        game.reset_game()
        game.reset_switch_timer()
        
        # Immediately after reset, elapsed should be near 0
        elapsed = game.get_switch_elapsed_time()
        assert elapsed < 0.1  # Should be very small
        
        # Wait a bit and check it increases
        time.sleep(0.1)
        elapsed_after_wait = game.get_switch_elapsed_time()
        assert elapsed_after_wait > elapsed
    
    def test_timer_exceeds_switch_time(self, game):
        """Test that elapsed time can exceed switch time"""
        game.reset_game()
        game.reset_switch_timer()
        
        switch_time = game.get_switch_time()
        
        # Wait for timer to exceed switch time
        time.sleep(switch_time + 0.1)
        
        elapsed = game.get_switch_elapsed_time()
        assert elapsed > switch_time
    
    def test_game_reset_clears_state(self, game):
        """Test that reset clears all game state"""
        game.reset_game()
        
        # Play for a bit
        game.add_score()
        game.add_score()
        game.add_strike()
        
        assert game.score == 2
        assert game.strikes == 1
        
        # Reset
        game.reset_game()
        
        assert game.score == 0
        assert game.strikes == 0
        assert game.game_over == False
    
    def test_difficulty_progression(self, game):
        """Test that difficulty increases with score"""
        game.reset_game()
        
        times = []
        for i in range(6):
            times.append(game.get_switch_time())
            game.add_score()
        
        # All times should be decreasing
        for i in range(len(times) - 1):
            assert times[i] > times[i + 1], f"Time {i} not greater than time {i+1}"
    
    def test_multiple_games(self, game):
        """Test that multiple games can be played sequentially"""
        for game_num in range(3):
            game.reset_game()
            assert game.score == 0
            assert game.strikes == 0
            
            game.add_score()
            game.add_score()
            assert game.score == 2
            
            game.add_strike()
            game.add_strike()
            game.add_strike()
            assert game.game_over == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
