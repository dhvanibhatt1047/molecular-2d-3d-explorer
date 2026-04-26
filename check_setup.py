import torch
import rdkit
from rdkit import rdBase

print("--- Hardware & Library Check ---")

# Fix for the version error
print("✅ RDKit Version:", rdBase.rdkitVersion)

# GPU Check for your RTX 5060
cuda_available = torch.cuda.is_available()
print(f"✅ CUDA Available: {cuda_available}")

if cuda_available:
    print(f"🚀 GPU Detected: {torch.cuda.get_device_name(0)}")
else:
    print("⚠️ GPU not detected. Ensure your LOQ is plugged into power.")