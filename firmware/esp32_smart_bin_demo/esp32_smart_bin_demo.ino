/*
  ESP32 Smart Bin

  Reads bin fill level with an HC-SR04 ultrasonic sensor and sends it to the
  FastAPI backend:
  POST http://YOUR_SERVER_IP:8000/iot/bin-reading

  Before uploading, set:
    - WIFI_SSID / WIFI_PASSWORD
    - SERVER_URL (use the server's LAN IP, not "localhost")
    - API_KEY    (must match IOT_API_KEY on the server; leave "" if the
                  server has no key configured)
    - BIN_HEIGHT_CM and SENSOR_OFFSET_CM (calibrate to your bin)

  Wiring (HC-SR04):
    VCC  -> 5V (VIN)
    GND  -> GND
    TRIG -> GPIO 5
    ECHO -> GPIO 18  (use a voltage divider: ECHO is 5V, ESP32 is 3.3V)
*/

#include <WiFi.h>
#include <HTTPClient.h>

// ---- Configuration -------------------------------------------------------
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL = "http://192.168.1.100:8000/iot/bin-reading";
const char* API_KEY = "";  // must match server IOT_API_KEY; "" = no key

const char* BIN_ID = "TPS-001";
const char* DEVICE_ID = "ESP32-001";

// HC-SR04 pins
const int TRIG_PIN = 5;
const int ECHO_PIN = 18;

// Bin geometry for converting distance -> fill percentage.
// BIN_HEIGHT_CM  : inside height of the bin (sensor face to bin bottom).
// SENSOR_OFFSET_CM: dead zone right under the sensor that counts as 100% full.
const float BIN_HEIGHT_CM = 100.0;
const float SENSOR_OFFSET_CM = 4.0;

// Timing
const unsigned long SEND_INTERVAL_MS = 30000;  // 30 seconds
const unsigned long ECHO_TIMEOUT_US = 30000;   // ~5 m max range

// Offline buffer: store readings when the network is unavailable and flush
// them once the connection is back, so data is not lost.
const int BUFFER_CAPACITY = 60;
float fillBuffer[BUFFER_CAPACITY];
int bufferCount = 0;

unsigned long lastSendAt = 0;

// ---- WiFi ----------------------------------------------------------------
bool connectToWiFi(unsigned long timeoutMs = 15000) {
  if (WiFi.status() == WL_CONNECTED) {
    return true;
  }

  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < timeoutMs) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Connected. ESP32 IP: ");
    Serial.println(WiFi.localIP());
    return true;
  }

  Serial.println("WiFi connection failed; will retry later.");
  return false;
}

// ---- Sensor --------------------------------------------------------------
// Single ultrasonic distance measurement in centimeters. Returns -1 on timeout.
float measureDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long duration = pulseIn(ECHO_PIN, HIGH, ECHO_TIMEOUT_US);
  if (duration == 0) {
    return -1.0;  // no echo within timeout
  }

  // Speed of sound ~340 m/s -> distance = duration / 58 (round trip).
  return duration / 58.0;
}

// Median of several samples to reject spikes. Returns -1 if all reads fail.
float readDistanceStable(int samples = 5) {
  float values[samples];
  int valid = 0;

  for (int i = 0; i < samples; i++) {
    float d = measureDistanceCm();
    if (d > 0) {
      values[valid++] = d;
    }
    delay(40);
  }

  if (valid == 0) {
    return -1.0;
  }

  // Simple insertion sort, then take the middle value.
  for (int i = 1; i < valid; i++) {
    float key = values[i];
    int j = i - 1;
    while (j >= 0 && values[j] > key) {
      values[j + 1] = values[j];
      j--;
    }
    values[j + 1] = key;
  }
  return values[valid / 2];
}

// Convert a measured distance into a 0-100 fill percentage.
float distanceToFillLevel(float distanceCm) {
  // Distance large  -> bin empty  -> low fill.
  // Distance small  -> bin full   -> high fill.
  float usableHeight = BIN_HEIGHT_CM - SENSOR_OFFSET_CM;
  if (usableHeight <= 0) {
    return 0.0;
  }

  float fill = (BIN_HEIGHT_CM - distanceCm) / usableHeight * 100.0;
  if (fill < 0.0) fill = 0.0;
  if (fill > 100.0) fill = 100.0;
  return fill;
}

// Returns fill level (0-100), or -1 if the sensor could not be read.
float readFillLevel() {
  float distance = readDistanceStable();
  if (distance < 0) {
    Serial.println("Sensor read failed (no echo).");
    return -1.0;
  }
  float fill = distanceToFillLevel(distance);
  Serial.print("Distance: ");
  Serial.print(distance, 1);
  Serial.print(" cm -> fill: ");
  Serial.print(fill, 1);
  Serial.println(" %");
  return fill;
}

// ---- Networking ----------------------------------------------------------
// Try to POST one reading. Returns true on HTTP 2xx.
bool postReading(float fillLevel) {
  if (!connectToWiFi()) {
    return false;
  }

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");
  if (strlen(API_KEY) > 0) {
    http.addHeader("X-API-Key", API_KEY);
  }

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

  bool ok = responseCode >= 200 && responseCode < 300;
  if (responseCode > 0) {
    Serial.println(http.getString());
  } else {
    Serial.print("HTTP error: ");
    Serial.println(http.errorToString(responseCode));
  }

  http.end();
  return ok;
}

// Store a reading for later when sending fails (drops oldest if full).
void bufferReading(float fillLevel) {
  if (bufferCount < BUFFER_CAPACITY) {
    fillBuffer[bufferCount++] = fillLevel;
  } else {
    // Buffer full: drop the oldest, keep the most recent readings.
    for (int i = 1; i < BUFFER_CAPACITY; i++) {
      fillBuffer[i - 1] = fillBuffer[i];
    }
    fillBuffer[BUFFER_CAPACITY - 1] = fillLevel;
  }
  Serial.print("Buffered reading. Pending: ");
  Serial.println(bufferCount);
}

// Try to resend everything we have buffered. Stops on the first failure so
// readings are not lost or reordered.
void flushBuffer() {
  while (bufferCount > 0) {
    if (postReading(fillBuffer[0])) {
      for (int i = 1; i < bufferCount; i++) {
        fillBuffer[i - 1] = fillBuffer[i];
      }
      bufferCount--;
    } else {
      Serial.println("Flush paused; will retry next cycle.");
      return;
    }
  }
}

// ---- Arduino lifecycle ---------------------------------------------------
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  digitalWrite(TRIG_PIN, LOW);

  connectToWiFi();
}

void loop() {
  unsigned long now = millis();
  if (now - lastSendAt >= SEND_INTERVAL_MS || lastSendAt == 0) {
    lastSendAt = now;

    // Resend anything left from earlier failures first.
    flushBuffer();

    float fillLevel = readFillLevel();
    if (fillLevel < 0) {
      return;  // skip this cycle on sensor failure
    }

    if (!postReading(fillLevel)) {
      bufferReading(fillLevel);
    }
  }
}
