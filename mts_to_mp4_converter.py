
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import threading
import os
import sys
import re
from pathlib import Path

class MTStoMP4Converter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MTS to MP4 Converter")
        self.root.geometry("600x400")
        self.root.resizable(True, True)

        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.conversion_running = False
        self.ffmpeg_process = None

        # Check if ffmpeg is available
        if not self.check_ffmpeg():
            messagebox.showerror("Error", "FFmpeg is not installed or not in PATH.\nPlease install FFmpeg first.")
            sys.exit(1)

        self.setup_ui()

    def check_ffmpeg(self):
        """Check if ffmpeg is available in system PATH"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Input file selection
        ttk.Label(main_frame, text="Input MTS File:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)

        ttk.Entry(input_frame, textvariable=self.input_file, state="readonly").grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_input_file).grid(
            row=0, column=1)

        # Output file selection
        ttk.Label(main_frame, text="Output MP4 File:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))

        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)

        ttk.Entry(output_frame, textvariable=self.output_file).grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_file).grid(
            row=0, column=1)

        # Quality settings frame
        quality_frame = ttk.LabelFrame(main_frame, text="Quality Settings", padding="5")
        quality_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        quality_frame.columnconfigure(1, weight=1)

        ttk.Label(quality_frame, text="Quality (CRF):").grid(row=0, column=0, sticky=tk.W)
        self.crf_var = tk.StringVar(value="18")
        crf_spinbox = ttk.Spinbox(quality_frame, from_=0, to=51, textvariable=self.crf_var, width=10)
        crf_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))

        ttk.Label(quality_frame, text="(Lower = Better Quality, Higher = Smaller File)").grid(
            row=0, column=2, sticky=tk.W, padx=(10, 0))

        # Preset settings
        ttk.Label(quality_frame, text="Encoding Speed:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.preset_var = tk.StringVar(value="medium")
        preset_combo = ttk.Combobox(quality_frame, textvariable=self.preset_var, 
                                   values=["veryslow", "slower", "slow", "medium", "fast", "faster", "veryfast"],
                                   state="readonly", width=15)
        preset_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))

        # Copy streams option (for lossless conversion)
        self.copy_streams = tk.BooleanVar(value=False)
        ttk.Checkbutton(quality_frame, text="Copy streams (lossless, fastest)", 
                       variable=self.copy_streams, command=self.toggle_copy_mode).grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Conversion Progress", padding="5")
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        self.status_label = ttk.Label(progress_frame, text="Ready to convert")
        self.status_label.grid(row=1, column=0, sticky=tk.W)

        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Conversion Log", padding="5")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)

        # Text widget with scrollbar
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_text_frame.columnconfigure(0, weight=1)
        log_text_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_text_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        log_scrollbar = ttk.Scrollbar(log_text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))

        self.convert_button = ttk.Button(button_frame, text="Start Conversion", 
                                        command=self.start_conversion, style="Accent.TButton")
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))

        self.cancel_button = ttk.Button(button_frame, text="Cancel", 
                                       command=self.cancel_conversion, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT)

    def browse_input_file(self):
        """Browse for input MTS file"""
        filename = filedialog.askopenfilename(
            title="Select MTS file",
            filetypes=[
                ("MTS files", "*.mts *.MTS"),
                ("AVCHD files", "*.m2ts *.M2TS"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.input_file.set(filename)
            # Auto-generate output filename
            input_path = Path(filename)
            output_path = input_path.with_suffix('.mp4')
            self.output_file.set(str(output_path))

    def browse_output_file(self):
        """Browse for output MP4 file location"""
        filename = filedialog.asksaveasfilename(
            title="Save MP4 file as",
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)

    def toggle_copy_mode(self):
        """Toggle between copy mode and re-encoding mode"""
        # This function can be extended to enable/disable quality options
        pass

    def log_message(self, message):
        """Add message to log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def update_progress(self, percentage):
        """Update progress bar"""
        self.progress_var.set(percentage)
        self.root.update_idletasks()

    def validate_inputs(self):
        """Validate input and output file paths"""
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input MTS file.")
            return False

        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Error", "Input file does not exist.")
            return False

        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output file.")
            return False

        # Check if output directory exists, create if not
        output_dir = os.path.dirname(self.output_file.get())
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                messagebox.showerror("Error", f"Cannot create output directory: {e}")
                return False

        return True

    def get_video_duration(self, input_file):
        """Get video duration using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', input_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            return None

    def parse_ffmpeg_output(self, line, total_duration):
        """Parse ffmpeg output to extract progress information"""
        # Look for time information in ffmpeg output
        time_match = re.search(r'time=([0-9:.]+)', line)
        if time_match and total_duration:
            time_str = time_match.group(1)
            try:
                # Parse time string (HH:MM:SS.microseconds)
                time_parts = time_str.split(':')
                if len(time_parts) == 3:
                    hours = float(time_parts[0])
                    minutes = float(time_parts[1])
                    seconds = float(time_parts[2])
                    current_time = hours * 3600 + minutes * 60 + seconds

                    progress = (current_time / total_duration) * 100
                    return min(progress, 100)  # Cap at 100%
            except (ValueError, IndexError):
                pass
        return None

    def run_conversion(self):
        """Run the actual conversion process"""
        input_path = self.input_file.get()
        output_path = self.output_file.get()

        try:
            # Get video duration for progress calculation
            self.log_message("Analyzing input file...")
            total_duration = self.get_video_duration(input_path)
            if total_duration:
                self.log_message(f"Video duration: {total_duration:.2f} seconds")
            else:
                self.log_message("Could not determine video duration - progress may not be accurate")

            # Build ffmpeg command
            if self.copy_streams.get():
                # Lossless copy mode
                cmd = [
                    'ffmpeg', '-i', input_path, '-c', 'copy', '-f', 'mp4',
                    '-movflags', '+faststart', '-y', output_path
                ]
                self.log_message("Using lossless copy mode...")
            else:
                # Re-encoding mode with quality settings
                cmd = [
                    'ffmpeg', '-i', input_path,
                    '-c:v', 'libx264', '-crf', self.crf_var.get(),
                    '-preset', self.preset_var.get(),
                    '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart',
                    '-y', output_path
                ]
                self.log_message(f"Using re-encoding mode with CRF {self.crf_var.get()} and {self.preset_var.get()} preset...")

            self.log_message(f"Command: {' '.join(cmd)}")
            self.log_message("Starting conversion...")

            # Start ffmpeg process
            self.ffmpeg_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, universal_newlines=True, bufsize=1
            )

            # Process output line by line
            for line in iter(self.ffmpeg_process.stdout.readline, ''):
                if not self.conversion_running:
                    break

                line = line.strip()
                if line:
                    # Update progress if possible
                    if total_duration:
                        progress = self.parse_ffmpeg_output(line, total_duration)
                        if progress is not None:
                            self.update_progress(progress)
                            self.status_label.config(text=f"Converting... {progress:.1f}%")

                    # Log important information
                    if any(keyword in line.lower() for keyword in ['error', 'warning', 'frame=', 'time=']):
                        self.log_message(line)

            # Wait for process to complete
            self.ffmpeg_process.wait()

            if self.conversion_running:  # Not cancelled
                if self.ffmpeg_process.returncode == 0:
                    self.update_progress(100)
                    self.status_label.config(text="Conversion completed successfully!")
                    self.log_message("Conversion completed successfully!")

                    # Show file info
                    if os.path.exists(output_path):
                        file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                        self.log_message(f"Output file size: {file_size:.2f} MB")

                    messagebox.showinfo("Success", f"Conversion completed successfully!\nOutput saved to: {output_path}")
                else:
                    self.status_label.config(text="Conversion failed!")
                    self.log_message(f"Conversion failed with return code: {self.ffmpeg_process.returncode}")
                    messagebox.showerror("Error", "Conversion failed! Check the log for details.")

        except Exception as e:
            self.log_message(f"Error during conversion: {str(e)}")
            self.status_label.config(text="Conversion failed!")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")

        finally:
            # Reset UI state
            self.conversion_running = False
            self.convert_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            if self.ffmpeg_process:
                self.ffmpeg_process = None

    def start_conversion(self):
        """Start the conversion process"""
        if not self.validate_inputs():
            return

        if self.conversion_running:
            messagebox.showwarning("Warning", "Conversion is already running!")
            return

        # Check if output file already exists
        if os.path.exists(self.output_file.get()):
            if not messagebox.askyesno("File Exists", 
                                     "Output file already exists. Do you want to overwrite it?"):
                return

        # Update UI state
        self.conversion_running = True
        self.convert_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_label.config(text="Starting conversion...")

        # Clear log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

        # Start conversion in separate thread
        conversion_thread = threading.Thread(target=self.run_conversion, daemon=True)
        conversion_thread.start()

    def cancel_conversion(self):
        """Cancel the running conversion"""
        if self.conversion_running and self.ffmpeg_process:
            if messagebox.askyesno("Cancel Conversion", "Are you sure you want to cancel the conversion?"):
                self.conversion_running = False
                self.ffmpeg_process.terminate()

                # Wait a bit for graceful termination
                try:
                    self.ffmpeg_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.ffmpeg_process.kill()

                self.status_label.config(text="Conversion cancelled")
                self.log_message("Conversion cancelled by user")

                # Reset UI state
                self.convert_button.config(state=tk.NORMAL)
                self.cancel_button.config(state=tk.DISABLED)

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main function to run the application"""
    try:
        app = MTStoMP4Converter()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
