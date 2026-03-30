#include <WiFi.h>
#include <ESPAsyncWebServer.h>

const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

AsyncWebServer server(80);

const int buzzer1Pin = 5;
const int buzzer2Pin = 19;
const int buttons[] = {15, 16, 17, 18};
const int trigPin = 23;
const int echoPin = 22;

long duration;
int distanceCm;
bool alarmActive = false;
bool isDrowsiness = true;
bool buttonsState[4] = {false, false, false, false};

void triggerAlarm() {
  alarmActive = true;
  digitalWrite(buzzer1Pin, HIGH);
  digitalWrite(buzzer2Pin, HIGH);
  for(int i = 0; i < 4; i++) buttonsState[i] = false;
}

void stopAlarm(){
  alarmActive = false;
  digitalWrite(buzzer1Pin, LOW);
  digitalWrite(buzzer2Pin, LOW);
  Serial.println("Alarm stopped");
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");
  Serial.println(WiFi.localIP());

  pinMode(buzzer1Pin, OUTPUT);
  pinMode(buzzer2Pin, OUTPUT);
  for(int i = 0; i < 4; i++) pinMode(buttons[i], INPUT_PULLUP);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  digitalWrite(buzzer1Pin, LOW);
  digitalWrite(buzzer2Pin, LOW);

  server.on("/trigger", HTTP_GET, [](AsyncWebServerRequest *request){
    triggerAlarm();
    request->send(200, "text/plain", "Alarm triggered");
  });

  server.begin();
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);

  distanceCm = duration * 0.034 / 2;
  if(distanceCm < 200 && distanceCm > 0){
    if(!alarmActive) triggerAlarm();
    isDrowsiness = false;
  }

  if(alarmActive && isDrowsiness){
    bool allPressed = true;
    for(int i = 0; i < 4; i++){
      if(digitalRead(buttons[i])== LOW){
        buttonsState[i] = true;
      }

      if(buttonsState[i] == false){
        allPressed = false;
      }
    }

    if(alarmActive){
      stopAlarm();
    }
  }

  delay(100);
}
