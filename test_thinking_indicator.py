"""Test the thinking indicator"""
import sys
import time
sys.path.insert(0, '.')

from simple_agent import ThinkingIndicator

def test_thinking_indicator():
    print("[TEST] Testing Thinking Indicator\n")

    # Test 1: Basic animation
    print("[1] Starting thinking animation for 3 seconds...")
    indicator = ThinkingIndicator("Agent: Thinking")
    indicator.start()
    time.sleep(3)
    indicator.stop()
    print("Done! Indicator stopped.\n")

    # Test 2: Shorter duration
    print("[2] Quick test (1 second)...")
    indicator2 = ThinkingIndicator("Processing")
    indicator2.start()
    time.sleep(1)
    indicator2.stop()
    print("Done!\n")

    # Test 3: Custom message
    print("[3] Custom message test...")
    indicator3 = ThinkingIndicator("Agent: Analyzing your request")
    indicator3.start()
    time.sleep(2)
    indicator3.stop()
    print("Complete!\n")

    print("[SUCCESS] Thinking indicator working correctly!")
    print("\nYou should have seen animated dots (...) during each test.")

if __name__ == "__main__":
    test_thinking_indicator()
