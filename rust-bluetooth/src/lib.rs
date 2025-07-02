// standard libraries
use std::io::{self, Write};
use std::convert::TryInto;
use tokio::time::{sleep, Duration};
use tokio::signal;

use bluest::{Adapter, Uuid, Device};
use futures_util::StreamExt; // maybe futures_lite instead? in examples/pair.rs

// IMU sensor UUIDs as strings
// NOTE: these services are formatted in a "hyphenated" way. This is important as bluest differentiates between formats
const SERVICE_UUID_STR: &str = "0b91a798-23b1-4369-9d45-a3a26d936904";
const SWITCH_CHARACTERISTIC_ACCEL_X_UUID_STR: &str = "026080c9-dc3a-401b-829c-2ee3b5565200";
const SWITCH_CHARACTERISTIC_ACCEL_Y_UUID_STR: &str = "e0a0b53e-5c53-4acf-bf79-39d2982362e9";
const SWITCH_CHARACTERISTIC_ACCEL_Z_UUID_STR: &str = "94b54966-faa7-48c1-9b53-7e44a9a872be";
// const SWITCH_CHARACTERISTIC_GYRO_X_UUID_STR: &str = "d30c8099-5b3e-4d4f-9c42-40b47a3f71ea";
// const SWITCH_CHARACTERISTIC_GYRO_Y_UUID_STR: &str = "734c0d37-c4fc-4265-953f-0aa24d28b1a5";
// const SWITCH_CHARACTERISTIC_GYRO_Z_UUID_STR: &str = "e51f3e60-3fdd-4591-9910-87362247c68d";
const SWITCH_CHARACTERISTIC_CURRENT_TIME_UUID_STR: &str = "72d913bb-e8df-44b8-b8ec-4f098978e0be";

// let switch_characteristic_accel_x_uuid = Uuid::parse_str(SWITCH_CHARACTERISTIC_ACCEL_X_UUID_STR);
// let switch_characteristic_accel_y_uuid = Uuid::parse_str(SWITCH_CHARACTERISTIC_ACCEL_Y_UUID_STR);
// let switch_characteristic_accel_z_uuid = Uuid::parse_str(SWITCH_CHARACTERISTIC_ACCEL_Z_UUID_STR);
// let switch_characteristic_gyro_x_uuid = Uuid::parse_str(SWITCH_CHARACTERISTIC_GYRO_X_UUID_STR);
// let switch_characteristic_gyro_y_uuid = Uuid::parse_str(SWITCH_CHARACTERISTIC_GYRO_Y_UUID_STR);
// let switch_characteristic_gyro_z_uuid = Uuid::parse_str(SWITCH_CHARACTERISTIC_GYRO_Z_UUID_STR);
// let switch_characteristic_current_time_uuid = Uuid::parse_str(SWITCH_CHARACTERISTIC_CURRENT_TIME_UUID_STR);

// read float32 device's characteristics
async fn read_ble_f32_characteristic(
    device: &Device,
    characteristic_uuid_str: &str,
) -> Result<f32, Box<dyn std::error::Error>> {
    // Discover all services and characteristics
    let services = device.discover_services().await?;

    // convert uuid string into uuid target
    let target_uuid = Uuid::parse_str(characteristic_uuid_str)?;

    // get the bluetooth service
    for service in services {
        let characteristics = service.characteristics().await?;

        // loop through the characteristics
        for characteristic in characteristics {
            // get the uuid
            let uuid = characteristic.uuid();

            // if uuid does not match, go to next characteristic
            if uuid != target_uuid {
                continue;
            }

            let props = characteristic.properties().await?;

            // characteristic cannot be read
            if !props.read {
                return Err("Characteristic is not readable".into());
            }

            // characteristic can be read
            let raw: Vec<u8> = characteristic.read().await?;

            if raw.len() != 4 {
                return Err("Expected 4 bytes for f32".into());
            }

            let val = f32::from_le_bytes(raw[..4].try_into()?);
            return Ok(val);
        }
    }

    Err(format!("Characteristic {} not found", characteristic_uuid_str).into())
}

