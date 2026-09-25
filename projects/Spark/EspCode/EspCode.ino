#include <driver/i2s.h>

// منافذ ESP32 NodeMCU القياسية
#define I2S_SCK 33
#define I2S_WS  25
#define I2S_SD  32
#define I2S_PORT I2S_NUM_0

#define BUFFER_SIZE 512
int32_t i2s_raw_buffer[BUFFER_SIZE];
int16_t audio_out_buffer[BUFFER_SIZE];

void setup() {
  // سرعة 921600 لمنع تساقط البايتات والتسريع
  Serial.begin(921600);

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
}

void loop() {
  size_t bytes_read = 0;
  
  // قراءة مصفوفة بيانات دفعة واحدة عبر DMA
  i2s_read(I2S_PORT, i2s_raw_buffer, sizeof(i2s_raw_buffer), &bytes_read, portMAX_DELAY);
  
  int samples_read = bytes_read / sizeof(int32_t);
  for (int i = 0; i < samples_read; i++) {
    // تحويل الدقة لـ 16-bit
    audio_out_buffer[i] = (int16_t)(i2s_raw_buffer[i] >> 14);
  }

  // إرسال البيانات مجمعة
  Serial.write((uint8_t*)audio_out_buffer, samples_read * sizeof(int16_t));
}