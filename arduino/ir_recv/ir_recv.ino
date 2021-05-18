const int analogInPin = A3;
int sensorValue = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  sensorValue = analogRead(analogInPin);
  Serial.println(sensorValue);
  delay(10);
}
