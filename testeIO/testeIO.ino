const int numAnalog = 6;  // Número de portas analógicas
const int numDigital = 14; // Número de portas digitais
const int digitalPins[numDigital] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, A6, A7};

void setup() {
    Serial.begin(9600);
    for (int i = 0; i < numDigital; i++) {
        pinMode(digitalPins[i], INPUT_PULLUP);
    }
}

void loop() {
    if (Serial.available() > 0) {
        char command = Serial.read();
        if (command == 'R') {
            // Leitura das portas analógicas
            for (int i = 0; i < numAnalog; i++) {
                Serial.print(map(analogRead(i), 0, 1023, 0, 255));
                Serial.print(",");
            }

            // Leitura das portas digitais
            for (int i = 0; i < numDigital; i++) {
                Serial.print(digitalRead(digitalPins[i]) == HIGH ? 255 : 0);
                if (i < numDigital - 1) Serial.print(",");
            }

            Serial.println();
        }
    }
    delay(10);
}

