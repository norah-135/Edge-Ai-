#include <Wire.h>
#include <Adafruit_MLX90614.h>

Adafruit_MLX90614 mlx = Adafruit_MLX90614();

// تحديد أرجل I2C الخاصة بـ ESP32-S3
#define I2C_SDA 8
#define I2C_SCL 9

void setup() {
  Serial.begin(115200);
  while (!Serial); // انتظار فتح شاشة السيريال
  delay(1000);

  Serial.println("\n--- بدء تهيئة حساس MLX90614 لمشروع نبيه ---");

  // تهيئة مسار I2C
  Wire.begin(I2C_SDA, I2C_SCL);

  if (!mlx.begin()) {
    Serial.println("❌ فشل الاتصال بحساس MLX90614. تحققي من التوصيلات (SDA/SCL) والتغذية.");
    while (1);
  }

  Serial.println("✅ تم الاتصال بحساس MLX90614 بنجاح!");
  Serial.println("--------------------------------------------------");
}

void loop() {
  float ambientTemp = mlx.readAmbientTempC();
  float objectTemp = mlx.readObjectTempC();
  float deltaTemp = objectTemp - ambientTemp;

  Serial.printf("المحيط: %.2f °C | الهدف: %.2f °C | الفارق الحراري: %.2f °C", 
                ambientTemp, objectTemp, deltaTemp);

  // تمييز مبدئي لوجود كائن باعث للحرارة عن بعد
  if (deltaTemp > 3.0) {
    Serial.println("  --> 🔴 رصد كائن حراري مرتفع!");
  } else {
    Serial.println("  --> 🟢 طبيعي");
  }
  Serial.printf("%.2f,%.2f,%.2f\n", ambientTemp, objectTemp, deltaTemp);

  delay(250);
}