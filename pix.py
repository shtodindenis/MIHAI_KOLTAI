import os
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Pixelizer for game videos")
    parser.add_argument("-i", "--input", required=True, help="Input filename in assets/video/raw/")
    parser.add_argument("-o", "--output", required=True, help="Output filename in assets/video/")
    parser.add_argument("-s", "--scale", type=int, default=4, help="Pixel scale (default: 4)")
    
    args = parser.parse_args()

    raw_path = os.path.join("assets", "video", "raw", args.input)
    out_path = os.path.join("assets", "video", "zasora", args.output)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    command = [
        "ffmpeg", "-i", raw_path,
        "-vf", f"scale=iw/{args.scale}:-1:flags=neighbor,scale=iw*{args.scale}:-1:flags=neighbor",
        "-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0",
        "-c:a", "libopus", "-b:a", "128k",
        out_path, "-y"
    ]

    print(f"Обработка: {raw_path} -> {out_path} (Scale: {args.scale})")
    subprocess.run(command)

if __name__ == "__main__":
    main()