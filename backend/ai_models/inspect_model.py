import os
import glob
from datetime import datetime
from keras.models import load_model

BASE_DIR = os.path.dirname(__file__)
TRAIN_DB = os.path.join(BASE_DIR, "training_db")

print("Scanning training_db...")

# Get all .keras files
keras_files = glob.glob(os.path.join(TRAIN_DB, "*.keras"))

# Sort by modification time, newest first
keras_files.sort(key=os.path.getmtime, reverse=True)

with open(os.path.join(BASE_DIR, "db_summary.txt"), "w", encoding="utf-8") as f:
    f.write("===== TRAINING DB CONTENTS =====\n")
    if not keras_files:
        f.write("No models found in training_db.\n")
    else:
        f.write(f"Total Models Found: {len(keras_files)}\n\n")
        f.write(f"{'File Name':<30} | {'Last Modified':<20} | {'Size (KB)':<10}\n")
        f.write("-" * 65 + "\n")
        
        for file_path in keras_files:
            file_name = os.path.basename(file_path)
            mtime = os.path.getmtime(file_path)
            recent_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            size_kb = os.path.getsize(file_path) / 1024
            f.write(f"{file_name:<30} | {recent_time:<20} | {size_kb:.1f} KB\n")
            
        # Get details for the most recently updated model
        most_recent_model_path = keras_files[0]
        most_recent_name = os.path.basename(most_recent_model_path)
        
        f.write(f"\n\n===== DETAILS FOR MOST RECENT MODEL: {most_recent_name} =====\n\n")
        
        print(f"Loading most recent model: {most_recent_name}...")
        try:
            model = load_model(most_recent_model_path, compile=False)
            
            # Save summary
            model.summary(print_fn=lambda x: f.write(x + "\n"))

            f.write("\n\n===== MODEL INFO =====\n")
            f.write(f"Input shape: {model.input_shape}\n")
            f.write(f"Output shape: {model.output_shape}\n")
            f.write(f"Total layers: {len(model.layers)}\n\n")

            f.write("===== LAYER DETAILS =====\n")

            for layer in model.layers:
                f.write(f"\nLayer: {layer.name}\n")
                f.write(f"Type: {layer.__class__.__name__}\n")
                f.write(f"Params: {layer.count_params()}\n")
        except Exception as e:
            f.write(f"Error loading model {most_recent_name}: {e}\n")

print("✔ Database summary saved to db_summary.txt")