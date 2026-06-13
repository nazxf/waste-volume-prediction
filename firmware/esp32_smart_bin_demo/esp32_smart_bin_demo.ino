/*
  ESP32 Smart Bin Demo

  Sends simulated bin fill-level readings to the FastAPI backend:
  POST http://YOUR_SERVER_IP:8000/iot/bin-reading

  Replace WIFI_SSID, WIFI_PASSWORD, and SERVER_URL before uploading.
*/

#include <WiFi.h>
#include <HTTPClient.h>

const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL = "http://192.168.1.100:8000/iot/bin-reading";

const char* BIN_ID = "TPS-001";
const char* DEVICE_ID = "ESP32-001";

const unsigned long SEND_INTERVAL_MS = 30000;
unsigned long lastSendAt = 0;
float simulatedFillLevel = 35.0;

void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Connected. ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

float readFillLevel() {
  // Replace this simulated value with ultrasonic or weight sensor logic later.
  simulatedFillLevel += 7.5;
  if (simulatedFillLevel > 100.0) {
    simulatedFillLevel = 10.0;
  }
  return simulatedFillLevel;
}

void sendReading(float fillLevel) {
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  String payload = "{";
  payload += "\"bin_id\":\"" + String(BIN_ID) + "\",";
  payload += "\"fill_level\":" + String(fillLevel, 1) + ",";
  payload += "\"device_id\":\"" + String(DEVICE_ID) + "\"";
  payload += "}";

  int responseCode = http.POST(payload);
  Serial.print("POST ");
  Serial.print(SERVER_URL);
  Serial.print(" -> ");
  Serial.println(responseCode);

  if (responseCode > 0) {
    Serial.println(http.getString());
  } else {
    Serial.print("HTTP error: ");
    Serial.println(http.errorToString(responseCode));
  }

  http.end();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  connectToWiFi();
}

void loop() {
  unsigned long now = millis();
  if (now - lastSendAt >= SEND_INTERVAL_MS || lastSendAt == 0) {
    lastSendAt = now;
    float fillLevel = readFillLevel();
    sendReading(fillLevel);
  }
}
