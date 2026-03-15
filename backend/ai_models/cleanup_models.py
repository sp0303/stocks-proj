import os
import glob

base_dir = os.path.dirname(os.path.abspath(__file__))
train_db = os.path.join(base_dir, "training_db")

def cleanup():
    print(f"Checking for obsolete models in {train_db}...")
    
    # 1. Find all legacy .h5 files
    h5_files = glob.glob(os.path.join(train_db, "*.h5"))
    
    if not h5_files:
        print("No legacy .h5 files found. Your database is clean!")
        return

    print(f"Found {len(h5_files)} legacy .h5 files.")
    
    confirm = input("Are you sure you want to delete these files? (y/n): ")
    if confirm.lower() == 'y':
        for f in h5_files:
            try:
                os.remove(f)
                print(f"Deleted: {os.path.basename(f)}")
            except Exception as e:
                print(f"Error deleting {f}: {e}")
        print("\nCleanup complete!")
    else:
        print("Cleanup cancelled.")

if __name__ == "__main__":
    cleanup()
