# Bare Metal Arduino R4 with E2 Studio

Credits:

* [Eric M. Klaus](https://sites.google.com/site/ericmklaus/home?authuser=0) for Project Setup
* [Renesas Flexible Software Package Documentation](https://renesas.github.io/fsp)
* [Arduino Bootloader](https://github.com/arduino/ArduinoCore-renesas/blob/main/bootloaders/UNO_R4/README.md)
* ChatGPT Responses


## Getting Started

### Download & Install the required software

 As well as installing e2 Studio you must install the Arduino 2.0 IDE Software and then install board support for the Arduino Uno R4 WiFi board and also install the arduino-cli utility (optional).



[arduino-cli Optional]

1. Download and install the Arduino CLI from here: https://arduino.github.io/arduino-cli/0.35/installation/
2. Unpack the arduino-cli.exe file and copy it to: C:\Renesas\RA\e2_studio  (inside the e2 Studio install location)
3. Create "cli.bat":
4. In this same folder, create a file named "cli.bat" and paste the following line:

   `arduino-cli upload -v -i %2.bin -p %1 -b arduino:renesas_uno:unor4wifi`

  (we'll use this later when we configure an external tool to flash the device)

### Configure and build a simple project.

1. Now create a new Renesas C/C++ Project.
2. Board = "Custom User Board(Any Device)"
3. Device = "R7FA4M1AB3CFM"  (*this is NOT the default you'll have to find it)
4. Click Next make sure "Executable" is selected and click Next again.
5. Select "Bare Metal-Minimal" (the only option) and click Finish. 
   You should be in the FSP Configuration Perspective (if not, double click on the configuration.xml file)
6. Select the "BSP" tab  verify device is  R7FA4M1AB3CFM
7. In the lower portion UNDER the configuration window find the "Properties" tab
8. Expand the "RA Common" section
9. Set Heap Size (bytes)  to 0x2000   (from 0 )
10. Set Main Oscillator Populated  to "Not Populated"
11. Set Subclock Populated  to "Not Populated"
12. Goto the "Clocks" tab  
13. Set PLL Src: = Disabled
14. Change Clock Src: to HOCO
15. Change HOCO 24Mhz to HOCO 48Mhz
16. Change UCLK Src: to HOCO
17. Goto the "Pins" tab  then find and select the P102 pin.
18. Set Symbolic Name = LED_PIN
19. Set Mode = Output mode (initial Low)
20. Change Drive Capacity to Medium
21. Click "Generate Project Content"  (in upper right)

### Build the project... (just to create the \Debug folder with memory_regons.ld)

### Extract and modify the linker script files.  

1. From the new projects `\Debug` folder:
   Copy `memory_regions.ld` to the "script" folder of the new project
   Rename this copy of `memory_regions.ld` to `memory_regions_r4.ld` (this step protects the file from being cleaned & re-generated)
2. In "script" folder, Edit fsp.ld 
   Change `INCLUDE memory_regions.ld` to `INCLUDE memory_regions_r4.ld`
3. Edit memory_regions_r4.ld
   add these 3 lines to the end of the file:
```
FLASH_IMAGE_START = 0x4000;
VECTOR_TABLE_LENGTH = 0x100;
BSP_CFG_STACK_MAIN_BYTES = 0x400;
```
**NOTE: you may want to save a copy of these 2 modified files**

### Edit: src\hal_entry.c

After the comment line "/* TODO: add your own code here */"

Copy and insert these C code
```C
while(1)
{
    R_IOPORT_PinWrite(&g_ioport_ctrl, LED_PIN, BSP_IO_LEVEL_HIGH);

    R_BSP_SoftwareDelay (250, BSP_DELAY_UNITS_MILLISECONDS);

    R_IOPORT_PinWrite(&g_ioport_ctrl, LED_PIN, BSP_IO_LEVEL_LOW);

    R_BSP_SoftwareDelay (250, BSP_DELAY_UNITS_MILLISECONDS);
}
```

### Update the IDE settings to create a .bin file

1. Right click on the projct name and select "Properties"  (bottom of list)
2. At top, Set Configuration: = [All configurations]
3. Expand C/C++ Build and select "Settings"
4. Select "General" under "GNU Arm Cross Create Flash Image"
5. Change "Output file format(-O)" from "Motorola S-record" to "Raw Binary"
6. Check both "Section:-j.text" and "Section-j.data" checkboxes.
7. Click "Apply & Close"

### Re-Buid the new project (it should build withiout warnings or errors)
A new *.bin file should have been created in the Debug folder.

## Flashing the Arduino R4

The arduino r4 bootloader responds to the two baud rates
* 1200bps: triggers the bootloader mode for RA4 chip
* 2400bps: triggers ROM DFU mode

To flash our .bin file to the RA4M1 chip, we need to first perform a 1200-bps touch reset on serial port COMX

Use the following code to perform a touch reset with the R4
```py
import serial
import time

# Set up the serial connection
ser = serial.Serial('COM6', 1200)  # Open COM6 at 1200 baud rate
time.sleep(1)  # Wait a moment for the connection to establish

# Send a newline character (or any other character) to trigger the reset
ser.write(b'\r')  # \r = Carriage return, or \n = newline
ser.close()
```

Once complete, flash the .bin file to the R4 chip
`-d` is optional (for debugging)

`-U` This option tells bossac to perform a reset on the board after programming. It's required to ensure that the board runs the new firmware after it has been uploaded.

`-e` This option tells bossac to erase the flash before writing new data to it. It ensures that the memory is clean and free of old data, which prevents issues when uploading the new firmware.

`-w` This option tells bossac to write the firmware file to the board's flash memory.

`-R` This option tells bossac to reset the board after the upload is complete, ensuring the board restarts with the new program running.

```bat
"C:\Users\username\AppData\Local\Arduino15\packages\arduino\tools\bossac\1.9.1-arduino5/bossac" -d --port=COM6 -U -e -w ./Blinky.bin -R
```
