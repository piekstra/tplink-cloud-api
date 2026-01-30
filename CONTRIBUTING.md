# Contributing to tplink-cloud-api

Thanks for your interest in contributing! This document outlines how to get started.

## Development setup

1. Clone the repository:
   ```bash
   git clone https://github.com/piekstra/tplink-cloud-api.git
   cd tplink-cloud-api
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Running tests

This project uses `wiremock` to mock the TP-Link API for testing.

1. Start the wiremock service:
   ```bash
   docker compose up -d
   ```

2. Run the tests:
   ```bash
   pytest --verbose
   ```

See the [Testing section](README.md#testing) in the README for details on environment configuration.

## Submitting changes

1. Fork the repository
2. Create a feature branch (`git checkout -b my-feature`)
3. Make your changes
4. Run tests to ensure they pass
5. Commit your changes with a descriptive message
6. Push to your fork and open a pull request

## Adding support for new devices

If you'd like to add support for a new TP-Link device:

1. Open an issue first to discuss the device and its capabilities
2. If you have the device, capture the API responses it produces (device info, sys info, etc.)
3. Add wiremock mappings in `tests/wiremock/mappings/` for the new device
4. Implement the device class following existing patterns
5. Add tests for the new device
6. Update the README with the new device in the compatibility list

## Questions?

Feel free to open an issue if you have questions or need help getting started.
