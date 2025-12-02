IMU_DEVICE = {
    "SERVICE_UUID": "0b91a798-23b1-4369-9d45-a3a26d936904",
    "TIME_UUID": "72d913bb-e8df-44b8-b8ec-4f098978e0be",
    "ACCEL_X_UUID": "026080c9-dc3a-401b-829c-2ee3b5565200",
    "ACCEL_Y_UUID": "e0a0b53e-5c53-4acf-bf79-39d2982362e9",
    "ACCEL_Z_UUID": "94b54966-faa7-48c1-9b53-7e44a9a872be",
    "GYRO_X_UUID":  "d30c8099-5b3e-4d4f-9c42-40b47a3f71ea",
    "GYRO_Y_UUID":  "734c0d37-c4fc-4265-953f-0aa24d28b1a5",
    "GYRO_Z_UUID":  "e51f3e60-3fdd-4591-9910-87362247c68d",
}

# Example future device support:
ALT_IMU_DEVICE = {
    "SERVICE_UUID": "...",
    "TIME_UUID": "...",
}

AVAILABLE_DEVICES = {
    "Standard IMU": IMU_DEVICE,
    "Alternative IMU": ALT_IMU_DEVICE,
}
