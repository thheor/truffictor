#include <WiFi.h>
#include <ESPAsyncWebServer.h>

const char* ssid = "Truff";
const char* password = "Truff12345";

AsyncWebServer server(80);

const int buzzer1Pin = 5;
const int buzzer2Pin = 18;
const int buttonPin = 15;

volatile bool buzzer2Active = false;

void IRAM_ATTR handleButtonPress() {
  if (buzzer2Active) {
    digitalWrite(buzzer2Pin, LOW);
    buzzer2Active = false;
  }
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
  pinMode(buttonPin, INPUT_PULLUP);
  digitalWrite(buzzer1Pin, LOW);
  digitalWrite(buzzer2Pin, LOW);

  attachInterrupt(digitalPinToInterrupt(buttonPin), handleButtonPress, FALLING);

  server.on("/buzzer1", HTTP_GET, [](AsyncWebServerRequest *request){
    digitalWrite(buzzer1Pin, HIGH);
    delay(500);
    digitalWrite(buzzer1Pin, LOW);
    request->send(200, "text/plain", "Buzzer 1 aktif");
  });

  server.on("/buzzer2", HTTP_GET, [](AsyncWebServerRequest *request){
    digitalWrite(buzzer2Pin, HIGH);
    buzzer2Active = true; 
    delay(10000);
    if (buzzer2Active) {
      digitalWrite(buzzer2Pin, LOW);
      buzzer2Active = false;
    }
  });

  server.begin();
}

void loop() {
}
