from app import create_app
from pathlib import Path

# Create instance directory if it doesn't exist
instance_path = Path(__file__).parent / "instance"
instance_path.mkdir(exist_ok=True)

app = create_app()

if __name__ == '__main__':
    app.run()
