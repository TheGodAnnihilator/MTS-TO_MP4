
#!/usr/bin/env python3
"""
MTS to MP4 Converter - Command Line Version
A simple command-line tool to convert MTS files to MP4 format.
"""

import os
import sys
import subprocess
import argparse
import re
from pathlib import Path

class MTSConverterCLI:
    def __init__(self):
        self.check_ffmpeg()

    def check_ffmpeg(self):
        """Check if ffmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: FFmpeg is not installed or not in PATH.")
            print("Please install FFmpeg first. See INSTALLATION_AND_USAGE.md for instructions.")
            sys.exit(1)

    def get_video_info(self, input_file):
        """Get video information using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', input_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Video information for {input_file}:")

            # Extract basic info using ffprobe
            cmd_simple = ['ffprobe', '-v', 'quiet', '-show_entries', 
                         'format=duration,size,bit_rate', '-of', 'csv=p=0', input_file]
            result_simple = subprocess.run(cmd_simple, capture_output=True, text=True, check=True)

            duration_cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                           '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)

            try:
                duration = float(duration_result.stdout.strip())
                print(f"  Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            except ValueError:
                print("  Duration: Unknown")

            file_size = os.path.getsize(input_file) / (1024 * 1024 * 1024)  # GB
            print(f"  File size: {file_size:.2f} GB")

        except subprocess.CalledProcessError:
            print(f"Warning: Could not retrieve video information for {input_file}")

    def parse_progress(self, line, total_duration):
        """Parse ffmpeg output for progress"""
        time_match = re.search(r'time=([0-9:.]+)', line)
        if time_match and total_duration:
            time_str = time_match.group(1)
            try:
                time_parts = time_str.split(':')
                if len(time_parts) == 3:
                    hours = float(time_parts[0])
                    minutes = float(time_parts[1])
                    seconds = float(time_parts[2])
                    current_time = hours * 3600 + minutes * 60 + seconds
                    progress = (current_time / total_duration) * 100
                    return min(progress, 100)
            except (ValueError, IndexError):
                pass
        return None

    def convert_file(self, input_file, output_file, crf=18, preset='medium', copy_streams=False, verbose=False):
        """Convert MTS to MP4"""
        print(f"Converting: {input_file}")
        print(f"Output: {output_file}")

        # Get duration for progress tracking
        total_duration = None
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                   '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            total_duration = float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            pass

        # Build command
        if copy_streams:
            cmd = [
                'ffmpeg', '-i', input_file, '-c', 'copy', '-f', 'mp4',
                '-movflags', '+faststart', '-y', output_file
            ]
            print("Using lossless copy mode...")
        else:
            cmd = [
                'ffmpeg', '-i', input_file,
                '-c:v', 'libx264', '-crf', str(crf), '-preset', preset,
                '-c:a', 'aac', '-b:a', '192k',
                '-movflags', '+faststart', '-y', output_file
            ]
            print(f"Using re-encoding mode: CRF {crf}, preset {preset}")

        if verbose:
            print(f"Command: {' '.join(cmd)}")

        try:
            print("Starting conversion...")
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, universal_newlines=True
            )

            last_progress = 0
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if verbose and line:
                    print(f"FFmpeg: {line}")

                # Show progress
                if total_duration:
                    progress = self.parse_progress(line, total_duration)
                    if progress is not None and progress - last_progress >= 5:  # Update every 5%
                        print(f"Progress: {progress:.1f}%")
                        last_progress = progress

            process.wait()

            if process.returncode == 0:
                print("✓ Conversion completed successfully!")

                # Show output file info
                if os.path.exists(output_file):
                    output_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
                    print(f"Output file size: {output_size:.2f} MB")

                    if not copy_streams:
                        input_size = os.path.getsize(input_file) / (1024 * 1024)  # MB
                        compression_ratio = ((input_size - output_size) / input_size) * 100
                        print(f"Size reduction: {compression_ratio:.1f}%")

                return True
            else:
                print(f"✗ Conversion failed with return code: {process.returncode}")
                return False

        except KeyboardInterrupt:
            print("\n✗ Conversion cancelled by user")
            process.terminate()
            return False
        except Exception as e:
            print(f"✗ Error during conversion: {e}")
            return False

    def batch_convert(self, input_dir, output_dir=None, **kwargs):
        """Convert all MTS files in a directory"""
        input_path = Path(input_dir)
        if not input_path.exists() or not input_path.is_dir():
            print(f"Error: Input directory {input_dir} does not exist")
            return

        # Find MTS files
        mts_files = []
        for ext in ['*.mts', '*.MTS', '*.m2ts', '*.M2TS']:
            mts_files.extend(input_path.glob(ext))

        if not mts_files:
            print(f"No MTS files found in {input_dir}")
            return

        print(f"Found {len(mts_files)} MTS files")

        # Set output directory
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = input_path

        # Convert each file
        successful = 0
        for i, input_file in enumerate(mts_files, 1):
            print(f"\n[{i}/{len(mts_files)}] Processing {input_file.name}")

            output_file = output_path / f"{input_file.stem}.mp4"

            # Skip if output already exists
            if output_file.exists():
                response = input(f"Output file {output_file.name} already exists. Overwrite? (y/N): ")
                if response.lower() != 'y':
                    print("Skipping...")
                    continue

            if self.convert_file(str(input_file), str(output_file), **kwargs):
                successful += 1

        print(f"\nBatch conversion completed: {successful}/{len(mts_files)} files converted successfully")

