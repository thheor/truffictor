![Truffictor](./public/banner.png)

Truffictor is a research product that qualified as a finalist in the Indonesian Student Research Olympiad competition. Truffictor aims to optimize truck driver safety with AI vision. This product is built using OpenCV, mediapipe, and ESP32 DevKit.

## Installation

### Prerequisites

- Python 3.7 - 3.12 (Latest version of Pyhton (3.13) is not officially supported by the standard MediaPipe package via PyPi)
- ESP32, Arduino, Rasberry Pi, or other microcontroller
- Webcam
- Buzzer: 5V
- LED lamp
- Push button
- Bread board
- Jumper cable

### Step 1: Set Up Environment

1. Clone the Repository

```bash
git clone https://github.com/thheor/truffictor.git
cd truffictor
```

1. Set Up Environment (Optional)

```bash
python3 -m venv venv
source venv/bin/activate # On Linux or MacOs
venv\Scripts\activate # On Windows
```

1. Install Dependencies

```bash
pip install -r requirements.txt
```

_Note: If you are on Linux, you need to install **python3-tk** via your package manager_

### Step 2: Set Up Circuit and Diagram

Pair ESP32 to bread board then connect buzzer1's pin to 5, buzzer2's pin to 18, and button's pin to 15. Every negative pin of every buzzer must be connected to GND. Your final circuit should look like this

**IMAGE**

### Step 3: Set Up ESP32 Code

You can use any code editor, but I recommend using [Arduino IDE](https://www.arduino.cc/en/software/).

#### Quick Instructions

1. If this is the first time you are using ESP32, see [how to setup environment for ESP32 on Arduino IDE](https://esp32io.com/tutorials/esp32-software-installation)
2. Connect the ESP32 board to your PC via a micro USB cable
3. Open the code from **esp32kantuk.ino** on Arduino IDE on your PC
4. Select the right ESP32 board and COM port
5. Compile and upload code to ESP32 board by clicking **Upload** button on arrow right icon on top left corner
6. You will see the IP address of your ESP32 in Output section on Arduino IDE
7. Connect the WiFi from your smartphone to

   | SSID      | Password   |
   | --------- | ---------- |
   | **Truff** | Truff12345 |

## Run Code

Open terminal or command line in your PC and change the current directory to this project folder. Open with your favorite code editor (I use neovim btw). Run this command below.

```bash
python3 app.py
# or
python app.py
```

---

Thank you for visiting -- Please leave a star ⭐ if you like!
