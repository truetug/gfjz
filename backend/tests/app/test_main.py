import pytest
from io import BytesIO
from PIL import Image
from app.main import resize_image, pad_image, flip_image, crop_image, process_frame

@pytest.fixture
def sample_image():
    # Create a 100x100 red image with RGBA mode
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    return img

@pytest.fixture
def sample_transparent_image():
    # Create a 100x100 transparent image with RGBA mode
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    return img

def test_pad_image(sample_image):
    # Test padding with a solid background color
    padded = pad_image(sample_image, (200, 200), color=(0, 0, 255), centering=(0.5, 0.5))
    assert padded.size == (200, 200), "Padding failed: Size mismatch"
    assert padded.getpixel((150, 150)) == (0, 0, 255, 255), "Padding failed: Background color mismatch"
    assert padded.getpixel((50, 50)) == (255, 0, 0, 255), "Padding failed: Content mismatch"

def test_pad_image_transparent(sample_transparent_image):
    # Test padding on a fully transparent image
    padded = pad_image(sample_transparent_image, (200, 200), color=(0, 255, 0), centering=(0.3, 0.7))
    assert padded.size == (200, 200), "Padding failed: Size mismatch"
    assert padded.getpixel((150, 150)) == (0, 255, 0, 255), "Padding failed: Background color mismatch"
    assert padded.getpixel((50, 50)) == (0, 0, 0, 0), "Padding failed: Content mismatch"

def test_pad_image_with_different_centering(sample_image):
    # Test padding with custom centering
    padded = pad_image(sample_image, (200, 200), color=(0, 0, 255), centering=(0.3, 0.7))
    assert padded.size == (200, 200), "Padding failed: Size mismatch"
    assert padded.getpixel((20, 140)) == (0, 0, 255, 255), "Padding failed: Background color mismatch"
    assert padded.getpixel((70, 30)) == (255, 0, 0, 255), "Padding failed: Content position mismatch"

def test_flip_image_vertical(sample_image):
    flipped = flip_image(sample_image, mode="vertical")
    assert flipped.getpixel((0, 0)) == sample_image.getpixel((0, 99)), "Vertical flip failed"

def test_flip_image_horizontal(sample_image):
    flipped = flip_image(sample_image, mode="horizontal")
    assert flipped.getpixel((0, 0)) == sample_image.getpixel((99, 0)), "Horizontal flip failed"

def test_flip_image_both(sample_image):
    flipped = flip_image(sample_image, mode="both")
    assert flipped.getpixel((0, 0)) == sample_image.getpixel((99, 99)), "Both flip failed"

def test_crop_image(sample_image):
    cropped = crop_image(sample_image, (10, 10, 50, 50))
    assert cropped.size == (40, 40), "Crop failed: Size mismatch"

def test_process_frame(sample_image):
    pipeline = [
        {"plugin": "resize", "params": {"size": (50, 50)}},
        {"plugin": "pad", "params": {"target_size": (100, 100), "color": (0, 255, 0)}},
    ]
    plugin_mapping = {
        "resize": resize_image,
        "pad": pad_image,
    }
    processed = process_frame(sample_image, pipeline)
    assert processed.size == (100, 100), "Process frame failed: Size mismatch"
    assert processed.getpixel((75, 75)) == (0, 255, 0, 255), "Process frame failed: Color mismatch"
