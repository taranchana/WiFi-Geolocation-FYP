from AppController import AppController

if __name__ == "__main__":
    controller = AppController("data/wifi-ssid-captures.txt")
    controller.run()