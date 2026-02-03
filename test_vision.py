"""Test moondream vision capabilities"""
import ollama
import sys

def test_vision(image_path: str, prompt: str = "Describe this image in detail"):
    """Test vision model with an image"""
    print(f"[*] Testing moondream with image: {image_path}")
    print(f"[*] Prompt: {prompt}\n")

    try:
        response = ollama.chat(
            model='moondream',
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }]
        )

        print("Agent Response:")
        print(response['message']['content'])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_vision.py <image_path> [optional_prompt]")
        print("\nExample:")
        print("  python test_vision.py photo.jpg")
        print("  python test_vision.py photo.jpg 'What colors do you see?'")
        sys.exit(1)

    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else "Describe this image in detail"

    test_vision(image_path, prompt)
