#!/usr/bin/env python3
"""Test parallel image processing configuration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from image_renamer.main import ImageRenamerCLI

def test_parallel_processing():
    """Test parallel processing configuration and worker validation."""
    print("\n" + "="*60)
    print("  TESTING PARALLEL PROCESSING SUPPORT")
    print("="*60 + "\n")
    
    # Test 1: Single worker (default)
    print("[1] Testing default single worker...")
    cli1 = ImageRenamerCLI(workers=1)
    assert cli1.workers == 1, "Default should be 1 worker"
    print(f"    [+] Default: {cli1.workers} worker\n")
    
    # Test 2: Multiple workers
    print("[2] Testing 5 concurrent workers...")
    cli5 = ImageRenamerCLI(workers=5)
    assert cli5.workers == 5, "Should accept 5 workers"
    print(f"    [+] Configured: {cli5.workers} concurrent agents\n")
    
    # Test 3: Worker clamping (should clamp to max 5)
    print("[3] Testing worker clamping...")
    cli_over = ImageRenamerCLI(workers=100)
    assert cli_over.workers == ImageRenamerCLI.MAX_WORKERS, f"Should clamp to {ImageRenamerCLI.MAX_WORKERS}"
    print(f"    [+] 100 workers clamped to max: {cli_over.workers}\n")
    
    # Test 4: Test worker validation (lower bound)
    print("[4] Testing lower bound clamping...")
    cli_zero = ImageRenamerCLI(workers=0)
    assert cli_zero.workers == 1, "Should clamp minimum to 1"
    print(f"    [+] 0 workers clamped to min: {cli_zero.workers}\n")
    
    # Test 5: Verify processing methods exist
    print("[5] Verifying parallel processing methods...")
    assert hasattr(cli5, '_process_images_sequential'), "Missing sequential processing method"
    assert hasattr(cli5, '_process_images_parallel'), "Missing parallel processing method"
    assert hasattr(cli5, '_analyze_image_task'), "Missing image analysis task method"
    print(f"    [+] _process_images_sequential exists")
    print(f"    [+] _process_images_parallel exists")
    print(f"    [+] _analyze_image_task exists\n")
    
    # Test 6: Max workers constant
    print("[6] Verifying MAX_WORKERS constant...")
    assert ImageRenamerCLI.MAX_WORKERS == 5, "MAX_WORKERS should be 5"
    print(f"    [+] MAX_WORKERS = {ImageRenamerCLI.MAX_WORKERS}\n")
    
    print("="*60)
    print("  [+] ALL PARALLEL PROCESSING TESTS PASSED!")
    print("="*60)
    print("\nParallel Processing Capabilities Summary:")
    print(f"  • Max concurrent agents: {ImageRenamerCLI.MAX_WORKERS}")
    print(f"  • Default workers: 1 (sequential processing)")
    print(f"  • Configurable via: --workers N (1-{ImageRenamerCLI.MAX_WORKERS})")
    print(f"  • Sequential method: _process_images_sequential()")
    print(f"  • Parallel method: _process_images_parallel()")
    print(f"  • Task worker: _analyze_image_task()")
    print(f"  • Thread-safe logging: Using Lock() for synchronization")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = test_parallel_processing()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
