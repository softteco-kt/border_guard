import os
import shutil

HOME = os.getcwd()
FETCH_INTERVAL = os.getenv("FETCH_INTERVAL", 20)

POSTGRES_DATABASE = os.environ["POSTGRES_DATABASE"]
POSTGRES_USERNAME = os.environ["POSTGRES_USERNAME"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_PORT = os.environ["POSTGRES_PORT"]

RABBITMQ_HOST = os.environ["RABBITMQ_HOST"]
RABBITMQ_PORT = os.environ["RABBITMQ_PORT"]

IMAGE_EXCHANGE = os.environ["IMAGE_EXCHANGE"]
IMAGE_ROUTING_KEY = os.environ["IMAGE_ROUTING_KEY"]
IMAGE_QUEUE = os.environ["IMAGE_QUEUE"]


class CronActions:
    def __init__(self) -> None:
        self.file_handler = None
        self.action_args = None

    def write_to_file(self, file: str = None):
        # Write to a file and append newline to each write
        self.file_handler = open(file, "w")
        self.write_to = lambda fh, msg: fh.write("/n" + msg)
        return self

    def write_to_stdout(self):
        # If writing directly to cron file is not required
        self.write_to = lambda _, msg: print(msg)
        return self

    def __del__(self):
        if self.file_handler:
            self.file_handler.close()


class CronBuilder(CronActions):
    """Builder for cron job descriptor. Specifies what goes into cron file."""

    def set_envs(self):
        """Default contents of cron file, that contains environment variables."""
        # Default cron jobs env variables
        self.write_to(self.file_handler, f"HOME={HOME}")
        self.write_to(self.file_handler, f"POSTGRES_DATABASE={POSTGRES_DATABASE}")
        self.write_to(self.file_handler, f"POSTGRES_USERNAME={POSTGRES_USERNAME}")
        self.write_to(self.file_handler, f"POSTGRES_PASSWORD={POSTGRES_PASSWORD}")
        self.write_to(self.file_handler, f"POSTGRES_HOST={POSTGRES_HOST}")
        self.write_to(self.file_handler, f"POSTGRES_PORT={POSTGRES_PORT}")

        self.write_to(self.file_handler, f"RABBITMQ_HOST={RABBITMQ_HOST}")
        self.write_to(self.file_handler, f"RABBITMQ_PORT={RABBITMQ_PORT}")

        self.write_to(self.file_handler, f"IMAGE_EXCHANGE={IMAGE_EXCHANGE}")
        self.write_to(self.file_handler, f"IMAGE_ROUTING_KEY={IMAGE_ROUTING_KEY}")
        self.write_to(self.file_handler, f"IMAGE_QUEUE={IMAGE_QUEUE}")
        return self

    def set_standard(self):
        """Extends the contents of cron defaults and adds single cron command."""
        # The cron itself
        self.write_to(
            self.file_handler,
            f"*/{FETCH_INTERVAL} * * * * {shutil.which('python3')} main.py >> logs.log 2>&1",
        )
        return self

    def set_offset(self):
        """Extends the behaviour of standard cron script with cron per source logic."""

        # Reading the contents of CSV file for cron specific env variables
        with open("./urls.csv", "r") as csvfile:

            counter, offset = 1, 0

            for cron in csvfile:
                source, location = cron.split(",")

                self.write_to(self.file_handler, "\n")
                self.write_to(self.file_handler, f"URL={source}")
                self.write_to(self.file_handler, f"URL_LOCATION={location}")
                self.write_to(
                    self.file_handler,
                    f"{offset}-59/{FETCH_INTERVAL} * * * * {shutil.which('python3')} main.py >> logs.log 2>&1",
                )

                # Every 3rd task will start with 1 minute offset
                if counter % 2 == 0:
                    offset += 1
                counter += 1
        return self


if __name__ == "__main__":
    CronBuilder().write_to_stdout().set_envs().set_standard()
