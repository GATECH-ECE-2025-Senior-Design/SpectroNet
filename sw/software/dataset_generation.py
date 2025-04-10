#!/usr/bin/env python3
import spectrogram as spec
import numpy as np
import noise_integration
import windowing
import argparse
import librosa
import math
import os
from concurrent.futures import ProcessPoolExecutor
from collections import namedtuple

# ------------------------------------------------------------------------------
# 1) Parse command line arguments (unchanged)
# ------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Generate spectrograms.")
parser.add_argument('--enable_noise', action='store_true', default=False,
                    help="To enable mixing background noise.")
parser.add_argument('--snr', type=int, default=12,
                    help="Signal to noise ratio if background noise is enabled.")
parser.add_argument('--crop', action='store_true', default=False,
                    help="Crops audio, then pads left & right to desired time. Use with windowing=mid")
parser.add_argument('--windowing', type=str, default="mid",
                    help="The algorithm used to create a square spectrogram.")
parser.add_argument('--sr', type=int, default=8000,
                    help="Define sample rate of the audio signal.")
parser.add_argument('--spec_type', type=str, default="simple",
                    help="Define which spectrogram type is generated.")
parser.add_argument('--resolution', type=int, default=96,
                    help="Define resolution (square) of the spectrogram.")
parser.add_argument('--dtype', type=str, default="float32",
                    help="Define datatype of the audio/spectrogram.")
parser.add_argument('--time', type=float, default=1,
                    help="Define the time period that is included in a spectrogram.")
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    help="Verbose output to console.")
parser.add_argument('--noise_samples', type=int, default=1,
                    help="Number of noise samples to overlay on each digit.")
parser.add_argument('--samples_per_dft', type=int, default=256,
                    help="Number of samples used for each DFT.")
parser.add_argument('--input_dir', type=str, default="../datasets/digits",
                    help="Directory containing raw .wav files.")
parser.add_argument('--output_dir', type=str, default="../datasets/images",
                    help="Directory to save generated spectrograms.")
args = parser.parse_args()

# ------------------------------------------------------------------------------
# 2) Precompute constants & collect file list (unchanged)
# ------------------------------------------------------------------------------
if not os.path.exists(args.input_dir):
    raise FileNotFoundError(f"❌ Error: Input directory '{args.input_dir}' does not exist!")
os.makedirs(args.output_dir, exist_ok=True)

all_wav_paths = []
for root, _, files in os.walk(args.input_dir):
    for f in files:
        if f.lower().endswith(".wav"):
            all_wav_paths.append(os.path.join(root, f))

if not all_wav_paths:
    raise FileNotFoundError(f"❌ Error: No .wav files found in '{args.input_dir}' (including subfolders)!")

print(f"🔍 Found {len(all_wav_paths)} .wav files in {args.input_dir} (recursively).")
print(f"📂 Spectrograms will be saved in {args.output_dir}")

num_samples_per_square = args.time * args.sr
num_hop = num_samples_per_square - args.samples_per_dft
if args.spec_type in ("simple", "cqt"):
    hop_length = max(1, math.floor(num_hop / (args.resolution - 1)))
else:  # mel
    hop_length = max(1, math.ceil(num_hop / (args.resolution - 1)))

dtype = np.dtype(args.dtype).type

if args.enable_noise:
    noise_integration.integrate_noise(args.snr, args.noise_samples, args.verbose)
    # Optionally re-scan input_dir here if noise_integration writes new files.

# ------------------------------------------------------------------------------
# 3) Define module-level job and worker
# ------------------------------------------------------------------------------

SpectroJob = namedtuple("SpectroJob", ["wav_path", "out_path"])

def make_job(wav_path):
    base = os.path.splitext(os.path.basename(wav_path))[0]
    return SpectroJob(
        wav_path=wav_path,
        out_path=os.path.join(args.output_dir, base + ".npy")
    )

def process_job(job: SpectroJob):
    try:
        audio_data = spec.read_wav(
            job.wav_path,
            target_sample_rate=args.sr,
            target_dtype=dtype
        )
        if args.crop:
            audio_data = windowing.crop(audio_data, args.time, args.sr)

        bins, times, power = spec.spectrogram_choice(
            audio_data,
            sample_rate=args.sr,
            spec_type=args.spec_type,
            resolution=args.resolution,
            hop_length=hop_length,
            target_dtype=dtype,
            samples_per_dft=args.samples_per_dft
        )

        mode = args.windowing if not args.crop else "mid"
        power = windowing.window(power, audio_data, mode)
        power_dB = librosa.power_to_db(power, ref=np.max)

        np.save(job.out_path, power_dB)
        return True
    except Exception as e:
        print(f"❌ Error processing {job.wav_path}: {e}")
        return False

# ------------------------------------------------------------------------------
# 4) Build job list
# ------------------------------------------------------------------------------
jobs = [make_job(p) for p in all_wav_paths]

# ------------------------------------------------------------------------------
# 5) Batched multiprocessing
# ------------------------------------------------------------------------------
def batched_executor(jobs, batch_size=100, max_workers=30):
    total = len(jobs)
    num_batches = (total + batch_size - 1) // batch_size
    for idx in range(0, total, batch_size):
        batch = jobs[idx:idx+batch_size]
        print(f"🚀 Processing batch {idx//batch_size+1}/{num_batches} ({len(batch)} files)...")
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(process_job, batch))
        succeeded = sum(results)
        print(f"✅ Batch completed: {succeeded}/{len(batch)} succeeded")

# ------------------------------------------------------------------------------
# 6) Run pipeline
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    batched_executor(jobs, batch_size=100, max_workers=30)
    print(f"✅ Done generating spectrograms for {len(all_wav_paths)} WAV files.")
