import os
import sys
import csv


def main():
    """Check if folder contains directory for specific camera location."""
    data_folder = "./data/"

    with open("urls.csv", "r") as f:
        csvreader = csv.reader(f)
        for row in csvreader:
            # Second row contains camera location name
            camera_name = row[1]
            # Check if folder exists else create one
            camera_specific_folder = data_folder + camera_name
            if not os.path.exists(camera_specific_folder):
                os.makedirs(camera_specific_folder)


if __name__ == "__main__":
    main()
