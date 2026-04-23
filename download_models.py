"""Download required local inference models from Hugging Face."""

# Developer: Vishal Raj V, Senior Engineer

import os
from pathlib import Path
from huggingface_hub import snapshot_download, hf_hub_download

def main():
    # Define paths
    base_dir = Path(__file__).resolve().parent
    models_dir = base_dir / "data" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n[1/2] Downloading BAAI/bge-reranker-base (Cross-Encoder)...")
    try:
        reranker_path = models_dir / "bge-reranker-base"
        # Download the entire model repository structure
        snapshot_download(
            repo_id="BAAI/bge-reranker-base",
            local_dir=str(reranker_path),
            local_dir_use_symlinks=False,  # Download actual files instead of symlinks
            ignore_patterns=["*.msgpack", "*.h5", "rust_model.ot"] # Ignore non-PyTorch weight formats to save space
        )
        print(f"✅ Reranker downloaded to: {reranker_path}")
    except Exception as e:
        print(f"❌ Failed to download reranker: {e}")

    print("\n[2/2] Downloading Unsloth Gemma GGUF Model...")
    try:
        gguf_filename = "gemma-4-E4B-it-Q4_K_M.gguf"
        # NOTE: Update repo_id 'unsloth/gemma-4-E4B-it-GGUF' if your file resides in a different unsloth repository
        repo_id = "unsloth/gemma-4-E4B-it-GGUF" 
        
        file_path = hf_hub_download(
            repo_id=repo_id,
            filename=gguf_filename,
            local_dir=str(models_dir),
            local_dir_use_symlinks=False
        )
        print(f"✅ GGUF model downloaded to: {file_path}")
    except Exception as e:
        print(f"❌ Failed to download GGUF model: {e}")
        print("   If the file is not found, verify the exact 'repo_id' and 'filename' spelling on HuggingFace.")

    print("\n🎉 Download process complete. You can now disconnect from the internet.")

if __name__ == "__main__":
    main()
