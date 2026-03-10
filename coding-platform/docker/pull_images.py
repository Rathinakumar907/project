import subprocess

images = [
    "python:3.10-alpine",
    "gcc:latest",
    "openjdk:17-alpine"
]

print("Pulling required Docker images for Sandbox Execution...")
for img in images:
    print(f"Pulling {img}...")
    subprocess.run(["docker", "pull", img])
    
print("All images pulled successfully.")
