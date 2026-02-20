#!/usr/bin/env python3
"""Test retry logic without requiring Gemini API."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from image_renamer.analyzer import GeminiCliAnalyzer

def test_retry_parameters():
    """Test that retry parameters are correctly set."""
    print("\n" + "="*60)
    print("  TESTING RETRY LOGIC CONFIGURATION")
    print("="*60 + "\n")
    
    # Test 1: Default timeout
    print("[1] Testing default timeout...")
    analyzer = GeminiCliAnalyzer()
    assert analyzer.timeout == 30, f"Expected 30s, got {analyzer.timeout}s"
    print(f"    [+] Default timeout: {analyzer.timeout}s\n")
    
    # Test 2: Custom timeout
    print("[2] Testing custom timeout (60s)...")
    analyzer = GeminiCliAnalyzer(timeout_secs=60)
    assert analyzer.timeout == 60, f"Expected 60s, got {analyzer.timeout}s"
    print(f"    [+] Custom timeout: {analyzer.timeout}s\n")
    
    # Test 3: Retry parameters
    print("[3] Testing retry parameters...")
    assert GeminiCliAnalyzer.MAX_RETRIES == 2, "MAX_RETRIES should be 2"
    assert GeminiCliAnalyzer.RETRY_DELAY == 2, "RETRY_DELAY should be 2"
    print(f"    [+] MAX_RETRIES: {GeminiCliAnalyzer.MAX_RETRIES}")
    print(f"    [+] RETRY_DELAY: {GeminiCliAnalyzer.RETRY_DELAY}s\n")
    
    # Test 4: Total retry attempts
    total_attempts = 1 + GeminiCliAnalyzer.MAX_RETRIES
    print(f"[4] Total attempts per image: {total_attempts}")
    print(f"    Initial: 1")
    print(f"    Retries: {GeminiCliAnalyzer.MAX_RETRIES}")
    print(f"    Total: {total_attempts} attempts with exponential backoff\n")
    
    print("="*60)
    print("  [+] ALL RETRY LOGIC TESTS PASSED!")
    print("="*60)
    print("\nRetry Strategy Summary:")
    print(f"  • 1st attempt:     0s delay")
    print(f"  • 2nd attempt:     {GeminiCliAnalyzer.RETRY_DELAY}s delay")
    print(f"  • 3rd attempt:     {GeminiCliAnalyzer.RETRY_DELAY * 2}s delay")
    print(f"  • Max timeout per call: {analyzer.timeout}s")
    print(f"  • Total max time per image: ~{(GeminiCliAnalyzer.RETRY_DELAY + GeminiCliAnalyzer.RETRY_DELAY * 2) + (analyzer.timeout * total_attempts)}s")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = test_retry_parameters()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
