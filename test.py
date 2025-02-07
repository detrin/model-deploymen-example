# test.py
import requests
import base64
import time
import argparse
import os
from PIL import Image
import io

API_URL = "http://localhost:8000/process"
RESULT_URL = "http://localhost:8000/results/"

def encode_image(image_path):
    """Encode image to base64 with validation"""
    with open(image_path, "rb") as image_file:
        img_data = image_file.read()
        return base64.b64encode(img_data).decode()

def run_test(image_path=None, categories=["dog", "cat"]):
    """Run complete integration test"""
    
    if not image_path or not os.path.exists(image_path):
        raise ValueError("Valid image path required")
    
    # Test base64 encoding
    try:
        b64_image = encode_image(image_path)
    except Exception as e:
        print(f"Image encoding failed: {str(e)}")
        return
    
    # Test API submission
    try:
        start_time = time.time()
        response = requests.post(
            API_URL,
            json={"image_b64": b64_image, "categories": categories},
            timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {str(e)}")
        return
    
    task_data = response.json()
    if 'task_id' not in task_data:
        print("Invalid API response - missing task_id")
        return
    
    task_id = task_data['task_id']
    print(f"Task {task_id} submitted successfully")
    
    # Test result polling
    max_wait = 120  # 2 minutes timeout
    poll_interval = 1  # seconds
    start_time = time.time()
    
    while (time.time() - start_time) < max_wait:
        try:
            result_response = requests.get(
                f"{RESULT_URL}{task_id}",
                timeout=5
            )
            result_data = result_response.json()
            
            if result_data['status'] == 'completed':
                processing_time = time.time() - start_time
                print(f"\nProcessing completed in {processing_time:.2f} seconds")
                print(f"Result: {result_data['result']}")
                return True
                
            elif result_data['status'] == 'processing':
                print(f"\rProcessing... {int(time.time() - start_time)}s elapsed", end="")
                
        except requests.exceptions.RequestException as e:
            print(f"\nResult polling failed: {str(e)}")
            return False
        
        time.sleep(poll_interval)
    
    print("\nProcessing timeout reached")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Image Processing Service')
    parser.add_argument('--image', type=str, help='Path to test image')
    parser.add_argument('--categories', nargs='+', default=["dog", "cat"], help='List of categories to process')
    
    args = parser.parse_args()
    print(args.image)
    print(args.categories)
    
    success = run_test(args.image, args.categories)
    
    if success:
        print("Test completed successfully!")
        exit(0)
    else:
        print("Test failed")
        exit(1)