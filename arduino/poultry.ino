#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

#define WIFI_SSID "Act"         // Replace with your WiFi SSID
#define WIFI_PASSWORD "Madhumakeskilled" // Replace with your WiFi Password
#define THINGSPEAK_API_KEY "0YLE00JTFZ2IAZZF"  // Replace with your ThingSpeak API Key

#define DHTPIN 5         // DHT11 connected to GPIO 5
#define DHTTYPE DHT11    
#define GAS_SENSOR_PIN 34  // Gas sensor (Analog input)
#define FAN_PIN 15       // Fan Relay pin

DHT dht(DHTPIN, DHTTYPE);

const float TEMP_THRESHOLD = 30.0;  // Temperature threshold (°C)
const int GAS_THRESHOLD = 300;      // Gas level threshold

void setup() {
    Serial.begin(115200);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi!");

    dht.begin();
    
    pinMode(FAN_PIN, OUTPUT);
    digitalWrite(FAN_PIN, HIGH);
}

void loop() {
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    int gasValue = analogRead(GAS_SENSOR_PIN);

    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print("°C  | Humidity: ");
    Serial.print(humidity);
    Serial.print("%  | Gas Level: ");
    Serial.println(gasValue);
    

    // Fan Control Based on Temperature
    if (temperature > TEMP_THRESHOLD) {
        Serial.println("High Temperature! Turning ON Fan.");
        digitalWrite(FAN_PIN, LOW);
    } else {
        Serial.println("Temperature Normal. Turning OFF Fan.");
        digitalWrite(FAN_PIN, HIGH);
    }

    // Send Data to ThingSpeak
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        String url = "http://api.thingspeak.com/update?api_key=" + String(THINGSPEAK_API_KEY) +
                     "&field1=" + String(temperature) + 
                     "&field2=" + String(humidity) + 
                     "&field3=" + String(gasValue);
        
        Serial.println("Sending Data to ThingSpeak...");
        http.begin(url);
        int httpResponseCode = http.GET();
        
        if (httpResponseCode > 0) {
            Serial.println("Data Sent Successfully!");
        } else {
            Serial.print("Error Sending Data: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    } else {
        Serial.println("WiFi Not Connected!");
    }

    delay(15000);  // Update every 15 seconds
}
