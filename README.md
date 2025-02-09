# Face Recognition Attendance System

This project is a Face Recognition Attendance System that uses webcam feed to detect and recognize faces, and logs the attendance of recognized individuals into an Excel sheet. The system is designed to be simple, efficient, and easy to use.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The Face Recognition Attendance System is a Python-based application that leverages the power of OpenCV and the `face_recognition` library to detect and recognize faces in real-time. It logs the attendance of recognized individuals into an Excel file, making it easy to track attendance over time.

## Features

- Real-time face detection and recognition.
- Logs attendance with date and time.
- Stores attendance data in an Excel file.
- Simple and easy-to-use interface.
- Configurable list of students with their roll numbers.

## Requirements

To run this project, you need the following Python libraries installed:

- `opencv-python`
- `face_recognition`
- `openpyxl`
- `numpy`

You can install these libraries using pip:

```bash
pip install opencv-python face_recognition openpyxl numpy
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/face-recognition-attendance-system.git
   ```

2. Navigate to the project directory:

   ```bash
   cd face-recognition-attendance-system
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Place the student images in the `student_images` folder. The images should be named after the students (e.g., `Jafir.jpg`, `Hasib.jpg`).

## Usage

1. Run the script:

   ```bash
   python attendance_system.py
   ```

2. The webcam feed will open, and the system will start detecting faces. Recognized faces will be logged into the `attendance.xlsx` file.

3. Press `q` to exit the application.

## Configuration

You can configure the list of students and their roll numbers by modifying the `name_to_roll` dictionary in the script:

```python
name_to_roll = {
    "Jafir": 3,
    "Hasib": 10,
    "Hasan": 26,
    "Rafi": 18,
    "Masrafi": 25,
    "Md.Sanzis Hasnat": 26,
    "Md.Rafshan Jani": 27
}
```

You can also change the path to the student images and the name of the Excel file by modifying the following variables:

```python
path = 'student_images'
excel_file = 'attendance.xlsx'
```

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeatureName`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeatureName`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Thank you for using the Face Recognition Attendance System! If you have any questions or need further assistance, feel free to reach out.

Happy coding! 🚀
