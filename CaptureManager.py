import os

class CaptureManager:
    """
    Handles loading of Wi-Fi capture data from text files or logs.
    Used to read TShark or tcpdump output containing SSID information.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_capture(self):
        """
        Reads the capture log file and returns its contents as a list of lines.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"[CaptureManager] Capture file not found: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as file:
            data = file.readlines()

        print(f"[CaptureManager] Loaded {len(data)} lines from capture file.")
        return data