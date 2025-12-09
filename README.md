# Hades

December 9th, 2025

This project provides a complete solution for running Postgres 18 in Docker with Python 3.12 integration, automated dependency management, and a full test suite. It is one that I use as a base for coding projects.

The project includes a management script (`start.sh`) that handles container lifecycle, Python virtual environment setup, dependency installation, and connection testing. All components are designed to work together seamlessly with minimal configuration required.

## Documentation

For detailed information, see the following documentation files:

- **[start.sh Script Guide](doc/README-start.md)** - Complete documentation for the main management script
- **[Docker Management Guide](doc/README-docker.md)** - Quick reference for Docker commands and container management
- **[Test Suite Documentation](doc/README-test-suite.md)** - Guide to running and understanding the automated test cases
- **[Git Workflow Guide](doc/README-git.md)** - Step-by-step instructions for Git operations in Cursor IDE

## Quick Start

1. Ensure Docker and Python 3.12 are installed
2. Configure `.env` file with the included env.example file for your Postgres credentials
3. Run `./start.sh start` to initialize and start the database
4. Use `./start.sh status` to verify everything is working

For more details, see the [start.sh Script Guide](doc/README-start.md).