def main():
    parser = argparse.ArgumentParser(
        description="Convert MTS files to MP4 format using FFmpeg",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single file with default settings
  python mts_converter_cli.py input.mts

  # Convert with custom quality and preset
  python mts_converter_cli.py input.mts -o output.mp4 --crf 20 --preset slow

  # Lossless conversion (copy streams)
  python mts_converter_cli.py input.mts --copy

  # Batch convert all MTS files in directory
  python mts_converter_cli.py /path/to/mts/files --batch

  # Batch convert with output directory
  python mts_converter_cli.py /path/to/mts/files --batch -o /path/to/output
        """
    )

    parser.add_argument('input', help='Input MTS file or directory (for batch mode)')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('--crf', type=int, default=18, 
                       help='Quality factor (0-51, lower=better quality) [default: 18]')
    parser.add_argument('--preset', default='medium',
                       choices=['veryslow', 'slower', 'slow', 'medium', 'fast', 'faster', 'veryfast'],
                       help='Encoding preset [default: medium]')
    parser.add_argument('--copy', action='store_true',
                       help='Copy streams without re-encoding (lossless, fastest)')
    parser.add_argument('--batch', action='store_true',
                       help='Batch convert all MTS files in input directory')
    parser.add_argument('--info', action='store_true',
                       help='Show video information only (no conversion)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output (show FFmpeg messages)')

    args = parser.parse_args()

    converter = MTSConverterCLI()

    if args.info:
        # Just show video info
        if os.path.isfile(args.input):
            converter.get_video_info(args.input)
        else:
            print(f"Error: {args.input} is not a valid file")
        return

    if args.batch:
        # Batch mode
        converter.batch_convert(
            args.input, args.output,
            crf=args.crf, preset=args.preset, copy_streams=args.copy, verbose=args.verbose
        )
    else:
        # Single file mode
        if not os.path.isfile(args.input):
            print(f"Error: Input file {args.input} does not exist")
            return

        # Generate output filename if not provided
        if not args.output:
            input_path = Path(args.input)
            args.output = str(input_path.with_suffix('.mp4'))

        # Check if output exists
        if os.path.exists(args.output):
            response = input(f"Output file {args.output} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Conversion cancelled")
                return

        # Show input info
        converter.get_video_info(args.input)
        print()

        # Convert
        success = converter.convert_file(
            args.input, args.output,
            crf=args.crf, preset=args.preset, copy_streams=args.copy, verbose=args.verbose
        )

        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
