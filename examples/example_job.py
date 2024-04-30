from tiled.client import from_uri

test_data = from_uri("https://tiled-demo.blueskyproject.io/api/v1/metadata/rsoxs/raw")
test_data = test_data["5be6565a-22c2-4fe3-92f0-29e6da75be17/primary/data"]
test_data = test_data["Small Angle CCD Detector_image"]
print(f"The dataset has {test_data.shape[0]} frames.")
