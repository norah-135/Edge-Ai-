#include <Spark_inferencing.h>
#include <driver/i2s.h>

#define I2S_SCK 33
#define I2S_WS  25
#define I2S_SD  32
#define I2S_PORT I2S_NUM_0

static int16_t inference_buffer[EI_CLASSIFIER_RAW_SAMPLE_COUNT];

static int get_audio_signal_data(size_t offset, size_t length, float *out_ptr) {
    for (size_t i = 0; i < length; i++) {
        out_ptr[i] = (float)inference_buffer[offset + i];
    }
    return 0;
}

void setup() {
    Serial.begin(921600);
    delay(500);

    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

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

    Serial.println("\n--- Raw Classes Diagnostic Mode ---");
}

void loop() {
    size_t bytes_read = 0;
    int32_t dma_chunk[256];
    int collected = 0;

    while (collected < EI_CLASSIFIER_RAW_SAMPLE_COUNT) {
        int chunk_size = min(256, (int)(EI_CLASSIFIER_RAW_SAMPLE_COUNT - collected));
        i2s_read(I2S_PORT, dma_chunk, chunk_size * sizeof(int32_t), &bytes_read, portMAX_DELAY);
        
        int samples_read = bytes_read / sizeof(int32_t);
        for (int i = 0; i < samples_read; i++) {
            int32_t val = dma_chunk[i] >> 14;
            if (val > 32767) val = 32767;
            if (val < -32768) val = -32768;
            inference_buffer[collected + i] = (int16_t)val;
        }
        collected += samples_read;
    }

    signal_t signal;
    signal.total_length = EI_CLASSIFIER_RAW_SAMPLE_COUNT;
    signal.get_data = &get_audio_signal_data;

    ei_impulse_result_t result = { 0 };
    EI_IMPULSE_ERROR r = run_classifier(&signal, &result, false);
    if (r != EI_IMPULSE_OK) return;

    // طباعة كل مخرجات النموذج الفعلية
    Serial.print("Model Output -> ");
    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        Serial.printf("[%s: %.1f%%] ", result.classification[ix].label, result.classification[ix].value * 100.0);
    }
    Serial.println();
}