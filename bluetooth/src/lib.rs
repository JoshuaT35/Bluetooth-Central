use std::io::{self, Write};
use std::convert::TryInto;
use tokio::time::{sleep, Duration};
use tokio::signal;
use bluest::{Adapter, Uuid, Device};
use futures_util::StreamExt;    // maybe futures_lite instead? in examples/pair.rs

use pyo3::prelude::*;
use pyo3::types::{PyTuple, PyFloat};
use pyo3::{PyObject, Python};
use pyo3::wrap_pyfunction;

/// UUIDs for your BLE IMU service and characteristics
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

// Expose the module to Python
#[pymodule]
fn bluetooth(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(start_ble_stream, m)?)?;
    Ok(())
}

// Python-callable function that runs BLE code in a background task
#[pyfunction]
fn start_ble_stream(py_callback: PyObject) -> PyResult<()> {
    std::thread::spawn(move || {
        let rt = tokio::runtime::Runtime::new().unwrap();
        rt.block_on(async move {
            if let Err(e) = run_ble_stream(py_callback).await {
                eprintln!("BLE error: {:?}", e);
            }
        });
    });

    Ok(())
}

/// Async function to scan, connect, read, and stream IMU data
async fn run_ble_stream(callback: PyObject) -> Result<(), Box<dyn std::error::Error>> {
    let adapter = Adapter::default()
        .await
        .ok_or("Bluetooth adapter not found")?;
    adapter.wait_available().await?;

    println!("Scanning for BLE devices...");
    let service_uuid = Uuid::parse_str(SERVICE_UUID_STR)?;
    let services = &[service_uuid];
    let mut scan = adapter.scan(services).await?;

    // give time for adapter to scan
    sleep(Duration::from_secs(5)).await;

    // store devices
    let mut devices = Vec::new();

    // NOTE: does not normally break out of while loop, so manual break (dirty and inefficient)
    while let Some(result) = scan.next().await {
        let name = result.device.name().unwrap_or("(unknown)".to_string());
        println!("{}: {} (RSSI: {:?})", devices.len(), name, result.rssi);
        devices.push(result.device);
        break;
    }

    if devices.is_empty() {
        println!("No devices found.");
        return Ok(());
    }

    print!("\nEnter device number to connect: ");
    io::stdout().flush()?;
    let mut input = String::new();
    io::stdin().read_line(&mut input)?;
    let index: usize = input.trim().parse()?;

    if index >= devices.len() {
        println!("Invalid index.");
        return Ok(());
    }

    let selected_device = &devices[index];
    println!("Connecting to device {}...", index);
    adapter.connect_device(selected_device).await?;
    println!("Connected!");

    let mut shutdown_signal = tokio::spawn(async {
        signal::ctrl_c().await.expect("Failed to listen for Ctrl+C");
        println!("\nReceived Ctrl+C. Disconnecting...");
    });

    loop {
        tokio::select! {
            _ = &mut shutdown_signal => break,
            result = async {
                let ax = read_ble_f32_characteristic(selected_device, SWITCH_CHARACTERISTIC_ACCEL_X_UUID_STR).await?;
                let ay = read_ble_f32_characteristic(selected_device, SWITCH_CHARACTERISTIC_ACCEL_Y_UUID_STR).await?;
                let az = read_ble_f32_characteristic(selected_device, SWITCH_CHARACTERISTIC_ACCEL_Z_UUID_STR).await?;
                let time = read_ble_u64_characteristic(selected_device, SWITCH_CHARACTERISTIC_CURRENT_TIME_UUID_STR).await?;
            
                Ok::<_, Box<dyn std::error::Error>>((ax, ay, az, time))
            } => {
                match result {
                    Ok((ax, ay, az, time)) => {
                        // debug: print data
                        // println!("Read data: ax={} ay={} az={} time={}", ax, ay, az, time);

                        // Call Python callback with values
                        let _ = Python::with_gil(|py| -> PyResult<()> {
                            let args = PyTuple::new(
                                py,
                                &[
                                    PyFloat::new(py, ax as f64),  // Convert f32 → Python float (f64)
                                    PyFloat::new(py, ay as f64),
                                    PyFloat::new(py, az as f64),
                                    PyFloat::new(py, time as f64),
                                ],
                            ).unwrap();
                            callback.call1(py, &args)?;  // Pass the bound tuple
                            Ok(())
                        });

                        sleep(Duration::from_millis(500)).await;

                        // Ok::<_, Box<dyn std::error::Error>>(())
                    },
                    Err(e) => {
                        eprintln!("Error during read loop: {}", e);
                        break;
                    }
                }
            }
        }
    }

    adapter.disconnect_device(selected_device).await?;
    println!("Disconnected.");
    Ok(())
}

// Read BLE float32
async fn read_ble_f32_characteristic(device: &Device, uuid_str: &str) -> Result<f32, Box<dyn std::error::Error>> {
    let services = device.discover_services().await?;
    let target_uuid = Uuid::parse_str(uuid_str)?;

    for service in services {
        for characteristic in service.characteristics().await? {
            if characteristic.uuid() == target_uuid {
                if !characteristic.properties().await?.read {
                    return Err("Characteristic is not readable".into());
                }
                let raw = characteristic.read().await?;
                if raw.len() != 4 {
                    return Err("Expected 4 bytes for f32".into());
                }
                return Ok(f32::from_le_bytes(raw[..4].try_into()?));
            }
            else {
            }
        }
    }

    Err(format!("Characteristic {} not found", uuid_str).into())
}

// Read BLE u64
async fn read_ble_u64_characteristic(device: &Device, uuid_str: &str) -> Result<u64, Box<dyn std::error::Error>> {
    let services = device.discover_services().await?;
    let target_uuid = Uuid::parse_str(uuid_str)?;

    for service in services {
        for characteristic in service.characteristics().await? {
            if characteristic.uuid() == target_uuid {
                if !characteristic.properties().await?.read {
                    return Err("Characteristic is not readable".into());
                }
                let raw = characteristic.read().await?;
                match raw.len() {
                    4 => {
                        let val = u32::from_le_bytes(raw[..4].try_into()?);
                        return Ok(val as u64);
                    }
                    8 => {
                        return Ok(u64::from_le_bytes(raw[..8].try_into()?));
                    }
                    _ => return Err(format!("Unexpected byte length for u64: {}", raw.len()).into()),
                }
            }
        }
    }

    Err(format!("Characteristic {} not found", uuid_str).into())
}
