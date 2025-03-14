#include <WiFi.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <ESP32Servo.h>

// WiFi credentials
const char* ssid = "Act";
const char* password = "Madhumakeskilled";

// NTP Client setup
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000);

// Ultrasonic sensor pins
#define TRIG_FOOD 5
#define ECHO_FOOD 18
#define TRIG_WATER 19
#define ECHO_WATER 21

// Servo and relay pins
#define SERVO_PIN 15
#define RELAY_PIN 22

Servo feederServo;

// Feeding schedule
const int feedHour = 8; // 8 AM
const int waterHour = 12; // 12 PM
const int waterMinute = 0;

void setup() {
    Serial.begin(115200);
    
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");
    
    timeClient.begin();
    
    pinMode(TRIG_FOOD, OUTPUT);
    pinMode(ECHO_FOOD, INPUT);
    pinMode(TRIG_WATER, OUTPUT);
    pinMode(ECHO_WATER, INPUT);
    
    pinMode(RELAY_PIN, OUTPUT);
    feederServo.attach(SERVO_PIN);
}

float getDistance(int trigPin, int echoPin) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    long duration = pulseIn(echoPin, HIGH);
    return duration * 0.034 / 2;
}

void dispenseFood() {
    Serial.println("Dispensing Food");
    feederServo.write(90);
    delay(1000);
    feederServo.write(0);
}

void activateWater() {
    Serial.println("Activating Water Relay");
    digitalWrite(RELAY_PIN, LOW);
    delay(3000);
    digitalWrite(RELAY_PIN, HIGH);
}

void loop() {
    timeClient.update();
    int currentHour = timeClient.getHours();
    int currentMinute = timeClient.getMinutes();

    float foodDistance = getDistance(TRIG_FOOD, ECHO_FOOD);
    float waterDistance = getDistance(TRIG_WATER, ECHO_WATER);

    Serial.print("Food Bowl Distance: "); Serial.println(foodDistance);
    Serial.print("Water Bowl Distance: "); Serial.println(waterDistance);

    if (foodDistance > 10) { // If bowl is empty
        dispenseFood();
    }

    if (waterDistance > 10) { // If water is low
        activateWater();
    }

    if (currentHour == feedHour && currentMinute == 0) { // Scheduled feeding time
        dispenseFood();
    }

    if (currentHour == waterHour && currentMinute == waterMinute) { // Scheduled water activation
        activateWater();
    }
    
    delay(10000); // Check every 10 seconds
}
