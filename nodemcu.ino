#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// -------------------- CONFIG --------------------
const char* ssid = "BSNL3G";
const char* password = "Asdf1234..";

// Django update endpoint
const char* serverUrl = "http://192.168.115.253:8000/api/slot/update/";

// Parking slot codes for each sensor
const char* slotCode1 = "A1";
const char* slotCode2 = "A2";
const char* slotCode3 = "A3";

// Set to true if your IR sensor is active LOW
const bool SENSOR_ACTIVE_LOW = true;

// Sensor pins
const int sensorPin1 = D1;
const int sensorPin2 = D2;
const int sensorPin3 = D5;

// Debounce variables
bool stableState1 = false;
bool stableState2 = false;
bool stableState3 = false;
unsigned long lastChange1 = 0;
unsigned long lastChange2 = 0;
unsigned long lastChange3 = 0;
const unsigned long debounceDelay = 500;

// -------------------- WIFI RECONNECT --------------------
void ensureWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.println("Reconnecting WiFi...");
  WiFi.disconnect();
  WiFi.begin(ssid, password);

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 40) {
    delay(250);
    Serial.print(".");
    tries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Connected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi reconnect FAILED");
  }
}

// -------------------- SETUP --------------------
void setup() {
  Serial.begin(115200);
  pinMode(sensorPin1, INPUT);
  pinMode(sensorPin2, INPUT);
  pinMode(sensorPin3, INPUT);

  WiFi.begin(ssid, password);
  ensureWiFi();
}

// -------------------- LOOP --------------------
void loop() {
  ensureWiFi();

  // Read the sensor states
  bool raw1 = digitalRead(sensorPin1);
  bool raw2 = digitalRead(sensorPin2);
  bool raw3 = digitalRead(sensorPin3);

  bool occupied1 = SENSOR_ACTIVE_LOW ? (raw1 == LOW) : (raw1 == HIGH);
  bool occupied2 = SENSOR_ACTIVE_LOW ? (raw2 == LOW) : (raw2 == HIGH);
  bool occupied3 = SENSOR_ACTIVE_LOW ? (raw3 == LOW) : (raw3 == HIGH);

  bool isAvailable1 = !occupied1;
  bool isAvailable2 = !occupied2;
  bool isAvailable3 = !occupied3;

  unsigned long now = millis();

  // Handle debouncing for each sensor
  if (occupied1 != stableState1 && (now - lastChange1 > debounceDelay)) {
    stableState1 = occupied1;
    lastChange1 = now;
    sendUpdate(slotCode1, isAvailable1);
  }

  if (occupied2 != stableState2 && (now - lastChange2 > debounceDelay)) {
    stableState2 = occupied2;
    lastChange2 = now;
    sendUpdate(slotCode2, isAvailable2);
  }

  if (occupied3 != stableState3 && (now - lastChange3 > debounceDelay)) {
    stableState3 = occupied3;
    lastChange3 = now;
    sendUpdate(slotCode3, isAvailable3);
  }

  delay(100);  // Small delay to reduce load
}

// -------------------- SEND UPDATE --------------------
void sendUpdate(const char* slotCode, bool isAvailable) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClient client;

    if (!http.begin(client, serverUrl)) {
      Serial.println("HTTP begin FAIL");
      return;
    }

    http.addHeader("Content-Type", "application/json");

    String json = "{\"slot_code\":\"";
    json += slotCode;
    json += "\",\"is_available\":";
    json += (isAvailable ? "true" : "false");
    json += "}";

    Serial.print("POST -> ");
    Serial.println(json);

    int code = http.POST(json);
    if (code > 0) {
      Serial.printf("Response code: %d\n", code);
      Serial.println(http.getString());
    } else {
      Serial.printf("POST error: %s\n", http.errorToString(code).c_str());
    }

    http.end();
  }
}
