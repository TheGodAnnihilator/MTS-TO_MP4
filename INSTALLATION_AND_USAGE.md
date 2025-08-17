
# MTS to MP4 Converter - Installation and Usage Guide

## Prerequisites

### 1. Install FFmpeg
FFmpeg is required for video conversion. Install it based on your operating system:

#### Windows:
1. Download FFmpeg from https://ffmpeg.org/download.html#build-windows
2. Extract the files to a folder (e.g., C:\ffmpeg)
3. Add the bin folder to your system PATH:
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Under System Variables, find "Path" and click Edit
   - Click "New" and add: C:\ffmpeg\bin
   - Click OK and restart command prompt

#### macOS:
```bash
# Using Homebrew (recommended)
brew install ffmpeg

# Or using MacPorts
sudo port install ffmpeg
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Linux (CentOS/RHEL/Fedora):
```bash
# CentOS/RHEL
sudo yum install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

### 2. Verify FFmpeg Installation
Open terminal/command prompt and run:
```bash
ffmpeg -version
```
You should see version information if installed correctly.

### 3. Python Requirements
This script requires Python 3.6 or higher with tkinter (usually included by default).

## Installation Steps

1. Save the `mts_to_mp4_converter.py` file to your desired directory
2. No additional Python packages need to be installed - the script uses only built-in libraries

## Usage Instructions

### Running the Application
1. Open terminal/command prompt
2. Navigate to the directory containing the script
3. Run: `python mts_to_mp4_converter.py`

### Using the GUI

#### 1. Select Input File
- Click "Browse" next to "Input MTS File"
- Select your .mts, .MTS, .m2ts, or .M2TS file
- The output filename will be automatically generated

#### 2. Choose Output Location (Optional)
- Click "Browse" next to "Output MP4 File" to change the output location
- Or manually edit the output path in the text field

#### 3. Configure Quality Settings

**Quality (CRF):**
- Range: 0-51
- Lower values = Better quality, larger files
- Higher values = Lower quality, smaller files
- Recommended values:
  - 18-20: Visually lossless (large files)
  - 21-23: High quality (balanced)
  - 24-28: Good quality (smaller files)
  - Default: 18 (high quality)

**Encoding Speed:**
- veryslow: Best compression, slowest
- slower: Better compression, slower
- slow: Good compression, slow
- medium: Balanced (default)
- fast: Faster encoding, larger files
- faster: Much faster, larger files
- veryfast: Fastest, largest files

**Copy Streams (Lossless):**
- Check this for absolutely no quality loss
- Fastest conversion method
- Only changes container format, not video/audio data
- Recommended for preserving original quality

#### 4. Start Conversion
- Click "Start Conversion"
- Monitor progress in the progress bar
- View detailed information in the conversion log
- Cancel anytime using the "Cancel" button

### Command Line Usage (Alternative)
If you prefer command line, you can use ffmpeg directly:

```bash
# Lossless conversion (recommended for quality preservation)
ffmpeg -i input.mts -c copy -f mp4 -movflags +faststart output.mp4

# High quality with re-encoding (smaller file)
ffmpeg -i input.mts -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k -movflags +faststart output.mp4

# Batch conversion (all MTS files in current directory)
for i in *.mts; do ffmpeg -i "$i" -c copy -f mp4 -movflags +faststart "${i%.*}.mp4"; done
```

## Quality Settings Explanation

### CRF (Constant Rate Factor)
- **CRF 0**: Lossless (not recommended, extremely large files)
- **CRF 17-18**: Visually lossless for most content
- **CRF 20-23**: High quality, good balance
- **CRF 24-28**: Standard quality for web/streaming
- **CRF 28+**: Lower quality, very small files

### Presets
Presets control encoding speed vs compression efficiency:
- **Slower presets**: Better compression, smaller files, longer conversion time
- **Faster presets**: Worse compression, larger files, shorter conversion time

## Troubleshooting

### Common Issues:

1. **"FFmpeg is not installed" error**
   - Ensure FFmpeg is installed and in system PATH
   - Verify with `ffmpeg -version` command

2. **"Permission denied" error**
   - Check write permissions for output directory
   - Run as administrator if necessary

3. **"File not found" error**
   - Verify input file exists and path is correct
   - Check for special characters in filename

4. **Very slow conversion**
   - Use "Copy streams" option for fastest conversion
   - Choose faster preset (fast, faster, veryfast)
   - Ensure sufficient disk space and RAM

5. **Poor quality output**
   - Lower CRF value (18-20 recommended)
   - Use slower preset for better compression
   - Use "Copy streams" for no quality loss

### Performance Tips:

1. **For maximum quality**: Use "Copy streams" option
2. **For balanced quality/size**: CRF 20-22 with medium preset
3. **For smallest files**: CRF 28+ with veryslow preset
4. **For fastest conversion**: Use "Copy streams" or veryfast preset

## File Size Considerations

- **MTS files** are typically large (several GB)
- **Copy mode** maintains original size
- **Re-encoding** can reduce size by 30-70% depending on settings
- Ensure sufficient free disk space (at least 2x input file size)

## Advanced Usage

### Batch Processing Multiple Files:
The GUI currently processes one file at a time. For batch processing:

1. Use the command line method shown above, or
2. Run the GUI multiple times for different files, or
3. Modify the script to add batch processing features

### Custom FFmpeg Parameters:
You can modify the script to add custom FFmpeg parameters by editing the command construction section in the code.

## Support

This script handles most common MTS conversion scenarios. If you encounter issues:

1. Check the conversion log for detailed error messages
2. Verify FFmpeg installation and version
3. Test with a small MTS file first
4. Ensure sufficient system resources (RAM, disk space, CPU)

The script is designed to handle large files efficiently and provides comprehensive error handling and progress feedback.
