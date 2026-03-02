"""Test script for the Vision/Disease Detection endpoint."""
import httpx
import base64
import json
from PIL import Image
import io


BASE = "http://127.0.0.1:8000"


def create_test_image():
    """Create a simple test image (green leaf-like) and encode to base64."""
    img = Image.new("RGB", (256, 256), color=(34, 139, 34))  # Forest green
    # Add some variation to simulate a leaf
    for x in range(50, 200):
        for y in range(50, 200):
            r = 34 + (x % 30)
            g = 120 + (y % 40)
            b = 20
            img.putpixel((x, y), (r, g, b))

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def main():
    # First create a farmer
    print("=== Creating test farmer ===")
    import random
    r = httpx.post(
        f"{BASE}/api/farmers/",
        json={
            "name": "Vision Test Farmer",
            "phone": f"8{random.randint(100000000, 999999999)}",
            "location": "Maharashtra",
            "language": "en",
        },
    )
    farmer = r.json()
    fid = farmer["id"]
    print(f"Farmer: {fid}")

    # Test vision endpoint
    print("\n=== DISEASE DETECTION TEST ===")
    img_b64 = create_test_image()
    print(f"Test image: 256x256 green image, base64 length={len(img_b64)}")

    r = httpx.post(
        f"{BASE}/api/vision/detect",
        json={
            "farmer_id": fid,
            "image_base64": img_b64,
            "crop_type": "Tomato",
        },
        timeout=60,
    )

    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Disease: {data['disease']}")
        print(f"Confidence: {data['confidence']}")
        print(f"Risk Level: {data['risk_level']}")
        print(f"Treatment (first 300): {data['treatment_plan'][:300]}...")
        print("\n✅ VISION ENDPOINT WORKING!")
    else:
        print(f"Error: {r.text}")
        print("\n❌ VISION ENDPOINT FAILED")


if __name__ == "__main__":
    main()
