# Eldom Boiler Home Assistant Integration

This Home Assistant integration allows you to monitor and control your Eldom Boiler. The integration leverages WebSocket communication to fetch real-time data from your boiler and integrates it with Home Assistant sensors for easy monitoring.

## Features
- Real-time temperature readings (Cylinder 1 and Cylinder 2).
- Energy consumption tracking (Day and Night).
- Power status and boiler state monitoring.
- Integration with Home Assistant sensors for seamless interaction.
  
## Installation

### Manual Installation

1. Download the `ha-eldom-boiler-integration` repository from [GitHub](https://github.com/gizmo-boss/ha-eldom-boiler-integration).
2. Extract the files and place them in the `custom_components/eldom/` directory within your Home Assistant configuration directory.
3. Ensure that your configuration directory contains the following structure:

    ```bash
    └── custom_components
        └── eldom
            ├── __init__.py
            ├── config_flow.py
            ├── const.py
            ├── sensor.py
            ├── manifest.json
    ```

4. Restart Home Assistant.

## Configuration

1. After installation, go to the Home Assistant UI and navigate to the **Configuration** page.
2. Click on **Devices & Services** and then click on the **Add Integration** button.
3. Search for "Eldom Boiler" in the list and select it.
4. Enter the boiler ID when prompted.

Once configured, sensors for your boiler’s state, temperature, and energy consumption will automatically be added.

## Sensors

The following sensors are available after integration:

- **Set Temperature** (SetTemp): The target temperature for the boiler.
- **Power State** (State): Indicates whether the boiler is on or off.
- **Temperature Cylinder 1** (STL_Temp): Temperature of the first cylinder.
- **Temperature Cylinder 2** (FT_Temp): Temperature of the second cylinder.
- **Energy Consumption Day** (EnergyD): Energy consumption during the day in kWh.
- **Energy Consumption Night** (EnergyN): Energy consumption during the night in kWh.
- **Power Status** (PowerFlag): Shows the current power status of the boiler.

## Requirements

- Home Assistant version 2021.11 or newer.
- Active internet connection to communicate with Eldom Boiler API (via WebSocket).

## Known Issues

- Delayed data updates if the WebSocket connection is interrupted.

## Links

- [GitHub Repository](https://github.com/gizmo-boss/ha-eldom-boiler-integration)
- [Home Assistant Documentation](https://www.home-assistant.io/docs/)
