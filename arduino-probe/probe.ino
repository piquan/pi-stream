const int tempSensorPin = A0;
//const int dialSensorPin = A4;
const int ledPin = 13;
const float aRef = 1.1;

void setup() {
    Serial.begin(9600);
    pinMode(ledPin, OUTPUT);
    analogReference(INTERNAL);
}

void loop() {
    static bool ledIsOn = false;

    int tempSensorRaw = analogRead(tempSensorPin);
    float tempSensorVolts = tempSensorRaw * aRef / 1023;
    Serial.print("{\"temp\":");
    Serial.print(tempSensorVolts, 6);
#if 0
    int dialSensorRaw = analogRead(dialSensorPin);
    float dialSensorVolts = dialSensorRaw * aRef / 1023;
    Serial.print(",\"dial\":");
    Serial.print(dialSensorVolts, 6);
#endif
    Serial.print("}\n");

    ledIsOn = !ledIsOn;
    digitalWrite(ledPin, ledIsOn);

    delay(100);
}