// read unsigned64 device's characteristics
async fn read_ble_u64_characteristic(
    device: &Device,
    characteristic_uuid_str: &str,
) -> Result<u64, Box<dyn std::error::Error>> {
    // Discover all services and characteristics
    let services = device.discover_services().await?;

    // convert uuid string into uuid target
    let target_uuid = Uuid::parse_str(characteristic_uuid_str)?;

    // get the bluetooth service
    for service in services {
        let characteristics = service.characteristics().await?;

        // loop through the characteristics
        for characteristic in characteristics {
            // get the uuid
            let uuid = characteristic.uuid();

            // if uuid does not match, go to next characteristic
            if uuid != target_uuid {
                continue;
            }

            let props = characteristic.properties().await?;

            // characteristic cannot be read
            if !props.read {
                return Err("Characteristic is not readable".into());
            }

            // characteristic can be read
            let raw: Vec<u8> = characteristic.read().await?;

            if raw.len() != 8 {
                return Err("Expected 8 bytes for u64".into());
            }

            let val = u64::from_le_bytes(raw[..8].try_into()?);
            return Ok(val);
        }
    }

    Err(format!("Characteristic {} not found", characteristic_uuid_str).into())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Get the default Bluetooth adapter
    let adapter = Adapter::default()
        .await
        .ok_or("Bluetooth adapter not found")?;
    adapter.wait_available().await?;

    // scan for all devices with the service ID
    println!("Scanning for BLE devices...");
    // IMU sensor UUIDs as Uuids
    let service_uuid = Uuid::parse_str(SERVICE_UUID_STR)?;
    let services = &[service_uuid];
    let mut scan = adapter.scan(services).await?;
    sleep(Duration::from_secs(5)).await; // wait for scan results

    // Collect and print all matching devices
    let mut devices = Vec::new();
    while let Some(result) = scan.next().await {
        // get the device
        let name: String = result.device.name().unwrap();
        // let name: String = result
        //     .device
        //     .name()
        //     // .await?
        //     .into_iter()
        //     .flatten()
        //     .unwrap_or("(unknown)".to_string());
        
        // print the device and add it to our list
        println!("{}: {} (RSSI: {:?})", devices.len(), name, result.rssi);
        devices.push(result.device);
    }

    // if no devices, return
    if devices.is_empty() {
        println!("No devices found with the given service UUID.");
        return Ok(());
    }

    // Ask user to choose a device
    print!("\nEnter device number to connect: ");
    io::stdout().flush()?; // flush stdout so prompt appears
    let mut input = String::new();
    io::stdin().read_line(&mut input)?;
    let index: usize = input.trim().parse()?;

    if index >= devices.len() {
        println!("Invalid index.");
        return Ok(());
    }

    // Connect to selected device
    let selected_device = &devices[index];
    println!("Connecting to device {}...", index);
    adapter.connect_device(selected_device).await?;
    println!("Connected!");

    // Spawn a task to handle Ctrl+C
    let mut shutdown_signal = tokio::spawn(async {
        signal::ctrl_c().await.expect("Failed to listen for Ctrl+C");
        println!("\nReceived Ctrl+C. Disconnecting...");
    });

        // Reading loop
    loop {
        // wait for multiple async operations, and proceed with whichever finishes first
        tokio::select! {
            // option to handle shutdown signal
            _ = &mut shutdown_signal => {
                break;
            }
            // other option
            _ = async {
                // read data from the device characteristics
                let ax: f32 = read_ble_f32_characteristic(&selected_device, SWITCH_CHARACTERISTIC_ACCEL_X_UUID_STR).await?;
                let ay: f32 = read_ble_f32_characteristic(&selected_device, SWITCH_CHARACTERISTIC_ACCEL_Y_UUID_STR).await?;
                let az: f32 = read_ble_f32_characteristic(&selected_device, SWITCH_CHARACTERISTIC_ACCEL_Z_UUID_STR).await?;
                // let gx: f32 = read_ble_f32_characteristic(&device, SWITCH_CHARACTERISTIC_GYRO_X_UUID_STR).await?;
                // let gy: f32 = read_ble_f32_characteristic(&device, SWITCH_CHARACTERISTIC_GYRO_Y_UUID_STR).await?;
                // let gz: f32 = read_ble_f32_characteristic(&device, SWITCH_CHARACTERISTIC_GYRO_Z_UUID_STR).await?;
                let time: u64 = read_ble_u64_characteristic(&selected_device, SWITCH_CHARACTERISTIC_CURRENT_TIME_UUID_STR).await?;

                println!("{:.2},{:.2},{:.2},{}", ax, ay, az, time);

                // sleep to give time. might affect results?
                sleep(Duration::from_millis(500)).await;

                Ok::<(), Box<dyn std::error::Error>>(())
            } => {}
        }
    }

    // Disconnect from device
    adapter.disconnect_device(selected_device).await?;
    println!("Disconnected.");

    Ok(())
}
