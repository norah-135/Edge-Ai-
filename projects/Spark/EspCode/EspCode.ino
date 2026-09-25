#include <Spark_inferencing.h>
#include <driver/i2s.h>

// منافذ ESP32 NodeMCU
#define I2S_SCK 33
#define I2S_WS  25
#define I2S_SD  32
#define I2S_PORT I2S_NUM_0

// مصفوفة استقبال الصوت للنموذج
static int16_t sample_buffer[EI_CLASSIFIER_RAW_SAMPLE_COUNT];

// دالة تحويل إشارة الصوت إلى النموذج
static int microphone_audio_signal_get_data(size_t offset, size_t length, float *out_ptr) {
    for (size_t i = 0; i < length; i++) {
        out_ptr[i] = (float)sample_buffer[offset + i];
    }
    return 0;
}

void setup() {
    // رفع سرعة الباود ريت
    Serial.begin(921600);
    delay(1000); // مهلة زمنية لتثبيت السيريال ومنع تشوه البداية

    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    // إعداد I2S للمايك
    const i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 16000,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 512,
        .use_apll = false
    };

    const i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_SCK,
        .ws_io_num = I2S_WS,
        .data_out_num = -1,
        .data_in_num = I2S_SD
    };

    i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_PORT, &pin_config);

    Serial.println("\n--- Spark Detector Started Successfully (921600 baud) ---");
}

void loop() {
    size_t bytes_read = 0;
    int32_t raw_sample = 0;

    // تجميع عينات الصوت
    for (int i = 0; i < EI_CLASSIFIER_RAW_SAMPLE_COUNT; i++) {
        i2s_read(I2S_PORT, &raw_sample, sizeof(raw_sample), &bytes_read, portMAX_DELAY);
        sample_buffer[i] = (int16_t)(raw_sample >> 14);
    }

    // تغليف الإشارة للنموذج
    signal_t signal;
    signal.total_length = EI_CLASSIFIER_RAW_SAMPLE_COUNT;
    signal.get_data = &microphone_audio_signal_get_data;

    // استنتاج النموذج
    ei_impulse_result_t result = { 0 };
    EI_IMPULSE_ERROR r = run_classifier(&signal, &result, false);
    if (r != EI_IMPULSE_OK) {
        Serial.printf("Classifier Error: %d\n", r);
        return;
    }

    // استخراج النتائج
    float spark_val = 0.0;
    float noise_val = 0.0;

    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        if (strcmp(result.classification[ix].label, "spark") == 0) {
            spark_val = result.classification[ix].value;
        } else if (strcmp(result.classification[ix].label, "noise") == 0) {
            noise_val = result.classification[ix].value;
        }
    }

    // طباعة نظيفة للنتائج بدون أي رموز غريبة
    Serial.printf("Predictions -> Noise: %.2f%% | Spark: %.2f%%", noise_val * 100.0, spark_val * 100.0);

    // إنذار في حال رصد الشرارة
    if (spark_val >= 0.80) {
        Serial.print("  ===> [FIRE ALERT: SPARK DETECTED!]");
        digitalWrite(LED_BUILTIN, HIGH);
        delay(150);
        digitalWrite(LED_BUILTIN, LOW);
    }
    Serial.println();
}