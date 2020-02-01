#include "esphome.h"

using namespace esphome;

static const char *TAG = "filter.stddev";

class SlidingWindowStdDevFilter {
  protected:
    std::vector<float> *window_;
    size_t window_size_;
  public:
    SlidingWindowStdDevFilter(size_t window_size)  {
      this->window_size_ = window_size;
      this->window_ = new std::vector<float>();
      this->window_->reserve(window_size);
    }
    
    optional<float> new_value(float value) {
      if(this->window_->size() == this->window_size_) {
        float sd = this->compute_stddev(this->window_);
        ESP_LOGI(TAG, "SlidingWindowStdDevFilter(%p)::new_value(%f) -> stddev=%f", this, value, sd);
        this->window_->clear();
        return sd;
      }
      this->window_->push_back(value);
      return {};
    }

    float compute_stddev(std::vector<float> *window) {
      float sum = 0;
      
      for(int i=0; i<window->size();i++) {
        sum += (*window)[i];
      }

      float mean = sum/window->size();
      sum = 0;
      for(int i=0; i<window->size();i++) {
        sum += ((*window)[i]-mean) * ((*window)[i]-mean);
      }
      return sqrtf(sum/(window->size()-1));
    }
};