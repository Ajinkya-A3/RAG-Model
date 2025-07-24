import nltk
import os

def download_all_punkt():
    try:
        print("📥 Downloading all punkt resources...")

        # Create the target directory if it doesn't exist
        local_nltk_path = os.path.abspath("./nltk_data")
        os.makedirs(local_nltk_path, exist_ok=True)

        # Download punkt into local directory
        nltk.download("punkt", download_dir=local_nltk_path, raise_on_error=True)

        # Make sure it’s usable immediately in other scripts
        nltk.data.path.append(local_nltk_path)

        # Ensure the resource is actually found
        nltk.data.find("tokenizers/punkt")
        print("✅ 'punkt' resources downloaded successfully at:", local_nltk_path)

    except Exception as e:
        print(f"❌ Failed to download 'punkt': {e}")

if __name__ == "__main__":
    download_all_punkt()
