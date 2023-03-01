import os

HOME = os.getcwd()
FETCH_INTERVAL = os.getenv("FETCH_INTERVAL", 20)

POSTGRES_DATABASE = os.environ["POSTGRES_DATABASE"]
POSTGRES_USERNAME = os.environ["POSTGRES_USERNAME"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_PORT = os.environ["POSTGRES_PORT"]

RABBITMQ_HOST = os.environ["RABBITMQ_HOST"]
RABBITMQ_PORT = os.environ["RABBITMQ_PORT"]


def cron_standard():
    # Writing to custom cron file
    with open("cron.txt", "w") as cron_file:

        # Convenience function to append newline to each write
        write = lambda fh, msg: fh.write("\n" + msg)

        # Default cron jobs env variables
        write(cron_file, f"HOME={HOME}")
        write(cron_file, f"POSTGRES_DATABASE={POSTGRES_DATABASE}")
        write(cron_file, f"POSTGRES_USERNAME={POSTGRES_USERNAME}")
        write(cron_file, f"POSTGRES_PASSWORD={POSTGRES_PASSWORD}")
        write(cron_file, f"POSTGRES_HOST={POSTGRES_HOST}")

        write(cron_file, f"RABBITMQ_HOST={RABBITMQ_HOST}")
        write(cron_file, f"RABBITMQ_PORT={RABBITMQ_PORT}")

        write(
            cron_file,
            f"*/{FETCH_INTERVAL} * * * * $(which python3) main.py >> logs.log 2>&1",
        )


def cron_offset():
    # Writing to custom cron file
    with open("cron.txt", "w") as cron_file:

        # Convenience function to append newline to each write
        write = lambda fh, msg: fh.write("\n" + msg)

        # Default cron jobs env variables
        write(cron_file, f"HOME={HOME}")
        write(cron_file, f"POSTGRES_DATABASE={POSTGRES_DATABASE}")
        write(cron_file, f"POSTGRES_USERNAME={POSTGRES_USERNAME}")
        write(cron_file, f"POSTGRES_PASSWORD={POSTGRES_PASSWORD}")
        write(cron_file, f"POSTGRES_HOST={POSTGRES_HOST}")

        write(cron_file, f"RABBITMQ_HOST={RABBITMQ_HOST}")
        write(cron_file, f"RABBITMQ_PORT={RABBITMQ_PORT}")

        # Reading the contents of CSV file for cron specific env variables
        with open("./urls.csv", "r") as csvfile:

            counter, offset = 1, 0

            for cron in csvfile:
                source, location = cron.split(",")

                write(cron_file, "\n")
                write(cron_file, f"URL={source}")
                write(cron_file, f"URL_LOCATION={location}")
                write(
                    cron_file,
                    f"{offset}-*/{FETCH_INTERVAL} * * * * $(which python3) main.py >> logs.log 2>&1",
                )

                # Every 3rd task will start with 1 minute offset
                if counter % 2 == 0:
                    offset += 1
                counter += 1
