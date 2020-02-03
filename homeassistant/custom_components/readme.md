# Installation instructions

Copy the whole `schmitt_trigger` folder into the `custom_components` folder under you Home Assistant configuration folder. 

## Usage

```
  # the schmitt trigger sensor configuration
  - platform: schmitt_trigger
    name: Washer Vibration Schmitt Band
    id: washingmac_vibration_schmitt
    entity_id: sensor.mpu6050_accel_x
    ranges: 
    # tweak these ranges based on vibration levels from your washer. 
    - name: idle
    - name: washing
      utp: 0.06
      ltp: 0.045
    - name: spinning
      utp: 0.11
      ltp: 0.09
```