"""Test vision model capabilities"""
import ollama
import sys
from pathlib import Path

def test_vision(image_path: str, prompt: str = "Describe this image in detail", model: str = "moondream"):
    """Test vision model with an image"""
    print(f"[*] Testing {model} with image: {image_path}")
    print(f"[*] Prompt: {prompt}\n")

    # Check if file exists
    img_path = Path(image_path)
    if not img_path.exists():
        print(f"ERROR: Image file not found at {image_path}")
        return

    print(f"[*] File exists: {img_path.absolute()}")
    print(f"[*] File size: {img_path.stat().st_size} bytes\n")

    try:
        # Use absolute path
        abs_path = str(img_path.absolute())

        print("[*] Sending to vision model...")
        response = ollama.chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [abs_path]
            }]
        )

        print("\n" + "="*60)
        print("VISION MODEL RESPONSE:")
        print("="*60)
        print(response['message']['content'])
        print("="*60)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_vision.py <image_path> [optional_prompt] [model]")
        print("\nExample:")
        print("  python test_vision.py photo.jpg")
        print("  python test_vision.py photo.jpg 'What colors do you see?'")
        print("  python test_vision.py photo.jpg 'Describe this' moondream")
        sys.exit(1)

    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else "Describe this image in detail"
    model = sys.argv[3] if len(sys.argv) > 3 else "moondream"

    test_vision(image_path, prompt, model)
